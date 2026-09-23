# -*- coding: utf-8 -*-
# Обложка «актуального» на тему «наши работы». Без робота, в его же палитре.
# Кадр 1080×1920, Instagram вырежет круг по центру — всё держим внутри круга
# диаметром 900 с центром (540, 960), то есть в квадрате 900×900 по центру.
import pathlib, sys

OUT = pathlib.Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)

# палитра робота
DEEP, TEAL, MID, LIGHT, PALE = '#1C3D4A', '#2E505E', '#5D8493', '#7DA1B0', '#9CBECB'
SHELL, WHITE, SAND, MIST = '#E2E8EF', '#FFFFFF', '#F4EEE4', '#EDF2F5'

BASE = '''
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1080px;height:1920px;overflow:hidden}
.art{position:absolute;left:540px;top:960px;transform:translate(-50%,-50%);
     width:900px;height:900px;display:block}
'''

def page(name, bg, svg):
    (OUT / f'{name}.html').write_text(
        f'''<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>{name}</title>
<style>{BASE}body{{background:{bg}}}</style></head><body>
<svg class="art" viewBox="0 0 900 900" aria-hidden="true">{svg}</svg>
</body></html>\n''', encoding='utf-8')


def window(x, y, w, h, fill, chrome=True, r=26):
    """Окно браузера: шапка с точками и полоски содержимого."""
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}"/>'
    if chrome:
        s += (f'<path d="M{x} {y + 52}h{w}" stroke="#FFFFFF" stroke-opacity=".2" stroke-width="3"/>'
              f'<circle cx="{x + 30}" cy="{y + 26}" r="8" fill="#FFF" opacity=".5"/>'
              f'<circle cx="{x + 58}" cy="{y + 26}" r="8" fill="#FFF" opacity=".34"/>'
              f'<circle cx="{x + 86}" cy="{y + 26}" r="8" fill="#FFF" opacity=".24"/>')
    return s


# ── 1 · три окна веером: стопка работ ────────────────────────────────────
page('01-okna', MIST, f'''
<g transform="translate(450 450) scale(1.24) translate(-450 -450)">
<g transform="rotate(-12 450 450)" opacity=".75">
  {window(240, 250, 420, 300, PALE, chrome=False)}
</g>
<g transform="rotate(-5 450 470)" opacity=".9">
  {window(230, 290, 440, 310, MID, chrome=False)}
</g>
<g transform="rotate(6 450 500)">
  {window(210, 330, 480, 340, DEEP)}
  <g transform="rotate(6 450 500)"></g>
  <rect x="244" y="412" width="210" height="24" rx="12" fill="#FFF" opacity=".9"/>
  <rect x="244" y="456" width="320" height="14" rx="7" fill="#FFF" opacity=".34"/>
  <rect x="244" y="490" width="270" height="14" rx="7" fill="#FFF" opacity=".34"/>
  <rect x="244" y="540" width="150" height="44" rx="22" fill="{LIGHT}"/>
</g>
</g>''')

# ── 2 · мозаика разных по размеру плиток ─────────────────────────────────
page('02-mozaika', SAND, f'''
<rect x="60" y="110" width="430" height="430" rx="30" fill="{DEEP}"/>
<polyline points="112,440 190,368 268,404 346,300 424,246" fill="none"
          stroke="{PALE}" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/>
<circle cx="424" cy="246" r="22" fill="{WHITE}"/>

<rect x="516" y="110" width="324" height="200" rx="26" fill="{MID}"/>
<rect x="552" y="160" width="150" height="20" rx="10" fill="#FFF" opacity=".85"/>
<rect x="552" y="198" width="240" height="14" rx="7" fill="#FFF" opacity=".38"/>
<rect x="552" y="228" width="190" height="14" rx="7" fill="#FFF" opacity=".38"/>

<rect x="516" y="336" width="324" height="204" rx="26" fill="{WHITE}"/>
<g fill="{LIGHT}">
  <rect x="556" y="452" width="46" height="52" rx="8"/>
  <rect x="616" y="418" width="46" height="86" rx="8"/>
  <rect x="676" y="386" width="46" height="118" rx="8"/>
</g>
<rect x="736" y="366" width="66" height="138" rx="8" fill="{TEAL}"/>

<rect x="60" y="566" width="324" height="224" rx="26" fill="{SHELL}"/>
<circle cx="168" cy="660" r="46" fill="{TEAL}"/>
<rect x="232" y="640" width="120" height="16" rx="8" fill="{MID}" opacity=".6"/>
<rect x="232" y="672" width="86" height="16" rx="8" fill="{MID}" opacity=".35"/>
<rect x="96" y="726" width="252" height="40" rx="20" fill="{DEEP}"/>

<rect x="410" y="566" width="430" height="224" rx="26" fill="{TEAL}"/>
<rect x="450" y="610" width="200" height="22" rx="11" fill="#FFF" opacity=".9"/>
<rect x="450" y="650" width="300" height="14" rx="7" fill="#FFF" opacity=".34"/>
<rect x="450" y="700" width="140" height="46" rx="23" fill="{PALE}"/>''')

# ── 3 · одно окно крупно: самый простой силуэт ───────────────────────────
page('03-ekran', MIST, f'''
<rect x="92" y="212" width="716" height="476" rx="34" fill="{DEEP}"/>
<path d="M92 282h716" stroke="#FFFFFF" stroke-opacity=".18" stroke-width="3"/>
<circle cx="136" cy="247" r="11" fill="#FFF" opacity=".5"/>
<circle cx="172" cy="247" r="11" fill="#FFF" opacity=".34"/>
<circle cx="208" cy="247" r="11" fill="#FFF" opacity=".24"/>
<rect x="136" y="330" width="300" height="30" rx="15" fill="#FFF" opacity=".92"/>
<rect x="136" y="382" width="420" height="18" rx="9" fill="#FFF" opacity=".34"/>
<rect x="136" y="418" width="360" height="18" rx="9" fill="#FFF" opacity=".34"/>
<rect x="136" y="476" width="180" height="54" rx="27" fill="{LIGHT}"/>
<g fill="#FFFFFF" opacity=".12">
  <rect x="580" y="330" width="184" height="86" rx="16"/>
  <rect x="580" y="432" width="184" height="86" rx="16"/>
</g>
<rect x="136" y="580" width="628" height="62" rx="20" fill="{TEAL}"/>
<rect x="168" y="602" width="120" height="18" rx="9" fill="#FFF" opacity=".45"/>''')

# ── 4 · окно и курсор: работу открывают и нажимают ───────────────────────
page('04-kursor', SAND, f'''
<g transform="translate(450 450) scale(1.08) translate(-428 -417)">
<rect x="118" y="196" width="620" height="430" rx="32" fill="{MID}"/>
<path d="M118 262h620" stroke="#FFFFFF" stroke-opacity=".22" stroke-width="3"/>
<circle cx="158" cy="229" r="10" fill="#FFF" opacity=".5"/>
<circle cx="190" cy="229" r="10" fill="#FFF" opacity=".34"/>
<circle cx="222" cy="229" r="10" fill="#FFF" opacity=".24"/>
<rect x="158" y="306" width="250" height="26" rx="13" fill="#FFF" opacity=".9"/>
<rect x="158" y="352" width="360" height="16" rx="8" fill="#FFF" opacity=".34"/>
<rect x="158" y="386" width="300" height="16" rx="8" fill="#FFF" opacity=".34"/>
<rect x="158" y="440" width="220" height="60" rx="30" fill="{DEEP}"/>
<rect x="196" y="462" width="144" height="16" rx="8" fill="#FFF" opacity=".55"/>

<g transform="translate(330 402)">
  <path d="M0 0l0 236 56-58 36 84 46-22-38-84 78-4z" fill="{DEEP}"
        stroke="{WHITE}" stroke-width="16" stroke-linejoin="round"/>
</g>
</g>''')

print('обложек:', len(list(OUT.glob('*.html'))))
