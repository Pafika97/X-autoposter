# -*- coding: utf-8 -*-
import os
from openai import OpenAI
import random

client = None
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    client = OpenAI(api_key=api_key)

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

SYSTEM = """Вы — лаконичный автор Твиттера (до 280 символов).
Стиль: 1 мысль, дружелюбно, без инвестиционных советов, 1–2 хэштега, 0–2 эмодзи, иногда вопрос в конце.
"""

def generate_post(topic: dict) -> str:
    if client is None:
        raise RuntimeError("OPENAI_API_KEY не задан")
    subject = topic["topic"]
    angle = random.choice(topic["angles"])
    tags = " ".join(random.sample(topic["hashtags_pool"], k=min(2, len(topic["hashtags_pool"]))))
    ems = " ".join(random.sample(topic["emojis"], k=min(2, len(topic["emojis"]))))
    prompt = f"Тема: {subject}. Угол: {angle}. Итог ≤ 280 символов. Добавь: {tags} {ems}."
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=120,
    )
    return resp.choices[0].message.content.strip()
