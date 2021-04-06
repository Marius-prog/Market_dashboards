import requests


class IEXStock:

    def __init__(self, token, symbol):
        self.BASE_URL = 'https://cloud.iexapis.com/stable'
        self.token = token
        self.symbol = symbol

    def get_logo(self):
        url = f'{self.BASE_URL}/stock/{self.symbol}/logo?token={self.token}'
        r = requests.get(url)

        return r.json()

    def get_company_info(self):
        url = f'https://cloud.iexapis.com/stable/stock/{self.symbol}/company?token={self.token}'
        r = requests.get(url)

        return r.json()

    def get_stats(self):
        url = f'https://cloud.iexapis.com/stable/stock/{self.symbol}/advanced-stats?token={self.token}'
        r = requests.get(url)

        return r.json()

    def get_company_news(self, last=10):
        url = f"{self.BASE_URL}/stock/{self.symbol}/news/last/{last}?token={self.token}"
        r = requests.get(url)

        return r.json()
