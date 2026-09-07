/* =========================================================
   ЮВИ — интерактив главной страницы
   Без зависимостей. Всё уважает prefers-reduced-motion.
   ========================================================= */
(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var coarsePointer = window.matchMedia('(hover: none)').matches;
  var $ = function (sel, root) { return (root || document).querySelector(sel); };
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };

  /* ---------------------------------------------------------
     1. Тикер — дублируем содержимое для бесшовной прокрутки
     --------------------------------------------------------- */
  var tickerTrack = $('#tickerTrack');
  if (tickerTrack) tickerTrack.innerHTML += tickerTrack.innerHTML;

  /* ---------------------------------------------------------
     2. Переключение языка RU / EN
     --------------------------------------------------------- */
  var LANG_KEY = 'yuvi-lang';

  function setLang(lang) {
    if (lang !== 'ru' && lang !== 'en') lang = 'ru';
    document.documentElement.lang = lang;

    $$('[data-ru]').forEach(function (el) {
      var value = el.getAttribute('data-' + lang);
      if (value !== null) el.textContent = value;
    });

    $$('.lang__btn').forEach(function (btn) {
      var on = btn.dataset.lang === lang;
      btn.classList.toggle('is-active', on);
      btn.setAttribute('aria-pressed', String(on));
    });

    try { localStorage.setItem(LANG_KEY, lang); } catch (e) { /* приватный режим */ }
  }

  $$('.lang__btn').forEach(function (btn) {
    btn.addEventListener('click', function () { setLang(btn.dataset.lang); });
  });

  var savedLang = null;
  try { savedLang = localStorage.getItem(LANG_KEY); } catch (e) { /* приватный режим */ }
  setLang(savedLang || 'ru');

  /* ---------------------------------------------------------
     3. Шапка: линия появляется после скролла
     --------------------------------------------------------- */
  var header = $('#header');
  var onScroll = function () {
    header.classList.toggle('is-stuck', window.scrollY > 8);
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---------------------------------------------------------
     4. Мобильное меню
     --------------------------------------------------------- */
  var burger = $('#burger');
  var mmenu = $('#mobileMenu');

  function closeMenu() {
    burger.setAttribute('aria-expanded', 'false');
    mmenu.hidden = true;
    document.body.style.overflow = '';
  }

  burger.addEventListener('click', function () {
    var open = burger.getAttribute('aria-expanded') === 'true';
    if (open) { closeMenu(); return; }
    burger.setAttribute('aria-expanded', 'true');
    mmenu.hidden = false;
    document.body.style.overflow = 'hidden';
  });

  $$('.mmenu__nav a').forEach(function (a) { a.addEventListener('click', closeMenu); });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && burger.getAttribute('aria-expanded') === 'true') {
      closeMenu();
      burger.focus();
    }
  });

  window.addEventListener('resize', function () {
    if (window.innerWidth > 880 && burger.getAttribute('aria-expanded') === 'true') closeMenu();
  });

  /* ---------------------------------------------------------
     5. Главный приём: «скучный сайт чинится под курсором»
     Курсор открывает круглое окно в настоящий дизайн.
     Чем больше пути пройдено мышью, тем шире окно; после
     TARGET пикселей дизайн раскрывается целиком и остаётся.
     --------------------------------------------------------- */
  var hero = $('#hero');
  var bar = $('#revealBar');
  var pctOut = $('#revealPct');
  var skipBtn = $('#revealSkip');

  var TARGET = 3400;      // пикселей движения мыши до полного раскрытия
  var R_MIN = 140;        // стартовый радиус окна
  var R_MAX = 300;        // радиус перед раскрытием
  var IDLE_MS = 6000;     // если мышь стоит — раскрываем сами

  var travel = 0;
  var lastX = null, lastY = null;
  var unlocked = false;
  var idleTimer = null;

  function setHole(x, y) {
    hero.style.setProperty('--rx', x + 'px');
    hero.style.setProperty('--ry', y + 'px');
  }

  function setRadius(r) {
    hero.style.setProperty('--rr', r + 'px');
  }

  function unlock() {
    if (unlocked) return;
    unlocked = true;
    clearTimeout(idleTimer);
    if (bar) bar.style.width = '100%';
    if (pctOut) pctOut.textContent = '100';
    hero.classList.add('is-revealed');
    window.setTimeout(function () { hero.classList.add('is-open'); }, 1100);
  }

  function armIdle() {
    clearTimeout(idleTimer);
    idleTimer = window.setTimeout(unlock, IDLE_MS);
  }

  if (hero && !reduceMotion) {
    if (coarsePointer) {
      // На тач-устройствах курсора нет — открываем сразу после первого касания
      // или через короткую паузу, чтобы приём всё же считывался.
      setHole(window.innerWidth / 2, window.innerHeight * 0.4);
      setRadius(R_MIN);
      window.setTimeout(unlock, 2200);
      hero.addEventListener('touchstart', unlock, { passive: true, once: true });
    } else {
      setRadius(R_MIN);
      armIdle();

      hero.addEventListener('pointermove', function (e) {
        var rect = hero.getBoundingClientRect();
        var x = e.clientX - rect.left;
        var y = e.clientY - rect.top;
        setHole(x, y);

        if (unlocked) return;

        if (lastX !== null) {
          travel += Math.hypot(x - lastX, y - lastY);
        }
        lastX = x; lastY = y;

        var progress = Math.min(travel / TARGET, 1);
        setRadius(R_MIN + (R_MAX - R_MIN) * progress);
        if (bar) bar.style.width = (progress * 100).toFixed(1) + '%';
        if (pctOut) pctOut.textContent = String(Math.round(progress * 100));

        armIdle();
        if (progress >= 1) unlock();
      });

      // Ушли со страницы вниз — приём отыграл, показываем дизайн
      window.addEventListener('scroll', function () {
        if (!unlocked && window.scrollY > window.innerHeight * 0.35) unlock();
      }, { passive: true });
    }

    if (skipBtn) skipBtn.addEventListener('click', unlock);

    // Клавиатура: доходя фокусом до содержимого, пользователь тоже должен всё видеть
    hero.addEventListener('focusin', unlock);
  }

  /* ---------------------------------------------------------
     6. Робот: взгляд за курсором и моргание
     --------------------------------------------------------- */
  var robot = $('#robot');
  var eyes = $('#robotEyes');

  if (robot && eyes && !reduceMotion && !coarsePointer) {
    window.addEventListener('pointermove', function (e) {
      var box = robot.getBoundingClientRect();
      if (!box.width) return;
      var cx = box.left + box.width * 0.52;
      var cy = box.top + box.height * 0.42;
      var dx = (e.clientX - cx) / box.width;
      var dy = (e.clientY - cy) / box.height;
      var max = 5;
      var tx = Math.max(-max, Math.min(max, dx * 18));
      var ty = Math.max(-max, Math.min(max, dy * 18));
      eyes.setAttribute('transform', 'translate(' + tx.toFixed(1) + ' ' + ty.toFixed(1) + ')');
    }, { passive: true });
  }

  if (robot && !reduceMotion) {
    (function blinkLoop() {
      var wait = 2600 + Math.random() * 3600;
      window.setTimeout(function () {
        robot.classList.add('is-blinking');
        window.setTimeout(function () { robot.classList.remove('is-blinking'); }, 130);
        blinkLoop();
      }, wait);
    })();
  }

  /* ---------------------------------------------------------
     7. Реактивный геометрический фон
     Сетка правильных фигур: рядом с курсором квадраты растут,
     поворачиваются к нему и окрашиваются в акцент.
     --------------------------------------------------------- */
  var canvas = $('#fxCanvas');

  if (canvas) {
    var ctx = canvas.getContext('2d');
    var STEP = 46;          // шаг сетки
    var RADIUS = 260;       // радиус влияния курсора
    var dpr = 1;
    var w = 0, h = 0;
    var px = -9999, py = -9999;   // позиция курсора
    var cx = -9999, cy = -9999;   // сглаженная позиция
    var running = false;

    function resize() {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      w = canvas.clientWidth;
      h = canvas.clientHeight;
      canvas.width = Math.round(w * dpr);
      canvas.height = Math.round(h * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      draw();
    }

    function draw() {
      ctx.clearRect(0, 0, w, h);

      // мягкое синее свечение под курсором
      if (cx > -9999) {
        var glow = ctx.createRadialGradient(cx, cy, 0, cx, cy, RADIUS * 1.5);
        glow.addColorStop(0, 'rgba(62,139,255,.10)');
        glow.addColorStop(1, 'rgba(62,139,255,0)');
        ctx.fillStyle = glow;
        ctx.fillRect(cx - RADIUS * 1.5, cy - RADIUS * 1.5, RADIUS * 3, RADIUS * 3);
      }

      for (var x = STEP / 2; x < w; x += STEP) {
        for (var y = STEP / 2; y < h; y += STEP) {
          var dx = cx - x;
          var dy = cy - y;
          var dist = Math.sqrt(dx * dx + dy * dy);

          if (dist > RADIUS) {
            // спокойное состояние — едва заметная точка сетки
            ctx.fillStyle = 'rgba(11,11,12,.10)';
            ctx.fillRect(x - 1, y - 1, 2, 2);
            continue;
          }

          var t = 1 - dist / RADIUS;          // 0 на краю, 1 под курсором
          var size = 2 + t * t * 13;
          var angle = Math.atan2(dy, dx) * t;

          ctx.save();
          ctx.translate(x, y);
          ctx.rotate(angle);
          ctx.strokeStyle = 'rgba(62,139,255,' + (0.14 + t * 0.66).toFixed(3) + ')';
          ctx.lineWidth = 1;
          ctx.strokeRect(-size / 2, -size / 2, size, size);
          ctx.restore();
        }
      }
    }

    function tick() {
      cx += (px - cx) * 0.14;
      cy += (py - cy) * 0.14;
      draw();

      if (Math.abs(px - cx) < 0.4 && Math.abs(py - cy) < 0.4) {
        cx = px; cy = py;
        draw();
        running = false;
        return;
      }
      requestAnimationFrame(tick);
    }

    function start() {
      if (running) return;
      running = true;
      requestAnimationFrame(tick);
    }

    resize();
    window.addEventListener('resize', resize);

    if (!reduceMotion && !coarsePointer) {
      window.addEventListener('pointermove', function (e) {
        px = e.clientX; py = e.clientY;
        if (cx < -9000) { cx = px; cy = py; }
        start();
      }, { passive: true });

      document.addEventListener('visibilitychange', function () {
        if (!document.hidden) start();
      });
    }
  }

  /* ---------------------------------------------------------
     8. Появление блоков при скролле
     --------------------------------------------------------- */
  var pending = $$('.reveal-up');

  if (reduceMotion) {
    pending.forEach(function (el) { el.classList.add('is-in'); });
  } else {
    // Прямая проверка по скроллу, а не IntersectionObserver: так блок физически
    // не может остаться скрытым, если наблюдатель не сработал.
    var sweepQueued = false;

    function sweep() {
      sweepQueued = false;
      var limit = window.innerHeight - 40;
      var shown = 0;

      pending = pending.filter(function (el) {
        if (el.getBoundingClientRect().top > limit) return true;
        el.style.transitionDelay = (shown++ % 3) * 70 + 'ms';
        el.classList.add('is-in');
        return false;
      });

      if (!pending.length) {
        window.removeEventListener('scroll', queueSweep);
        window.removeEventListener('resize', queueSweep);
      }
    }

    function queueSweep() {
      if (sweepQueued) return;
      sweepQueued = true;
      requestAnimationFrame(sweep);
    }

    window.addEventListener('scroll', queueSweep, { passive: true });
    window.addEventListener('resize', queueSweep);
    sweep();
  }

  /* ---------------------------------------------------------
     9. Год в подвале
     --------------------------------------------------------- */
  var year = $('#year');
  if (year) year.textContent = String(new Date().getFullYear());
})();
