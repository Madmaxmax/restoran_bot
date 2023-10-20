import logging
from functions.user_function import *
from functions.admin_functions import *


async def ad_all_callback(call: types.CallbackQuery, state: FSMContext):
    admins_id = await db().get_admin_id()
    if call.from_user.id not in admins_id:
        return
    elif 'customer_menu' in call.data:
        await customer_menu(call, state)
        return
    elif'del_admin_' in call.data:
        await del_admin(call, state)
        return
    elif 'application_accepted_' in call.data:
        await application_accepted(call, state)
        return
    elif 'cancel_order_' in call.data:
        await cancel_order(call, state)
        return
    elif 'successful_completion' in call.data:
        await successful_completion(call, state)
        return
    else:
        name = call.data[3:]
        await eval(f"{name}(call=call, state=state)")
        return


async def ad_all_states_handler(message: types.Message, state: FSMContext):
    state_name = await state.get_state()
    state_name = state_name[3:]
    admins_id = await db().get_admin_id()
    if message.from_user.id not in admins_id:
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