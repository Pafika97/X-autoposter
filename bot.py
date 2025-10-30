# -*- coding: utf-8 -*-
import os
import random
import hashlib
import sqlite3
import logging
from datetime import datetime, time, timedelta, date
from zoneinfo import ZoneInfo

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from dotenv import load_dotenv

from utils.poster import post_to_x
from generators.simple_templates import generate_post as generate_simple
try:
    from generators.openai_generator import generate_post as generate_ai
except Exception:
    generate_ai = None

import json

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

load_dotenv()

TZ = ZoneInfo(os.getenv("TIMEZONE", "Europe/Riga"))
WINDOW_START = os.getenv("POST_WINDOW_START", "09:00")
WINDOW_END = os.getenv("POST_WINDOW_END", "21:00")
MIN_POSTS = int(os.getenv("MIN_POSTS_PER_DAY", "1"))
MAX_POSTS = int(os.getenv("MAX_POSTS_PER_DAY", "2"))
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"
GENERATOR = os.getenv("GENERATOR", "simple")
TOPIC_KEY = os.getenv("TOPIC_KEY", "crypto_daily")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DB_PATH = os.path.join(DATA_DIR, "history.db")
CONTENT_DIR = os.path.join(os.path.dirname(__file__), "content")

os.makedirs(DATA_DIR, exist_ok=True)

def ensure_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            hash TEXT NOT NULL UNIQUE,
            content TEXT NOT NULL
        );
    """)
    con.commit()
    con.close()

def load_topic(topic_key):
    with open(os.path.join(CONTENT_DIR, "topics.json"), "r", encoding="utf-8") as f:
        topics = json.load(f)
    if topic_key not in topics:
        raise ValueError(f"TOPIC_KEY '{topic_key}' не найден в topics.json")
    return topics[topic_key]

def random_times_for_today(n):
    start_h, start_m = map(int, WINDOW_START.split(":"))
    end_h, end_m = map(int, WINDOW_END.split(":"))
    today = datetime.now(TZ).date()
    start_dt = datetime.combine(today, time(start_h, start_m, tzinfo=TZ))
    end_dt = datetime.combine(today, time(end_h, end_m, tzinfo=TZ))
    total_minutes = int((end_dt - start_dt).total_seconds() // 60)
    picks = sorted(random.sample(range(total_minutes+1), n))
    return [start_dt + timedelta(minutes=off) for off in picks]

def store_hash_if_new(content):
    h = hashlib.sha256(content.encode("utf-8")).hexdigest()
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    today = datetime.now(TZ).date().isoformat()
    try:
        cur.execute("INSERT INTO posts(date, hash, content) VALUES(?,?,?)", (today, h, content))
        con.commit()
        con.close()
        return True
    except sqlite3.IntegrityError:
        con.close()
        return False

def make_unique(generate_fn, *args, **kwargs):
    # попытаться сгенерировать уникальный текст до 8 попыток
    for _ in range(8):
        text = generate_fn(*args, **kwargs).strip()
        # ограничение X: 280 символов
        if len(text) > 280:
            text = text[:277] + "…"
        if store_hash_if_new(text):
            return text
    raise RuntimeError("Не удалось сгенерировать уникальный текст (повторы). Увеличьте вариативность.")

def generate_post():
    topic = load_topic(TOPIC_KEY)
    if GENERATOR == "openai":
        if generate_ai is None:
            logging.warning("OpenAI генератор не доступен, переключаюсь на simple")
            return make_unique(generate_simple, topic)
        return make_unique(generate_ai, topic)
    else:
        return make_unique(generate_simple, topic)

def schedule_today(scheduler):
    n_posts = random.randint(MIN_POSTS, MAX_POSTS)
    times = random_times_for_today(n_posts)
    for dt in times:
        logging.info(f"Пост запланирован на {dt.isoformat()}")
        scheduler.add_job(run_once, trigger=DateTrigger(run_date=dt))

def run_once():
    try:
        text = generate_post()
        if DRY_RUN:
            logging.info(f"[DRY_RUN] Текст поста: {text}")
        else:
            resp = post_to_x(text)
            logging.info(f"Опубликовано: {text} | resp={resp}")
    except Exception as e:
        logging.exception(f"Ошибка публикации: {e}")

def reschedule_daily(scheduler):
    # каждый день в 00:05 по TZ создаём новое расписание
    tomorrow = (datetime.now(TZ) + timedelta(days=1)).date()
    run_at = datetime.combine(tomorrow, time(0,5, tzinfo=TZ))
    scheduler.add_job(lambda: schedule_today(scheduler), trigger=DateTrigger(run_date=run_at))
    logging.info(f"Запланировано пересоздание расписания на {run_at.isoformat()}")

def main():
    ensure_db()
    scheduler = BackgroundScheduler(timezone=TZ)
    scheduler.start()
    schedule_today(scheduler)
    reschedule_daily(scheduler)

    logging.info("Бот запущен. Нажмите Ctrl+C для выхода.")
    try:
        import time as _t
        while True:
            _t.sleep(1)
    except KeyboardInterrupt:
        scheduler.shutdown()

if __name__ == "__main__":
    main()
