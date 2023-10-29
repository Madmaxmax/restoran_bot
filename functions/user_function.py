import asyncio
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import random
from database.Database import Database as db
from database.Settings_database import Settings_database as st_db

from functions.service_function import (mailing_order, mailing_purchase, delete_all_messages, get_moscow_time,
                                        is_valid_time_format)


async def welcome(message: types.Message, state: FSMContext):
    # await db().add_new_admin(944439582, "Maaaadmax")
    user_id = message.from_user.id
    username = message.from_user.username
    await state.update_data(user_id=user_id)
    ref = message.get_args()
    flag = await db().check_link(link=ref, link_type="user")
    is_user = await db().check_user(user_id=user_id)
    if ref[:3] == 'use' and str(flag[0]) == "1":
        await db().add_user_db(user_id=user_id, username=username)
        await db().delete_link(ref)
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        button = types.InlineKeyboardButton
        msg = await st_db().get_admin_settings_item(message_info="Start_message")
        keyboard.add(button(text='Заказчик', callback_data='restaurant_name'))
        keyboard.add(button(text='Курьер', callback_data='get_courier_phone'))
        await message.answer(msg, reply_markup=keyboard)
    elif str(is_user[0]) == "1":
        user_type = await db().get_user_type(user_id)
        if user_type[0] == 'customer':
            random_num = random.randint(1, 5)
            msg = await st_db().get_admin_settings_item(message_info=f"Customer_hello_message_{random_num}")
            await message.answer(msg, reply_markup=await customer_keyboard())
            await customer_menu(types.CallbackQuery(message=message), state, id_=message.from_user.id)
            # await message.bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id + 2)
        else:
            random_num = random.randint(1, 5)
            msg = await st_db().get_admin_settings_item(message_info=f"Courier_hello_message_{random_num}")
            await message.answer(msg, reply_markup=await reverse_receiving_keyboard_1())
            phone = await db().get_user_phone(user_id=user_id)
            if phone is not None:
                await courier_menu(types.CallbackQuery(message=message), state, id_=message.from_user.id)
            else:
                await get_courier_phone(types.CallbackQuery(message=message), state)
    elif ref[:3] == 'adm':
        flag = await db().check_link(link=ref, link_type="admin")
        if str(flag[0]) == "1":
            await db().add_new_admin(admin_id=user_id, username=username)
            await db().delete_link(ref)
        admin_msg = '''
<b>Добро пожаловать!</b>
Для вывода паненили администратора введите команду /admin
'''
        await message.reply(admin_msg)
    else:
        await message.reply("Доступ запрещен")


async def contact_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    first_button = KeyboardButton(text="📱 Отправить", request_contact=True)
    markup.add(first_button)
    return markup

async def reverse_receiving_keyboard_0():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    first_button = KeyboardButton(text="Вы не принимаете заказы❌", callback_data="reverse_receiving_keyboard_text")
    markup.add(first_button)

    return markup

async def reverse_receiving_keyboard_1():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    first_button = KeyboardButton(text="Вы принимаете заказы✅", callback_data="reverse_receiving_keyboard_text")
    markup.add(first_button)

    return markup


async def reverse_receiving_keyboard_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    id = message.from_user.id
    user_receiving = await db().get_receiving_order(id)
    # print("Статус")
    # print(user_receiving)
    if int(user_receiving[0]) == 1:
        await db().update_receiving_order(user_id=id, receiving_order=0)
        await message.answer(text="Вы не принимаете заказы❌", reply_markup=await reverse_receiving_keyboard_0())
        await message.delete()
    else:
        await db().update_receiving_order(user_id=id, receiving_order=1)
        await message.answer(text="Вы принимаете заказы ✅", reply_markup=await reverse_receiving_keyboard_1())
        await message.delete()


async def get_courier_phone(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Нажмите на кнопку ниже, чтобы отправить контакт",
                              reply_markup=await contact_keyboard())
    await call.message.delete()
    await state.set_state('get_courier_phone_text')


async def get_courier_phone_text(message: types.Message, state: FSMContext):
    contact = message.contact
    id = message.from_user.id
    print(contact)
    # await message.delete_reply_markup()
    # await message.delete()
    random_num = random.randint(1, 5)
    print(f"рандомное число {random_num}")
    msg = await st_db().get_admin_settings_item(message_info=f"Courier_hello_message_{random_num}")
    await message.answer(".", reply_markup=types.ReplyKeyboardRemove())
    await message.bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id +1)
    await message.bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id - 1)
    await db().update_restaurant_phone_phone_number(user_id=id, phone=str(contact['phone_number']))
    await message.answer(msg, reply_markup=await reverse_receiving_keyboard_1())
    await courier_menu(types.CallbackQuery(message=message), state, id_=message.from_user.id)


async def courier_menu(call: types.CallbackQuery, state: FSMContext, id_=None):
    if id_:
        await db().update_user_type("courier", id_)
        user_info = await db().get_data(id_)
    else:
        user_info = await db().get_data(call.from_user.id)
        await db().update_user_type("courier", call.from_user.id)
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    orders = int(user_info[5])
    good_orders = int(user_info[6])
    bad_orders = int(orders - good_orders)
    ms = await st_db().get_admin_settings_item(message_info="Courier_menu")
    msg = ms.replace('{item1}', str(orders)).replace('{item2}', str(good_orders)).replace('{item3}', str(bad_orders))
    # if int(user_info[7]) == 1:
    #     keyboard.add(button(text='✅', callback_data='reverse_receiving'))
    # else:
    #     keyboard.add(button(text='❌', callback_data='reverse_receiving'))
    await call.message.delete()
    await call.message.answer(msg, reply_markup=keyboard)


async def reverse_receiving(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    id = call.from_user.id
    user_receiving = await db().get_receiving_order(id)
    if int(user_receiving[0]) == 1:
        await db().update_receiving_order(user_id=id, receiving_order=0)
    else:
        await db().update_receiving_order(user_id=id, receiving_order=1)
    await courier_menu(call, state)


async def restaurant_name(call: types.CallbackQuery, state: FSMContext):
    msg = await st_db().get_admin_settings_item(message_info="Enter_restaurant_name")
    await call.message.answer(msg)
    await call.message.delete()
    await state.set_state('restaurant_address')


async def restaurant_address(message: types.Message, state: FSMContext):
    await message.bot.delete_message(message.from_user.id, message.message_id - 1)
    restaurant_name = message.text
    user_id = message.from_user.id
    msg = await st_db().get_admin_settings_item(message_info="Enter_restaurant_address")
    await db().update_restaurant_name(user_id, restaurant_name)
    await message.answer(msg)
    await message.delete()
    await state.set_state('restaurant_name_text')


async def restaurant_name_text(message: types.Message, state: FSMContext, ):
    await message.bot.delete_message(message.from_user.id, message.message_id - 1)
    restaurant_adress = message.text
    user_id = message.from_user.id
    await db().update_user_type("customer", user_id)
    await db().update_restaurant_phone_phone_address(user_id=user_id, address=restaurant_adress)
    user_info = await db().get_data(message.from_user.id)
    # keyboard = types.InlineKeyboardMarkup(row_width=2)
    # button = types.InlineKeyboardButton
    orders = int(user_info[5])
    name = user_info[8]
    random_num = random.randint(1, 5)
    hello_msg = await st_db().get_admin_settings_item(message_info=f"Customer_hello_message_{random_num}")
    await message.answer(hello_msg)
    ms = await st_db().get_admin_settings_item(message_info="Customer_menu")
    msg = ms.replace('{item1}', str(name)).replace('{item2}', str(orders))
    # keyboard.add(button(text='Изменить адрес', callback_data='create_orders'))
    # keyboard.add(button(text='Изменить имя', callback_data='get_last_order'))
    await message.delete()
    await message.answer(msg, reply_markup=await customer_keyboard())


async def customer_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(text="Заказ", callback_data='create_orders'),
               KeyboardButton(text="Закупка", callback_data='create_purchase'))
    return markup


async def customer_menu(call: types.CallbackQuery, state: FSMContext, id_=None, reply_markup=None):
    if id_:
        await db().update_user_type("customer", id_)
        user_info = await db().get_data(id_)
    else:
        await db().update_user_type("customer", call.from_user.id)
        user_info = await db().get_data(call.from_user.id)
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    orders = int(user_info[5])
    name = user_info[8]
    ms = await st_db().get_admin_settings_item(message_info="Customer_menu")
    msg = ms.replace('{item1}', str(name)).replace('{item2}', str(orders))
    keyboard.add(button(text='Изменить адрес', callback_data='change_adress'))
    keyboard.add(button(text='Изменить имя', callback_data='change_name'))
    await call.message.delete()
    await call.message.answer(msg, reply_markup=keyboard)

async def change_adress (call: types.CallbackQuery, state: FSMContext):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    msg = '''
<b>Введите новое место отправления </b>
'''
    keyboard.add(button(text='назад', callback_data='customer_menu'))
    await call.message.answer(msg, reply_markup=keyboard)
    await call.message.delete()
    await state.set_state('change_adress_text')

async def change_adress_text (message: types.Message, state: FSMContext):
    id = message.from_user.id
    new_adress =message.text
    await db().update_restaurant_phone_phone_address(user_id=id, address=new_adress)
    user_info = await db().get_data(user_id=id)
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    orders = int(user_info[5])
    name = user_info[8]
    ms = await st_db().get_admin_settings_item(message_info="Customer_menu")
    msg = ms.replace('{item1}', str(name)).replace('{item2}', str(orders))
    keyboard.add(button(text='Изменить адрес', callback_data='change_adress'))
    keyboard.add(button(text='Изменить имя', callback_data='change_name'))
    await message.delete()
    await message.answer(msg, reply_markup=keyboard)

async def change_name (call: types.CallbackQuery, state: FSMContext):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    msg = '''
<b>Введите новое имя ресторана </b>
'''
    keyboard.add(button(text='назад', callback_data='customer_menu'))
    await call.message.answer(msg, reply_markup=keyboard)
    await call.message.delete()
    await state.set_state('change_name_text')

async def change_name_text (message: types.Message, state: FSMContext):
    id = message.from_user.id
    new_name =message.text
    await db().update_restaurant_name(user_id=id, restaurant_name=new_name)
    user_info = await db().get_data(user_id=id)
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    orders = int(user_info[5])
    name = user_info[8]
    ms = await st_db().get_admin_settings_item(message_info="Customer_menu")
    msg = ms.replace('{item1}', str(name)).replace('{item2}', str(orders))
    keyboard.add(button(text='Изменить адрес', callback_data='change_adress'))
    keyboard.add(button(text='Изменить имя', callback_data='change_name'))
    await message.delete()
    await message.answer(msg, reply_markup=keyboard)

# async def get_last_order(call: types.CallbackQuery, state: FSMContext):
#     user_id = call.from_user.id
#     order = await db().get_count_orders(user_id)
#     order_num = int(order[0][0])
#     order_id = str(user_id) + str(order_num - 1)
#     data = await state.get_data()
#     await state.update_data(order_id=order_id)
#     info = await db().get_order_details_by_id(order_id)
#     keyboard = types.InlineKeyboardMarkup(row_width=2)
#     button = types.InlineKeyboardButton
#     ms = await st_db().get_admin_settings_item(message_info="Last_order")
#     msg = ms.replace('{item1}', str(info[3])).replace('{item2}', str(info[4])).replace('{item3}', str(info[5]))\
#         .replace('{item4}', str(info[6])).replace('{item5}', str(info[7]))
#     flag = await db().check_finish_order(order_id)
#     if flag:
#         keyboard.add(button(text='Изменить цену', callback_data='change_order_price'))
#     keyboard.add(button(text='Назад', callback_data='customer_menu'))
#     await call.message.delete()
#     await call.message.answer(msg, reply_markup=keyboard)

#


async def new_order(state: FSMContext):
    data = await state.get_data()

    '''<b>Меню | Добавить заказ</b>

<b>Место отправления:</b> <code>{item1}</code>
<b>Место доставки:</b> <code>{item2}</code>
<b>Будет готово до:</b> <code>{item3}</code>
<b>Доставить до:</b> <code>{item4}</code>
<b>Телефон клиента:</b> <code>{item5}</code>
<b>Цена:</b> <code>{item6}</code>
<b>Комментарий:</b> <code>{item7}</code>
'''

    point_A = data['point_A'] if data['point_A'] else '...'
    point_B = data['point_B'] if data['point_B'] else '...'
    deliver_start_time = data['deliver_start_time'] if data['deliver_start_time'] else '...'
    deliver_end_time = data['deliver_end_time'] if data['deliver_end_time'] else '...'
    phone = data['phone'] if data['phone'] else '...'
    price = data['price'] if data['price'] else '...'
    comment = data['comment'] if data['comment'] else '...'

    ms = await st_db().get_admin_settings_item(message_info="New_order")
    msg = (ms.replace('{item1}', str(point_A)).replace('{item2}', str(point_B))
           .replace('{item3}', str(deliver_start_time)).replace('{item4}', str(deliver_end_time))
           .replace('{item5}', str(phone)).replace('{item6}', str(price)).replace('{item7}', str(comment)))
    return msg


async def create_orders(message: types.Message, state: FSMContext):
    await state.update_data(point_A=None, point_B=None, deliver_start_time=None, deliver_end_time=None, phone=None,
                            price=None, comment=None)
    msg = await new_order(state=state)
    msg += '\n<b>Введите: Место отправления:</b>'
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    address = await db().get_restaurant_address(message.from_user.id)

    keyboard.add(button(text=f'{address}', callback_data='create_orders_point_A'))
    keyboard.add(button(text='Назад', callback_data='customer_menu'))
    await message.answer(msg, reply_markup=keyboard)
    await state.set_state('create_orders_point_A')


async def create_orders_point_A(state: FSMContext, call: types.CallbackQuery = None, message: types.Message = None):
    data = await state.get_data()
    if message:
        await message.bot.delete_message(message.from_user.id, message.message_id - 1)
        await message.bot.delete_message(message.from_user.id, message.message_id)
        point_A = message.text
        await state.update_data(point_A=point_A)
    else:
        adress = await db().get_restaurant_address(call.from_user.id)
        await call.message.bot.delete_message(call.from_user.id, call.message.message_id)
        await state.update_data(point_A=adress)

    msg = await new_order(state=state)
    msg += '\n<b>Введите: Место доставки</b>'
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    keyboard.add(button(text='Назад', callback_data='customer_menu'))
    if message:
        await message.answer(msg, reply_markup=keyboard)
    elif call:
        await call.message.answer(msg, reply_markup=keyboard)

    await state.set_state('create_orders_point_B')


async def create_orders_point_B(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.bot.delete_message(message.from_user.id, message.message_id - 1)
    await message.bot.delete_message(message.from_user.id, message.message_id)
    point_B = message.text
    await state.update_data(point_B=point_B)
    msg = await new_order(state=state)
    msg += '\n<b>Введите: Будет готово до в формате ЧЧ:ММ:</b>'
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    keyboard.add(button(text='Назад', callback_data='customer_menu'))
    await message.answer(msg, reply_markup=keyboard)
    # await message.bot.delete_message(message.from_user.id, message.message_id - 1)
    await state.set_state('create_orders_deliver_start_time')


async def create_orders_deliver_start_time(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.bot.delete_message(message.from_user.id, message.message_id - 1)
    await message.bot.delete_message(message.from_user.id, message.message_id)
    deliver_start_time = message.text
    if is_valid_time_format(deliver_start_time):
        await state.update_data(deliver_start_time=deliver_start_time)
        msg = await new_order(state=state)
        msg += '\n<b>Введите: Доставить до в формате ЧЧ:ММ:</b>'
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        button = types.InlineKeyboardButton
        keyboard.add(button(text='Назад', callback_data='customer_menu'))
        await message.answer(msg, reply_markup=keyboard)
        # await message.bot.delete_message(message.from_user.id, message.message_id - 1)
        await state.set_state('create_orders_deliver_end_time')
    else:
        msg = await new_order(state=state)
        msg += '\n<b>Неверный ввод введите время в формате ЧЧ:ММ:</b>'
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        button = types.InlineKeyboardButton
        keyboard.add(button(text='Назад', callback_data='customer_menu'))
        await message.answer(msg, reply_markup=keyboard)


async def create_orders_deliver_end_time(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.bot.delete_message(message.from_user.id, message.message_id - 1)
    await message.bot.delete_message(message.from_user.id, message.message_id)
    deliver_end_time = message.text
    if is_valid_time_format(deliver_end_time):
        await state.update_data(deliver_end_time=deliver_end_time)
        msg = await new_order(state=state)
        msg += '\n<b>Введите: Телефон клиента:</b>'
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        button = types.InlineKeyboardButton
        keyboard.add(button(text='Назад', callback_data='customer_menu'))
        await message.answer(msg, reply_markup=keyboard)
        # await message.bot.delete_message(message.from_user.id, message.message_id - 1)
        await state.set_state('create_orders_order_phone')
    else:
        msg = await new_order(state=state)
        msg += '\n<b>Неверный ввод введите время в формате ЧЧ:ММ:</b>'
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        button = types.InlineKeyboardButton
        keyboard.add(button(text='Назад', callback_data='customer_menu'))
        await message.answer(msg, reply_markup=keyboard)


async def create_orders_order_phone(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = message.from_user.id
    await state.update_data(customer_id=user_id)
    await message.bot.delete_message(message.from_user.id, message.message_id - 1)
    await message.bot.delete_message(message.from_user.id, message.message_id)
    phone = message.text
    await state.update_data(phone=phone)
    msg = await new_order(state=state)
    msg += '\n<b>Введите: Место Цена:</b>'
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
    msg += '\n<b>Введите: Комментарий</b>'
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    keyboard.add(button(text='Назад', callback_data='customer_menu'))
    await message.answer(msg, reply_markup=keyboard)
    await state.set_state('create_orders_comment')


tasks_dict = {}


async def create_orders_comment(message: types.Message, state: FSMContext):
    await message.bot.delete_message(message.from_user.id, message.message_id - 1)
    comment = message.text
    user_id = message.from_user.id
    restaurant = await db().get_restaurant_name(user_id)
    username = message.from_user.username
    data = await state.get_data()
    await state.update_data(comment=comment)
    count = await db().get_count_orders(user_id)
    order_id = str(user_id) + str(count[0][0]) + "0"
    print(count[0][0])
    print(order_id)
    await db().add_orders_db(order_id=int(order_id), customer_id=user_id, customer_name=username,
                             restaurant_name=restaurant[0][0], point_A=data['point_A'], point_B=data['point_B'],
                             deliver_start_time=data['deliver_start_time'], deliver_end_time=data['deliver_end_time'],
                             phone=data['phone'], price=data['price'], comment=comment)
    await db().update_count_orders(user_id)
    current_task = asyncio.create_task(
        mailing_order(call=types.CallbackQuery(message=message), state=state, order_id=int(order_id),
                      restaurant_name=restaurant[0][0], point_A=data['point_A'],
                      point_B=data['point_B'], deliver_start_time=data['deliver_start_time'],
                      deliver_end_time=data['deliver_end_time'], phone=data['phone'], price=data['price'],
                      comment=comment))
    task_name = order_id + "0"
    tasks_dict[task_name] = current_task
    ms = await st_db().get_admin_settings_item(message_info="New_order")
    '''<b>Меню | Добавить заказ</b>

<b>Место отправления:</b> <code>{item1}</code>
<b>Место доставки:</b> <code>{item2}</code>
<b>Будет готово до:</b> <code>{item3}</code>
<b>Доставить до:</b> <code>{item4}</code>
<b>Телефон клиента:</b> <code>{item5}</code>
<b>Цена:</b> <code>{item6}</code>
<b>Комментарий:</b> <code>{item7}</code>
'''
    msg = (ms.replace('{item1}', data['point_A']).replace('{item2}', data['point_B'])
           .replace('{item3}', data['deliver_start_time']).replace('{item4}', data['deliver_end_time'])
           .replace('{item5}', data['phone']).replace('{item6}', data['price']).replace('{item7}', comment))
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    flag = await db().check_finish_application(application_id=order_id, table="Orders", parameter="Order_Id")
    if flag:
        keyboard.add(button(text='Изменить цену', callback_data=f'change_application_price_{order_id}'))
        keyboard.add(button(text='Отменить', callback_data=f'cancel_application_{order_id}'))
    await message.answer(msg, reply_markup=keyboard)
    # await customer_menu(types.CallbackQuery(message=message), state, user_id)


async def cancel_application(call: types.CallbackQuery, state: FSMContext):
    application_id = int(call.data[19:])
    if call.data[-1] == "0":
        flag = await db().check_finish_application(application_id=application_id, table="Orders", parameter="Order_Id")
    else:
        flag = await db().check_finish_application(application_id=application_id, table="Purchase", parameter="Purchase_Id")
    if flag:
        if call.data[-1] == "0":
            asyncio.create_task(delete_all_messages(call=call, state=state,
                                                    order_id=application_id, table="Orders",
                                                    parameter="Order_Id"))
        else:
            asyncio.create_task(
                delete_all_messages(call=call, state=state, order_id=application_id,
                                    table="Purchase",
                                    parameter="Purchase_Id"))
        msg = '''
    <b>Заказ отменен</b>'''
    else:
        msg = '''
<b>Заказ уже в работе</b>
'''
    await call.message.answer(msg)
    return


async def change_application_price(call: types.CallbackQuery, state: FSMContext):
    application_id = int(call.data[25:])
    if call.data[-1] == "0":
        # order
        info = await db().get_order_details_by_id(application_id)
        print(f"Order{info}")
        msg_co = await st_db().get_admin_settings_item(message_info="Сhange_order")
        msg_courier = (
            msg_co.replace('{item1}', str(info[5])).replace('{item2}', str(info[6])).replace('{item3}', str(info[7]))
            .replace('{item4}', str(info[8])).replace('{item5}', str(info[9])).replace('{item6}', str(info[10]))
            .replace('{item7}', str(info[11])))
    else:
        # purchase
        info = await db().get_purchase_details_by_id(application_id)
        msg_co = await st_db().get_admin_settings_item(message_info="Change_purchase")
        msg_courier = (
            msg_co.replace('{item1}', str(info[5])).replace('{item2}', str(info[6])).replace('{item3}', str(info[7]))
            .replace('{item4}', str(info[8])).replace('{item5}', str(info[9])).replace('{item6}', str(info[10]))
            .replace('{item7}', str(info[11])))

    data = await state.get_data()
    await state.update_data(application_id=application_id)
    # keyboard = types.InlineKeyboardMarkup(row_width=2)
    # button = types.InlineKeyboardButton
    await call.message.answer(msg_courier)
    await call.message.delete()
    await state.set_state(f'change_application_price_text')


async def change_application_price_text(message: types.Message, state: FSMContext):
    await message.bot.delete_message(message.from_user.id, message.message_id - 1)
    data = await state.get_data()
    application_id = str(data['application_id'])
    new_price = message.text
    print(f"новая цена: {new_price}")
    print(f"application_id: {application_id}")
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    if application_id[-1] == "0":
        flag = await db().check_finish_application(application_id=data['application_id'], table="Orders",
                                                   parameter="Order_Id")
        info = await db().get_order_details_by_id(application_id)
        print(f"Флаг: {flag}")
        if flag:
            keyboard.add(button(text='Изменить цену', callback_data=f'change_application_price_{application_id}'))
            keyboard.add(button(text='Отменить', callback_data=f'cancel_application_{application_id}'))
            asyncio.create_task(delete_all_messages(call=types.CallbackQuery(message=message), state=state,
                                                    order_id=application_id, table="Orders",
                                                    parameter="Order_Id"))
            await db().update_order(parametr=new_price, order_id=data['application_id'], table="Price")
            info = await db().get_order_details_by_id(application_id)
            asyncio.create_task(
                mailing_order(call=types.CallbackQuery(message=message), state=state, order_id=int(application_id),
                              restaurant_name=info[4], point_A=info[5],
                              point_B=info[6], deliver_start_time=info[7],
                              deliver_end_time=info[8], phone=info[9], price=info[10],
                              comment=info[11]))
        ms = await st_db().get_admin_settings_item(message_info="New_order")
        msg = (ms.replace('{item1}', str(info[5])).replace('{item2}', str(info[6]))
               .replace('{item3}', str(info[7])).replace('{item4}', str(info[8]))
               .replace('{item5}', str(info[9])).replace('{item6}', str(info[10])).replace('{item7}', str(info[11])))
    else:
        flag = await db().check_finish_application(application_id=data['application_id'], table="Purchase",
                                                   parameter="Purchase_Id")
        info = await db().get_purchase_details_by_id(application_id)
        if flag:
            keyboard.add(button(text='Изменить цену', callback_data=f'change_application_price_{application_id}'))
            keyboard.add(button(text='Отменить', callback_data=f'cancel_application_{application_id}'))
            asyncio.create_task(
                delete_all_messages(call=types.CallbackQuery(message=message), state=state, order_id=application_id,
                                    table="Purchase",
                                    parameter="Purchase_Id"))
            await db().update_purchase(parametr=new_price, purchase_id=data['application_id'], table="Price")
            info = await db().get_purchase_details_by_id(application_id)
            asyncio.create_task(
                mailing_purchase(call=types.CallbackQuery(message=message), state=state,
                                 purchase_id=int(application_id),
                                 restaurant_name=info[4], point_A=info[5], point_B=info[6],
                                 count=info[7], weight=info[8], purchase_end_time=info[9],
                                 price=info[10], comment=info[11]))
        ms = await st_db().get_admin_settings_item(message_info="New_order")
        msg = (ms.replace('{item1}', str(info[5])).replace('{item2}', str(info[6]))
               .replace('{item3}', str(info[7])).replace('{item4}', str(info[8]))
               .replace('{item5}', str(info[9])).replace('{item6}', str(info[10])).replace('{item7}', str(info[11])))

    await message.delete()
    await message.answer(msg, reply_markup=keyboard)


async def new_purchase(state: FSMContext):
    data = await state.get_data()
    '''<b>Меню | Добавить заказ</b>

<b>Место Закупки:</b> <code>{item1}</code>
<b>Куда:</b> <code>{item2}</code>
<b>Количество позиций:</b> <code>{item3}</code>
<b>Вес закупки:</b> <code>{item4}</code>
<b>Доставить до:</b> <code>{item5}</code>
<b>Цена:</b> <code>{item6}</code>
<b>Комментарий:</b> <code>{item7}</code>
'''
    point_A = data['point_A'] if data['point_A'] else '...'
    point_B = data['point_B'] if data['point_B'] else '...'
    count = data['count'] if data['count'] else '...'
    weight = data['weight'] if data['weight'] else '...'
    purchase_end_time = data['purchase_end_time'] if data['purchase_end_time'] else '...'
    price = data['price'] if data['price'] else '...'
    comment = data['comment'] if data['comment'] else '...'

    ms = await st_db().get_admin_settings_item(message_info="New_purchase")
    print(ms)
    msg = (ms.replace('{item1}', str(point_A)).replace('{item2}', str(point_B)).replace('{item3}', str(count))
           .replace('{item4}', str(weight)).replace('{item5}', str(purchase_end_time)).replace('{item6}', str(price))
           .replace('{item7}', str(comment)))
    return msg


async def create_purchase(message: types.Message, state: FSMContext):
    await state.update_data(order_type=None, point_A=None, point_B=None, count=None, weight=None,
                            purchase_end_time=None, price=None, comment=None)
    msg = await new_purchase(state=state)
    msg += '\n<b>Введите: Место Закупки</b>'
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    keyboard.add(button(text='Назад', callback_data='customer_menu'))
    await message.answer(msg, reply_markup=keyboard)
    await state.set_state('create_purchase_point_A')


async def create_purchase_point_A(state: FSMContext, message: types.Message = None, call: types.CallbackQuery = None):
    data = await state.get_data()
    await message.bot.delete_message(message.from_user.id, message.message_id - 1)
    await message.bot.delete_message(message.from_user.id, message.message_id)
    point_A = message.text
    await state.update_data(point_A=point_A)
    msg = await new_purchase(state=state)
    msg += '\n<b>Введите: Куда</b>'
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    adress = await db().get_restaurant_address(user_id=message.from_user.id)
    keyboard.add(button(text=f'{adress}', callback_data='create_purchase_point_B'))
    keyboard.add(button(text='Назад', callback_data='customer_menu'))
    await message.answer(msg, reply_markup=keyboard)
    # await message.bot.delete_message(message.from_user.id, message.message_id - 1)
    await state.set_state('create_purchase_point_B')


async def create_purchase_point_B(state: FSMContext, message: types.Message = None, call: types.CallbackQuery = None):
    data = await state.get_data()
    if message:
        await message.bot.delete_message(message.from_user.id, message.message_id - 1)
        await message.bot.delete_message(message.from_user.id, message.message_id)
        point_B = message.text
        await state.update_data(point_B=point_B)
    else:
        adress = await db().get_restaurant_address(call.from_user.id)
        await call.message.bot.delete_message(call.from_user.id, call.message.message_id)
        await state.update_data(point_B=adress)
    msg = await new_purchase(state=state)
    msg += '\n<b>Введите: Количество позиций</b>'
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    keyboard.add(button(text='Назад', callback_data='customer_menu'))
    if message:
        await message.answer(msg, reply_markup=keyboard)
    elif call:
        await call.message.answer(msg, reply_markup=keyboard)
    # await message.bot.delete_message(message.from_user.id, message.message_id - 1)
    await state.set_state('create_purchase_count')


async def create_purchase_count(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.bot.delete_message(message.from_user.id, message.message_id - 1)
    await message.bot.delete_message(message.from_user.id, message.message_id)
    count = message.text
    await state.update_data(count=count)
    msg = await new_purchase(state=state)
    msg += '\n<b>Введите: Вес закупки</b>'
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    keyboard.add(button(text='Назад', callback_data='customer_menu'))
    await message.answer(msg, reply_markup=keyboard)
    await state.set_state('create_purchase_weight')


async def create_purchase_weight(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.bot.delete_message(message.from_user.id, message.message_id - 1)
    await message.bot.delete_message(message.from_user.id, message.message_id)
    weight = message.text
    await state.update_data(weight=weight)
    msg = await new_purchase(state=state)
    msg += '\n<b>Введите: Доставить до в формате ЧЧ:ММ:</b>'
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    keyboard.add(button(text='Назад', callback_data='customer_menu'))
    await message.answer(msg, reply_markup=keyboard)
    await state.set_state('create_purchase_purchase_end_time')


async def create_purchase_purchase_end_time(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.bot.delete_message(message.from_user.id, message.message_id - 1)
    await message.bot.delete_message(message.from_user.id, message.message_id)
    purchase_end_time = message.text
    if is_valid_time_format(purchase_end_time):
        await state.update_data(purchase_end_time=purchase_end_time)
        msg = await new_purchase(state=state)
        msg += '\n<b>Введите: Цену заказа</b>'
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        button = types.InlineKeyboardButton
        keyboard.add(button(text='Назад', callback_data='customer_menu'))
        await message.answer(msg, reply_markup=keyboard)
        await state.set_state('create_purchase_price')
    else:
        msg = await new_purchase(state=state)
        msg += '\n<b>Неверный ввод введите время в формате ЧЧ:ММ:</b>'
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        button = types.InlineKeyboardButton
        keyboard.add(button(text='Назад', callback_data='customer_menu'))
        await message.answer(msg, reply_markup=keyboard)



async def create_purchase_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.bot.delete_message(message.from_user.id, message.message_id - 1)
    await message.bot.delete_message(message.from_user.id, message.message_id)
    price = message.text
    await state.update_data(price=price)
    msg = await new_purchase(state=state)
    msg += '\n<b>Введите: Комментарий</b>'
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    keyboard.add(button(text='Назад', callback_data='customer_menu'))
    await message.answer(msg, reply_markup=keyboard)
    await state.set_state('create_purchase_comment')


async def create_purchase_comment(message: types.Message, state: FSMContext):
    await message.bot.delete_message(message.from_user.id, message.message_id - 1)
    comment = message.text
    user_id = message.from_user.id
    restaurant = await db().get_restaurant_name(user_id)
    username = message.from_user.username
    data = await state.get_data()
    await state.update_data(comment=comment)
    count = await db().get_count_orders(user_id)
    purchase_id = str(user_id) + str(count[0][0]) + "1"
    await db().add_purchase_db(purchase_id=int(purchase_id), customer_id=user_id, customer_name=username,
                               restaurant_name=restaurant[0][0], point_A=data['point_A'], point_B=data['point_B'],
                               count=data['count'], weight=data['weight'], purchase_end_time=data['purchase_end_time'],
                               price=data['price'], comment=comment)
    await db().update_count_orders(user_id)
    current_task = asyncio.create_task(
        mailing_purchase(call=types.CallbackQuery(message=message), state=state, purchase_id=int(purchase_id),
                         restaurant_name=restaurant[0][0], point_A=data['point_A'], point_B=data['point_B'],
                         count=data['count'], weight=data['weight'], purchase_end_time=data['purchase_end_time'],
                         price=data['price'], comment=comment))
    task_name = purchase_id + "1"
    tasks_dict[task_name] = current_task
    ms = await st_db().get_admin_settings_item(message_info="New_purchase")
    '''<b>Меню | Добавить Закупку</b>

<b>Место Закупки:</b> <code>{item1}</code>
<b>Куда:</b> <code>{item2}</code>
<b>Количество позиций:</b> <code>{item3}</code>
<b>Вес закупки:</b> <code>{item4}</code>
<b>Доставить до:</b> <code>{item5}</code>
<b>Цена:</b> <code>{item6}</code>
<b>Комментарий:</b> <code>{item7}</code>

'''
    msg = (ms.replace('{item1}', data['point_A']).replace('{item2}', data['point_B'])
           .replace('{item3}', data['count']).replace('{item4}', data['weight'])
           .replace('{item5}', data['purchase_end_time']).replace('{item6}', data['price']).replace('{item7}', comment))
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    flag = await db().check_finish_application(application_id=purchase_id, table="Purchase", parameter="Purchase_Id")
    if flag:
        keyboard.add(button(text='Изменить цену', callback_data=f'change_application_price_{purchase_id}'))
        keyboard.add(button(text='Отменить', callback_data=f'cancel_application_{purchase_id}'))
    await message.answer(msg, reply_markup=keyboard)
    # await customer_menu(types.CallbackQuery(message=message), state, user_id)


async def application_accepted(call: types.CallbackQuery, state: FSMContext):
    application_id = int(call.data[21:])
    courier_name = call.from_user.username
    global tasks_dict
    if application_id in tasks_dict:
        tasks_dict[application_id].cancel()
        del tasks_dict[application_id]
    courier_id = call.from_user.id
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    await db().update_count_orders(courier_id)
    start_time = await get_moscow_time()
    time = await st_db().get_admin_settings_item(message_info="Cancel_time")
    if call.data[-1] == "0":
        # order
        await db().update_order(parametr=start_time, order_id=application_id, table="Start_time")
        table = "Orders"
        parameter = "Order_Id"
        info = await db().get_order_details_by_id(application_id)
        print(f"Order{info}")
        await db().update_order(parametr=courier_id, order_id=application_id, table="Courier_id")
        await db().update_order(parametr=courier_name, order_id=application_id, table="Courier_name")
        msg_co = await st_db().get_admin_settings_item(message_info="Accepted_order_courier")
        msg_courier = (
            msg_co.replace('{item1}', str(info[3])).replace('{item2}', str(info[4])).replace('{item3}', str(info[5]))
            .replace('{item4}', str(info[6])).replace('{item5}', str(info[7])).replace('{item6}', str(info[8]))
            .replace('{item8}', str(info[10])).replace('{item9}', str(info[11])).replace('{time}', str(time)))
        ms = await st_db().get_admin_settings_item(message_info="Accepted_order_customer")
        msg_customer = ms.replace('{item1}', str(info[6])).replace('{item2}', str(courier_name))
    else:
        # purchase
        await db().update_purchase(parametr=start_time, purchase_id=application_id, table="Start_time")
        table = "Purchase"
        parameter = "Purchase_Id"
        info = await db().get_purchase_details_by_id(application_id)
        await db().update_purchase(parametr=courier_id, purchase_id=application_id, table="Courier_id")
        await db().update_purchase(parametr=courier_name, purchase_id=application_id, table="Courier_name")
        msg_co = await st_db().get_admin_settings_item(message_info="Accepted_purchase_courier")
        msg_courier = (
            msg_co.replace('{item1}', str(info[3])).replace('{item2}', str(info[4])).replace('{item3}', str(info[5]))
            .replace('{item4}', str(info[6])).replace('{item5}', str(info[7])).replace('{item6}', str(info[8]))
            .replace('{item7}', str(info[9])).replace('{item8}', str(info[10])).replace('{item9}', str(info[11]))
            .replace('{time}', str(time)))
        ms = await st_db().get_admin_settings_item(message_info="Accepted_purshase_customer")
        msg_customer = ms.replace('{item1}', str(info[6])).replace('{item2}', str(courier_name))
    asyncio.create_task(
        delete_all_messages(call=call, state=state, order_id=application_id, table=table, parameter=parameter))
    keyboard.add(button(text='Отказаться', callback_data=f'courier_cancel_application_{application_id}'))
    await call.bot.send_message(info[1], msg_customer)
    sent_message = await call.bot.send_message(courier_id, msg_courier, reply_markup=keyboard)
    await asyncio.sleep(int(time))
    try:
        msg_co = await st_db().get_admin_settings_item(message_info="Total_accepted_order_courier")
        msg_courier = (
            msg_co.replace('{item1}', str(info[3])).replace('{item2}', str(info[4])).replace('{item3}', str(info[5]))
            .replace('{item4}', str(info[6])).replace('{item5}', str(info[7])).replace('{item6}', str(info[8]))
            .replace('{item7}', str(info[9])).replace('{item8}', str(info[10])).replace('{item9}', str(info[11]))
            .replace('{time}', str(time)))
        new_keyboard = types.InlineKeyboardMarkup(row_width=2)
        new_keyboard.add(button(text='Доставил', callback_data=f'successful_completion_{application_id}'))
        await call.bot.edit_message_text(chat_id=courier_id, message_id=sent_message.message_id, text=msg_courier,
                                         reply_markup=new_keyboard)
    except:
        pass


async def courier_cancel_application(call: types.CallbackQuery, state: FSMContext):
    courier_id = call.from_user.id
    msg_courier = await st_db().get_admin_settings_item(message_info="Cancel_order_courier")
    application_id = int(call.data[27:])
    if call.data[-1] == "0":
        # order
        asyncio.create_task(
            delete_all_messages(call=call, state=state, order_id=application_id, table="Orders", parameter="Order_Id"))
        info = await db().get_order_details_by_id(application_id)
        customer_id = info[1]
        asyncio.create_task(
            mailing_order(call=call, state=state, order_id=int(application_id),
                          restaurant_name=info[4], point_A=info[5],
                          point_B=info[6], deliver_start_time=info[7],
                          deliver_end_time=info[8], phone=info[9], price=info[10],
                          comment=info[11]))
        ms = await st_db().get_admin_settings_item(message_info="Cancel_order_customer")
        msg_customer = ms.replace('{item1}', str(info[6])).replace('{item2}', str(info[2]))
    else:
        # purchase
        asyncio.create_task(delete_all_messages(call=call, state=state, order_id=application_id, table="Purchase",
                                                parameter="Purchase_Id"))
        info = await db().get_purchase_details_by_id(application_id)
        customer_id = info[1]
        asyncio.create_task(
            mailing_purchase(call=call, state=state, purchase_id=int(application_id),
                             restaurant_name=info[4], point_A=info[5], point_B=info[6],
                             count=info[7], weight=info[8], purchase_end_time=info[9],
                             price=info[10], comment=info[11]))
        ms = await st_db().get_admin_settings_item(message_info="Cancel_purshase_customer")
        msg_customer = ms.replace('{item1}', str(info[6])).replace('{item2}', str(info[2]))
    print(application_id)
    order_data = await db().get_order_details_by_id(application_id)
    print(order_data)

    await call.bot.send_message(customer_id, msg_customer)
    await call.answer(msg_courier, show_alert=True)
    await call.message.delete()


async def successful_completion(call: types.CallbackQuery, state: FSMContext):
    username = call.from_user.username
    courier_id = call.from_user.id
    application_id = int(call.data[22:])
    end_time = await get_moscow_time()
    if call.data[-1] == "0":
        # order
        customer_id = await db().get_customer_id_application(application_id=application_id, table="Orders",
                                                             parameter="Order_id")
        point_B = await db().get_point_B_application(application_id=application_id, table="Orders",
                                                           parameter="Order_id")
        ms = await st_db().get_admin_settings_item(message_info="Finish_order_message_customer")
        msg = (ms.replace('{item1}', str(point_B[0][0])).replace('{item2}', str(username)))
        await db().update_order(parametr=end_time, order_id=application_id, table="End_time")
    else:
        # purchase
        customer_id = await db().get_customer_id_application(application_id=application_id, table="Purchase",
                                                             parameter="Purchase_Id")
        point_B = await db().get_point_B_application(application_id=application_id, table="Purchase",
                                                     parameter="Purchase_Id")
        ms = await st_db().get_admin_settings_item(message_info="Finish_purchase_message_customer")
        msg = (ms.replace('{item1}', str(point_B[0][0])).replace('{item2}', str(username)))
        await db().update_purchase(parametr=end_time, purchase_id=application_id, table="End_time")

    await db().update_good_count_orders(courier_id)
    await call.message.delete()
    await call.bot.send_message(int(customer_id[0]), msg)
