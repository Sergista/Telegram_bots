import asyncio

import aiogram.utils.exceptions
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters import Command, BoundFilter
import io
import re
import datetime

BOT_TOKEN = "I don't show you my Token))))"


class AdminFilter(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        member = await message.chat.get_member(message.from_user.id)  # получим инфу о юзере через объект message
        return member.is_chat_admin()


class IsGroup(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        return message.chat.type in (types.ChatType.GROUP, types.ChatType.SUPERGROUP)


async def on_startup(_):
    setup(dp)
    await dp.bot.set_my_commands([
        types.BotCommand(command='set_photo', description='установить фото в чате'),
        types.BotCommand(command='set_title', description='установить название группы'),
        types.BotCommand(command='set_description', description='установить описание группы'),
        types.BotCommand(command='ro', description='Режим ReadOnly'),
        types.BotCommand(command='ban', description='забанить'),
        types.BotCommand(command='unban', description='разбанить'),
    ])  # с помощью данной команды можно задавать команды по дефолту, тогда они будут отображаться внизу сразу при нажатии /


bot = Bot(BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


def setup(dp: Dispatcher):
    dp.filters_factory.bind(AdminFilter)
    dp.filters_factory.bind(IsGroup)


@dp.message_handler(content_types=types.ContentTypes.NEW_CHAT_MEMBERS)
async def new_member(message: types.Message):
    print(message)
    await message.reply(f"Hello, {message.new_chat_members[0].full_name}")


@dp.message_handler(content_types=types.ContentTypes.LEFT_CHAT_MEMBER)
async def left_member(message: types.Message):
    if message.left_chat_member.id == message.from_user.id:
        await message.answer(f"{message.left_chat_member.get_mention(as_html=True)}"
                             f"left the chat")
    elif message.from_user.id == (await bot.me).id:
        return
    else:
        await message.answer(f"{message.left_chat_member.full_name} was kicked by "
                             f"{message.from_user.full_name}")


@dp.message_handler(IsGroup(), Command('set_photo', prefixes='/!'),
                    AdminFilter())
async def new_group_photo(message: types.Message):
    source_message = message.reply_to_message

    photo = source_message.photo[-1]
    photo = await photo.download(destination=io.BytesIO())

    input_file = types.InputFile(path_or_bytesio=photo)

    await message.chat.set_photo(photo=input_file)


@dp.message_handler(IsGroup(), Command('set_title', prefixes='/!'),
                    AdminFilter())
async def new_group_title(message: types.Message):
    source_message = message.reply_to_message
    title = source_message.text
    await message.chat.set_title(title=title)


@dp.message_handler(IsGroup(), Command('set_description', prefixes='/!'),
                    AdminFilter())
async def new_group_description(message: types.Message):
    source_message = message.reply_to_message
    description = source_message.text
    await message.chat.set_description(description=description)


@dp.message_handler(IsGroup(), Command('ro', prefixes='!/'),
                    AdminFilter())
async def read_only_mode(message: types.Message):
    member = message.reply_to_message.from_user
    member_id = member.id
    chat_id = message.chat.id

    command_parse = re.compile(r"(!ro|/ro) ?(\d+)? ?([a-zA-Z]+)?")

    parsed = command_parse.match(message.text)

    time = parsed.group(2)
    reason = parsed.group(3)

    if not time:
        time = 5
    else:
        time = int(time)

    until_date = datetime.datetime.now() + datetime.timedelta(minutes=time)

    ReadOnlyPermission = types.ChatPermissions(
        can_send_messages=False,
        can_send_media_messages=False,
        can_send_polls=False,
        can_send_other_messages=False,
        can_add_web_page_previews=False,
        can_invite_users=True,
        can_change_info=False,
        can_pin_messages=False,
        can_manage_topics=False
    )

    try:
        await bot.restrict_chat_member(chat_id=chat_id, user_id=member_id,
                                       permissions=ReadOnlyPermission, until_date=until_date)

        await message.answer(f"User {member.get_mention(as_html=True)} is restricted "
                             f"for {time} minutes because of {reason if reason else ''}")

    except aiogram.utils.exceptions.BadRequest:
        await message.answer("User is administrator")

    service_message = await message.answer("This message will be automatically deleted "
                                           "after 5 secs")
    await asyncio.sleep(5)
    await message.delete()
    await service_message.delete()


@dp.message_handler(IsGroup(), Command('ban', prefixes='/!'),
                    AdminFilter())
async def ban_user(message: types.Message):
    member = message.reply_to_message.from_user
    member_id = member.id

    await message.chat.kick(user_id=member_id)
    await message.answer(f"User {member.full_name} was banned!")


@dp.message_handler(IsGroup(), Command('unban', prefixes='/!'),
                    AdminFilter())
async def unban_user(message: types.Message):
    member = message.reply_to_message.from_user
    member_id = member.id

    await message.chat.unban(user_id=member_id)
    await message.answer(f"User {member.full_name} was unbanned!")


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp,
                           skip_updates=True,
                           on_startup=on_startup)