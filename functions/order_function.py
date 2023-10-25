import asyncio
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from database.Database import Database as db
from database.Settings_database import Settings_database as st_db

from functions.service_function import mailing, delete_all_messages, get_moscow_time

async def create_orders(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(order_type=None, point_A=None, point_B=None, comment=None, price=None)
    msg = await new_order(state=state)
    msg += '\n<b>Введите: Тип заказа</b>'
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    keyboard.add(button(text='Назад', callback_data='customer_menu'))
    await call.message.edit_text(msg, reply_markup=keyboard)
    await state.set_state('create_orders_order_type')


async def create_orders_order_type(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = message.from_user.id
    await state.update_data(customer_id=user_id)
    await message.bot.delete_message(message.from_user.id, message.message_id - 1)
    await message.bot.delete_message(message.from_user.id, message.message_id)
    order_type = message.text
    await state.update_data(order_type=order_type)
    msg = await new_order(state=state)
    msg += '\n<b>Введите: Место отправления</b>'
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    keyboard.add(button(text='Назад', callback_data='customer_menu'))
    await message.answer(msg, reply_markup=keyboard)
    # await message.bot.delete_message(message.from_user.id, message.message_id - 1)
    await state.set_state('create_orders_price')

async def create_orders_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.bot.delete_message(message.from_user.id, message.message_id - 1)
    await message.bot.delete_message(message.from_user.id, message.message_id)
    price = message.text
    await state.update_data(price=price)
    msg = await new_order(state=state)
    msg += '\n<b>Введите: Цену заказа</b>'
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    keyboard.add(button(text='Назад', callback_data='customer_menu'))
    await message.answer(msg, reply_markup=keyboard)
    await state.set_state('create_orders_point_A')


async def create_orders_point_A(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.bot.delete_message(message.from_user.id, message.message_id - 1)
    await message.bot.delete_message(message.from_user.id, message.message_id)
    point_A = message.text
    await state.update_data(point_A=point_A)
    msg = await new_order(state=state)
    msg += '\n<b>Введите: Место доставки</b>'
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    keyboard.add(button(text='Назад', callback_data='customer_menu'))
    await message.answer(msg, reply_markup=keyboard)
    # await message.bot.delete_message(message.from_user.id, message.message_id - 1)
    await state.set_state('create_orders_point_B')


async def create_orders_point_B(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.bot.delete_message(message.from_user.id, message.message_id - 1)
    await message.bot.delete_message(message.from_user.id, message.message_id)
    point_B = message.text
    await state.update_data(point_B=point_B)
    msg = await new_order(state=state)
    msg += '\n<b>Введите: Комментарий</b>'
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    keyboard.add(button(text='Назад', callback_data='customer_menu'))
    await message.answer(msg, reply_markup=keyboard)
    # await message.bot.delete_message(message.from_user.id, message.message_id - 1)
    await state.set_state('create_orders_comment')

tasks_dict = {}

async def create_orders_comment(message: types.Message, state: FSMContext):
    await message.bot.delete_message(message.from_user.id, message.message_id - 1)
    comment = message.text
    user_id = message.from_user.id
    restaurant = await db().get_restaurant_name(user_id)
    username = message.from_user.username
    print(user_id)
    data = await state.get_data()
    await state.update_data(comment=comment)
    count = await db().get_count_orders(user_id)
    order_id = str(user_id) + str(count[0][0])
    print(order_id)
    print(comment)
    await db().add_orders_db(order_id=int(order_id), customer_id=user_id, order_type=data['order_type'],
                             point_A=data['point_A'], point_B=data['point_B'], comment=comment, customer_us=username,
                             price=data['price'], restaurant_name=restaurant[0][0])
    await db().update_count_orders(user_id)
    current_task = asyncio.create_task(
        mailing(order_id=int(order_id), order_type=data['order_type'], point_A=data['point_A'], point_B=data['point_B'],
                comment=comment, call=types.CallbackQuery(message=message), state=state, price=data['price'], restaurant=restaurant[0][0]))
    tasks_dict[order_id] = current_task
    await customer_menu(types.CallbackQuery(message=message), state, user_id)
