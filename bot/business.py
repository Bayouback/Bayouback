# -*- coding: utf-8 -*-
"""
Режим «автоответчик внутри @yuvi_web».

Отличие от обычного бота: клиент пишет не боту, а лично вам. Telegram Business
разрешает подключить бота к личному аккаунту, и тогда бот видит эти переписки
и отвечает в них от вашего имени. Для клиента это выглядит как ваш ответ.

Три правила, которые тут важны:

1. Не отвечать на собственные сообщения владельца. В обновление `business_message`
   попадают и те сообщения, которые вы пишете сами. Владельца определяем по
   `BusinessConnection.user.id`.

2. Молчать, когда подключился человек. Как только вы сами написали в переписку,
   бот замолкает в ней на PAUSE_HOURS часов — иначе он будет перебивать вас
   на середине разговора.

3. Честно подписываться. Клиент должен понимать, что отвечает автоматика,
   а не вы лично. Без этого первое же «здравствуйте, я посмотрю и вернусь»
   от робота выглядит как обман.
"""

import logging
import time

from telegram import Update
from telegram.ext import ContextTypes

import content
import router

log = logging.getLogger("yuvi-bot.business")

# Сколько бот молчит в переписке после того, как вы ответили сами
PAUSE_HOURS = 8

_OWNERS = "business_owners"   # connection_id -> user_id владельца
_PAUSED = "business_paused"   # chat_id -> время, до которого молчим


async def _owner_id(context: ContextTypes.DEFAULT_TYPE, connection_id: str):
    """ID владельца аккаунта. Спрашиваем у Telegram и запоминаем."""
    owners = context.bot_data.setdefault(_OWNERS, {})
    if connection_id in owners:
        return owners[connection_id]

    try:
        conn = await context.bot.get_business_connection(connection_id)
    except Exception:
        # Без ID владельца отвечать нельзя: бот начнёт отвечать на ваши же реплики
        log.exception("Не удалось узнать владельца подключения %s", connection_id)
        return None

    owners[connection_id] = conn.user.id
    log.info("Подключение %s принадлежит %s (ответы разрешены: %s)",
             connection_id, conn.user.id, conn.can_reply)
    return conn.user.id


async def on_connection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Аккаунт подключил или отключил бота в настройках Telegram Business."""
    conn = update.business_connection
    context.bot_data.setdefault(_OWNERS, {})[conn.id] = conn.user.id

    if conn.is_enabled:
        log.info("Бот подключён к аккаунту %s. Отвечать можно: %s",
                 conn.user.username or conn.user.id, conn.can_reply)
        if not conn.can_reply:
            log.warning(
                "В настройках подключения не выдано право отвечать — "
                "бот будет видеть сообщения, но не сможет писать."
            )
    else:
        log.info("Бот отключён от аккаунта %s", conn.user.username or conn.user.id)


async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Сообщение в личной переписке подключённого аккаунта."""
    msg = update.business_message
    if not msg or not msg.text:
        return

    connection_id = msg.business_connection_id
    owner = await _owner_id(context, connection_id)
    if owner is None:
        return

    paused = context.bot_data.setdefault(_PAUSED, {})
    now = time.time()

    # Написали вы сами — значит, разговор взял на себя человек
    if msg.from_user and msg.from_user.id == owner:
        paused[msg.chat.id] = now + PAUSE_HOURS * 3600
        log.info("Владелец ответил сам в чате %s — молчим %s ч", msg.chat.id, PAUSE_HOURS)
        return

    if paused.get(msg.chat.id, 0) > now:
        log.info("Чат %s на паузе, не отвечаем", msg.chat.id)
        return

    key = router.match(msg.text)
    log.info("Business-вопрос: %r → тема: %s", msg.text[:80], key)

    if key == "brief":
        body = content.BUSINESS_BRIEF
    elif key:
        body = content.answer(key)
    else:
        body = content.BUSINESS_FALLBACK

    await context.bot.send_message(
        chat_id=msg.chat.id,
        text=body + content.BUSINESS_SIGNATURE,
        business_connection_id=connection_id,
    )
