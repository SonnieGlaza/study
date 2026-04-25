from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def question_keyboard(question_number: int, options: list[str]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=option, callback_data=f"ans:{question_number}:{idx}")]
            for idx, option in enumerate(options)
        ]
        + [
            [InlineKeyboardButton(text="Пропустить тест", callback_data="test:skip")],
            [InlineKeyboardButton(text="Начать тест заново", callback_data="test:restart")],
        ]
    )


def image_intensity_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Лёгкая", callback_data="intensity:light")],
            [InlineKeyboardButton(text="Средняя", callback_data="intensity:medium")],
            [InlineKeyboardButton(text="Сильная", callback_data="intensity:strong")],
        ]
    )


def post_test_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Визуализация по фото", callback_data="visualize_mode")],
            [InlineKeyboardButton(text="Режим консультанта", callback_data="consultation_mode")],
            [InlineKeyboardButton(text="Начать тест заново", callback_data="restart_test")],
        ]
    )


def consultation_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Сделать визуализацию", callback_data="visualize_mode")],
            [InlineKeyboardButton(text="Начать тест заново", callback_data="restart_test")],
        ]
    )


def skip_restart_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Пропустить тест", callback_data="test:skip")],
            [InlineKeyboardButton(text="Начать тест заново", callback_data="restart_test")],
        ]
    )
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
