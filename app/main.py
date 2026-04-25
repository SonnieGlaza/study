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


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)


async def run_bot() -> None:
    if not settings.telegram_token:
        logger.warning("TELEGRAM_TOKEN is empty; bot polling is not started.")
        return
    bot = Bot(token=settings.telegram_token)
    dispatcher = Dispatcher()
    dispatcher.include_router(bot_router)
    await dispatcher.start_polling(bot)


def run() -> None:
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_bot())
