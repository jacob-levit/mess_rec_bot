import re

from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.storage import FSMContext

from data import config
from loader import database
from loader import dispatcher
from states import AddAdminsQuestions


@dispatcher.message_handler(Command('add_admins'))
async def add_admins(message: types.Message):
    schema_name = config.SCHEMA + str(message.chat.id).replace('-', '')
    if await database.exists_schema(schema_name):
        answer = await message.answer('Напишите, пожалуйста, каких пользователей вы хотите добавить '
                                      'в перечень админов? \n'
                                      'Передайте в ответном сообщении их <code>user_id</code> '
                                      '(уникальные идентификаторы). \n'
                                      'Можно передавать идентификаторы списком. \n'
                                      'Например, <code>911298894 129673633 890032481</code>.')
        await AddAdminsQuestions.first()
    else:
        answer = await message.answer('Выполните, пожалуйста, сначала инициализацию для этого чата, '
                                      'чтобы создать нужные таблицы в базе данных!')
    await database.add_service_message(schema_name, message.message_id)
    await database.add_service_message(schema_name, answer.message_id)


@dispatcher.message_handler(content_types='text', state=AddAdminsQuestions.Q1)
async def get_admins_names(message: types.Message, state: FSMContext):
    message_text = re.findall(config.PATTERN_ID, message.text)
    dict_statuses = dict()
    schema_name = config.SCHEMA + str(message.chat.id).replace('-', '')
    for admin_id in message_text:
        try:
            member_chat_info = await message.chat.get_member(admin_id)
        except:
            dict_statuses.update({admin_id: 'пользователя нет в чате или не существует'})
        else:
            if await database.exists_admin_in_dict(schema_name=schema_name,
                                                   table_name=config.TABLE_DICT_ADMINS, admin_id=admin_id):
                dict_statuses.update({member_chat_info['user']['username']: 'уже есть в списке админов'})
            else:
                sql = f"""INSERT INTO {schema_name}.{config.TABLE_DICT_ADMINS} VALUES ({admin_id});"""
                await database.execute(sql, execute=True)
                dict_statuses.update({member_chat_info['user']['username']: 'добавлен в список админов'})
    message_report = ''
    for status in dict_statuses:
        message_report = message_report + f'<code>{status}</code> — {dict_statuses[status]} \n'
    if message_report:
        answer = await message.answer(message_report)
    else:
        answer = await message.answer('В вашем сообщении не нашлось чего-то похожего на id, попробуйте ещё раз...')
    await database.add_service_message(schema_name, message.message_id)
    await database.add_service_message(schema_name, answer.message_id)
    await state.finish()
