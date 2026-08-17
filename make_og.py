"""OGP画像（1200x630）を生成する。Playwright で HTML をレンダリングして og.png を出力。"""
import pathlib, json
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent
d = json.load(open(ROOT/'data'/'events.json', encoding='utf-8'))
n = len(d['events'])
works = len({e['work'] for e in d['events']})

HTML = f"""<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1200px;height:630px;overflow:hidden;
  font-family:"Noto Sans CJK JP","Noto Sans JP",sans-serif;color:#e8eaf2;
  background:radial-gradient(760px 520px at 8% -18%,rgba(124,140,255,.42),transparent 62%),
             radial-gradient(700px 480px at 96% 4%,rgba(160,107,255,.34),transparent 60%),#0e1016;
  padding:74px 78px;display:flex;flex-direction:column;justify-content:space-between}}
.brand{{display:flex;align-items:center;gap:16px}}
.logo{{width:60px;height:60px;border-radius:17px;background:linear-gradient(135deg,#7c8cff,#a06bff);
  display:flex;align-items:center;justify-content:center;font-size:32px}}
.brand b{{font-size:20px;letter-spacing:.20em;color:#a5abc2;font-weight:700}}
h1{{font-size:76px;line-height:1.24;font-weight:900;letter-spacing:-.02em}}
h1 em{{font-style:normal;background:linear-gradient(90deg,#9fb0ff,#c79bff);
  -webkit-background-clip:text;background-clip:text;color:transparent}}
.row{{display:flex;gap:14px;align-items:center}}
.chip{{background:rgba(255,255,255,.07);border:1px solid #2a3047;border-radius:13px;
  padding:13px 24px;font-size:23px;font-weight:700;color:#a5abc2}}
.chip b{{color:#e8eaf2;font-size:27px}}
.chip.g b{{color:#2fd07a}}
</style></head><body>
<div class="brand"><div class="logo">🎪</div><b>ANIME POP UP TRACKER</b></div>
<h1>全国の<em>アニメ POP UP</em><br>イベントを、ひとつの画面で。</h1>
<div class="row">
  <div class="chip g"><b>{n}</b> 件のイベント</div>
  <div class="chip"><b>{works}</b> 作品</div>
  <div class="chip">一覧 · カレンダー · 作品別 · 地図</div>
</div>
</body></html>"""

(ROOT/'.og.tmp.html').write_text(HTML, encoding='utf-8')
with sync_playwright() as pw:
    b = pw.chromium.launch()
    p = b.new_page(viewport={"width":1200,"height":630})
    p.goto((ROOT/'.og.tmp.html').as_uri()); p.wait_for_timeout(400)
    p.screenshot(path=str(ROOT/'og.png'))
    b.close()
(ROOT/'.og.tmp.html').unlink()
print('og.png generated:', (ROOT/'og.png').stat().st_size, 'bytes')
