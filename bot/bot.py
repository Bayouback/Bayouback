# -*- coding: utf-8 -*-
"""
Телеграм-бот студии ЮВИ.

Отвечает на частые вопросы сам, а когда вопрос выходит за рамки сценария —
собирает заявку и передаёт её человеку. Ровно та схема, которую студия
продаёт клиентам, только про себя.

Запуск:
    export BOT_TOKEN="токен от @BotFather"
    python3 bot.py

Подробности — в README.md рядом.
"""

import logging
import os
import sys
import warnings

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from telegram.warnings import PTBUserWarning

import content
import router

# Опрос-заявку можно начать и командой /brief, и кнопкой меню. Из-за такого
# смешения точек входа библиотека предупреждает про per_message — поведение
# при этом верное, поэтому гасим только это одно предупреждение.
warnings.filterwarnings("ignore", message=r".*per_message.*", category=PTBUserWarning)

logging.basicConfig(
    format="%(asctime)s  %(levelname)-8s %(name)s  %(message)s",
    level=logging.INFO,
)
# библиотека на INFO сыплет каждым запросом к API — оставляем только своё
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("yuvi-bot")

# Шаги разговора при сборе заявки
ASK_NAME, ASK_TASK, ASK_CONTACT = range(3)


# --------------------------------------------------------------------- меню

def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(title, callback_data=code) for title, code in row]
            for row in content.MENU
        ]
    )


async def reply(update: Update, text: str) -> None:
    """Отправляет ответ и всегда показывает меню — чтобы не было тупика."""
    message = update.effective_message
    await message.reply_text(text, reply_markup=main_menu())


# --------------------------------------------------------------- команды

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    log.info("Старт: %s (id=%s)", user.full_name, user.id)
    await reply(update, content.GREETING)


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await reply(update, content.HELP)


# --------------------------------------------------- свободный текст и кнопки

async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Любое сообщение вне сбора заявки."""
    text = update.effective_message.text or ""
    key = router.match(text)
    log.info("Вопрос: %r → тема: %s", text[:80], key)

    if key == "brief":
        await start_brief(update, context)
        return

    await update.effective_chat.send_action(ChatAction.TYPING)
    await reply(update, content.answer(key) if key else content.FALLBACK)


async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Нажатие кнопки меню."""
    query = update.callback_query
    await query.answer()          # убирает «часики» на кнопке
    code = query.data
    log.info("Кнопка: %s", code)

    if code == "brief":
        await start_brief(update, context)
        return

    await query.message.reply_text(content.answer(code), reply_markup=main_menu())


# ----------------------------------------------------------------- заявка

async def start_brief(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.effective_message.reply_text(content.BRIEF_START)
    return ASK_NAME


async def brief_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["name"] = update.effective_message.text.strip()
    await update.effective_message.reply_text(content.BRIEF_TASK)
    return ASK_TASK


async def brief_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["task"] = update.effective_message.text.strip()
    await update.effective_message.reply_text(content.BRIEF_CONTACT)
    return ASK_CONTACT


async def brief_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["contact"] = update.effective_message.text.strip()
    user = update.effective_user

    lines = [
        "Новая заявка из бота",
        "",
        f"Имя: {context.user_data['name']}",
        f"Задача: {context.user_data['task']}",
        f"Связь: {context.user_data['contact']}",
        "",
    ]
    if user.username:
        lines.append(f"Профиль: @{user.username}")
    lines.append(f"ID чата: {user.id}")
    lead = "\n".join(lines)

    admin = os.environ.get("ADMIN_CHAT_ID", "").strip()
    if admin:
        try:
            await context.bot.send_message(chat_id=admin, text=lead)
        except Exception:
            # заявку человеку всё равно подтверждаем: она в логе, не потеряется
            log.exception("Не удалось отправить заявку админу (ADMIN_CHAT_ID=%s)", admin)
    else:
        log.warning("ADMIN_CHAT_ID не задан, заявка только в логе")

    log.info("ЗАЯВКА:\n%s", lead)
    await reply(update, content.BRIEF_DONE)
    context.user_data.clear()
    return ConversationHandler.END


async def brief_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await reply(update, content.BRIEF_CANCEL)
    return ConversationHandler.END


async def brief_restart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """/start посреди опроса: бросаем заявку и показываем меню, а не сухую отмену."""
    context.user_data.clear()
    await cmd_start(update, context)
    return ConversationHandler.END


# ------------------------------------------------------------------- ошибки

async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.exception("Ошибка при обработке обновления", exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "Что-то пошло не так с моей стороны. Попробуйте ещё раз "
            f"или напишите человеку — {content.TELEGRAM}."
        )


# -------------------------------------------------------------------- старт

def build_app(token: str) -> Application:
    app = Application.builder().token(token).build()

    brief = ConversationHandler(
        entry_points=[
            CommandHandler("brief", start_brief),
            CallbackQueryHandler(start_brief, pattern="^brief$"),
        ],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, brief_name)],
            ASK_TASK: [MessageHandler(filters.TEXT & ~filters.COMMAND, brief_task)],
            ASK_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, brief_contact)],
        },
        fallbacks=[CommandHandler("cancel", brief_cancel), CommandHandler("start", brief_restart)],
    )

    # порядок важен: разговор про заявку должен перехватывать текст раньше общего обработчика
    app.add_handler(brief)
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CallbackQueryHandler(on_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    app.add_error_handler(on_error)
    return app


def main() -> int:
    token = os.environ.get("BOT_TOKEN", "").strip()
    if not token:
        print(
            "Не задан BOT_TOKEN.\n\n"
            "Получите токен у @BotFather в Telegram и запустите так:\n"
            '    export BOT_TOKEN="123456:AA..."\n'
            "    python3 bot.py\n\n"
            "Подробнее — в README.md рядом с этим файлом.",
            file=sys.stderr,
        )
        return 1

    log.info("Бот запускается. Остановить — Ctrl+C")
    build_app(token).run_polling(allowed_updates=Update.ALL_TYPES)
    return 0


if __name__ == "__main__":
    sys.exit(main())
