from database.Database import Database as db
from aiogram.dispatcher import FSMContext

# async def mailing(call: types.CallbackQuery, state: FSMContext, order_type, point_A, point_B, comment):
#     users = db().get_user_for_mailing()
#
#     msg = f'''
# <b>Новый заказ</b>
# <b>Тип заказа:</b> {order_type}
# b>Место отправления:</b> {point_A}
# <b>Место доставки:</b> {point_B}
# <b>Информация:</b> {comment}'''
#     for user in users:
#         print(f"ID: {user[0]}, Уровень: {user[1]}")
#         await call.bot.send_message(user[0], "message_text")