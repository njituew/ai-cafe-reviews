from aiogram import types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from src.utils import is_manager
import dbtest

async def manager_panel(message: types.Message):
    chat_id = message.chat.id
    if not is_manager(chat_id):
        await message.answer("Вы не менеджер")
        return

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Непрочитанные отзывы 🗣️")],
            [KeyboardButton(text="Дашборд 💻"), KeyboardButton(text="Динамика удовлетворённости 📈")],
            [KeyboardButton(text="Профиль менеджера 👩‍💼")]
        ],
        resize_keyboard=True
    )
    await message.answer("Панель менеджера открыта", reply_markup=keyboard)


async def unread_reviews(message: types.Message):
    chat_id = message.chat.id
    if not is_manager(chat_id):
        await message.answer("Вы не менеджер")
        return

    text, keyboard = get_reviews_page(0)
    if keyboard is None:
        await message.answer(text)
    else:
        await message.answer(text, reply_markup=keyboard)


async def unread_reviews_pagination(callback_query: types.CallbackQuery):
    page = int(callback_query.data.split("_")[2])

    text, keyboard = get_reviews_page(page)
    if keyboard is None:
        await callback_query.message.edit_text(text)
    else:
        await callback_query.message.edit_text(text, reply_markup=keyboard)
    await callback_query.answer()


async def review(callback_query: types.CallbackQuery):
    review_id = int(callback_query.data.split("_")[1])
    review = dbtest.get_review(review_id)
    await callback_query.message.answer(
        f"ID: {review['review_id']}"
        f"\nОтзыв: {review['text']}"
        f"\nОценка: {review['mark']}"
        f"\nТональность: {review['tonality']}"
        f"\nПрочитан: {'Да' if review['readed'] else 'Нет'}",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Прочитано ✅", callback_data=f"readed_{review_id}")]]
        )
    )


def register_handlers(dp):
    dp.message.register(manager_panel, Command("manager"))
    dp.message.register(unread_reviews, F.text == "Непрочитанные отзывы 🗣️")
    dp.callback_query.register(unread_reviews_pagination, lambda c: c.data.startswith("prev_page_") or c.data.startswith("next_page_"))
    dp.callback_query.register(review, F.data.startswith("review_"))


# ================================================ Utils here ================================================
def get_reviews_page(page: int) -> tuple[str, InlineKeyboardMarkup]:
    reviews_per_page = 5
    unread_reviews = dbtest.get_unreaded_reviews()
    total_reviews = len(unread_reviews)
    start = page * reviews_per_page
    end = start + reviews_per_page
    reviews_to_display = unread_reviews[start:end]

    if not reviews_to_display:
        return "Нет непрочитанных отзывов.", None

    buttons = []
    
    # отзывы
    for review in reviews_to_display:
        review_text = f"Оценка: {review['mark']} - {review['text'][:10]}..."
        buttons.append([InlineKeyboardButton(text=review_text, callback_data=f"review_{review['review_id']}")])

    # взад-вперёд
    navigation_buttons = []
    if page > 0:
        navigation_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"prev_page_{page - 1}"))
    if end < total_reviews:
        navigation_buttons.append(InlineKeyboardButton(text="Вперёд ➡️", callback_data=f"next_page_{page + 1}"))
    if navigation_buttons:
        buttons.append(navigation_buttons)

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    text = f"Непрочитанные отзывы (страница {page + 1}):"
    return text, keyboard