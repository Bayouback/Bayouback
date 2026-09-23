# -*- coding: utf-8 -*-
# Обложки «актуального» с роботом. Каждая — сторис 1080×1920, из которой
# Instagram вырезает круг по центру кадра, поэтому всё важное держим внутри
# круга диаметром ~900 с центром в (540, 960).
import base64, pathlib, sys

OUT = pathlib.Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
REPO = pathlib.Path('/home/user/Bayouback')

def uri(p):
    return 'data:image/png;base64,' + base64.b64encode(pathlib.Path(p).read_bytes()).decode()

ROBOT = uri(REPO / 'social/robot/robot-open.png')      # вырезанный, с прозрачностью
MARK = 'data:image/svg+xml;base64,' + base64.b64encode(
    (REPO / 'assets/img/robot-mark.svg').read_bytes()).decode()

BASE = '''
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1080px;height:1920px;overflow:hidden}
body{font-family:"Inter",system-ui,sans-serif}
/* центр кружка, который вырежет Instagram */
.mid{position:absolute;left:540px;top:960px;transform:translate(-50%,-50%)}
.rb{display:block}
.mono{font-family:"JetBrains Mono",monospace;letter-spacing:.22em;text-transform:uppercase}
'''

def page(name, bg, body, extra=''):
    (OUT / f'{name}.html').write_text(
        f'''<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>{name}</title>
<style>{BASE}
body{{background:{bg}}}
{extra}</style></head><body>{body}</body></html>\n''', encoding='utf-8')


# Робот показывается КРУПНО: в приложении кружок размером с ноготь, и фигура
# в половину кадра там превращается в пятнышко. При ширине картинки 1120
# робот занимает 673×791 — почти весь круг диаметром 1080, но в него влезает.
BIG = 1120

# 1 · только аватарка на белом
page('01-belyy', '#FFFFFF',
     f'<img class="mid rb" src="{ROBOT}" style="width:{BIG}px" alt="">')

# 2 · только аватарка на графите
page('02-grafit', '#0B0B0C',
     f'<img class="mid rb" src="{ROBOT}" style="width:{BIG}px" alt="">')

# 3 · на фирменном синем
page('03-siniy', '#3E8BFF',
     f'<img class="mid rb" src="{ROBOT}" style="width:{BIG}px" alt="">')

# 4 · на бежевом
page('04-bezhevyy', '#F4EEE4',
     f'<img class="mid rb" src="{ROBOT}" style="width:{BIG}px" alt="">')

# 5 · синий диск под роботом: в ряду кружков читается как цветное пятно
page('05-disk', '#FFFFFF',
     f'<div class="mid disk"></div><img class="mid rb" src="{ROBOT}" style="width:980px" alt="">',
     '.disk{width:880px;height:880px;border-radius:50%;background:#3E8BFF}')

# 6 · крупный кроп головы — заполняет кружок целиком
page('06-golova', '#F4EEE4',
     f'<img class="rb" src="{ROBOT}" style="position:absolute;width:1700px;'
     f'left:-310px;top:378px" alt="">')

# 7 · фирменная геометрия за роботом, линии заметной толщины
page('07-geometriya', '#FFFFFF', f'''
<svg class="mid" width="1000" height="1000" viewBox="0 0 1000 1000" aria-hidden="true">
  <rect x="140" y="140" width="720" height="720" fill="none" stroke="#3E8BFF" stroke-width="10"/>
  <circle cx="500" cy="500" r="360" fill="none" stroke="#9CC8FF" stroke-width="10"/>
  <path d="M500 96v120M500 784v120M96 500h120M784 500h120" stroke="#3E8BFF" stroke-width="12"/>
</svg>
<img class="mid rb" src="{ROBOT}" style="width:980px" alt="">''')

# 8 · плоский знак с сайта вместо объёмного робота
page('08-znak', '#F4EEE4',
     f'<img class="mid rb" src="{MARK}" style="width:900px" alt="">')

print('обложек собрано:', len(list(OUT.glob('*.html'))))
