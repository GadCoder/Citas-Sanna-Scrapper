import os
from datetime import datetime

import requests
from dotenv import load_dotenv

from telegram_messages import send_telegram_message


load_dotenv()


TOKEN = os.getenv("TOKEN")
DNI = os.getenv("DNI")
TOKEN_PUSH = os.getenv("TOKEN_PUSH")


base_headers = {
    'Accept-Encoding': 'gzip',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json; charset=UTF-8',
    'Host': 'app.sanna.pe',
    "User-Agent": 'okhttp/4.9.2'
}


def get_current_day() -> str:
    current_date = datetime.now()
    formatted_date = current_date.strftime("%d/%m/%Y")
    return formatted_date


def make_post_request(url, headers, data) -> None | dict:
    request = requests.post(url=url, headers=headers, json=data)
    print(request.status_code)
    if request.status_code != 200:
        return None
    return request.json()


def login_token_updated_succesfully() -> bool:
    url = 'https://app.sanna.pe/Usuario.svc/ActualizarTokenPush/'
    headers = base_headers
    headers['Content-Length'] = '228'
    headers['token'] =  TOKEN
    data = {
        "numeroDocumento": DNI,
        "tipoDocumento": "1",
        "tokenPush": TOKEN_PUSH
    }
    request = make_post_request(url=url, headers=headers, data=data)
    if request is None:
        print(f"Error updating token")
        return False
    print(f"Token updated succesfully")
    return True
        
        
def get_schedules(current_date: str) -> None | dict:
    url = 'https://app.sanna.pe/Medico.svc/HorariosPorMedico/'
    headers = base_headers
    headers['Content-Length'] = '108'
    headers['token'] = TOKEN
    data = {
        "dia": current_date,
        "idClinica": "22",
        "idEspecialidad": "31",
        "numeroDocumento": DNI,
        "tipoDocumento": "1"
    }
    request = make_post_request(url=url, headers=headers, data=data)
    if request is None:
        print(f"Ups. Couldn't get schedules")
    else:
        print(f"No problem getting schedules buddy")
    return request


def no_appointments_available(schedules: dict) -> bool:
    for doctor_data in schedules["data"]:
        next_appointment = doctor_data["fechaProxima"]
        if next_appointment is not None:
            return True
    return False


def parse_schedules(schedules: dict, current_date: str):
    message = f"*CITAS - {current_date}*\n"
    for doctor_data in schedules["data"]:
        doctor_name = doctor_data["nombres"]
        next_appointment = doctor_data["fechaProxima"]
        if next_appointment is None:
            sub_msg = f"👩🏽‍⚕️ {doctor_name}: \n    No hay citas disponibles ☹️\n"
        else:
            sub_msg = f"👩🏽‍⚕️ {doctor_name}: \n    🗓️ {next_appointment}\n"
        message += sub_msg
        message += "\n"
    send_telegram_message(message=message)


def main():
    if login_token_updated_succesfully():
        current_date = get_current_day()
        schedules = get_schedules(current_date=current_date)
        if no_appointments_available(schedules=schedules):
            msg = "No hay citas disponibles para hoy ☹️"
            send_telegram_message(message=msg)
            return
        parse_schedules(schedules=schedules, current_date=current_date)


if __name__ == "__main__":
    main()
