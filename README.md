# Папка Telegram Ботов

В данной папке содержатся несколько Telegram-ботов, разработанных с использованием библиотеки `aiogram` для работы с Telegram Bot API. Каждый бот обладает своими функциональными возможностями. Ниже представлены краткие описания каждого бота вместе с инструкциями по использованию.

## How_to_send_youtube_video_in_tg_bot.py

Этот бот позволяет пользователям искать видеоролики на YouTube и делиться ими в чатах Telegram. Он использует библиотеку `aiogram` для обработки инлайн-запросов и библиотеку `youtube_search` для поиска видео на YouTube.

### Использование:

1. Замените переменную `BOT_TOKEN` своим токеном Telegram Bot API.
2. Запустите скрипт.

Как только бот запущен, пользователи могут вызвать его в чате, введя `@имя_вашего_бота`, а затем введя поисковый запрос. Бот предоставит список видеороликов с YouTube, и пользователи смогут выбрать видео для отправки в чат.

## admin_bot.py

Этот бот предназначен для администрирования группы и предоставляет различные команды для управления Telegram-группой. Включает в себя команды для установки фотографии, названия, описания группы, режима "только чтение", блокировки пользователей и другие.

### Использование:

1. Замените переменную `BOT_TOKEN` своим токеном Telegram Bot API.
2. Запустите скрипт.

Бот реагирует на команды администратора группы и помогает управлять настройками группы. Также отправляет уведомления о присоединении новых участников или об уходе участников из группы.

## bot_with_payment.py

Этот бот реализует систему подписок с интеграцией оплаты. Пользователи могут подписаться на ежемесячный план, и бот управляет их статусом подписки.

### Использование:

1. Замените переменные `BOT_TOKEN` и `YOOTOKEN` своими токенами Telegram Bot API и провайдера оплаты YooMoney соответственно.
2. Запустите скрипт.

Пользователи могут запустить бот, установить никнейм, просмотреть свой профиль и детали подписки, а также подписаться на ежемесячный план с оплатой.

## Зависимости:

- `aiogram`: Python-фреймворк для работы с Telegram Bot API.
- `youtube_search`: Библиотека для поиска видео на YouTube.
