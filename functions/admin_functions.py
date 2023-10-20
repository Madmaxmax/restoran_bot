import asyncio
import random
import string
import keyboard as keyboard
from aiogram import types
from aiogram.dispatcher import FSMContext
from database.Database import Database as db
from aiogram import Bot


async def admin_menu(message: types.Message = None, call: types.CallbackQuery = None, state: FSMContext = None):
    if call:
        delete = call.message.delete
        obj = call
        answer = call.message.answer
    else:
        delete = message.delete
        obj = message
        answer = message.answer
    user_id = obj.from_user.id
    admins_id = await db().get_admin_id()
    print(admins_id)
    if user_id in admins_id:
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        button = types.InlineKeyboardButton
        customers = await db().get_count_user_type("customer")
        couriers = await db().get_count_user_type("courier")
        all = customers[0] + couriers[0]
        msg = f'''
<b>Панель администратора</b>

<b>Инфо</b> 
╔Общее число пользователей: <b>{all}</b>
╠Число курьеров: <b>{couriers[0]}</b>
╚Число ресторанов:  <b>{customers[0]}</b>
'''
        keyboard.add(button(text='Добавить пользователя', callback_data='ad_add_user'))
        keyboard.add(button(text='Удалить пользователя', callback_data='ad_delete_user'))
        keyboard.add(button(text='Повысить ранг пользователя', callback_data='ad_user_buff'))

        # keyboard.add(button(text='Статистика', callback_data='statistic'))
        keyboard.add(button(text='Администраторы', callback_data='ad_admins'),
                     )
        await delete()
        await answer(msg, reply_markup=keyboard)

async def admins(call: types.CallbackQuery, state: FSMContext):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    admins = await db().get_all_admin()
    print(f"администраторы {admins}")
    msg = f'''
<b>Панель администратора
Администраторы</b>

Всего администраторов: {len(admins)}
'''
    if admins:
        for admin in admins:
            if admin[1] == 'None':
                username = 'Нет входа'
            else:
                username = admin[1]
            msg += f'''
╔ID:<code>{admin[0]}</code>
╚@{username}
'''
    keyboard.add(button(text='Добавить администратора', callback_data='ad_add_admin'))
    keyboard.add(button(text='Удалить администратора', callback_data='ad_delete_admin'))
    keyboard.add(button(text='назад', callback_data='ad_admin_menu'))
    await call.message.delete()
    await call.message.answer(msg, reply_markup=keyboard)

async def add_user(call: types.CallbackQuery, state: FSMContext):
    bot_info = await call.bot.get_me()
    bot_name = bot_info.username
    random = await generate_random_code()
    link = f"https://t.me/{bot_name}?start=use{random}"
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    msg = f'''
<b>Панель администратора</b>

<b>Ссылка для добавления нового пользователя:</b>
<code>{link}</code>
'''
    await db().add_new_link(f"use{random}", "user")
    keyboard.add(button(text='назад', callback_data='ad_admin_menu'))
    await call.message.answer(msg, reply_markup=keyboard)
    await call.message.delete()

async def delete_user(call: types.CallbackQuery, state: FSMContext):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    msg = f'''
<b>Панель администратора</b>

<b>Введите id пользователя которого надо удалить:</b>
'''
    keyboard.add(button(text='назад', callback_data='ad_admin_menu'))
    await call.message.answer(msg, reply_markup=keyboard)
    await call.message.delete()
    await state.set_state('ad_delete_user_text')

async def delete_user_text(message: types.Message, state: FSMContext):
    user_id = message.text
    await db().delete_user(user_id)
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    customers = await db().get_count_user_type("customer")
    couriers = await db().get_count_user_type("courier")
    all = customers[0] + couriers[0]
    msg = f'''
<b>Панель администратора</b>

<b>Инфо</b> 
╔Общее число пользователей: <b>{all}</b>
╠Число курьеров: <b>{couriers[0]}</b>
╚Число ресторанов:  <b>{customers[0]}</b>
'''
    keyboard.add(button(text='Добавить пользователя', callback_data='ad_add_user'))
    keyboard.add(button(text='Удалить пользователя', callback_data='ad_delete_user'))
    keyboard.add(button(text='Повысить ранг пользователя', callback_data='ad_user_buff'))
    keyboard.add(button(text='Администраторы', callback_data='ad_admins'))
    await message.delete()
    await message.answer(msg, reply_markup=keyboard)

async def user_buff(call: types.CallbackQuery, state: FSMContext):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    msg = f'''
<b>Панель администратора</b>

<b>Введите id пользователя которого нужно повысить:</b>
'''
    keyboard.add(button(text='назад', callback_data='ad_admin_menu'))
    await call.message.answer(msg, reply_markup=keyboard)
    await call.message.delete()
    await state.set_state('ad_user_buff_text')

async def user_buff_text(message: types.Message, state: FSMContext):
    print('привет')
    user_id = message.text
    await db().update_privileges_type(user_id)
    admins = await db().get_all_admin()
    print(f"администраторы {admins}")
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    customers = await db().get_count_user_type("customer")
    couriers = await db().get_count_user_type("courier")
    all = customers[0] + couriers[0]
    msg = f'''
<b>Панель администратора</b>

<b>Инфо</b> 
╔Общее число пользователей: <b>{all}</b>
╠Число курьеров: <b>{couriers[0]}</b>
╚Число ресторанов:  <b>{customers[0]}</b>
'''
    keyboard.add(button(text='Добавить пользователя', callback_data='ad_add_user'))
    keyboard.add(button(text='Удалить пользователя', callback_data='ad_delete_user'))
    keyboard.add(button(text='Повысить ранг пользователя', callback_data='ad_user_buff'))
    keyboard.add(button(text='Администраторы', callback_data='ad_admins'))
    await message.delete()
    await message.answer(msg, reply_markup=keyboard)

async def generate_random_code():
    characters = string.ascii_letters + string.digits
    random_code = ''.join(random.choices(characters, k=10))
    return random_code

async def add_admin(call: types.CallbackQuery, state: FSMContext):
    bot_info = await call.bot.get_me()
    bot_name = bot_info.username
    random = await generate_random_code()
    link = f"https://t.me/{bot_name}?start=adm{random}"
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    msg = f'''
<b>Панель администратора</b>

<b>Ссылка для добавления нового администратора:</b>
<code>{link}</code>
'''
    await db().add_new_link(f"adm{random}", "admin")
    keyboard.add(button(text='назад', callback_data='ad_admins'))
    await call.message.answer(msg, reply_markup=keyboard)
    await call.message.delete()

async def delete_admin(call: types.CallbackQuery, state: FSMContext):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    admins = await db().get_all_admin()
    msg = f'''
<b>Панель администратора</b>

<b>Выберите какого администратора необходимо удалить:</b>
'''
    if admins:
        for admin in admins:
            if admin[1] == 'None':
                username = 'Нет входа'
            else:
                username = admin[1]
            keyboard.add(button(text=f'{username}', callback_data=f'ad_del_admin_{admin[0]}'))
    keyboard.add(button(text='назад', callback_data='ad_admins'))
    await call.message.answer(msg, reply_markup=keyboard)
    await call.message.delete()

async def del_admin(call: types.CallbackQuery, state: FSMContext):
    admin_id = int(call.data[13:])
    await db().delete_admin_db(admin_id)
    await admins(call, state)