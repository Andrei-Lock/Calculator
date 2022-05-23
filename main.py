import re
import sqlite3
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

TOKEN = "TOKEN"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
state = "start"
username = ""

keyboard = types.InlineKeyboardMarkup()
callback_button = types.InlineKeyboardButton(text="Посчитать", callback_data="calculate")
callback_button_1 = types.InlineKeyboardButton(text="История", callback_data="history_event")
keyboard.add(callback_button, callback_button_1)


async def bd():
    global username
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS {username}_history(expression TEXT)'.replace("{username}", str(username)))


async def name_writer(name):
    global username
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    mass = []
    mass.append(name)
    cur.execute('INSERT INTO {username}_history VALUES(?)'.replace("{username}", str(username)), mass)
    con.commit()
    cur.close()


async def send_base():
    global username
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    query = 'SELECT * FROM {username}_history WHERE expression IS NOT NULL'.replace("{username}", str(username))
    cur.execute(query)
    data = cur.fetchall()
    if data == []:
        data = ['Нет истории']
    mm = []
    for i in data:
        mm.append(i)
    ww = len(data)
    g = []
    for i in range(ww):
        a = re.sub('|\(|\'|\,|\)', '', str(mm[i]))
        g.append(a)
    c = []
    for i in g:
        q = i + "\n"
        c.append(q)
    val = '\n'.join(c)
    return val


async def delete_all_history():
    global username
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute('DELETE FROM {username}_history'.replace("{username}", str(username)))
    con.commit()


@dp.callback_query_handler(text="delete_history")
async def delete_history(call: types.CallbackQuery):
    global state, username
    username = call.from_user.username
    await bd()
    await delete_all_history()
    await bot.answer_callback_query(call.id)
    await call.message.answer("Успешно", reply_markup=keyboard)


@dp.callback_query_handler(text="history_event")
async def history_event(call: types.CallbackQuery):
    global state, username
    username = call.from_user.username
    await bd()
    keyboard_1 = types.InlineKeyboardMarkup()
    callback_button_2 = types.InlineKeyboardButton(text="Удалить историю", callback_data="delete_history")
    keyboard_1.add(callback_button_2)
    await bot.answer_callback_query(call.id)
    await call.message.answer(await send_base(), reply_markup=keyboard_1)


@dp.callback_query_handler(text="calculate")
async def calculate(call: types.CallbackQuery):
    global state, username
    username = call.from_user.username
    await bd()
    state = "calculating"
    await bot.answer_callback_query(call.id)
    await call.message.answer(str("Напиши пример, который хочешь посчитать"))


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    global username
    username = message.from_user.username
    await bd()
    await bot.send_message(message.chat.id, "Привет! Я бот-калькулятор",
                           reply_markup=keyboard)


@dp.message_handler()
async def bot_message(message: types.Message):
    global state, username
    username = message.from_user.username
    await bd()
    if message.chat.type == 'private':
        if state == "calculating" and message.text != "Напиши пример, который хочешь посчитать":
            try:
                await bot.send_message(message.chat.id, str(eval(str(message.text))), reply_markup=keyboard)
                state = "start"
                await name_writer(str(message.text) + " = " + str(eval(str(message.text))))
            except OverflowError:
                await bot.send_message(message.chat.id, "Слишком большое число")
            except ZeroDivisionError:
                await bot.send_message(message.chat.id, "Деление на ноль")
            except ArithmeticError:
                await bot.send_message(message.chat.id, "С примером что-то не так")
            except:
                await bot.send_message(message.chat.id, "Что-то пошло не так")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
