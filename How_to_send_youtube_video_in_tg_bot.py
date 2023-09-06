from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent
from youtube_search import YoutubeSearch

BOT_TOKEN = ''

bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot)


def searcher(text):
    return YoutubeSearch(search_terms=text, max_results=20).to_dict()


@dp.inline_handler()
async def inline_echo(inline_query: types.InlineQuery):
    text = inline_query.query or 'Echo'
    links = searcher(text)

    articles = [InlineQueryResultArticle(
        id=link['id'],
        title=link['title'],
        input_message_content=InputTextMessageContent(f"https://youtube.com" +
                                                      link['url_suffix']),
        thumb_url=f"{link['thumbnails'][0]}"
    ) for link in links]

    await bot.answer_inline_query(inline_query_id=inline_query.id,
                                  results=articles,
                                  cache_time=60)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)