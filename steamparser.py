import requests
from bs4 import BeautifulSoup

from settings import mozillaHeaders
from settings import steamDiscountPage, steamTopPage

import time




class SteamParser:

    def __init__(self, cookies = {}):
        self.__headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0'
        }
        self.__cookies = cookies


    def generateDiscountLists(self) -> tuple:
        # if True:
        try:
            response = requests.get(
                steamDiscountPage, headers=self.__headers, cookies=self.__cookies, timeout=(3, 10))
            # print(response)
            # print(response.text)
            gameRows = BeautifulSoup(response.text, features='lxml').find_all('tr', {'class': 'app appimg'})
            print("Number of games in table: {}".format(len(gameRows)))
            newSalesList = []; endingSalesList = []

            counter = 0

            for gameRow in gameRows:
                gameChars = gameRow.find_all('td')
                # print(len(gameChars), end = '')
                if len(gameChars) != 9: print(gameChars.text)
                try: ratingFilter : bool = float(gameChars[5]["data-sort"]) >= 50
                except Exception: continue
                discountFilter : bool = float(gameChars[3]["data-sort"]) >= 50
                if ratingFilter and discountFilter:
                    current_time = time.time()
                    started_time = int(gameChars[7]['data-sort'])
                    ending_time = int(gameChars[6]['data-sort'])
                    started_filter = current_time - started_time <= 86400
                    ending_filter = 0 < ending_time - current_time <= 86400
                    if started_filter or ending_filter:
                        notCasualOr2d : bool = None
                        link = 'https://steamdb.info' + gameChars[2].find('a')['href']
                        responseGame = requests.get(
                                        link, headers=self.__headers, cookies=self.__cookies, timeout=(3, 10))
                        # print(link)
                        gamePageSoup = BeautifulSoup(responseGame.text, features='lxml')
                        with open('gamepage.txt', 'w', encoding='utf-8') as file: file.write(gamePageSoup.text)
                        tags = gamePageSoup.find_all('a', {'class' : 'btn btn-sm btn-outline btn-tag'})
                        # print(len(tags))
                        for tag in tags:
                            if tag.string == '2D' or tag.string == 'Casual':
                                notCasualOr2d = False
                                break
                        else:
                            notCasualOr2d = True

                        if notCasualOr2d:
                            gameRow = {
                                        "name" : gameChars[2].find('a').string,
                                        "discount" : gameChars[3]['data-sort'] + '%',
                                        "price" : str(float(gameChars[4]['data-sort']) / 100) + ' р.',
                                        "rating" : gameChars[5]["data-sort"] + '%',
                                        "steam_link" : 'https://store.steampowered.com' + gameChars[2].find('a')['href']
                                    }
                            if started_filter: newSalesList.append(gameRow)
                            if ending_filter: endingSalesList.append(gameRow)
                    


            print(counter)
            return newSalesList, endingSalesList

        except Exception as e:
            print(e)
            return None

    def generateTop(self):
        response = requests.get(
                steamTopPage, headers=self.__headers, cookies=self.__cookies, timeout=(3, 10))
        table = BeautifulSoup(response.text, features='lxml').find('table', {'class' : 'table-products table-hover table-responsive-flex text-left'})
        top = []
        
        gameRows = table.find('tbody').find_all('tr')
        for i in range(len(gameRows)):
            gameRow = gameRows[i]
            gameChars = gameRow.find_all('td')
            # print(len(gameChars), end = '')
            nameObject = gameChars[2].find('a')
            name = nameObject.string
            link = "https://store.steampowered.com" + nameObject['href'].rstrip('/graphs')
            top.append(
                {
                    "place" : i + 1,
                    "name" : name,
                    "steam_link" : link
                }
            )

        return top


            

if __name__ == "__main__":
    steamparser = SteamParser()
    newSalesList, endingSalesList = steamparser.generateDiscountLists()
    print('Новые скидки на игры в STEAM за последние 24 часа')
    print('\n'.join(map(str, newSalesList)))
    print('\n\n\n\n')
    print('Скидки на игры в STEAM, которые закончатся в течении 24 часов')
    print('\n'.join(map(str, endingSalesList)))
    
    topGames = steamparser.generateTop()
    print("ТОП продаж в STEAM за предыдущую неделю")
    print('\n'.join(map(str, topGames)))