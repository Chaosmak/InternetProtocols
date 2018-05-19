import requests


def get_weather(id, token):
    data = requests.get("http://api.openweathermap.org/data/2.5/weather",
                        params={'id': id, 'units': 'metric', 'lang': 'ru', 'APPID': token}).json()
    return f"{data['weather'][0]['description'].title()}\n{data['main']['temp']}°C"
