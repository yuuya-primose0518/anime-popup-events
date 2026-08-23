"""公開用の _site/ を組み立てるスクリプト。

サイト本体はデータを持たない静的ファイルになった:

    index.html          ← 骨組み。手で編集してよい
    assets/style.css    ← 見た目
    assets/app.js       ← data/events.json を実行時に fetch して描画
    data/events.json    ← データ本体。イベントの更新はこのファイルだけ差し替えればよい

この4つをそのまま置くだけでサイトは動く。したがってこのスクリプトの役割は
「検索エンジン向けの味付け」だけ:

  1. index.html の <!-- BUILD:JSONLD:START --> 〜 END の間に
     schema.org（ItemList + Event）の JSON-LD を差し込む
  2. sitemap.xml / robots.txt を生成する
  3. 以上をまとめて _site/ に配置する

**リポジトリ内のファイルは書き換えない。** 生成物はすべて _site/ の下に出る
（_site/ は .gitignore 済み）。そのため events.json を更新しても index.html の
差分は発生しない。

使い方:

    python3 build_site.py                      # _site/ を作る
    SITE_URL=https://example.github.io/repo python3 build_site.py

ローカル確認:

    python3 -m http.server 8000                # リポジトリ直下をそのまま（JSON-LDなし）
    python3 build_site.py && python3 -m http.server -d _site 8000   # 公開物と同じ状態

    ※ app.js が fetch を使うので index.html を file:// で直接開くと動かない。
      必ずHTTPサーバ経由で開くこと。
"""
import json, os, pathlib, re, shutil

# 公開URL。GitHub Actions では Pages の実URLが SITE_URL で渡ってくる。
DEFAULT_SITE_URL = 'https://yuuya-primose0518.github.io/anime-popup-events'
SITE_URL = (os.environ.get('SITE_URL') or DEFAULT_SITE_URL).rstrip('/')

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / '_site'
DATA_PATH = ROOT / 'data' / 'events.json'

TITLE = 'アニメ POP UP イベント情報 | 全国のポップアップストアまとめ'

MARK_START = '<!-- BUILD:JSONLD:START -->'
MARK_END   = '<!-- BUILD:JSONLD:END -->'

data = json.load(open(DATA_PATH, encoding='utf-8'))
events = data['events']


def jsonld(events):
    """schema.org の ItemList + Event。開始日順に並べる。"""
    items = []
    for i, e in enumerate(sorted(events, key=lambda x: x['start']), 1):
        items.append({
            "@type": "ListItem", "position": i,
            "item": {
                "@type": "Event", "name": e['title'],
                "startDate": e['start'], "endDate": e['end'],
                "eventStatus": "https://schema.org/EventScheduled",
                "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
                "location": {"@type": "Place", "name": e['venue'],
                             "address": {"@type": "PostalAddress",
                                         "addressRegion": e['pref'], "addressCountry": "JP"}},
                "url": e['url'],
                "about": e['work'],
            }})
    return json.dumps({"@context": "https://schema.org", "@type": "ItemList",
                       "name": TITLE, "numberOfItems": len(items), "itemListElement": items},
                      ensure_ascii=False, separators=(',', ':'))


# --- _site/ を作り直す ---
if OUT.exists():
    shutil.rmtree(OUT)
(OUT / 'assets').mkdir(parents=True)
(OUT / 'data').mkdir(parents=True)

# index.html に JSON-LD を差し込んで _site/ へ
html = (ROOT / 'index.html').read_text(encoding='utf-8')
if MARK_START not in html or MARK_END not in html:
    raise SystemExit(f'index.html に {MARK_START} / {MARK_END} が見つかりません。'
                     ' マーカーを消してしまった場合は <head> 内に復元してください。')
block = (f'{MARK_START}\n'
         f'<script type="application/ld+json">{jsonld(events)}</script>\n'
         f'{MARK_END}')
html = re.sub(re.escape(MARK_START) + r'.*?' + re.escape(MARK_END),
              lambda _: block, html, flags=re.S)
# SITE_URL が既定値と違う場合（別リポジトリ／独自ドメイン）は絶対URLを差し替える
if SITE_URL != DEFAULT_SITE_URL:
    html = html.replace(DEFAULT_SITE_URL, SITE_URL)
(OUT / 'index.html').write_text(html, encoding='utf-8')

# 静的ファイルをコピー
for name in ('style.css', 'app.js'):
    shutil.copy2(ROOT / 'assets' / name, OUT / 'assets' / name)
shutil.copy2(DATA_PATH, OUT / 'data' / 'events.json')
if (ROOT / 'og.png').exists():
    shutil.copy2(ROOT / 'og.png', OUT / 'og.png')

# sitemap.xml / robots.txt
(OUT / 'sitemap.xml').write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    f'  <url><loc>{SITE_URL}/</loc><lastmod>{data["meta"]["updated"]}</lastmod>'
    '<changefreq>weekly</changefreq><priority>1.0</priority></url>\n'
    '</urlset>\n', encoding='utf-8')
(OUT / 'robots.txt').write_text(
    f'User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n', encoding='utf-8')

# GitHub Pages が Jekyll 処理をしないように
(OUT / '.nojekyll').write_text('', encoding='utf-8')

print(f'_site/ を生成しました: {len(events)} 件 / SITE_URL={SITE_URL}')
print(f'  index.html {(OUT / "index.html").stat().st_size:,} bytes'
      f'（うち JSON-LD {len(jsonld(events)):,} bytes）')
