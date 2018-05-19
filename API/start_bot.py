import sys

import requests

from telegram_bot import Bot

EKB_ID = '1486209'
W_TOKEN = '93c5495ecda2427c3e8852c732d9b84c'
try:
    t_token = sys.argv[1]
    bot = Bot(t_token, W_TOKEN, EKB_ID)
    bot.run()
except requests.exceptions.RequestException:
    print('Ошибка доступа к серверам телеграма. Вероятно вы предварительно не запустили VPN :)')
except Exception as e:
    print('Укажите корректный токен телеграм бота (без скобок): python3 start_bot.py <TOKEN>')
