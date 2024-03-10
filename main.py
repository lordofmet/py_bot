import telebot
import sqlite3
import datetime
import time
from threading import Thread
from telebot import types
import pickle

connect = sqlite3.connect("/Users/dmirt/PycharmProjects/bot/db.db", check_same_thread=False)
curs = connect.cursor()
print(connect)

curs.execute('''  
CREATE TABLE IF NOT EXISTS users (
    id       INTEGER PRIMARY KEY AUTOINCREMENT
                     UNIQUE
                     NOT NULL,
    user_id  INTEGER NOT NULL,
    username TEXT    NOT NULL,
    day      INTEGER NOT NULL,
    month    INTEGER NOT NULL,
    year     INTEGER NOT NULL,
    name     TEXT    NOT NULL,
    tg_msg   TEXT    NOT NULL,
    congrat  INTEGER NOT NULL
);
''')

def db_table_add(user_id: int, username: str, day: int, month: int, year: int, name: str, tg_msg: str, congrat: int):
    curs.execute('INSERT INTO users (user_id, username, day, month, year, name, tg_msg, congrat) VALUES(?, ?, ?, ?, ?, ?, ?, ?)',
                                    (user_id, username,day, month, year, name, tg_msg, congrat))
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
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = "➕ Добавить дату"
    btn2 = "➖ Удалить дату"
    btn3 = "✍️Изменить дату"
    btn4 = "📄 Список"
    markup.add(btn1, btn2, btn3, btn4)
    file = open("greeting.txt", 'r', encoding="utf-8")
    s = readFileToStr(file)
    file.close()
    bot.send_message(message.chat.id, s, reply_markup=markup)

@bot.message_handler(content_types=['text'])
def text_handler(message):
    if message.text == "➕ Добавить дату" or message.text == "/edit":
        add(message)
    elif message.text == "➖ Удалить дату" or message.text == "del":
        got_del_query(message)
    elif message.text == "✍️Изменить дату" or message.text == "edit":
        edit(message)
    elif message.text == "📄 Список" or message.text == "list":
        get_list(message)
    else:
        file = open("idunno.txt", 'r', encoding="utf-8")
        s = readFileToStr(file)
        file.close()
        bot.send_message(message.chat.id, s)

@bot.message_handler(commands = ["add"])
def add(message):
    file = open("add.txt", 'r', encoding="utf-8")
    s = readFileToStr(file)
    file.close()

    msg = bot.send_message(message.chat.id, s) #
    bot.register_next_step_handler(msg, got_add_query)

@bot.message_handler(commands = ["del"])
def got_del_query(message):
    file = open("delete.txt", 'r', encoding = "utf-8")
    s = readFileToStr(file)
    file.close()

    msg = bot.send_message(message.chat.id, s)
    bot.register_next_step_handler(msg, del_query_handling)

def del_query_handling(message):
    s = message.text

    name = str(s)
    for person in curs.execute("SELECT name FROM users"):
        table_name = person[0]
        if name == table_name:
            sql = "DELETE FROM users WHERE name = ?"
            curs.execute(sql, (name,))
            connect.commit()
            success = "Запись была удалена"
            bot.send_message(message.chat.id, success)
            return

    warning = "Не было найдено подходящей записи. При необходимости повторите запрос"

    bot.send_message(message.chat.id, warning)

def convert (day, month, year):
    s = ""
    if (day < 10):
        day_str = '0' + str(day)
    else:
        day_str = str(day)
    if (month < 10):
        month_str = '0' + str(month)
    else:
        month_str = str(month)
    year = str(year)
    s = day_str + "." + month_str + "." + year

    return s

@bot.message_handler(commands=["list"])
def get_list(message):

    file = open("list.txt", 'r', encoding="utf-8")
    t = readFileToStr(file)
    file.close()
    bot.send_message(message.chat.id, t)

    s = ""
    for person in curs.execute("SELECT * FROM users"):
        name = person[6]
        day = person[3]
        month = person[4]
        year = person[5]
        s += name + '\n' + convert(day, month, year)
        s += "\n\n"

    bot.send_message(message.chat.id, s)

@bot.message_handler(commands = ["edit"])
def edit(message):

    file = open("edit.txt", 'r', encoding = "utf-8")
    t = readFileToStr(file)
    file.close()
    msg = bot.send_message(message.chat.id, t)

    bot.register_next_step_handler(msg, got_edit_query)

def got_edit_query(message):

    s = message.text.split(' ')

    date = s[0]

    if (len(date) != 10):
        warning = "Некорректный ввод1"
        bot.send_message(message.chat.id, warning)
        return

    date = date.split('.')

    if (len(s) <= 1 or len(date) != 3):
        warning = "Некорректный ввод2"
        print(len(s))
        print(len(date))
        bot.send_message(message.chat.id, warning)
        return

    name = ""
    for i in range(1, len(s)):
        name += s[i]
        name += ' '

    day = int(date[0])
    month = int(date[1])
    year = int(date[2])
    print("day, month, year", day, month, year)

    if (name != ""):
        name = str(name)

    flag = 0
    print(day, month, year, name)
    for person in curs.execute("SELECT day, month, year, name FROM users"):
        table_day = int(person[0])
        table_month = int(person[1])
        print(person[2])
        table_year = int(person[2])
        table_name = str(person[3])
        print(table_day, table_month, table_year, table_name)
        if (table_day == day and table_month == month and table_year == year):
            if (name != "" and table_name != name):
                continue
            flag = 1
            if (flag):
                break

    if (flag == 0):
        warning = "Запись не найдена. Проверьте правильность и повторите попытку при необходимости"
        bot.send_message(message.chat.id, warning)
        return

    file = open("edit1.txt", 'r', encoding = "utf-8")
    t = readFileToStr(file)
    msg = bot.send_message(message.chat.id, t)

    bot.register_next_step_handler(msg, edit_query_handling, day, month, year, name)

def edit_query_handling(message, d, m, y, n):

    s = message.text.split(' ')

    date = s[0]

    if (len(date) != 10 or len(s) < 2):
        warning = "Некорректный ввод"
        bot.send_message(message.chat.id, warning)
        edit(message)
        return

    date = s[0]
    name = ""
    for i in range(1, len(s)):
        name += s[i]
        name += ' '

    for i in date:
        if i == '.':
            continue
        if not i.isdigit():
            warning = "Некорректный ввод даты"
            bot.send_message(message.chat.id, warning)
            edit(message)
            return

    date = date.split('.')
    print(date)
    day = date[0]
    month = date[1]
    year = date[2]
    name = str(name)

    for person in curs.execute("SELECT day, month, year, name FROM users"):
        table_day = int(person[0])
        table_month = int(person[1])
        table_year = int(person[2])
        table_name = person[3]

        if (table_day == d and table_month == m and table_year == y and table_name == n):
            table_day = day
            table_month = month
            table_year = year
            table_name = name

            #sql = "UPDATE users SET day = ?, month = ?, year = ?, name = ? WHERE day = ?, month = ?, year = ?, name = ?"
            #curs.execute(sql, (day, month, year, name, d, m, y, n,))

            sql = "UPDATE users SET day = ?, month = ?, year = ?, name = ? WHERE day = ? AND month = ? AND year = ? AND name = ?"
            curs.execute(sql, (day, month, year, name, d, m, y, n,))

            connect.commit()

            done = "Запись изменена"
            bot.send_message(message.chat.id, done)


def got_add_query(msg):
    s1 = msg.text.split(' ')

    '''if (len(s1) != 2):
        print(len(s1))
        print(s1)
        warning = "Некорректный ввод имени"
        bot.send_message(msg.chat.id, warning)
        add(msg)
        return'''

    if (len(s1) == 1):
        warning = "Некорретный ввод: не найдено имя человека"
        bot.send_message(msg.chat.id, warning)
        return

    name = ""
    for i in range(1, len(s1)):
        name += s1[i]
        name += ' '

    s = s1[0]

    if (len(s) != 10):
        print(len(s))
        print(s)
        warning = "Некорректный ввод даты"
        bot.send_message(msg.chat.id, warning)
        return

    for i in s:
        if i == '.':
            continue
        if not i.isdigit():
            warning = "Некорректный ввод даты"
            bot.send_message(msg.chat.id, warning)
            return

    first_num = int(s[0]) - int('0')
    second_num = int(s[1]) - int('0')
    day = first_num * 10 + second_num

    if (day > 31):
        warning = "Некорректный ввод даты"
        bot.send_message(msg.chat.id, warning)
        return

    first_num = int(s[3]) - int('0')
    second_num = int(s[4]) - int('0')
    month = first_num * 10 + second_num

    if (month > 12):
        warning = "Некорректный ввод даты"
        bot.send_message(msg.chat.id, warning)
        return

    year = s[6:]
    year = int(year)

    cur_date = str(datetime.datetime.now())
    cur_date = cur_date.split()
    cur_year = (cur_date[0].split('-'))[0]
    if (year > int(cur_year)):
        warning = "Некорретный ввод даты"
        bot.send_message(msg.chat.id, warning)
        return

    uid = msg.from_user.id
    uname = msg.from_user.username
    day = int(day)
    month = int(month)
    tg_msg = pickle.dumps(msg)
    print("deserealized: ", tg_msg)
    congrat = 0

    db_table_add(uid, uname, day, month, year, name, tg_msg, congrat)
    bot.send_message(msg.chat.id, 'Ваша дата была добавлена в БД')

    #check_date(msg)

def polling():
    bot.polling(none_stop = True, interval = 0)

'''def check_date(msg):
    check_date_thread = Thread(target=check_date(msg))

    curT = str(datetime.datetime.now())

    curT = curT.split(' ')
    print(curT)

    cur_time = curT[1]
    #cur_time = "23:59:59"
    cur_time = cur_time.split(':')

    hours_to_sleep = 0
    minutes_to_sleep = 0
    seconds_to_sleep = 0

    hours_to_sleep = 24 - int(cur_time[0])

    if (int(cur_time[1]) != 0):
        hours_to_sleep -= 1
        if (hours_to_sleep == -1):
            hours_to_sleep = 23
        minutes_to_sleep += 60 - int(cur_time[1])

    if (minutes_to_sleep == 60):
        minutes_to_sleep = 0
        hours_to_sleep += 1

    if (float(cur_time[2]) >= 1e-15):
        minutes_to_sleep -= 1
        if (minutes_to_sleep == -1):
            hours_to_sleep = 23
            minutes_to_sleep = 59
        seconds_to_sleep += 60 - float(cur_time[2])

    print(hours_to_sleep, minutes_to_sleep, seconds_to_sleep)

    check_date_thread.start()

    await_time = seconds_to_sleep + minutes_to_sleep * 60 + hours_to_sleep * 3600
    print("waiting for", await_time)
    time.sleep(await_time)

    curT = str(datetime.datetime.now())
    curT = curT.split(' ')
    print(curT)

    cur_date = curT[0]
    cur_date = cur_date.split('-')
    cur_day = int(cur_date[2])
    cur_month = int(cur_date[1])
    cur_year = int(cur_date[0])
    print("new date:", cur_day, cur_month)

    for person in curs.execute("SELECT day, month, year, name FROM users"):
        day = person[0]
        month = person[1]
        year = person[2]
        name = person[3]
        if (cur_day == day and cur_month == month):
            f = "Поздравляем" + str(name) + "ему(ей) " + str(int(cur_year - year))
            bot.send_message(msg.chat.id, f)
'''

def check_dates():
    while True:
        curT = str(datetime.datetime.now())
        curT = curT.split(' ')
        cur_date = curT[0]
        cur_date = cur_date.split('-')
        prev_year = int(cur_date[0])
        print("fs ", prev_year)
        for person in curs.execute("SELECT day, month, year, name, tg_msg, congrat, id, username FROM users"):
            tday = person[0]
            tmonth = person[1]
            tyear = person[2]
            tname = person[3]

            tmsg = person[4]
            tg_msg = pickle.loads(tmsg)

            congrated_this_year = int(person[5])
            print(congrated_this_year, "= congrats")
            id = int(person[6])

            curT = str(datetime.datetime.now())
            curT = curT.split(' ')
            cur_date = curT[0]
            cur_date = cur_date.split('-')
            cur_day = int(cur_date[2])
            cur_month = int(cur_date[1])
            cur_year = int(cur_date[0])

            if cur_year > prev_year:
                print("entered cmp")
                print(cur_year, prev_year)
                prev_year = cur_year
                curs.execute('UPDATE users SET congrat = 0')
                connect.commit()

            if cur_day == tday and cur_month == tmonth and congrated_this_year == 0:
                print("there is some match")
                username = person[7]

                sql = "UPDATE users SET congrat = 1 WHERE username = ?"
                curs.execute(sql, (username,))
                connect.commit()
                print(username)

                f = "Поздравляем " + str(tname) + " ему(ей) " + str(int(cur_year - tyear))
                bot.send_message(tg_msg.chat.id, f)
            else:
                print("not a match")


        time.sleep(60)


polling_thread = Thread(target = polling)
check_dates_thread = Thread(target = check_dates)

check_dates_thread.start()
polling_thread.start()
