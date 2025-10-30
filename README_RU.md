# X (Twitter) Автопостер: 1–2 поста в день по заданной теме

Готовый проект, который **сам публикует** 1–2 поста в день (случайно) в аккаунт X (Twitter) на заданную тему.

## Что умеет
- ✅ Случайно выбирает **1 или 2 времени** публикаций в каждый день (в заданном окне, по умолчанию 09:00–21:00 по Europe/Riga).
- ✅ Генерация текста:
  - **Без интернета**: шаблоны/вариации из `generators/simple_templates.py`.
  - **Опционально**: генерация с помощью OpenAI (если добавите `OPENAI_API_KEY`).
- ✅ Хештеги и вариативность (эмодзи, CTA, вопрос).
- ✅ Защита от повторов (SQLite `data/history.db`).
- ✅ Ручной запуск единой командой: `python bot.py` (крутится постоянно).
- ✅ Флаг `DRY_RUN` для тестов (ничего не публикует, только логирует).
- ✅ Настройки через `.env`.

## Быстрый старт
1) Установите зависимости:
```bash
python -m venv .venv && . .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```
2) Создайте `.env` на основе примера:
```bash
cp .env.example .env
```
3) Впишите ключи X (Twitter) API в `.env` (нужен доступ с правом публикации).  
   Подходит пара OAuth 1.0a (consumer/access tokens) или OAuth 2.0 user context (в Tweepy используется Client).
4) (Опционально) добавьте `OPENAI_API_KEY`, если хотите AI‑генерацию.
5) Запустите:
```bash
python bot.py
```
Скрипт:
- сразу создаст расписание на сегодня (1–2 поста) в случайные моменты,
- каждый день в 00:05 пересоздаёт расписание на новый день.

## Настройка темы
- Основная тема и словарь — в `content/topics.json`.
- Стили/правила — в `content/style_guidelines.md`.
- Доп. фразы — в `content/seed_prompts.txt`.

## Параметры `.env`
```
# ЧАСОВОЙ ПОЯС
TIMEZONE=Europe/Riga

# ВРЕМЕННОЕ ОКНО ПУБЛИКАЦИЙ (включительно)
POST_WINDOW_START=09:00
POST_WINDOW_END=21:00

# МАКС. И МИН. ПОСТОВ В ДЕНЬ
MIN_POSTS_PER_DAY=1
MAX_POSTS_PER_DAY=2

# РЕЖИМ ТЕСТА (true/false) — не публикует, только лог
DRY_RUN=true

# СПОСОБ ГЕНЕРАЦИИ: simple или openai
GENERATOR=simple

# ТЕМА (ключ из topics.json)
TOPIC_KEY=crypto_daily

# X (Twitter) ключи (нужны права на post/write)
X_CONSUMER_KEY=
X_CONSUMER_SECRET=
X_ACCESS_TOKEN=
X_ACCESS_TOKEN_SECRET=

# (Опционально) OpenAI
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
```

## Частые вопросы
**Нужно ли платное API X?** Для публикации постов требуется доступ с правом `write` в вашем проекте X API (условия у X меняются — проверьте в вашей консоли разработчика).

**Можно ли запускать по cron?** Да, но проще держать один процесс `bot.py`, он сам создаёт расписание на каждый день.

**Как убедиться, что твит не повторяется?** Хэш контента сохраняется в БД `data/history.db`; при совпадении — пересоздаётся текст.

**Как поменять тему/стиль?** Отредактируйте `content/topics.json` и `content/style_guidelines.md`, перезапустите скрипт.

Удачных запусков! 🚀
