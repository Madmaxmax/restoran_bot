import logging
from functools import partial
from aiogram import Dispatcher
from functions.user_function import *
from functions.admin_functions import *
from handlers.admin_handlers import ad_all_states_handler, ad_all_callback


async def us_all_callback(call: types.CallbackQuery, state: FSMContext):
    users_id = await db().get_user_id()
    if call.from_user.id not in users_id:
        return
    elif 'customer_menu' in call.data:
        await customer_menu(call, state)
        return
    elif 'del_admin_' in call.data:
        await del_admin(call, state)
        return
    elif 'application_accepted_' in call.data:
        await application_accepted(call, state)
        return
    elif 'courier_cancel_application_' in call.data:
        await courier_cancel_application(call, state)
        return
    elif 'cancel_application_' in call.data:
        await cancel_application(call, state)
        return
    elif 'successful_completion_' in call.data:
        await successful_completion(call, state)
        return
    elif 'change_application_price' in call.data:
        await change_application_price(call, state)
        return
    elif 'reverse_receiving_keyboard_text' in call.data:
        await reverse_receiving_keyboard_text(call, state)
        return
    else:
        # name = call.data[3:]
        await eval(f"{call.data}(call=call, state=state)")
        return


def reg_handlers(dp: Dispatcher):
    dp.register_message_handler(welcome, commands=['start'], state='*')
    dp.register_message_handler(admin_menu, commands=['admin'], state='*')
    dp.register_message_handler(partial(us_all_states_handler), content_types=types.ContentType.ANY, state='*')
    dp.register_callback_query_handler(partial(ad_all_callback), lambda call: call.data[:3] == "ad_", state='*')
    dp.register_callback_query_handler(partial(us_all_callback), state='*')


async def us_all_states_handler(message: types.Message, state: FSMContext):
    print(message.text)
    state_name = await state.get_state()
    if str(state_name)[:3] == "ad_":
        await ad_all_states_handler(message, state)
        return
    else:
        users_id = await db().get_user_id()
        if message.from_user.id not in users_id:
            return
        if message.text == 'Заказ':
            await create_orders(message=message, state=state)
            return
        if message.text == 'Закупка':
            await create_purchase(message=message, state=state)
            return
        if message.text == 'Вы не принимаете заказы❌':
            await reverse_receiving_keyboard_text(message=message, state=state)
            return
        if message.text == 'Вы принимаете заказы✅':
            await reverse_receiving_keyboard_text(message=message, state=state)
            return
        try:
            if 'delete_admin_text' in state_name:
                await delete_user_text(message=message, state=state)
                return
            else:
                await eval(f"{state_name}(message=message, state=state)")
                return
        except Exception as e:
            logging.error('State_handler has Exception - %s' % e)
