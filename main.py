import telebot
import sqlite3

connect = sqlite3.connect("/Users/dmirt/PycharmProjects/db", check_same_thread=False)
curs = connect.cursor()
print(connect)

def db_table_add(user_id: int, username: str, day: int, month: int, year: int):
    curs.execute('INSERT INTO test (user_id, username, day, month, year) VALUES(?, ?, ?, ?, ?)', (user_id, username,
                                                                                                   day, month, year))
    connect.commit()

def readFileToStr(file):
    s = ''
    for line in file:
        s += line
    return s

token = "6965050561:AAGphYfWPbPQU2Mk82ZjGssyej7pRpsFYTU"

bot = telebot.TeleBot(token)

@bot.message_handler(commands = ["start"])
def start(message):
    file = open("greeting.txt", 'r', encoding="utf-8")
    s = readFileToStr(file)
    file.close()
    bot.send_message(message.chat.id, s)

@bot.message_handler(commands = ["add"])
def add(message):
    file = open("add.txt", 'r', encoding="utf-8")
    s = readFileToStr(file)
    file.close()

    msg = bot.send_message(message.from_user.id, s)
    bot.register_next_step_handler(msg, got_add_query)

def got_add_query(msg):
    s = msg.text

    if (len(s) != 8):
        warning = "Некорректный ввод даты"
        bot.send_message(msg.chat.id, warning)
        add(msg)
        return

    flag = 0
    for i in s:
        if i == '.':
            continue
        if not i.isdigit():
            warning = "Некорректный ввод даты"
            bot.send_message(msg.chat.id, warning)
            add(msg)
            return

    first_num = int(s[0]) - int('0')
    second_num = int(s[1]) - int('0')
    day = first_num * 10 + second_num

    if (day > 31):
        warning = "Некорректный ввод даты"
        bot.send_message(msg.chat.id, warning)
        add(msg)
        return

    first_num = int(s[3]) - int('0')
    second_num = int(s[4]) - int('0')
    month = first_num * 10 + second_num

    if (month > 12):
        warning = "Некорректный ввод даты"
        bot.send_message(msg.chat.id, warning)
        add(msg)
        return

    first_num = int(s[6]) - int('0')
    second_num = int(s[7]) - int('0')
    year = first_num * 10 + second_num

    uid = msg.from_user.id
    uname = msg.from_user.username
    day = int(day)
    month = int(month)
    year = int(year)

    db_table_add(uid, uname, day, month, year)
    bot.send_message(msg.chat.id, 'Ваша дата была добавлена в БД')

bot.polling(none_stop = True, interval = 0)