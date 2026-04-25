# Interior Telegram Bot

Реализация Telegram-бота по дизайну интерьера:
- тест личности (20 вопросов, 4 inline-ответа, сохранение прогресса, restart/skip),
- персональные рекомендации + PDF-отчет,
- визуализация интерьера по фото с выбранной интенсивностью,
- режим консультаций (включая фото),
- подключение внутренних материалов через RAG,
- подписочная модель с GetCourse,
- web-админка (UI + API).

## Ключевые модули

- `app/bot/handlers.py` — Telegram-сценарии.
- `app/services/test_engine.py` — движок теста + формула психотипов.
- `app/services/getcourse.py` + `app/services/subscription.py` — доступ, тарифы, синхронизация.
- `app/services/ai_services.py` — генерация изображений и консультации через провайдеры.
- `app/services/rag.py` — поиск релевантных фрагментов материалов.
- `app/services/file_storage.py` — хранение файлов генераций.
- `app/admin/api.py` + `app/admin/templates/dashboard.html` — админка.

## Формула психотипов

Точная формула хранится в JSON и может редактироваться администратором:
- дефолт: `app/personality_formula.default.json`,
- runtime override: поле `BotConfig.personality_formula_json` (через админку).

Это позволяет загрузить формулу заказчика без деплоя кода.

## Внешние интеграции

### GetCourse

Используются эндпоинты (настраиваются в `.env`):
- `GETCOURSE_API_URL/subscriptions/check?telegram_id=...`
- `GETCOURSE_API_URL/subscriptions/sync` (POST)

Ожидаемые поля:
- `active` (bool),
- `plan` (string),
- `expires_at` (ISO datetime).

### Arena AI (единый провайдер)

По умолчанию проект использует единый endpoint:
- `ARENA_API_URL=https://arena.ai/`

Используется единый POST JSON с полем режима:
- `mode=image_edit` для визуализаций интерьера,
- `mode=text` для консультационных текстов,
- `mode=agent` для agent-like задач.

Базовые поля запроса:
- `prompt`,
- `image_base64` и `image_mime` (если есть входное фото),
- `strength` (для visual режимов),
- `metadata` (произвольные служебные данные).

Ожидаемые поля ответа:
- `output_image_base64` (для изображений),
- `answer` (для текста/агента),
- `job_id` (optional).

## Запуск

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
uvicorn app.main:app --reload
```

## Админка

Открыть: `http://localhost:8000/admin`

Авторизация:
- query параметр `?token=<ADMIN_API_KEY>` или заголовок `x-admin-token`.

Возможности:
- включить/выключить бота;
- менять системный промпт и стиль ответов;
- редактировать JSON-формулу психотипов;
- загружать материалы для базы знаний;
- смотреть пользователей и диалоги.
