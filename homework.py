import os
import time
import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# По второму замечанию нельзя ввести в функцию send_message
# второй параметр, иначе тесты не проходят.
# Что бы не вызывать создание бота при каждой отправке сообщения
# 
bots = {'telebot': telegram.Bot(token=TELEGRAM_TOKEN), }


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    if homework.get('status') != 'approved':
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    params = {'from_date': current_timestamp}
    hw_url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    homework_statuses = requests.get(hw_url, params=params, headers=headers)
    return homework_statuses.json()


def send_message(message):
    return bots['telebot'].send_message(
        chat_id=CHAT_ID, 
        text='Код проверен, можно смотреть и радоваться. Или нельзя...'
        )


def main():
    current_timestamp = int(time.time())  # начальное значение timestamp
    
    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(new_homework.get('homeworks')[0]))
            current_timestamp = new_homework.get('current_date')  # обновить timestamp
            time.sleep(300)  # опрашивать раз в пять минут

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
