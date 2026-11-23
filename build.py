# -*- coding: utf-8 -*-
"""Сборка сайта СтройАутсорс: оборачивает фрагменты site_src/pages/*.html
общим head/header/footer и пишет готовые страницы в site/."""
import os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, 'site_src', 'pages')
OUT = os.path.join(ROOT, 'site')

LOGO_SVG = ('<svg viewBox="0 0 216 249" width="30" height="35" aria-hidden="true">'
            '<g fill="#B6FF00"><rect x="0" y="33" width="100" height="100" rx="10"/>'
            '<path d="M138 0 L207 0 Q216 0 216 9 L216 111 L194 133 L125 133 Q116 133 116 124 L116 22 Z"/>'
            '<rect x="0" y="149" width="100" height="100" rx="10"/>'
            '<rect x="116" y="149" width="100" height="100" rx="10"/></g></svg>')

PAGES = {
    'raznorabochie-na-stroyku': dict(title='Рабочие на стройку в Москве и МО — СтройАутсорс',
        desc='Разнорабочие на строительный объект: разгрузка и подъём материалов, вынос мусора, подготовка площадки, усиление бригады. Звоните — согласуем выход.',
        canonical='/raznorabochie-na-stroyku/', depth=1, dir='raznorabochie-na-stroyku', file='index.html'),
    'dlya-chastnyh-lic':   dict(title='Разнорабочие для дома, участка и гаража — СтройАутсорс',
        desc='Подсобные рабочие для частных заказчиков: разобрать гараж и сарай, расчистить участок, вынести мусор, помочь при ремонте и строительстве дома.',
        canonical='/dlya-chastnyh-lic/', depth=1, dir='dlya-chastnyh-lic', file='index.html'),
    'srochno':             dict(title='Срочно нужны рабочие — позвоните +7 (986) 089-85-60',
        desc='Рабочие нужны срочно? Скажите, сколько людей, адрес, к какому часу и что делать. Обсудим, какой выход реально возможен.',
        canonical='/srochno/', depth=1, dir='srochno', file='index.html'),
    'uborka-snega':        dict(title='Уборка снега вручную в Москве и МО — СтройАутсорс',
        desc='Ручная уборка снега: расчистка дорожек, проходов, площадок и территории дома. Разово и сезонно по согласованию.',
        canonical='/uborka-snega/', depth=1, dir='uborka-snega', file='index.html'),
    'ceny':                dict(title='Цены на рабочих — получить расчёт стоимости смены',
        desc='Сколько стоит смена разнорабочих? Цена зависит от числа людей, района, вида работ и графика. Оставьте заявку — согласуем расчёт.',
        canonical='/ceny/', depth=1, dir='ceny', file='index.html'),
    'kak-rabotaem':        dict(title='Как работает СтройАутсорс — пять шагов до выхода',
        desc='Как мы работаем: заявка, расчёт, подтверждение состава, выход на объект, табель и документы. Прозрачно и по договору.',
        canonical='/kak-rabotaem/', depth=1, dir='kak-rabotaem', file='index.html'),
    'kontakty':            dict(title='Контакты СтройАутсорс — телефон, email, Москва и МО',
        desc='Свяжитесь с нами: +7 (986) 089-85-60, info@stroyautsors.ru. Москва и Московская область. Реквизиты и форма заявки.',
        canonical='/kontakty/', depth=1, dir='kontakty', file='index.html'),
    'politika-personalnyh-dannyh': dict(title='Политика обработки персональных данных — СтройАутсорс',
        desc='Политика ООО «ММ +» (бренд «СтройАутсорс») в отношении обработки персональных данных.',
        canonical='/politika-personalnyh-dannyh/', depth=1, dir='politika-personalnyh-dannyh', file='index.html', legal=True),
    'soglasie-klienta':    dict(title='Согласие клиента на обработку персональных данных — СтройАутсорс',
        desc='Текст согласия на обработку персональных данных при отправке заявки на сайте stroyautsors.ru.',
        canonical='/soglasie-klienta/', depth=1, dir='soglasie-klienta', file='index.html', legal=True),
    'soglasie-soiskatelya':dict(title='Согласие соискателя на обработку персональных данных — СтройАутсорс',
        desc='Текст согласия на обработку персональных данных при отклике на работу на сайте stroyautsors.ru.',
        canonical='/soglasie-soiskatelya/', depth=1, dir='soglasie-soiskatelya', file='index.html', legal=True),
    '404':                 dict(title='Страница не найдена — СтройАутсорс',
        desc='Запрошенная страница не существует.',
        canonical='', depth=0, file='404.html'),
}

def head(p, base):
    canon = ('<link rel="canonical" href="https://stroyautsors.ru' + p['canonical'] + '">'
             if p['canonical'] else '')
    return f'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{p['title']}</title>
<meta name="description" content="{p['desc']}">
{canon}
<meta property="og:type" content="website">
<meta property="og:title" content="{p['title']}">
<meta property="og:description" content="{p['desc']}">
<meta property="og:url" content="https://stroyautsors.ru{p['canonical']}">
<link rel="icon" href="{base}favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{base}assets/css/style.css">
</head>
<body>'''

def header(p, base):
    b = base
    return f'''<header class="site-header">
  <div class="container header-inner">
    <a class="logo" href="{b}" aria-label="СтройАутсорс — на главную">
      {LOGO_SVG.replace('width="30" height="35"', '')}
      <span class="logo__name">СтройАутсорс<small>РАЗНОРАБОЧИЕ · МОСКВА И МО</small></span>
    </a>
    <nav class="main-nav" id="siteNav" aria-label="Основная навигация">
      <a href="{b}raznorabochie-na-stroyku/">На стройку</a>
      <a href="{b}dlya-chastnyh-lic/">Частным лицам</a>
      <a href="{b}srochno/">Срочно</a>
      <a href="{b}kak-rabotaem/">Как работаем</a>
      <a href="{b}ceny/">Цены</a>
      <a href="{b}kontakty/">Контакты</a>
    </nav>
    <a class="header-phone" href="tel:+79860898560">+7 (986) 089-85-60</a>
    <button class="burger" aria-label="Открыть меню" aria-expanded="false"><span></span><span></span><span></span></button>
  </div>
</header>'''

def footer(p, base):
    b = base
    return f'''<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-brand">
        <a class="logo" href="{b}" aria-label="СтройАутсорс">
          {LOGO_SVG.replace('width="30" height="35"', '')}
          <span class="logo__name">СтройАутсорс</span>
        </a>
        <p>Разнорабочие для строек и частных подсобных работ в Москве и Московской области.</p>
      </div>
      <div>
        <h4>Услуги</h4>
        <ul>
          <li><a href="{b}raznorabochie-na-stroyku/">Рабочие на стройку</a></li>
          <li><a href="{b}dlya-chastnyh-lic/">Для частных лиц</a></li>
          <li><a href="{b}uborka-snega/">Уборка снега</a></li>
          <li><a href="{b}ceny/">Цены и расчёт</a></li>
        </ul>
      </div>
      <div>
        <h4>Компания</h4>
        <ul>
          <li><a href="{b}kak-rabotaem/">Как мы работаем</a></li>
          <li><a href="{b}srochno/">Срочно нужны рабочие</a></li>
          <li><a href="{b}kontakty/">Контакты</a></li>
          <li><a href="{b}politika-personalnyh-dannyh/">Политика персональных данных</a></li>
          <li><a href="{b}soglasie-klienta/">Согласие клиента</a></li>
          <li><a href="{b}soglasie-soiskatelya/">Согласие соискателя</a></li>
        </ul>
      </div>
      <div>
        <h4>Контакты</h4>
        <div class="footer-contacts">
          <a href="tel:+79860898560">+7 (986) 089-85-60</a>
          <a href="mailto:info@stroyautsors.ru">info@stroyautsors.ru</a>
          <span>Москва и Московская область</span>
        </div>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© 2026 ООО «ММ +» · Бренд «СтройАутсорс» · ИНН 9715531327 · ОГРН 1267700261498</span>
      <span class="reqs">127410, г. Москва, Алтуфьевское шоссе, д. 79А, стр. 3, помещ. 9/1/4</span>
    </div>
  </div>
</footer>
<script src="{b}assets/js/main.js" defer></script>
</body>
</html>'''

def build():
    os.makedirs(OUT, exist_ok=True)
    for key, p in PAGES.items():
        frag_path = os.path.join(SRC, key + '.html')
        with open(frag_path, encoding='utf-8') as f:
            body = f.read().strip()
        depth = p['depth']
        base = '../' * depth
        html = head(p, base) + '\n' + header(p, base) + '\n<main>\n' + body + '\n</main>\n' + footer(p, base)
        if p.get('dir'):
            outdir = os.path.join(OUT, p['dir'])
            os.makedirs(outdir, exist_ok=True)
            out = os.path.join(outdir, p['file'])
        else:
            out = os.path.join(OUT, p['file'])
        with open(out, 'w', encoding='utf-8') as f:
            f.write(html)
        print('built', os.path.relpath(out, OUT))

if __name__ == '__main__':
    build()
