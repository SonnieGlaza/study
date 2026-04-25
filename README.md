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

### AI визуализация

`IMAGE_API_URL` ожидает POST JSON:
- `image_base64`, `image_mime`, `prompt`, `strength`
Ответ:
- `output_image_base64`,
- `job_id` (optional).

### LLM/RAG

- `RAG_API_URL`: POST `{query, top_k}` -> `results[]`.
- `LLM_API_URL`: POST с system prompt, question, personality, context -> `answer`.

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
