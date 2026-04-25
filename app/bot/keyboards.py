from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def answers_keyboard(question_index: int, answers: list[str]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=answer, callback_data=f"ans:{question_index}:{idx}")]
            for idx, answer in enumerate(answers)
        ]
        + [
            [InlineKeyboardButton(text="Пропустить тест", callback_data="test:skip")],
            [InlineKeyboardButton(text="Начать тест заново", callback_data="test:restart")],
        ]
    )


def intensity_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Лёгкая", callback_data="intensity:light")],
            [InlineKeyboardButton(text="Средняя", callback_data="intensity:medium")],
            [InlineKeyboardButton(text="Сильная", callback_data="intensity:strong")],
        ]
    )


def after_generation_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Сделать ещё вариант", callback_data="gen:again")],
            [InlineKeyboardButton(text="Загрузить новое фото", callback_data="gen:new_photo")],
            [InlineKeyboardButton(text="Открыть режим консультанта", callback_data="consult:open")],
        ]
    )
