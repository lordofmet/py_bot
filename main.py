import telebot
import sqlite3
import datetime
import time
from threading import Thread
import pickle

connect = sqlite3.connect("/Users/dmirt/PycharmProjects/db", check_same_thread=False)
curs = connect.cursor()
print(connect)

curs.execute('''  
CREATE TABLE IF NOT EXISTS users (
    id       INTEGER PRIMARY KEY AUTOINCREMENT
                     UNIQUE
                     NOT NULL,
    user_id  INTEGER UNIQUE
                     NOT NULL,
    username TEXT    NOT NULL,
    day      INTEGER NOT NULL,
    month    INTEGER NOT NULL,
    year     INTEGER NOT NULL,
    name     TEXT    NOT NULL,
    tg_msg   TEXT    NOT NULL
);
''')

def db_table_add(user_id: int, username: str, day: int, month: int, year: int, name: str, tg_msg: str):
    curs.execute('INSERT INTO users (user_id, username, day, month, year, name, tg_msg) VALUES(?, ?, ?, ?, ?, ?, ?)',
                                    (user_id, username,day, month, year, name, tg_msg))
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
    s1 = msg.text.split(' ')

    if (len(s1) != 2):
        print(len(s1))
        print(s1)
        warning = "Некорректный ввод имени"
        bot.send_message(msg.chat.id, warning)
        add(msg)
        return

    s = s1[0]

    if (len(s) != 8):
        print(len(s))
        print(s)
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
    name = s1[1]
    tg_msg = pickle.dumps(msg)
    print("deserealized: ", tg_msg)

    db_table_add(uid, uname, day, month, year, name, tg_msg)
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
        for person in curs.execute("SELECT day, month, year, name, tg_msg FROM users"):
            tday = person[0]
            tmonth = person[1]
            tyear = person[2]
            tname = person[3]

            tmsg = person[4]
            tg_msg = pickle.loads(tmsg)

            curT = str(datetime.datetime.now())
            curT = curT.split(' ')
            cur_date = curT[0]
            cur_date = cur_date.split('-')
            cur_day = int(cur_date[2])
            cur_month = int(cur_date[1])
            cur_year = int(cur_date[0])

            if cur_day == tday and cur_month == tmonth:
                print("there is some match")
                if tyear > 24:
                    tyear = 1900 + tyear
                else:
                    tyear = 2000 + tyear
                f = "Поздравляем " + str(tname) + " ему(ей) " + str(int(cur_year - tyear))
                bot.send_message(tg_msg.chat.id, f)
            else:
                print("not a match")
        time.sleep(60)



polling_thread = Thread(target = polling)
check_dates_thread = Thread(target = check_dates)

check_dates_thread.start()
polling_thread.start()
