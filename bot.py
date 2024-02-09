import requests


class TGBOT:
    def __init__(self, token: str):
        self.token = token
        self.bot_url = f'https://api.telegram.org/bot{token}/'

    def sendMessage(self, params: dict) -> str:
        r = requests.post(url=(f'{self.bot_url}sendMessage'), params=params)
        if r.status_code == 200:
            return (r.text)
