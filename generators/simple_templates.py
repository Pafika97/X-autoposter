# -*- coding: utf-8 -*-
import random

def _choose(pool, k_min=1, k_max=2):
    k = random.randint(k_min, k_max)
    return random.sample(pool, min(k, len(pool)))

def generate_post(topic: dict) -> str:
    # topic: dict с ключами topic, angles, hashtags_pool, emojis
    subject = topic["topic"]
    angle = random.choice(topic["angles"])
    tags = _choose(topic["hashtags_pool"], 1, 2)
    ems = _choose(topic["emojis"], 0, 2)

    frames = [
        "Коротко о {angle}: главное — фокус на процессе и рисках, а не на шуме рынка. {tail}",
        "Если смотреть на {angle} через призму дисциплины, результаты стабильнее. {tail}",
        "В {angle} выигрывает тот, кто планирует заранее и не гонится за хайпом. {tail}",
        "{angle.capitalize()} — это не прогноз, а система решений. Сделайте её простой и повторяемой. {tail}",
        "Совет по теме «{subject}»: выберите одну метрику, которая действительно двигает результат по {angle}, измеряйте её каждый день. {tail}",
        "Не ищите «сигнал», стройте привычку. {angle.capitalize()} любит последовательность. {tail}",
    ]
    frame = random.choice(frames)

    tails = [
        "Согласны?",
        "Как вы к этому подходите?",
        "Запишите идею и проверьте через неделю.",
        "Пусть это будет вашим маленьким экспериментом сегодня."
    ]
    tail = random.choice(tails)

    base = frame.format(angle=angle, subject=subject, tail=tail)
    suffix = ""
    if tags:
        suffix += " " + " ".join(tags)
    if ems:
        suffix += " " + " ".join(ems)

    # лёгкая вариативность CTA
    if random.random() < 0.25:
        suffix += " Напишите в ответах одну вещь, которую улучшите сегодня."

    return (base + suffix).strip()
