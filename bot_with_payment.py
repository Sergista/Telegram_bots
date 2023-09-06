import datetime

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters import CommandStart
import psycopg2
import re
import time

BOT_TOKEN = ""
YOOTOKEN = ''

bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot)

kb = ReplyKeyboardMarkup(resize_keyboard=True)
btn_profile = KeyboardButton(text="Profile")
btn_sub = KeyboardButton(text="Subscription")
secret_button = KeyboardButton(text="Получить видео со вписок!")
kb.add(btn_profile, btn_sub, secret_button)

ikb = InlineKeyboardMarkup(row_width=1)
btn_sub_month = InlineKeyboardButton(text="One month - 300P",
                                     callback_data="submonth")

ikb.add(btn_sub_month)


async def on_startup(_):
    db.create_db()


class Database:

    def __init__(self, password, user='postgres', database='postgres',
                 host='localhost'):
        self.connection = psycopg2.connect(password=password,
                                           user=user,
                                           database=database,
                                           host=host)
        self.cursor = self.connection.cursor()

    def create_db(self):  # метод по созданию таблицы
        with self.connection:  # __enter__   __exit__
            self.cursor.execute("""CREATE TABLE IF NOT exists tg_users_2
                                   (id SERIAL PRIMARY KEY,
                                   user_id BIGINT NOT NULL UNIQUE,
                                   nickname VARCHAR(60),
                                   time_sub INTEGER NOT NULL DEFAULT 0,
                                   singup VARCHAR(60) NOT NULL DEFAULT 'setnickname')""")

    def add_user(self, user_id):
        with self.connection:
            self.cursor.execute("""
                INSERT INTO tg_users_2 (user_id)
                VALUES (%s)
            """, [user_id])

    def user_exists(self, user_id):
        with self.connection:
            self.cursor.execute("""
                SELECT * FROM tg_users_2
                WHERE user_id=(%s)
            """, [user_id])  # [(id,user_id,nickname,time_sub,singup), (), ()]

        result = self.cursor.fetchall()  # [('*')]

        return bool(result)

    def set_nickname(self, user_id, nickname):
        return self.cursor.execute("""
            UPDATE tg_users_2
            SET nickname=(%s)
            WHERE user_id=(%s)
        """, [nickname, user_id])

    def get_singup(self, user_id):
        with self.connection:
            self.cursor.execute("""SELECT singup
                                         FROM tg_users_2
                                         WHERE user_id = (%s)""", (user_id,))
            result = self.cursor.fetchall()  # [(singup)]
        for row in result:  #
            singup = str(row[0])  # забрали значение поля singup

        return singup

    def set_singup(self, user_id, singup):
        with self.connection:
            return self.cursor.execute("""UPDATE tg_users_2
                                                SET singup = (%s)
                                                WHERE user_id = (%s)""", (singup, user_id))

    def get_nickname(self, user_id):
        with self.connection:
            self.cursor.execute("""SELECT nickname
                                         FROM tg_users_2
                                         WHERE user_id = (%s)""", (user_id,))
            result = self.cursor.fetchall()  # [(nickname)]
        for row in result:  #
            nickname = str(row[0])  # забрали значение поля nickname

        return nickname

    def set_time_sub(self, user_id, timesub):  # данная функция изменяет переменную time_sub в БД
        with self.connection:
            return self.cursor.execute("""UPDATE tg_users_2
                                          SET time_sub = (%s)
                                          WHERE user_id = (%s)""", (
                timesub, user_id))  # Обновим значение поля timesub для пользователя с определенным id

    def get_time_sub(self, user_id):  # метод получения даты подписки
        with self.connection:
            self.cursor.execute("""SELECT time_sub
                                    FROM tg_users_2
                                    WHERE user_id = (%s)""", (user_id,))
            result = self.cursor.fetchall()
        for row in result:
            time_sub = int(row[0])
        return time_sub

    def get_sub_status(self,
                       user_id):  # метод получения наличия подписки(по сути тот же метод, что выше, но возвоащает булево значение, True - если есть подписка)
        with self.connection:
            self.cursor.execute("""SELECT time_sub
                                    FROM tg_users_2
                                    WHERE user_id = (%s)""", (user_id,))
            result = self.cursor.fetchall()
        for row in result:
            time_sub = int(row[0])
        if time_sub > int(time.time()):  # если время подписки больше нынешнего времени
            return True
        else:
            return False


db = Database('1')


def days_to_sec(days):
    return days * 24 * 60 * 60


def to_long_nickname(nick: str):
    return len(nick) > 15  # true or false


def time_sub_day(sub_time):
    time_now = int(time.time())
    middle_time = int(sub_time) - time_now

    if middle_time <= 0:
        return False
    return str(datetime.timedelta(seconds=middle_time))


@dp.message_handler(CommandStart())  # /start
async def start(message: types.Message):
    usr = message.from_user.id

    if not db.user_exists(usr):
        db.add_user(usr)
        await bot.send_message(usr, "Please, enter your nickname")
    else:
        await bot.send_message(usr, "You are already registered",
                               reply_markup=kb)


@dp.callback_query_handler(text='submonth')
async def sub_buy(callback: types.CallbackQuery):
    await bot.delete_message(callback.from_user.id,
                             callback.message.message_id)

    await bot.send_invoice(chat_id=callback.from_user.id,
                           title='Subscription for month',
                           description='Usual monthly subscription for users',
                           payload='month_sub',
                           provider_token=YOOTOKEN, currency='RUB',
                           start_parameter='test_bot',
                           prices=[types.LabeledPrice(label='rub', amount=30000)])


@dp.pre_checkout_query_handler()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def pay(message: types.Message):
    if message.successful_payment.invoice_payload == 'month_sub':
        await bot.send_message(
            message.from_user.id,
            "You have successfully bought monthly subscription"
        )
        curr_time = int(time.time())
        month_sub = curr_time + days_to_sec(30)
        db.set_time_sub(message.from_user.id, month_sub)


@dp.message_handler()
async def process_nick(message: types.Message):
    usr = message.from_user.id
    msg_txt = message.text
    if message.chat.type == types.ChatType.PRIVATE:
        if msg_txt == 'Profile':
            usr_nickname = f"Your nickname: {db.get_nickname(usr)}"
            user_sub = time_sub_day(db.get_time_sub(usr))
            if not user_sub:
                user_sub = '\nEnd of subscription. Please,pay money!'
            user_sub = f"\nSubscription active for: {user_sub}"
            await bot.send_message(usr, usr_nickname + user_sub)

        elif msg_txt == 'Subscription':
            await bot.send_message(usr, 'Subscription details', reply_markup=ikb)
        elif msg_txt == 'Получить фото!':
            if db.get_sub_status(usr):
                await bot.send_message(usr, 'заплати еще 1к рублей и получишь фото')

            else:
                await bot.send_message(usr, 'А не забыл ли ты купить подписку?')
        else:
            if db.get_singup(usr) == 'setnickname':
                if to_long_nickname(msg_txt):
                    await bot.send_message(usr, "Nick should be less than 15 symbols")

                elif re.search(r'[@/]', msg_txt):
                    await bot.send_message(usr, "You entered prohibited symbol")

                else:
                    db.set_nickname(usr, msg_txt)
                    db.set_singup(usr, 'done')
                    await bot.send_message(usr, "You were successfully registered!",
                                           reply_markup=kb)
            else:
                await bot.send_message(usr, "Stop doing this ....!")


if __name__ == "__main__":
    executor.start_polling(dispatcher=dp,
                           skip_updates=True,
                           on_startup=on_startup)