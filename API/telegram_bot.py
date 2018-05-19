import json

import requests

from weather import get_weather


class Bot:
    def __init__(self, t_token, w_token, city_id):
        self.url = 'https://api.telegram.org/bot' + t_token
        self.w_token = w_token
        self.city_id = city_id

    def run(self):
        offset = None
        while True:
            updates = self.send_request('getUpdates', offset=offset)
            for update in updates['result']:
                method_name, answer = self.handle_update(update)
                if answer:
                    self.send_request(method_name, **answer)
                offset = update['update_id'] + 1

    def send_request(self, method_name, **kwargs):
        response = requests.post('{}/{}'.format(self.url, method_name),
                                 params=kwargs)
        return response.json()

    def handle_update(self, update):
        right_msg = 'Получить текущий прогноз'
        try:
            id = update['message']['from']['id']
            text = update['message']['text']
            reply_markup = json.dumps({'keyboard': [[right_msg]], 'resize_keyboard': True})
            if text == right_msg:
                weather = get_weather(self.city_id, self.w_token)
                return 'sendMessage', {'text': weather, 'chat_id': id,
                                       'reply_markup': reply_markup}
            elif text == '/start':
                return 'sendMessage', {'text': 'Узнавайте текущую погоду в Екб.', 'chat_id': id,
                                       'reply_markup': reply_markup}
        except Exception as e:
            pass
        return None, None
