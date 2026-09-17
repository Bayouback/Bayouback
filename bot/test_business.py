# -*- coding: utf-8 -*-
"""
Проверка режима автоответчика. Запускается без токена и без сети:

    python3 test_business.py

Главное, что тут проверяется — бот не должен отвечать на сообщения самого
владельца аккаунта. В обновление `business_message` попадают и ваши реплики
тоже, и если их не отфильтровать, бот начнёт спорить сам с собой на глазах
у клиента.
"""

import asyncio
import logging
import sys
import time
import types

import business
import content

# Седьмая проверка намеренно роняет связь с Telegram, и модуль честно пишет
# это в лог с трейсбеком. В выводе тестов он только пугает — глушим.
logging.getLogger("yuvi-bot.business").setLevel(logging.CRITICAL)


# ------------------------------------------------------------- подставки

class FakeUser:
    def __init__(self, uid, username=None):
        self.id = uid
        self.username = username


class FakeChat:
    def __init__(self, cid):
        self.id = cid


class FakeMessage:
    def __init__(self, text, from_id, chat_id, connection_id="conn-1"):
        self.text = text
        self.from_user = FakeUser(from_id)
        self.chat = FakeChat(chat_id)
        self.business_connection_id = connection_id


class FakeBot:
    """Записывает отправленное вместо обращения к Telegram."""

    def __init__(self, owner_id):
        self.sent = []
        self._owner_id = owner_id
        self.lookups = 0

    async def get_business_connection(self, connection_id):
        self.lookups += 1
        return types.SimpleNamespace(
            id=connection_id, user=FakeUser(self._owner_id), can_reply=True
        )

    async def send_message(self, chat_id, text, business_connection_id=None):
        self.sent.append(
            {"chat_id": chat_id, "text": text, "connection": business_connection_id}
        )


class FakeContext:
    def __init__(self, bot):
        self.bot = bot
        self.bot_data = {}


def message_update(msg):
    return types.SimpleNamespace(business_message=msg)


# ---------------------------------------------------------------- проверки

OWNER = 111          # вы
CLIENT = 222         # клиент
CHAT = 900           # переписка с клиентом


async def run():
    failures = []

    def check(condition, label):
        if not condition:
            failures.append(label)

    # 1. Клиент спрашивает — бот отвечает
    bot = FakeBot(OWNER)
    ctx = FakeContext(bot)
    await business.on_message(
        message_update(FakeMessage("сколько стоит сайт", CLIENT, CHAT)), ctx
    )
    check(len(bot.sent) == 1, "на вопрос клиента ответа не было")
    if bot.sent:
        check("прайса" in bot.sent[0]["text"], "ответ не про цену")
        check(bot.sent[0]["text"].endswith(content.BUSINESS_SIGNATURE),
              "нет подписи про автоответ")
        check(bot.sent[0]["connection"] == "conn-1", "потерян business_connection_id")

    # 2. Владелец пишет сам — бот молчит
    bot = FakeBot(OWNER)
    ctx = FakeContext(bot)
    await business.on_message(
        message_update(FakeMessage("добрый день, сейчас посчитаю", OWNER, CHAT)), ctx
    )
    check(bot.sent == [], "бот ответил на сообщение владельца")

    # 3. После реплики владельца бот молчит и на следующий вопрос клиента
    await business.on_message(
        message_update(FakeMessage("а какие сроки?", CLIENT, CHAT)), ctx
    )
    check(bot.sent == [], "бот перебил человека, который уже отвечает")

    # 4. Пауза действует только в этой переписке, в другой бот работает
    await business.on_message(
        message_update(FakeMessage("какие сроки?", CLIENT, CHAT + 1)), ctx
    )
    check(len(bot.sent) == 1, "пауза распространилась на чужую переписку")

    # 5. Пауза не вечная
    ctx.bot_data[business._PAUSED][CHAT] = time.time() - 1
    await business.on_message(
        message_update(FakeMessage("так что со сроками?", CLIENT, CHAT)), ctx
    )
    check(len(bot.sent) == 2, "после истечения паузы бот не вернулся")

    # 6. Владелец узнаётся один раз и запоминается
    check(bot.lookups == 1, f"лишние запросы владельца: {bot.lookups}")

    # 7. Если владельца выяснить не удалось — молчим, а не отвечаем вслепую
    class BrokenBot(FakeBot):
        async def get_business_connection(self, connection_id):
            raise RuntimeError("Telegram недоступен")

    broken = BrokenBot(OWNER)
    await business.on_message(
        message_update(FakeMessage("привет", CLIENT, CHAT)), FakeContext(broken)
    )
    check(broken.sent == [], "ответил, не зная владельца — рискует отвечать себе")

    # 8. Нетекстовые сообщения игнорируются
    bot = FakeBot(OWNER)
    ctx = FakeContext(bot)
    await business.on_message(
        message_update(FakeMessage(None, CLIENT, CHAT)), ctx
    )
    check(bot.sent == [], "попытался ответить на сообщение без текста")

    for f in failures:
        print("ПРОВАЛ:", f)
    if failures:
        print(f"\nПровалено проверок: {len(failures)}")
        return 1
    print("Автоответчик: все 8 проверок пройдены.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(run()))
