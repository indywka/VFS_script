import requests

def telegram_bot_sendtext(bot_message):
    bot_token = '5489603497:AAHKoOWplQVThZm-LiuaCr157Dflnf5XD0Y'
    bot_chatID = '-1001492818568'
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)

    return response.json()