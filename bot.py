def loadBot(bot):
    import json
    import telebot
    import requests

    with open('./languages.json') as languageJson:
        languageFile = json.load(languageJson)
        def getMsg(query):
            return languageFile[LANGUAGE][query]

        @bot.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            keyboard = telebot.types.InlineKeyboardMarkup()
            for id, contents in languageFile.items():
                option = telebot.types.InlineKeyboardButton(contents['name'], callback_data=id)
                keyboard.add(option)
            global LANGUAGE
            global CHAT_ID
            CHAT_ID = message.chat.id
            LANGUAGE = 'default'
            bot.send_message(message.chat.id, getMsg('setLanguage'), reply_markup=keyboard)
            
            msg = bot.send_photo(
                message.chat.id, 
                photo=open('./images/domain.png', 'rb'), 
                caption=getMsg('setDomain')
            )
            bot.register_next_step_handler(msg, setDomain)


        @bot.callback_query_handler(func=lambda call: True)
        def callback_query(call):
            if (call.data.isdigit()):
                global PROJECT
                PROJECT = call.data
                bot.answer_callback_query(call.id, getMsg('projectChosen'))
                complete()
            else:
                global LANGUAGE
                LANGUAGE = call.data
                bot.answer_callback_query(call.id, getMsg('languageChosen'))

        
        def setDomain(message):
            global DOMAIN
            DOMAIN = message.text
            msg = bot.send_photo(
                message.chat.id, 
                photo=open('./images/API.png', 'rb'), 
                caption=f"{ getMsg('setAPI') } \n{ DOMAIN }/my/account")
            bot.register_next_step_handler(msg, setAPIKey)
        

        def setAPIKey(message):
            global API
            API = message.text
            validateRedmine(message)


        def validateRedmine(message):
            res = requests.get(f"{ DOMAIN }/projects.json?key={ API }")
            if (res.status_code != 200):
                bot.send_message(message.chat.id, getMsg('connectionError'))
                msg = bot.send_photo(
                    message.chat.id, 
                    photo=open('./images/domain.png', 'rb'), 
                    caption=getMsg('setDomain')
                )
                bot.register_next_step_handler(msg, setDomain)
            else:
                projects = json.loads(res.text)['projects']
                projectsKeyboard = telebot.types.InlineKeyboardMarkup()
                for contents in projects:
                    option = telebot.types.InlineKeyboardButton(contents['name'], callback_data=contents['id'])
                    projectsKeyboard.add(option)
                bot.send_message(message.chat.id, getMsg('setProject'), reply_markup=projectsKeyboard)

        
        def complete():
            print(123)
            global CHAT_ID
            startLoop(CHAT_ID)

        
        def startLoop(id):
            global DOMAIN
            import time
            res = requests.get(f"{ DOMAIN }/projects/{ PROJECT }/issues.json?sort=updated_on:desc&limit=1&key={ API }")
            res = json.loads(res.text)['issues']
            while True:
                new_res = json.loads(requests.get(f"{ DOMAIN }/projects/{ PROJECT }/issues.json?sort=updated_on:desc&limit=1&key={ API }").text)['issues']

                if res != new_res:
                    import re
                    desc = new_res[0]['description']
                    pattern = re.compile('<.*?>')
                    result = re.sub(pattern, '', desc)
                    bot.send_message(id, getMsg('newTask').format(**{
                        "task_id": new_res[0]['id'],
                        "task_status": new_res[0]['status']['name'],
                        "task_subject": new_res[0]['subject'],
                        "task_priority": calculatePriority(new_res[0]['priority']),
                        "task_description": result,
                        "task_link": f"{ DOMAIN }/issues/{ new_res[0]['id'] }"
                    }))
                time.sleep(30)
        

        def calculatePriority(num):
            return num['name'] + ' ' + int(num['id']) * "⚡"