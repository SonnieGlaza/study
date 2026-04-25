from __future__ import annotations

from pathlib import Path

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from app.bot.keyboards import (
    consultation_menu,
    image_intensity_keyboard,
    post_test_menu,
    question_keyboard,
    skip_restart_menu,
)
from app.bot.states import DialogStates
from app.models import GenerationIntensity
from app.services.ai_services import (
    ask_consultant,
    generate_interior_image,
    visualize_object_on_wall,
)
from app.services.pdf_service import render_personality_pdf
from app.services.repository import Repository
from app.services.subscription import is_subscription_active
from app.services.test_engine import QUESTION_COUNT, question_by_number, summarize_result

router = Router()
repo = Repository()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext) -> None:
    user = repo.upsert_user(
        telegram_user_id=message.from_user.id,
        username=message.from_user.username or "",
        full_name=message.from_user.full_name or "",
    )
    if user.completed_test:
        await message.answer(
            "Тест уже пройден. Можно пройти заново, перейти в генерацию или консультацию.",
            reply_markup=post_test_menu(),
        )
        return

    await state.set_state(DialogStates.testing)
    await send_next_question(message, user.telegram_user_id)


@router.message(Command("skip_test"))
async def cmd_skip_test(message: Message, state: FSMContext) -> None:
    repo.set_skipped(message.from_user.id, True)
    await state.set_state(DialogStates.consultation)
    await message.answer(
        "Опрос пропущен. Можно задавать вопросы и отправлять фото для консультации.",
        reply_markup=consultation_menu(),
    )


@router.message(Command("restart_test"))
async def cmd_restart_test(message: Message, state: FSMContext) -> None:
    repo.restart_test(message.from_user.id)
    await state.set_state(DialogStates.testing)
    await message.answer("Начинаем тест заново.", reply_markup=skip_restart_menu())
    await send_next_question(message, message.from_user.id)


@router.callback_query(F.data.startswith("ans:"))
async def handle_answer(callback: CallbackQuery, state: FSMContext) -> None:
    user = repo.get_user(callback.from_user.id)
    if not user:
        await callback.message.answer("Сначала запустите /start.")
        await callback.answer()
        return

    _, question_number_raw, option_raw = callback.data.split(":")
    repo.save_answer(
        telegram_user_id=user.telegram_user_id,
        question_number=int(question_number_raw),
        selected_option=int(option_raw),
    )
    await callback.answer("Ответ сохранён.")
    await send_next_question(callback.message, user.telegram_user_id)
    await state.set_state(DialogStates.testing)


@router.callback_query(F.data == "consultation_mode")
async def callback_consultation_mode(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(DialogStates.consultation)
    await callback.message.answer(
        "Режим консультации включен. Отправьте вопрос текстом или фото с вопросом.",
        reply_markup=consultation_menu(),
    )
    await callback.answer()


@router.callback_query(F.data == "visualize_mode")
async def callback_visualize_mode(callback: CallbackQuery, state: FSMContext) -> None:
    if not is_subscription_active(callback.from_user.id):
        await callback.answer("Доступно только по подписке.", show_alert=True)
        return
    await state.set_state(DialogStates.awaiting_room_photo)
    await callback.message.answer("Отправьте фото комнаты для визуализации.")
    await callback.answer()


@router.message(DialogStates.awaiting_room_photo, F.photo)
async def receive_room_photo(message: Message, state: FSMContext) -> None:
    largest = message.photo[-1]
    file = await message.bot.get_file(largest.file_id)
    out_dir = Path("storage/user_uploads")
    out_dir.mkdir(parents=True, exist_ok=True)
    file_path = out_dir / f"{message.from_user.id}_{largest.file_id}.jpg"
    await message.bot.download_file(file.file_path, destination=file_path)

    await state.update_data(room_photo_path=str(file_path))
    await state.set_state(DialogStates.awaiting_visual_intensity)
    await message.answer(
        "Выберите степень изменений интерьера:",
        reply_markup=image_intensity_keyboard(),
    )


@router.callback_query(DialogStates.awaiting_visual_intensity, F.data.startswith("intensity:"))
async def receive_intensity(callback: CallbackQuery, state: FSMContext) -> None:
    if not is_subscription_active(callback.from_user.id):
        await callback.answer("Подписка не активна.", show_alert=True)
        return

    intensity = callback.data.split(":")[1]
    data = await state.get_data()
    photo_path = data.get("room_photo_path")
    user = repo.get_user(callback.from_user.id)
    if not photo_path or not user:
        await callback.message.answer("Не удалось обработать фото, попробуйте снова.")
        await callback.answer()
        return

    result = summarize_result(repo.list_answers(user.telegram_user_id))
    generated_path = generate_interior_image(
        input_photo_path=photo_path,
        personality_type=result.personality_type,
        intensity=GenerationIntensity(intensity),
    )
    record = repo.add_generation(
        telegram_user_id=user.telegram_user_id,
        source_photo_path=photo_path,
        output_photo_path=generated_path,
        intensity=GenerationIntensity(intensity),
    )
    await callback.answer("Готово.")
    await callback.message.answer_photo(
        BufferedInputFile(Path(generated_path).read_bytes(), filename=Path(generated_path).name),
        caption=f"Вариант #{record.id}. Можно отправить другое фото или снова выбрать визуализацию.",
        reply_markup=post_test_menu(),
    )
    await state.set_state(DialogStates.consultation)


@router.message(StateFilter(DialogStates.consultation), F.photo)
async def consultation_with_photo(message: Message, state: FSMContext) -> None:
    caption = message.caption or ""
    file = await message.bot.get_file(message.photo[-1].file_id)
    out_dir = Path("storage/consultation")
    out_dir.mkdir(parents=True, exist_ok=True)
    file_path = out_dir / f"{message.from_user.id}_{message.photo[-1].file_id}.jpg"
    await message.bot.download_file(file.file_path, destination=file_path)

    if "зеркал" in caption.lower():
        result_path = visualize_object_on_wall(str(file_path), object_name="mirror")
        await message.answer_photo(
            BufferedInputFile(Path(result_path).read_bytes(), filename=Path(result_path).name),
            caption="Подобран вариант зеркала для вашей стены.",
        )
        return

    reply = ask_consultant(question=caption or "Проанализируй интерьер по фото.", image_path=str(file_path))
    await message.answer(reply)
    await state.set_state(DialogStates.consultation)


@router.message(StateFilter(DialogStates.consultation), F.text)
async def consultation_text(message: Message) -> None:
    reply = ask_consultant(question=message.text)
    await message.answer(reply, reply_markup=consultation_menu())


@router.callback_query(F.data == "restart_test")
async def callback_restart_test(callback: CallbackQuery, state: FSMContext) -> None:
    repo.restart_test(callback.from_user.id)
    await state.set_state(DialogStates.testing)
    await callback.answer("Тест сброшен.")
    await send_next_question(callback.message, callback.from_user.id)


async def send_next_question(message: Message, telegram_user_id: int) -> None:
    answers = repo.list_answers(telegram_user_id)
    next_number = len(answers) + 1

    if next_number > QUESTION_COUNT:
        result = summarize_result(answers)
        repo.finalize_test(telegram_user_id, result.personality_type)
        pdf_path = render_personality_pdf(
            telegram_user_id=telegram_user_id,
            personality_type=result.personality_type,
            summary_text=result.summary_text,
            interior_recommendations=result.interior_recommendations,
        )
        await message.answer(
            (
                f"Вы — тип личности {result.personality_type}.\n"
                f"{result.summary_text}\n\n"
                f"Рекомендации: {result.interior_recommendations}"
            ),
            reply_markup=post_test_menu(),
        )
        await message.answer_document(
            BufferedInputFile(Path(pdf_path).read_bytes(), filename=Path(pdf_path).name),
            caption="Итоговый PDF-отчёт",
        )
        return

    q = question_by_number(next_number)
    await message.answer(
        f"Вопрос {q.number}/{QUESTION_COUNT}\n\n{q.text}",
        reply_markup=question_keyboard(q.number, q.options),
    )
