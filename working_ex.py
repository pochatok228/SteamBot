import logging

import requests
from bs4 import BeautifulSoup


class Parser(object):
    baseurl = 'https://steamdb.info/calculator/'

    def __init__(self, currency='us', cookies={}):
        self.currency = currency
        self.__headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0'
        }
        self.__cookies = cookies
        logging.info(
            'New instance of SteamDB Profile Parser has been instanciated'
        )
        



    def getSteamDBProfile(self, steamId):

        steamDBUrl = f'{self.baseurl}{steamId}/?cc={self.currency}'
        steamDBUrl = 'https://steamdb.info/sales/'
        try:
            logging.info(f'Requesting {steamDBUrl}')
            r = requests.get(
                steamDBUrl, headers=self.__headers, cookies=self.__cookies, timeout=(3, 10))
            print(r)
            with open('result.txt', 'w', encoding='utf-8') as file:
                file.write(r.text)
            return "OK"
        except Exception:
            return 'a'
        


if __name__ == '__main__':
    steam = Parser()
    profile = steam.getSteamDBProfile('76561198287455504')
    print(profile)