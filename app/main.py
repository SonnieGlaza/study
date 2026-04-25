from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from aiogram import Bot, Dispatcher
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.admin.api import router as admin_router
from app.bot.handlers import router as bot_router
from app.config import settings
from app.db import Base, engine

logger = logging.getLogger(__name__)

# Ensure media directory exists before StaticFiles mount.
Path(settings.media_root).mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Interior Telegram Bot + Admin")
app.include_router(admin_router)
app.mount("/media", StaticFiles(directory=settings.media_root), name="media")
BOT_TASK_KEY = "bot_polling_task"


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)
    if not settings.telegram_token:
        logger.warning("TELEGRAM_TOKEN is empty; bot polling is not started.")
        return
    bot_task = asyncio.create_task(run_bot(), name="telegram-bot-polling")
    setattr(app.state, BOT_TASK_KEY, bot_task)


@app.on_event("shutdown")
async def shutdown() -> None:
    bot_task = getattr(app.state, BOT_TASK_KEY, None)
    if bot_task is None:
        return
    bot_task.cancel()
    try:
        await bot_task
    except asyncio.CancelledError:
        pass


async def run_bot() -> None:
    bot = Bot(token=settings.telegram_token)
    dispatcher = Dispatcher()
    dispatcher.include_router(bot_router)
    try:
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()


def run() -> None:
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_bot())
