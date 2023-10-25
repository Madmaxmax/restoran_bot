import ast
import asyncio
import random
import string
from aiogram import types
from aiogram.dispatcher import FSMContext
from database.Database import Database as db
from database.Settings_database import Settings_database as st_db

from datetime import datetime
import pytz


async def mailing(call: types.CallbackQuery, state: FSMContext, order_id, order_type, point_A, point_B, comment, price, restaurant):
    users = await db().get_user_for_mailing()
    print(users)
    msg = f'''
<b>Новый заказ</b>
<b>Ресторан:</b> {restaurant}
<b>Тип заказа:</b> {order_type}
<b>Цена:</b> {price}
<b>Место отправления:</b> {point_A}
<b>Место доставки:</b> {point_B}
<b>Информация:</b> {comment}
'''
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    keyboard.add(button(text='Взять заказ', callback_data=f'application_accepted_{order_id}'))

    user_levels = {}
    for user in users:
        user_id, level = user[0], user[1]
        if level not in user_levels:
            user_levels[level] = []
        user_levels[level].append(user_id)
    print(user_levels)
    arr = []
    try:
        for level, user_ids in user_levels.items():
            for user_id in user_ids:
                print("Сообщение для уровня " + str(level))
                send_msg = await call.bot.send_message(user_id, msg, reply_markup=keyboard)
                send_msg_id = send_msg.message_id
                arr.append([send_msg_id, user_id])
                print(arr)
                time = await st_db().get_admin_settings_item(message_info="Time_between_groups")
                await db().update_order(parametr=arr, order_id=order_id, table="Messages")
            await asyncio.sleep(int(time))
    finally:
        await db().update_order(parametr=arr, order_id=order_id, table="Messages")
        return arr


async def delete_all_messages(call: types.CallbackQuery, state: FSMContext, order_id):
    info = await db().get_messages_from_db(order_id)
    users = [tuple(sublist) for sublist in info[0]]
    for user in users:
        try:
            await call.bot.delete_message(chat_id=int(user[1]), message_id=int(user[0]))
            print(f"delete {user[1]} , {user[0]}")
        except:
            pass

async def get_moscow_time():
    moscow_tz = pytz.timezone('Europe/Moscow')
    utc_now = datetime.utcnow()
    moscow_now = utc_now.replace(tzinfo=pytz.utc).astimezone(moscow_tz)
    time = moscow_now.strftime('%Y-%m-%d %H:%M:%S')
    return time

async def generate_random_code():
    characters = string.ascii_letters + string.digits
    random_code = ''.join(random.choices(characters, k=10))
    return random_code