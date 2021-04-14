from aiogram import types

from data import config
from loader import database
from loader import dispatcher


@dispatcher.message_handler(regexp=config.PATTERN_PROBLEM, state=None)
async def rec_re(message: types.Message):
    result_problem = config.PATTERN_PROBLEM.search(message.text)
    dict_problem = result_problem.group(0).split('/')
    hub = dict_problem[0].replace('#', '')
    city = dict_problem[1].replace(' ', '')
    number_problem = dict_problem[2]
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    user_name = message.from_user.username
    message_text = message.text
    date_time = message.date
    shema_name = config.SCHEMA + str(message.chat.id).replace('-', '')
    if await database.exists_schema(shema_name):
        sql = f"""INSERT INTO {shema_name}.{config.MESSAGES_STRUCT} 
            (hub, city, number_problem, user_id, full_name, user_name, message_text, date_time)
            VALUES ({hub}, '{city}', {number_problem}, {user_id}, '{full_name}', 
                '{user_name}', '{message_text}', '{date_time}')
        """
        await database.execute(sql, execute=True)
    else:
        pass


@dispatcher.message_handler(content_types='text', state=None)
async def rec_rest(message: types.Message):
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    user_name = message.from_user.username
    date_time = message.date
    message_text = message.text
    shema_name = config.SCHEMA + str(message.chat.id).replace('-', '')
    if await database.exists_schema(shema_name):
        sql = f"""INSERT INTO {shema_name}.{config.MESSAGES_UNSTRUCT}
            (user_id, full_name, user_name, message_text, date_time)
            VALUES ({user_id}, '{full_name}', '{user_name}', '{message_text}', '{date_time}')
        """
        await database.execute(sql, execute=True)
    else:
        pass


@dispatcher.message_handler(content_types=types.ContentTypes.all(), state=None)
async def delete_message(message: types.Message):
    schema_name = config.SCHEMA + str(message.chat.id).replace('-', '')
    sql = f"""
        SELECT admin_id FROM {schema_name}.{config.DICT_ADMINS} 
            UNION SELECT user_id FROM {schema_name}.{config.DICT_USERS};
    """
    data = await database.execute(sql, fetch=True)
    dict_admins_users = [dict(row) for row in data]
    if not any(d['admin_id'] == message.from_user.id for d in dict_admins_users):
        await message.delete()
    else:
        pass
