import os
global bot

class Telegram:
    def __init__(self) -> None:
        connect_telebot()
        print('Connection successful')

        from bot import loadBot
        loadBot(BOT)

        BOT.infinity_polling()

def connect_telebot() -> None:
    with open('./dependancies.txt') as dependancyList:
        dependancyList = dependancyList.read().split()
        os.system("pip install --upgrade pip")
        for dependancy in dependancyList:
            os.system(f"pip install { dependancy } -U")
        
        import telebot

    
    API = '6576716707:AAHbz6qq2nb26bGGuwxvIQzhAH6WtJjAs8Q' # input('Enter your telegram API key: ')
    global BOT
    BOT = telebot.TeleBot(API)
    if BOT:
        print('Success')
    else:
        print('Wrong API')
        connect_telebot()