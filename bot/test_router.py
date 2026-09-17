# -*- coding: utf-8 -*-
"""
Проверка подбора тем. Запускается без токена и без интернета:

    python3 test_router.py

Если добавляете ключевые слова в router.py — допишите сюда пару примеров
и обязательно проверьте, что новое слово не перехватывает чужие вопросы.
"""

import sys
import content
import router

# (что написал человек, какая тема должна сработать)
CASES = [
    # деньги
    ("сколько стоит сайт?", "price"),
    ("какая цена лендинга", "price"),
    ("Сколько это будет стоить?", "price"),
    ("есть прайс?", "price"),
    ("а это не дорого?", "price"),
    ("пришлите смету", "price"),

    # сроки
    ("как долго делается сайт", "terms"),
    ("какие сроки?", "terms"),
    ("за сколько сделаете магазин", "terms"),
    ("успеете до нового года?", "terms"),

    # боты
    ("нужен бот для записи", "bots"),
    ("делаете чат-ботов?", "bots"),
    ("хочу телеграм бота", "bots"),

    # процесс
    ("как вы работаете", "process"),
    ("какие этапы", "process"),
    ("с чего начать", "process"),
    ("что от меня нужно", "process"),

    # условия
    ("какие условия", "conditions"),
    ("нужна ли предоплата", "conditions"),
    ("а если не понравится дизайн", "conditions"),
    ("а если мне не понравится макет", "conditions"),
    ("что если результат не устроит", "conditions"),
    ("исходники отдаете?", "conditions"),

    # работы и ниши
    ("покажите портфолио", "work"),
    ("есть кейсы?", "work"),
    ("делали сайты для стоматологии?", "work"),
    ("работаете со строительными компаниями", "work"),

    # услуги
    ("что вы делаете", "services"),
    ("какие услуги", "services"),
    ("нужен интернет-магазин", "services"),
    ("сделайте редизайн", "services"),

    # заявка
    ("хочу оставить заявку", "brief"),
    ("хочу заказать сайт", "brief"),
    ("давайте обсудить проект", "brief"),

    # контакты и вежливость
    ("дайте контакты", "contacts"),
    ("можно связаться с человеком", "contacts"),
    ("здравствуйте", "greeting"),
    ("Привет!", "greeting"),
    ("спасибо большое", "thanks"),

    # ловушки: короткий ключ не должен срабатывать внутри другого слова.
    # Эти фразы тем не попадают ни в одну — важно лишь, что не в «bots».
    ("как у вас построена работа над проектом", None),
    ("расскажите про ваши подходы к заботе о клиентах", None),

    # мусор
    ("", None),
    ("   ", None),
    ("ыфваыфва", None),
    ("погода в москве", None),
]


# Отдельно: фраза ни при каких условиях не должна уехать в эту тему.
NEVER = [
    ("как у вас построена работа над проектом", "bots"),
    ("расскажите про ваши подходы к заботе о клиентах", "bots"),
    ("работа с документами", "bots"),
    ("оборот компании", "bots"),
]


def main() -> int:
    failed = []

    for text, forbidden in NEVER:
        got = router.match(text)
        if got == forbidden:
            failed.append((text, f"что угодно кроме {forbidden}", got))
    for text, expected in CASES:
        got = router.match(text)
        if got != expected:
            failed.append((text, expected, got))

    # каждая тема, на которую может указать роутер, обязана иметь текст ответа
    keys = {key for key, _ in router.INTENTS} - {"brief"}
    missing = sorted(k for k in keys if k not in content.ANSWERS)

    # и каждая кнопка меню тоже
    buttons = {code for row in content.MENU for _, code in row} - {"brief"}
    missing_buttons = sorted(b for b in buttons if b not in content.ANSWERS)

    for text, expected, got in failed:
        print(f"ПРОВАЛ  {text!r}: ждали {expected}, получили {got}")
    if missing:
        print("Нет ответа для тем:", missing)
    if missing_buttons:
        print("Нет ответа для кнопок:", missing_buttons)

    # все тексты должны собираться без ошибок
    for key in sorted(content.ANSWERS):
        body = content.answer(key)
        if not body or not body.strip():
            print("Пустой ответ:", key)
            failed.append((key, "текст", "пусто"))

    total = len(CASES)
    if failed or missing or missing_buttons:
        print(f"\nПровалено {len(failed)} из {total}.")
        return 1

    print(f"Все проверки пройдены: {total} фраз, {len(content.ANSWERS)} тем.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
