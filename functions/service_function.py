import re
import asyncio
import random
import string
from aiogram import types
from aiogram.dispatcher import FSMContext
from database.Database import Database as db
from database.Settings_database import Settings_database as st_db

from datetime import datetime
import pytz


async def mailing_order(call: types.CallbackQuery, state: FSMContext, restaurant_name, point_A, point_B, deliver_start_time,
                        deliver_end_time, phone, price, comment, order_id):
    users = await db().get_user_for_mailing()
    ms = await st_db().get_admin_settings_item(message_info="Mailing_Order")
    msg = (ms.replace('{item1}', str(restaurant_name)).replace('{item2}', str(point_A))
           .replace('{item3}', str(point_B)).replace('{item4}', str(deliver_start_time))
           .replace('{item5}', str(deliver_end_time)).replace('{item7}', str(price))
           .replace('{item8}', str(comment)))
    print(users)
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    keyboard.add(button(text='Взять заказ', callback_data=f'application_accepted_{order_id}'))

    user_levels = {}
    for user in users:
        user_id, level = user[0], user[1]
        if level not in user_levels:
            user_levels[level] = []
        user_levels[level].append(user_id)
    arr = []
    try:
        for level, user_ids in user_levels.items():
            for user_id in user_ids:
                send_msg = await call.bot.send_message(user_id, msg, reply_markup=keyboard)
                send_msg_id = send_msg.message_id
                arr.append([send_msg_id, user_id])
                time = await st_db().get_admin_settings_item(message_info="Time_between_groups")
                await db().update_order(parametr=str(arr), order_id=order_id, table="Messages")
            await asyncio.sleep(int(time))
    finally:
        await db().update_order(parametr=str(arr), order_id=order_id, table="Messages")
        return arr


async def mailing_purchase(call: types.CallbackQuery, state: FSMContext, restaurant_name, point_A, point_B,
                        count, weight, purchase_end_time, price, comment, purchase_id):
    users = await db().get_user_for_mailing()
    ms = await st_db().get_admin_settings_item(message_info="Mailing_Purchase")
    print(ms)
    msg = (ms.replace('{item1}', str(restaurant_name)).replace('{item2}', str(point_A))
           .replace('{item3}', str(point_B)).replace('{item4}', str(count))
           .replace('{item5}', str(weight)).replace('{item6}', str(purchase_end_time)).replace('{item7}', str(price))
           .replace('{item8}', str(comment)))
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    keyboard.add(button(text='Взять заказ', callback_data=f'application_accepted_{purchase_id}'))

    user_levels = {}
    for user in users:
        user_id, level = user[0], user[1]
        if level not in user_levels:
            user_levels[level] = []
        user_levels[level].append(user_id)
    arr = []
    try:
        for level, user_ids in user_levels.items():
            for user_id in user_ids:
                send_msg = await call.bot.send_message(user_id, msg, reply_markup=keyboard)
                send_msg_id = send_msg.message_id
                arr.append([send_msg_id, user_id])
                time = await st_db().get_admin_settings_item(message_info="Time_between_groups")
                await db().update_purchase(parametr=str(arr), purchase_id=purchase_id, table="Messages")
            await asyncio.sleep(int(time))
    finally:
        await db().update_purchase(parametr=str(arr), purchase_id=purchase_id, table="Messages")
        return arr


async def delete_all_messages(call: types.CallbackQuery, state: FSMContext, order_id, table, parameter):
    print("Deleting all messages")
    print(table)
    print(order_id)
    print(parameter)
    info = await db().get_messages_from_db(order_id, table=table, parametr=parameter)
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

def is_valid_time_format(text):
    pattern = r'^((0?[0-9]|1[0-9]|2[0-3]):([0-5][0-9]))$'  # Updated regular expression for flexible time format
    if re.match(pattern, text):
        return True
    else:
        return False

async def generate_random_code():
    characters = string.ascii_letters + string.digits
    random_code = ''.join(random.choices(characters, k=10))
    return random_code