import asyncio
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from database.Database import Database as db
from database.Settings_database import Settings_database as st_db

from functions.service_function import mailing, delete_all_messages, get_moscow_time

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
            await customer_menu(types.CallbackQuery(message=message), state, id_=message.from_user.id)
        else:
            await get_courier_phone(types.CallbackQuery(message=message), state, id_=message.from_user.id)
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

async def get_courier_phone(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Нажмите на кнопку ниже, чтобы отправить контакт",
                              reply_markup=await contact_keyboard())
    await call.message.delete()
    await state.set_state('get_courier_phone_text')


async def get_courier_phone_text(message: types.Message, state: FSMContext):
    contact = message.contact
    id = message.from_user.id
    print(contact)
    await db().update_restaurant_phone_phone_number(user_id=id, phone=str(contact))
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
    if int(user_info[7]) == 1:
        keyboard.add(button(text='✅', callback_data='reverse_receiving'))
    else:
        keyboard.add(button(text='❌', callback_data='reverse_receiving'))
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

async def restaurant_name_text(message: types.Message, state: FSMContext,):
    await message.bot.delete_message(message.from_user.id, message.message_id - 1)
    restaurant_adress = message.text
    user_id = message.from_user.id
    await db().update_user_type("customer", user_id)
    await db().update_restaurant_phone_phone_address(user_id=user_id, address=restaurant_adress)
    user_info = await db().get_data(message.from_user.id)
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    orders = int(user_info[5])
    name = user_info[8]
    print(name)
    ms = await st_db().get_admin_settings_item(message_info="Customer_menu")
    print(name)
    msg = ms.replace('{item1}', str(name)).replace('{item2}', str(orders))
    print(name)
    keyboard.add(button(text='Создать заказ', callback_data='create_orders'))
    keyboard.add(button(text='Мой последний заказ', callback_data='get_last_order'))
    await message.delete()
    await message.answer(msg, reply_markup=await customer_keyboard())

async def customer_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(text="Заказ", callback_data='create_orders'),
               KeyboardButton(text="Закупка", callback_data='create_purchase'))
    return markup

async def customer_menu(call: types.CallbackQuery, state: FSMContext, id_=None):
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
    keyboard.add(button(text='Создать заказ', callback_data='create_orders'))
    keyboard.add(button(text='Мой последний заказ', callback_data='get_last_order'))
    await call.message.delete()
    await call.message.answer(msg, reply_markup=await customer_keyboard())

async def get_last_order(call: types.CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    order = await db().get_count_orders(user_id)
    order_num = int(order[0][0])
    order_id = str(user_id) + str(order_num - 1)
    data = await state.get_data()
    await state.update_data(order_id=order_id)
    info = await db().get_order_details_by_id(order_id)
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    ms = await st_db().get_admin_settings_item(message_info="Last_order")
    msg = ms.replace('{item1}', str(info[3])).replace('{item2}', str(info[4])).replace('{item3}', str(info[5]))\
        .replace('{item4}', str(info[6])).replace('{item5}', str(info[7]))
    flag = await db().check_finish_order(order_id)
    if flag:
        keyboard.add(button(text='Изменить цену', callback_data='change_order_price'))
    keyboard.add(button(text='Назад', callback_data='customer_menu'))
    await call.message.delete()
    await call.message.answer(msg, reply_markup=keyboard)


async def change_order_price(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    msg = await st_db().get_admin_settings_item(message_info="Change_order_price")
    keyboard.add(button(text='Назад', callback_data='get_last_order'))
    await call.message.answer(msg, reply_markup=keyboard)
    await call.message.delete()
    await state.set_state('change_order_price_text')

async def change_order_price_text(message: types.Message, state: FSMContext):
    new_price = message.text
    data = await state.get_data()
    flag = await db().check_finish_order(data['order_id'])
    if flag:
        await db().update_order(parametr=new_price, order_id=data['order_id'], table="Price")
        order_data= await db().get_order_details_by_id(data['order_id'])
        restaurant = order_data[2]
        order_type = order_data[3]
        price = order_data[4]
        point_A = order_data[5]
        point_B = order_data[6]
        comment = order_data[7]
        asyncio.create_task(delete_all_messages(types.CallbackQuery(message=message), state, data['order_id']))
        asyncio.create_task(
            mailing(order_id=int(data['order_id']), order_type=order_type, point_A=point_A, point_B=point_B,
                    comment=comment, call=types.CallbackQuery(message=message), state=state, price=price, restaurant=restaurant))
    info = await db().get_order_details_by_id(data['order_id'])
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    ms = await st_db().get_admin_settings_item(message_info="Last_order")
    msg = ms.replace('{item1}', str(info[3])).replace('{item2}', str(info[4])).replace('{item3}', str(info[5]))\
        .replace('{item4}', str(info[6])).replace('{item5}', str(info[7]))
    keyboard.add(button(text='Изменить цену', callback_data='change_order_price'))
    keyboard.add(button(text='Назад', callback_data='customer_menu'))
    await message.delete()
    await message.answer(msg, reply_markup=keyboard)
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

async def create_orders(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(point_A=None, point_B=None, deliver_start_time=None, deliver_end_time=None,phone=None,
                            price=None, comment=None)
    msg = await new_order(state=state)
    msg += '\n<b>Введите: Место отправления:</b>'
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    print(10)
    keyboard.add(button(text='Назад', callback_data='customer_menu'))
    await call.message.answer(msg, reply_markup=keyboard)
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
    msg += '\n<b>Введите: Будет готово до:</b>'
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
    await state.update_data(deliver_start_time=deliver_start_time)
    msg = await new_order(state=state)
    msg += '\n<b>Введите: Доставить до:</b>'
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    keyboard.add(button(text='Назад', callback_data='customer_menu'))
    await message.answer(msg, reply_markup=keyboard)
    # await message.bot.delete_message(message.from_user.id, message.message_id - 1)
    await state.set_state('create_orders_deliver_end_time')

async def create_orders_deliver_end_time(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.bot.delete_message(message.from_user.id, message.message_id - 1)
    await message.bot.delete_message(message.from_user.id, message.message_id)
    deliver_end_time = message.text
    await state.update_data(deliver_end_time=deliver_end_time)
    msg = await new_order(state=state)
    msg += '\n<b>Введите: Телефон клиента:</b>'
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    keyboard.add(button(text='Назад', callback_data='customer_menu'))
    await message.answer(msg, reply_markup=keyboard)
    # await message.bot.delete_message(message.from_user.id, message.message_id - 1)
    await state.set_state('create_orders_order_phone')

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
    print(user_id)
    data = await state.get_data()
    await state.update_data(comment=comment)
    count = await db().get_count_orders(user_id)
    order_id = str(user_id) + str(count[0][0])
    print(order_id)
    print(comment)
    await db().add_orders_db(order_id=int(order_id), customer_id=user_id, customer_name=username,
                             restaurant_name=restaurant[0][0], point_A=data['point_A'], point_B=data['point_B'],
                             deliver_start_time=data['deliver_start_time'], deliver_end_time=data['deliver_end_time'],
                             phone=data['phone'], price=data['price'], comment=comment)
    print("Added order")
    await db().update_count_orders(user_id)
    current_task = asyncio.create_task(
        mailing(order_id=int(order_id), order_type=data['order_type'], point_A=data['point_A'], point_B=data['point_B'],
                comment=comment, call=types.CallbackQuery(message=message), state=state, price=data['price'], restaurant=restaurant[0][0]))
    task_name = order_id + "0"
    tasks_dict[task_name] = current_task
    await customer_menu(types.CallbackQuery(message=message), state, user_id)

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

    ms = await st_db().get_admin_settings_item(message_info="New_order")
    msg = (ms.replace('{item1}', str(point_A)).replace('{item2}', str(point_B)).replace('{item3}', str(count))
           .replace('{item4}', str(weight)).replace('{item5}', str(purchase_end_time)).replace('{item6}', str(price))
           .replace('{item7}', str(comment)))
    return msg

async def create_purchase(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(order_type=None, point_A=None, point_B=None, comment=None, price=None)
    msg = await new_order(state=state)
    msg += '\n<b>Введите: Место Закупки</b>'
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    keyboard.add(button(text='Назад', callback_data='customer_menu'))
    await call.message.edit_text(msg, reply_markup=keyboard)
    await state.set_state('create_purchase_point_A')

async def create_purchase_point_A(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.bot.delete_message(message.from_user.id, message.message_id - 1)
    await message.bot.delete_message(message.from_user.id, message.message_id)
    point_A = message.text
    await state.update_data(point_A=point_A)
    msg = await new_order(state=state)
    msg += '\n<b>Введите: Куда</b>'
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    keyboard.add(button(text='Назад', callback_data='customer_menu'))
    await message.answer(msg, reply_markup=keyboard)
    # await message.bot.delete_message(message.from_user.id, message.message_id - 1)
    await state.set_state('create_purchase_point_B')


async def create_purchase_point_B(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.bot.delete_message(message.from_user.id, message.message_id - 1)
    await message.bot.delete_message(message.from_user.id, message.message_id)
    point_B = message.text
    await state.update_data(point_B=point_B)
    msg = await new_order(state=state)
    msg += '\n<b>Введите: Количество позиций</b>'
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    keyboard.add(button(text='Назад', callback_data='customer_menu'))
    await message.answer(msg, reply_markup=keyboard)
    # await message.bot.delete_message(message.from_user.id, message.message_id - 1)
    await state.set_state('create_purchase_count')

async def create_purchase_count(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.bot.delete_message(message.from_user.id, message.message_id - 1)
    await message.bot.delete_message(message.from_user.id, message.message_id)
    count = message.text
    await state.update_data(count=count)
    msg = await new_order(state=state)
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
    msg = await new_order(state=state)
    msg += '\n<b>Введите: Доставить до</b>'
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
    await state.update_data(purchase_end_time=purchase_end_time)
    msg = await new_order(state=state)
    msg += '\n<b>Введите: Цену заказа</b>'
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    keyboard.add(button(text='Назад', callback_data='customer_menu'))
    await message.answer(msg, reply_markup=keyboard)
    await state.set_state('create_purchase_price')

async def create_purchase_price(message: types.Message, state: FSMContext):
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
    await state.set_state('create_purchase_comment')

async def create_purchase_comment(message: types.Message, state: FSMContext):
    await message.bot.delete_message(message.from_user.id, message.message_id - 1)
    comment = message.text
    user_id = message.from_user.id
    restaurant = await db().get_restaurant_name(user_id)
    username = message.from_user.username
    print(user_id)
    data = await state.get_data()
    await state.update_data(comment=comment)
    count = await db().get_count_orders(user_id)
    purchase_id = str(user_id) + str(count[0][0])
    print(purchase_id)
    print(comment)
    await db().add_purchase_db(purchase_id=int(purchase_id), customer_id=user_id, customer_name=username,
                               restaurant_name=restaurant[0][0], point_A=data['point_A'], point_B=data['point_B'],
                               count=data['count'], weight=data['weight'], purchase_end_time=data['purchase_end_time'],
                               price=data['price'], comment=comment)
    await db().update_count_orders(user_id)
    current_task = asyncio.create_task(
        mailing(order_id=int(purchase_id), order_type=data['order_type'], point_A=data['point_A'], point_B=data['point_B'],
                comment=comment, call=types.CallbackQuery(message=message), state=state, price=data['price'], restaurant=restaurant[0][0]))
    task_name = purchase_id + "1"
    tasks_dict[task_name] = current_task
    await customer_menu(types.CallbackQuery(message=message), state, user_id)


async def application_accepted(call: types.CallbackQuery, state: FSMContext):
    order_id = int(call.data[21:])
    courier_name = call.from_user.username
    global tasks_dict
    if order_id in tasks_dict:
        tasks_dict[order_id].cancel()
        del tasks_dict[order_id]
    courier_id = call.from_user.id
    await db().update_order(parametr=courier_id, order_id=order_id, table="Courier_id")
    asyncio.create_task(delete_all_messages(call, state, order_id))
    courier_username = call.from_user.username
    info = await db().get_order_details_by_id(order_id)
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    customer_id = await db().get_customer_id_order(order_id)
    await db().update_count_orders(courier_id)
    ms = await st_db().get_admin_settings_item(message_info="Accepted_order_customer")
    msg_customer = ms.replace('{item1}', str(courier_name))
    time = await st_db().get_admin_settings_item(message_info="Cancel_time")
    msg_co = await st_db().get_admin_settings_item(message_info="Accepted_order_courier")
    msg_courier = msg_co.replace('{item1}', str(info[1])).replace('{item2}', str(info[2])).replace('{item3}', str(info[3]))\
        .replace('{item4}', str(info[4])).replace('{item5}', str(info[5])).replace('{item6}', str(info[6]))\
        .replace('{item7}', str(info[7])).replace('{time}', str(time))
    # print(customer_id)
    # print(courier_id)
    await db().update_order(parametr=courier_name, order_id=order_id, table="Courier_name")
    start_time = await get_moscow_time()
    await db().update_order(parametr=start_time, order_id=order_id, table="Start_time")
    keyboard.add(button(text='Отказаться', callback_data=f'cancel_order_{order_id}'))
    await call.bot.send_message(customer_id[0], msg_customer)
    sent_message = await call.bot.send_message(courier_id, msg_courier, reply_markup=keyboard)
    await asyncio.sleep(int(time))
    try:
        new_keyboard = types.InlineKeyboardMarkup(row_width=2)
        new_keyboard.add(button(text='Доставил', callback_data=f'successful_completion_{order_id}'))
        await call.bot.edit_message_reply_markup(courier_id, sent_message.message_id, reply_markup=new_keyboard)
    except:
        pass


async def cancel_order(call: types.CallbackQuery, state: FSMContext):
    msg_customer = await st_db().get_admin_settings_item(message_info="Cancel_order_customer")
    msg_courier = await st_db().get_admin_settings_item(message_info="Cancel_order_courier")
    order_id = int(call.data[13:])
    print(order_id)
    order_data = await db().get_order_details_by_id(order_id)
    print(order_data)
    restaurant = order_data[2]
    customer_id = order_data[9]
    order_type = order_data[3]
    price = order_data[4]
    point_A = order_data[5]
    point_B = order_data[6]
    comment = order_data[7]
    await call.bot.send_message(customer_id, msg_customer)
    await call.answer(msg_courier, show_alert=True)
    await call.message.delete()
    asyncio.create_task(delete_all_messages(call, state, order_id))
    asyncio.create_task(
        mailing(order_id=int(order_id), order_type=order_type, point_A=point_A, point_B=point_B,
                comment=comment, call=call, state=state, price=price, restaurant=restaurant))



async def successful_completion(call: types.CallbackQuery, state: FSMContext):
    order_id = int(call.data[22:])
    end_time = await get_moscow_time()
    customer_id = await db().get_customer_id_order(order_id)
    courier_id = await db().get_courier_id_order(order_id)
    print(f"Customer {customer_id}")
    print(courier_id[0][0])
    await db().update_good_count_orders(courier_id[0][0])
    await db().update_order(parametr=end_time, order_id=order_id, table="End_time")
    msg = await st_db().get_admin_settings_item(message_info="Finish_message_customer")
    await call.message.delete()
    await call.bot.send_message(int(customer_id[0]), msg)



