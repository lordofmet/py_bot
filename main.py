import telebot
import sqlite3
import datetime
import time
from threading import Thread
import pickle


'''
TODO
год: str -> int
4 знака
подправить под это дело методы
'''

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
        s += "\n"

    bot.send_message(message.chat.id, s)

def got_add_query(msg):
    s1 = msg.text.split(' ')

    if (len(s1) != 2):
        print(len(s1))
        print(s1)
        warning = "Некорректный ввод имени"
        bot.send_message(msg.chat.id, warning)
        add(msg)
        return

    s = s1[0]

    if (len(s) != 10):
        print(len(s))
        print(s)
        warning = "Некорректный ввод даты4"
        bot.send_message(msg.chat.id, warning)
        add(msg)
        return

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

    year = s[6:]
    year = int(year)

    cur_date = str(datetime.datetime.now())
    cur_date = cur_date.split()
    cur_year = (cur_date[0].split('-'))[0]
    if (year > int(cur_year)):
        warning = "Некорретный ввод даты"
        bot.send_message(msg.chat.id, warning)
        add(msg)
        return

    uid = msg.from_user.id
    uname = msg.from_user.username
    day = int(day)
    month = int(month)
    name = s1[1]
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


        time.sleep(5)


polling_thread = Thread(target = polling)
check_dates_thread = Thread(target = check_dates)

check_dates_thread.start()
polling_thread.start()
