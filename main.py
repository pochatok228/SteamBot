import telebot
from settings import telegramToken
from steamparser import SteamParser
import sqlite3
import time
import threading

bot = telebot.TeleBot(telegramToken)
databaseConnection = sqlite3.connect('UCID.db')
databaseConnection.close()



def constructSailMessages() -> tuple:
    steamparser = SteamParser()
    newSalesList, endingSalesList = steamparser.generateDiscountLists()
    string_template1 = "Новые скидки на игры в STEAM за последние 24 часа:\n\n"
    for newSale in newSalesList:
        string_template1 += "{}\nСкидка: {}, Цена: {}, Рейтинг: {}\n{}\n\n".format(newSale['name'],
                                                                                 newSale['discount'],
                                                                                 newSale['price'], newSale['rating'],
                                                                                 newSale['steam_link'])
    string_template2 = "Скидки на игры в STEAM, которые закончатся в течении 24 часов:\n\n"
    for newSale in endingSalesList:
        string_template2 += "{}\nСкидка: {}, Цена: {} Рейтинг: {}\n{}\n\n".format(newSale['name'],
                                                                                 newSale['discount'],
                                                                                 newSale['price'], newSale['rating'],
                                                                                 newSale['steam_link'])
    return string_template1, string_template2


def constructTopMessage() -> str:

    steamparser = SteamParser()
    topGames = steamparser.generateTop()
    string_template = "ТОП продаж в STEAM за предыдущую неделю:\n\n"
    for topGame in topGames:
        string_template += "{}. {}\n{}\n\n".format(topGame['place'], topGame['name'], topGame['steam_link'])
    return string_template


def salesMailingThread(bot):

    print("Started salesMailingThread 1 ")
    # time.sleep(300)
    print("Started salesMailingThread 2")
    while True:
        if time.gmtime(time.time()).tm_hour == 8:
            print("Sending sales")
            mes1, mes2  = constructSailMessages()
            databaseConnection = sqlite3.connect('UCID.db')
            cursor = databaseConnection.cursor()
            cursor.execute('SELECT * FROM ids')
            userChatIDs : list = cursor.fetchall() # list [ tuple (id : int, )]
            databaseConnection.close()

            for tuple_pair in userChatIDs:
                userChatID = tuple_pair[0]
                try:
                    bot.send_message(userChatID, mes1, disable_web_page_preview = True)
                    bot.send_message(userChatID, mes2, disable_web_page_preview = True)
                except telebot.apihelper.ApiException:
                    databaseConnection = sqlite3.connect('UCID.db'); cursor = databaseConnection.cursor()
                    cursor.execute("DELETE FROM ids WHERE chat_id = {}".format(userChatID))
                    databaseConnection.commit(); databaseConnection.close()
            time.sleep(3800)
        time.sleep(120)


def topMailingThread(bot):

    print("Started topMailingThread 1")
    # time.sleep(360)
    print("Started ropMailingThread 2")
    while True:
        
        timeSinceEpochGMT = time.gmtime(time.time())
        if timeSinceEpochGMT.tm_hour == 6 and timeSinceEpochGMT.tm_wday == 0:
            print("Sending top")
            message = constructTopMessage()
            databaseConnection = sqlite3.connect('UCID.db'); cursor = databaseConnection.cursor(); cursor.execute('SELECT * FROM ids')
            userChatIDs = cursor.fetchall(); databaseConnection.close()
            for tuple_pair in userChatIDs:
                userChatID = tuple_pair[0]
                try:
                    bot.send_message(userChatID, message, disable_web_page_preview = True)
                except telebot.apihelper.ApiException:
                    databaseConnection = sqlite3.connect('UCID.db'); cursor = databaseConnection.cursor()
                    cursor.execute("DELETE FROM ids WHERE chat_id = {}".format(userChatID))
                    databaseConnection.commit(); databaseConnection.close()
            time.sleep(3800)
        time.sleep(120)
        

@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id : int = message.chat.id
    bot.send_message(chat_id, "Доброго времени суток, вы подписались на рассылку от SteamBot")
    databaseConnection = sqlite3.connect('UCID.db')
    cursor = databaseConnection.cursor()
    try: 
        cursor.execute("INSERT INTO ids (chat_id) VALUES('{}')".format(chat_id)); databaseConnection.commit()
        print("New subscriber")
    except sqlite3.IntegrityError: 
        pass
    databaseConnection.close()

@bot.message_handler(commands=['add'])
def addMessage(message):
    chat_id : int = message.chat.id
    try: chanel_id : int = message.text.split()[1]; 
    except Exception: return 0
    try:
        databaseConnection = sqlite3.connect('UCID.db'); cursor = databaseConnection.cursor()
        cursor.execute("INSERT INTO ids (chat_id) VALUES('{}')".format(chanel_id)); databaseConnection.commit()
        bot.send_message(chat_id, "Successfully added")
    except sqlite3.IntegrityError:
        pass
    databaseConnection.close()






print('Running sales Mailing Thread')
sales_mailing_thread = threading.Thread(target = salesMailingThread, args = (bot, )); sales_mailing_thread.start()
top_mailing_thread = threading.Thread(target=topMailingThread, args=(bot,)); top_mailing_thread.start()

print('Bot is running correctly')
bot.polling()