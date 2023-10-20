import ast
import asyncio
import random
import string
import keyboard as keyboard
from aiogram import types
from aiogram.dispatcher import FSMContext
from database.Database import Database as db
from aiogram import Bot

async def welcome(message: types.Message, state: FSMContext):
    # await db().add_new_admin(5823260569, "MaximSummer")
    # await db().add_new_admin(1610007895, "iliaul2")
    user_id = message.from_user.id
    username = message.from_user.username
    await state.update_data(user_id=user_id)
    ref = message.get_args()
    flag = await db().check_link(link=ref, link_type="user")
    is_user = await db().check_user(user_id=user_id)
    if ref[:3] == 'use' and str(flag[0]) == "1":
        await db().add_user_db(user_id=user_id, username=username, access=1)
        await db().delete_link(ref)
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        button = types.InlineKeyboardButton
        msg = f'''
<b>Выберите то кем вы являетесь</b>
<b>В дальнейшем нельзя будет изменить свой выбор</b>

<b>Заказчик: </b>

Оставляет заявки для выполнения заказов 🗒

<b>Курьер: </b>

Берет заказы для исполнения 📦
'''
        keyboard.add(button(text='Заказчик', callback_data='customer_menu'))
        keyboard.add(button(text='Курьер', callback_data='courier_menu'))
        await message.answer(msg, reply_markup=keyboard)
    elif str(is_user[0]) == "1":
        user_type = await db().get_user_type(user_id)
        if user_type[0] == 'customer':
            await customer_menu(types.CallbackQuery(message=message), state, id_=message.from_user.id)
        else:
            await courier_menu(types.CallbackQuery(message=message), state, id_=message.from_user.id)
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
    msg = f'''
<b>Главное меню</b>

<i>Моя статистика </i>

╔<b>Всего заказов: </b> {orders}
╠<b>Успешных заказов: </b> {good_orders}
╚<b>Отказался от заказов: </b> {bad_orders}
'''
    if int(user_info[9]) == 1:
        keyboard.add(button(text='Получаю заказы [✅]', callback_data='reverse_receiving'))
    else:
        keyboard.add(button(text='Получаю заказы [❌]', callback_data='reverse_receiving'))
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
    msg = f'''
<b>Главное меню</b>
<i>Моя статистика </i>

═<b>Всего заказов: </b> {orders}
'''
    keyboard.add(button(text='Создать заказ', callback_data='create_orders'))
    await call.message.delete()
    await call.message.answer(msg, reply_markup=keyboard)

async def new_order(state: FSMContext):
    data = await state.get_data()

    order_type = data['order_type'] if data['order_type'] else '...'
    point_A = data['point_A'] if data['point_A'] else '...'
    point_B = data['point_B'] if data['point_B'] else '...'
    comment = data['comment'] if data['comment'] else '...'

    msg = f'''
<b>Меню | Добавить заказ</b>
Обязательно выберите тип заказа: Доставка или Закупка

<b>Тип заказа:</b> <code>{order_type}</code>
<b>Место отправления:</b> <code>{point_A}</code>
<b>Место доставки:</b> <code>{point_B}</code>
<b>Комментарий:</b> <code>{comment}</code>
'''
    return msg

async def create_orders(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(order_type=None, point_A=None, point_B=None, comment=None)
    msg = await new_order(state=state)
    msg += '<b>Введите: Тип заказа</b>'
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    keyboard.add(button(text='Назад', callback_data='customer_menu'))
    await call.message.edit_text(msg, reply_markup=keyboard)
    await state.set_state('create_orders_order_type')


async def create_orders_order_type(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = message.from_user.id
    print(user_id)
    await state.update_data(customer_id=user_id)
    await message.bot.delete_message(message.from_user.id, message.message_id - 1)
    await message.bot.delete_message(message.from_user.id, message.message_id)
    order_type = message.text
    await state.update_data(order_type=order_type)
    msg = await new_order(state=state)
    msg += '<b>Введите: Место отправления</b>'
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    keyboard.add(button(text='Назад', callback_data='customer_menu'))
    await message.answer(msg, reply_markup=keyboard)
    # await message.bot.delete_message(message.from_user.id, message.message_id - 1)
    await state.set_state('create_orders_point_A')


async def create_orders_point_A(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.bot.delete_message(message.from_user.id, message.message_id - 1)
    await message.bot.delete_message(message.from_user.id, message.message_id)
    point_A = message.text
    await state.update_data(point_A=point_A)
    msg = await new_order(state=state)
    msg += '<b>Введите: Место доставки</b>'
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
    msg += '<b>Введите: Комментарий</b>'
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
    print(user_id)
    data = await state.get_data()
    await state.update_data(comment=comment)
    count = await db().get_count_orders(user_id)
    msg = await new_order(state=state)
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    keyboard.add(button(text='Назад', callback_data='customer_menu'))
    await message.answer(msg, reply_markup=keyboard)
    order_id = str(user_id) + str(count[0][0])
    await db().add_orders_db(order_id=int(order_id), customer_id=data['user_id'], order_type=data['order_type'],
                             point_A=data['point_A'], point_B=data['point_B'], comment=comment)
    await db().update_count_orders(user_id)
    await customer_menu(types.CallbackQuery(message=message), state, user_id)
    current_task = asyncio.create_task(
        mailing(order_id=int(order_id), order_type=data['order_type'], point_A=data['point_A'], point_B=data['point_B'],
                comment=comment, call=types.CallbackQuery(message=message), state=state))
    tasks_dict[order_id] = current_task




async def mailing(call: types.CallbackQuery, state: FSMContext, order_id, order_type, point_A, point_B, comment):
    users = await db().get_user_for_mailing()
    print(users)
    msg = f'''
<b>Новый заказ</b>
<b>Тип заказа:</b> {order_type}
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
                await db().update_messages(arr, order_id)
            await asyncio.sleep(30)
    finally:
        await db().update_messages(arr, order_id)
        return arr


async def delete_all_messages(call: types.CallbackQuery, state: FSMContext, order_id):
    info = await db().get_messages_from_db(order_id)
    users = [tuple(sublist) for sublist in info[0]]
    for user in users:
        await call.bot.delete_message(chat_id=int(user[1]), message_id=int(user[0]))
        print(f"delete {user[1]} , {user[0]}")

async def application_accepted(call: types.CallbackQuery, state: FSMContext):
    order_id = int(call.data[21:])

    global tasks_dict
    if order_id in tasks_dict:
        tasks_dict[order_id].cancel()
        del tasks_dict[order_id]
    courier_id = call.from_user.id
    await db().update_order(courier_id=courier_id, order_id=order_id)
    print("waiting")
    asyncio.create_task(delete_all_messages(call, state, order_id))
    print("WOW")
    courier_username = call.from_user.username
    print()
    info = await db().get_order_details_by_id(order_id)
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton
    customer_id = await db().get_customer_id_order(order_id)
    await db().update_count_orders(courier_id)
    msg_customer = f'''
<b>Ваш заказ принят для исполнения</b>
Курьер: @{courier_username}

Свяжитесь с курьером для уточнения деталей заказа
    '''
    msg_courier = f'''
<b>Вы приняли заказ</b>

<b>Тип заказа:</b> {info[2]}
<b>Место отправления:</b> {info[3]}
<b>Место доставки:</b> {info[4]}
<b>Информация:</b> {info[5]}

Ожидайте, в скором времени с вами свяжуться.
После завершения заказа необходимо нажать кнопку <b>Доставил</b>
Вы можете отказаться от заказа в течение <b>30</b> секунд ⏲
    '''
    # print(customer_id)
    # print(courier_id)
    keyboard.add(button(text='Отказаться', callback_data=f'cancel_order_{order_id}'))
    await call.bot.send_message(customer_id[0], msg_customer)
    sent_message = await call.bot.send_message(courier_id, msg_courier, reply_markup=keyboard)
    await asyncio.sleep(30)
    new_keyboard = types.InlineKeyboardMarkup(row_width=2)
    new_keyboard.add(button(text='Доставил', callback_data=f'successful_completion_{order_id}'))
    await call.bot.edit_message_reply_markup(courier_id, sent_message.message_id, reply_markup=new_keyboard)


async def cancel_order(call: types.CallbackQuery, state: FSMContext):
    msg_customer = f'''
<b>Курьер отказался от заказа</b>

<b>Ищем нового курьера</b> 🔄
'''
    msg_courier = f'''
Вы отказались от заказa ❌
'''
    order_id = int(call.data[13:])
    print(order_id)
    order_data = await db().get_order_details_by_id(order_id)
    print(order_data)
    courier_id = call.from_user.id
    customer_id = order_data[1]
    order_type = order_data[2]
    point_A = order_data[3]
    point_B = order_data[4]
    comment = order_data[5]
    await call.bot.send_message(customer_id, msg_customer)
    await call.answer(msg_courier, show_alert=True)
    await call.message.delete()
    asyncio.create_task(delete_all_messages(call, state, order_id))
    asyncio.create_task(
        mailing(order_id=int(order_id), order_type=order_type, point_A=point_A, point_B=point_B, comment=comment,
                      call=call, state=state))



async def successful_completion(call: types.CallbackQuery, state: FSMContext):
    order_id = int(call.data[22:])
    customer_id = await db().get_customer_id_order(order_id)
    courier_id = await db().get_courier_id_order(order_id)
    print(f"Customer {customer_id}")
    print(courier_id[0][0])
    await db().update_good_count_orders(courier_id[0][0])
    msg = f'''
<b>Курьер завершил заказ</b>
'''
    await call.message.delete()
    await call.bot.send_message(int(customer_id[0]), msg)

async def delete_messages():
    print()


