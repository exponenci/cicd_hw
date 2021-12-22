import random
from string import ascii_letters, digits

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from bot.sqlighter.sqlighter import keyboards_dp, db, file_type_to_method, global_values_container


class UploadFile(StatesGroup):
    waiting_for_file = State()
    waiting_for_password = State()
    waiting_files_password = State()


async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    db.register_user(message.from_user.id)
    command_args = message.get_args()
    if not command_args:
        await message.answer(
                "This is the file hosting bot. "
                "With it you can share photos, audios, videos and documents."
                "Send any content so that you can share it with others.",
                reply_markup=keyboards_dp['main']
        )
        return
    file_instance = db.get_file(command_args)
    if file_instance.password == '-':
        db.increment_file_views(command_args)
        await getattr(message,
                      file_type_to_method[file_instance.file_type])(
                file_instance.file_id,
                caption=file_instance.caption,
                reply_markup=keyboards_dp['main']
        )
    else:
        await message.answer(
                "password is required...",
                reply_markup=keyboards_dp['cancel']
        )
        await state.update_data(file_id=command_args)
        await UploadFile.waiting_files_password.set()


async def password_required(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    file_instance = db.get_file(state_data['file_id'])
    if file_instance.password != message.text:
        await message.answer('Wrong password;\nPlease try again!')
        return
    db.increment_file_views(state_data['file_id'])
    await getattr(message,
                  file_type_to_method[file_instance.file_type])(
            file_instance.file_id,
            file_instance.caption,
            reply_markup=keyboards_dp['main']
    )
    await state.finish()


async def upload_start(message: types.Message):
    await message.answer("Send any type of content",
                         reply_markup=keyboards_dp['cancel'])
    await UploadFile.waiting_for_file.set()


async def file_uploaded(message: types.Message, state: FSMContext):
    if message.photo:
        file_id = message.photo[-1].file_id
        file_type = 'photo'
    elif message.video:
        file_id = message.video.file_id
        file_type = 'video'
    elif message.voice:
        file_id = message.voice.file_id
        file_type = 'voice'
    elif message.document:
        file_id = message.document.file_id
        file_type = 'document'
    elif message.audio:
        file_id = message.document.file_id
        file_type = 'audio'
    else:
        await state.finish()
        await message.answer('Unsupported type of content; please send another document.',
                             reply_markup=keyboards_dp['main'])
        return
    await state.update_data(file_id=file_id,
                            file_type=file_type,
                            holder_id=message.from_user.id,
                            code=''.join(random.sample(ascii_letters + digits, random.randint(33, 40))))
    await UploadFile.waiting_for_password.set()
    await message.answer("Send password or send `-` if you don't want set password")


async def password_registration(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    state_data['password'] = message.text
    db.add_new_file(state_data)
    await message.answer(f'File has been successfully uploaded;\n'
                         f'password: {message.text}\n\n'
                         f'you can share with file via '
                         f'https://t.me/{global_values_container["bot_username"]}'
                         f'?start={state_data["code"]}',
                         reply_markup=keyboards_dp['main'])
    await state.finish()


async def show_user_files(message: types.Message, state: FSMContext):
    await state.finish()
    operating_data = db.get_users_files(message.from_user.id)
    if not operating_data:
        await message.answer('You have not uploaded files yet',
                             reply_markup=keyboards_dp['main'])
        return
    await message.answer(
            "\n\n".join(
                    list(
                            map(
                                    lambda pair:
                                    f'{pair[0]}. https://t.me/{global_values_container["bot_username"]}'
                                    f'?start={pair[1].code} '
                                    f'| {pair[1].file_type} '
                                    f'| {pair[1].views_count} '
                                    f'| {pair[1].password}',
                                    enumerate(
                                            operating_data
                                    )
                            )
                    )
            ),
            reply_markup=keyboards_dp['main']
    )


async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(
            "Action was canceled",
            reply_markup=keyboards_dp['main']
    )


def register_handlers_upload(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_message_handler(cmd_cancel, commands="cancel", state="*")
    dp.register_message_handler(cmd_cancel, Text(equals="cancel", ignore_case=True), state="*")
    dp.register_message_handler(password_required, state=UploadFile.waiting_files_password)

    dp.register_message_handler(upload_start, commands="upload", state="*")
    dp.register_message_handler(upload_start, Text(equals="upload file", ignore_case=True), state="*")
    dp.register_message_handler(file_uploaded, state=UploadFile.waiting_for_file, content_types=types.ContentTypes.ANY)
    dp.register_message_handler(password_registration, state=UploadFile.waiting_for_password)

    dp.register_message_handler(show_user_files, Text(equals="my files", ignore_case=True), state="*")
