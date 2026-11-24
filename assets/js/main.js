/* СтройАутсорс — main.js */
(function () {
  'use strict';
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var SA_MESSENGERS = { telegram: '', whatsapp: '', max: '' };
  var MSG_LABELS = { telegram: 'Telegram', whatsapp: 'WhatsApp', max: 'MAX' };
  var MSG_ICONS = { telegram: 'TG', whatsapp: 'WA', max: 'MAX' };
  document.querySelectorAll('[data-messenger-links]').forEach(function (box) {
    var html = Object.keys(SA_MESSENGERS).filter(function (k) { return SA_MESSENGERS[k]; }).map(function (k) {
      return '<a class="messenger-link messenger-link--' + k + '" href="' + SA_MESSENGERS[k] + '" target="_blank" rel="noopener"><span aria-hidden="true">' + MSG_ICONS[k] + '</span><span>' + MSG_LABELS[k] + '</span></a>';
    }).join('');
    if (html) { box.innerHTML = html; box.hidden = false; }
  });

  /* ---- Mobile menu ---- */
  var burger = document.querySelector('.burger');
  var nav = document.getElementById('siteNav');
  if (burger && nav) {
    burger.addEventListener('click', function () {
      var open = nav.classList.toggle('site-nav-open');
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
      document.body.style.overflow = open ? 'hidden' : '';
    });
    nav.addEventListener('click', function (e) {
      if (e.target.closest('a')) {
        nav.classList.remove('site-nav-open');
        burger.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
      }
    });
  }

  /* ---- Scroll reveal ---- */
  var reveals = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && !reduceMotion) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('is-visible'); io.unobserve(en.target); }
      });
    }, { threshold: 0.12 });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add('is-visible'); });
  }

  /* ---- Steps ribbon animation (motion #2), once on view ---- */
  document.querySelectorAll('.steps--anim').forEach(function (el) {
    if (reduceMotion) { el.classList.add('is-run'); return; }
    var done = false;
    var sio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting && !done) { done = true; el.classList.add('is-run'); sio.disconnect(); }
      });
    }, { threshold: 0.3 });
    sio.observe(el);
  });

  /* ---- Logo assembly on hero (motion #1), once ---- */
  document.querySelectorAll('.logo-anim').forEach(function (el) {
    if (reduceMotion) return;
    requestAnimationFrame(function () { el.classList.add('is-anim'); });
  });

  /* ---- Forms ---- */
  var PHONE_RE = /^[\d\s\-()+]{10,18}$/;
  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

  function normPhone(v) {
    var d = v.replace(/\D/g, '');
    if (d.length === 11 && d[0] === '8') d = '7' + d.slice(1);
    if (d.length === 10) d = '7' + d;
    return d;
  }
  function fmtPhone(d) {
    d = d.slice(0, 11);
    var cc = d[0];
    var r = d.slice(1);
    var out = '+' + cc;
    if (r.length > 0) out += ' (' + r.slice(0, Math.min(3, r.length));
    if (r.length >= 3) out += ')';
    if (r.length > 3) out += ' ' + r.slice(3, 6);
    if (r.length > 6) out += '-' + r.slice(6, 8);
    if (r.length > 8) out += '-' + r.slice(8, 10);
    return out;
  }

  document.querySelectorAll('form[data-lead]').forEach(function (form) {
    var phone = form.querySelector('[name="phone"]');
    if (phone) {
      phone.addEventListener('input', function () {
        var pos = phone.selectionStart;
        var before = phone.value.slice(0, pos).replace(/\D/g, '').length;
        var d = normPhone(phone.value);
        phone.value = d ? fmtPhone(d) : '';
        // восстановить курсор приблизительно
        var i = 0, count = 0;
        while (i < phone.value.length && count < before) { if (/\d/.test(phone.value[i])) count++; i++; }
        phone.setSelectionRange(i, i);
      });
      phone.addEventListener('blur', function () {
        var d = normPhone(phone.value);
        if (d.length === 11) phone.value = fmtPhone(d);
      });
    }

    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var ok = true;
      form.querySelectorAll('.field.has-error,.check-row.has-error').forEach(function (el) { el.classList.remove('has-error'); });
      form.querySelectorAll('.form-msg').forEach(function (el) { el.style.display = 'none'; });

      var req = form.querySelectorAll('[required]');
      req.forEach(function (f) {
        var wrap = f.closest('.field') || f.closest('.check-row');
        var val = f.type === 'checkbox' ? f.checked : f.value.trim();
        if (!val || (f.name === 'phone' && normPhone(f.value).length !== 11)) {
          if (wrap) wrap.classList.add('has-error');
          ok = false;
        }
      });
      var email = form.querySelector('[name="email"]');
      if (email && email.value.trim() && !EMAIL_RE.test(email.value.trim())) {
        email.closest('.field').classList.add('has-error'); ok = false;
      }
      if (!ok) {
        var m = form.querySelector('.form-msg--err');
        if (m) { m.textContent = 'Проверьте выделенные поля и попробуйте ещё раз.'; m.style.display = 'block'; }
        return;
      }

      var btn = form.querySelector('[type="submit"]');
      if (btn) btn.disabled = true;

      var data = {};
      new FormData(form).forEach(function (v, k) { data[k] = v; });
      data.phone_norm = normPhone(data.phone || '');
      data.page = location.pathname;
      data.consent_version = '2026-11-19';
      data.ts = new Date().toISOString();

      fetch(form.getAttribute('action') || 'send.php', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify(data)
      }).then(function (r) { return r.json().catch(function () { return { ok: r.ok }; }); })
        .then(function (res) {
          if (res && res.ok) { showSuccess(form); }
          else { showFail(form, res && res.error); }
        })
        .catch(function () { showFail(form); });
    });
  });

  function showSuccess(form) {
    form.style.display = 'none';
    var succ = form.parentElement.querySelector('.form-success') || form.querySelector('.form-success');
    if (succ) {
      succ.style.display = 'block';
      succ.classList.add('is-show');
      var sig = succ.querySelector('.sig');
      if (sig && !reduceMotion) sig.classList.add('is-signal');
    } else {
      var m = document.createElement('div');
      m.className = 'form-msg form-msg--ok';
      m.textContent = 'Заявка отправлена. Мы свяжемся с вами по указанному номеру.';
      form.parentElement.appendChild(m);
    }
    var hidden = form.querySelector('input[type="hidden"][name="form_type"]');
    // скролл к сообщению
    var target = form.parentElement.querySelector('.form-success') || form.parentElement;
    target.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'center' });
  }

  function showFail(form, msg) {
    var btn = form.querySelector('[type="submit"]');
    if (btn) btn.disabled = false;
    var m = form.querySelector('.form-msg--err');
    if (m) {
      m.textContent = (msg || 'Не удалось отправить заявку. Позвоните нам: +7 (986) 089-85-60') + ' или напишите на info@stroyautsors.ru.';
      m.style.display = 'block';
    }
  }

  /* ---- Phone links: отметить текущую страницу в меню ---- */
  var path = location.pathname.replace(/\/+$/, '') || '/';
  document.querySelectorAll('.main-nav a, .site-nav-open a, .footer-grid a').forEach(function (a) {
    var href = a.getAttribute('href');
    if (!href || href.charAt(0) !== '/' || href.charAt(1) === '/') return;
    var p = href.replace(/\/+$/, '') || '/';
    if (p === path || (p !== '/' && path.indexOf(p + '/') === 0)) a.setAttribute('aria-current', 'page');
  });
})();
