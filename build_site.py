import json, os, pathlib

# 公開URL。GitHub Pages なら https://<ユーザー名>.github.io/<リポジトリ名>/ を設定する。
# 環境変数 SITE_URL でも上書きできる。未設定なら canonical / OGP の絶対URLは出力しない。
SITE_URL = os.environ.get('SITE_URL', '').rstrip('/')

ROOT = pathlib.Path(__file__).resolve().parent
DATA_PATH = ROOT / 'data' / 'events.json'
if not DATA_PATH.exists():          # 旧レイアウト（リポジトリ化前）との互換
    DATA_PATH = ROOT / 'events.json'
OUT_PATH = ROOT / 'index.html' if (ROOT / 'data').exists() else ROOT / 'anime-popup-events.html'

data = json.load(open(DATA_PATH, encoding='utf-8'))
payload = json.dumps(data, ensure_ascii=False, separators=(',', ':'))

TITLE = 'アニメ POP UP イベント情報 | 全国のポップアップストアまとめ'
DESC  = ('全国のアニメ・マンガ関連ポップアップストア／期間限定ショップの開催情報を'
         'まとめて掲載。開催中・開催予定を一覧・カレンダー・作品別で探せて、'
         '会場の地図もすぐ開けます。')

# --- 構造化データ（schema.org Event） ---
def jsonld(events):
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

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E"
           "%3Crect width='64' height='64' rx='14' fill='%237c8cff'/%3E"
           "%3Ctext x='32' y='45' font-size='36' text-anchor='middle'%3E%F0%9F%8E%AA%3C/text%3E%3C/svg%3E")

head_extra = f'''<link rel="icon" href="{FAVICON}">
<meta name="theme-color" content="#0e1016">
<meta property="og:type" content="website">
<meta property="og:site_name" content="ANIME POP UP TRACKER">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{DESC}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{TITLE}">
<meta name="twitter:description" content="{DESC}">'''
if SITE_URL:
    head_extra += f'''
<link rel="canonical" href="{SITE_URL}/">
<meta property="og:url" content="{SITE_URL}/">
<meta property="og:image" content="{SITE_URL}/og.png">
<meta name="twitter:image" content="{SITE_URL}/og.png">'''
head_extra += f'\n<script type="application/ld+json">{jsonld(data["events"])}</script>'

CSS = r'''
:root{
  --bg:#0e1016; --bg2:#151824; --card:#191d2b; --card-h:#1f2436;
  --line:#2a3047; --line2:#39415e;
  --tx:#e8eaf2; --tx2:#a5abc2; --tx3:#767d99;
  --ac:#7c8cff; --ac2:#a06bff;
  --live:#2fd07a; --soon:#f0b537; --done:#6b7291;
  --r:14px;
}
*{box-sizing:border-box;margin:0;padding:0}
body{
  background:var(--bg); color:var(--tx);
  font-family:"Hiragino Kaku Gothic ProN","Hiragino Sans","Noto Sans JP",-apple-system,BlinkMacSystemFont,"Segoe UI",Meiryo,sans-serif;
  line-height:1.65; -webkit-font-smoothing:antialiased;
}
a{color:inherit;text-decoration:none}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px}
[hidden]{display:none !important}

/* ---------- header ---------- */
header{
  background:
    radial-gradient(900px 420px at 12% -10%, rgba(124,140,255,.30), transparent 62%),
    radial-gradient(760px 380px at 88% 0%, rgba(160,107,255,.24), transparent 60%),
    var(--bg2);
  border-bottom:1px solid var(--line); padding:38px 0 0;
}
.brand{display:flex;align-items:center;gap:11px;margin-bottom:14px}
.logo{width:36px;height:36px;border-radius:10px;flex:none;
  background:linear-gradient(135deg,var(--ac),var(--ac2));display:grid;place-items:center;font-size:19px}
.brand b{font-size:14px;letter-spacing:.14em;color:var(--tx2);font-weight:600}
h1{font-size:clamp(23px,4.2vw,36px);line-height:1.28;letter-spacing:-.01em;font-weight:800}
h1 em{font-style:normal;background:linear-gradient(90deg,#9fb0ff,#c79bff);
  -webkit-background-clip:text;background-clip:text;color:transparent}
.lede{color:var(--tx2);margin-top:11px;font-size:14.5px;max-width:640px}
.upd{margin-top:12px;font-size:12.5px;color:var(--tx3);display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.dot{width:6px;height:6px;border-radius:50%;background:var(--live);box-shadow:0 0 0 3px rgba(47,208,122,.16)}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:22px}
.stat{background:rgba(255,255,255,.045);border:1px solid var(--line);border-radius:12px;padding:12px 15px}
.stat .n{font-size:25px;font-weight:800;line-height:1.15;font-variant-numeric:tabular-nums}
.stat .l{font-size:11.5px;color:var(--tx3);letter-spacing:.05em;margin-top:2px}
.stat.live .n{color:var(--live)} .stat.soon .n{color:var(--soon)} .stat.done .n{color:var(--done)}

/* ---------- view nav ---------- */
.nav{display:flex;gap:2px;margin-top:26px}
.nav a{
  padding:11px 20px;font-size:14px;font-weight:700;color:var(--tx3);
  border-bottom:2px solid transparent;transition:.15s;display:flex;align-items:center;gap:7px;
}
.nav a:hover{color:var(--tx2)}
.nav a.on{color:var(--tx);border-bottom-color:var(--ac)}
.nav .ic{font-size:15px;opacity:.85}

/* ---------- controls ---------- */
.ctl{position:sticky;top:0;z-index:20;background:rgba(14,16,22,.93);backdrop-filter:blur(12px);border-bottom:1px solid var(--line)}
.ctl-in{padding:13px 0;display:flex;gap:10px;flex-wrap:wrap;align-items:center}
.tabs{display:flex;gap:5px;background:var(--bg2);border:1px solid var(--line);border-radius:11px;padding:4px}
.tab{border:0;background:transparent;color:var(--tx2);cursor:pointer;font:inherit;font-size:13px;font-weight:600;
  padding:7px 14px;border-radius:8px;white-space:nowrap;transition:.15s}
.tab:hover{color:var(--tx)}
.tab[aria-selected="true"]{background:linear-gradient(135deg,var(--ac),var(--ac2));color:#fff}
.field{background:var(--bg2);border:1px solid var(--line);border-radius:11px;color:var(--tx);
  font:inherit;font-size:13.5px;padding:9px 13px;outline:none;transition:.15s}
.field:focus{border-color:var(--ac);box-shadow:0 0 0 3px rgba(124,140,255,.16)}
#q{flex:1;min-width:190px}
select.field{cursor:pointer;padding-right:30px;appearance:none;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='10' height='7'><path d='M1 1l4 4 4-4' stroke='%23a5abc2' stroke-width='1.6' fill='none' stroke-linecap='round'/></svg>");
  background-repeat:no-repeat;background-position:right 11px center}
.count{font-size:12.5px;color:var(--tx3);margin-left:auto;white-space:nowrap}

main{padding:26px 0 60px;min-height:50vh}

/* ---------- cards ---------- */
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--r);
  padding:17px 18px 15px;display:flex;flex-direction:column;gap:10px;transition:.16s;position:relative;overflow:hidden}
.card::before{content:"";position:absolute;inset:0 auto 0 0;width:3px;background:var(--done);opacity:.85}
.card.s-live::before{background:linear-gradient(180deg,var(--live),#1fa85f)}
.card.s-soon::before{background:linear-gradient(180deg,var(--soon),#d99420)}
.card:hover{background:var(--card-h);border-color:var(--line2);transform:translateY(-2px)}
.card.s-done{opacity:.62} .card.s-done:hover{opacity:1}
.row1{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.badge{font-size:11px;font-weight:700;padding:3px 9px;border-radius:99px;letter-spacing:.03em;white-space:nowrap}
.b-live{background:rgba(47,208,122,.15);color:var(--live);border:1px solid rgba(47,208,122,.35)}
.b-soon{background:rgba(240,181,55,.14);color:var(--soon);border:1px solid rgba(240,181,55,.32)}
.b-done{background:rgba(107,114,145,.16);color:var(--done);border:1px solid rgba(107,114,145,.3)}
.work{font-size:11.5px;color:var(--ac);font-weight:700;letter-spacing:.02em}
.work:hover{text-decoration:underline}
.ttl{font-size:15.5px;font-weight:700;line-height:1.45;letter-spacing:-.005em;display:block;margin-top:2px}
.ttl:hover{color:#c7cfff}
.work{display:inline-block}
.meta{display:flex;flex-direction:column;gap:5px;font-size:12.8px;color:var(--tx2);margin-top:auto}
.meta div{display:flex;gap:8px;align-items:flex-start}
.ico{flex:none;width:14px;text-align:center;opacity:.6;font-size:12px;line-height:1.6}
.date{font-variant-numeric:tabular-nums;color:var(--tx)}
.maplinks{display:flex;gap:5px;flex-wrap:wrap}
.maplink{font-size:11.5px;font-weight:600;color:#9fb0ff;background:rgba(124,140,255,.10);
  border:1px solid rgba(124,140,255,.28);padding:2px 8px;border-radius:7px;line-height:1.6;
  transition:.14s;white-space:nowrap}
.maplink:hover{background:rgba(124,140,255,.22);border-color:var(--ac);color:#c7cfff}
.tags{display:flex;gap:5px;flex-wrap:wrap;margin-top:2px}
.tag{font-size:10.5px;color:var(--tx3);background:rgba(255,255,255,.05);border:1px solid var(--line);padding:2px 7px;border-radius:6px}
.left{font-size:11px;color:var(--soon);font-weight:700}
.empty{text-align:center;padding:70px 20px;color:var(--tx3)}
.empty b{display:block;font-size:16px;color:var(--tx2);margin-bottom:6px}

/* ---------- calendar ---------- */
.cal-head{display:flex;align-items:center;gap:12px;margin-bottom:16px;flex-wrap:wrap}
.cal-title{font-size:20px;font-weight:800;font-variant-numeric:tabular-nums;min-width:150px}
.nav-btn{background:var(--bg2);border:1px solid var(--line);color:var(--tx2);cursor:pointer;
  font:inherit;font-size:15px;width:34px;height:34px;border-radius:9px;transition:.15s;line-height:1}
.nav-btn:hover{background:var(--card-h);color:var(--tx);border-color:var(--line2)}
.today-btn{width:auto;padding:0 14px;font-size:12.5px;font-weight:600}
.legend{margin-left:auto;display:flex;gap:14px;font-size:11.5px;color:var(--tx3);flex-wrap:wrap}
.legend span{display:flex;align-items:center;gap:5px}
.sw{width:10px;height:10px;border-radius:3px}

.cal{border:1px solid var(--line);border-radius:var(--r);overflow:hidden;background:var(--bg2)}
.cal-dow{display:grid;grid-template-columns:repeat(7,1fr);background:rgba(255,255,255,.03);border-bottom:1px solid var(--line)}
.cal-dow div{padding:8px 6px;text-align:center;font-size:11.5px;font-weight:700;color:var(--tx3);letter-spacing:.05em}
.cal-dow div:first-child{color:#ff8a8a} .cal-dow div:last-child{color:#8ab4ff}
.cal-body{display:grid;grid-template-columns:repeat(7,1fr)}
.day{min-height:112px;min-width:0;overflow:hidden;border-right:1px solid var(--line);border-bottom:1px solid var(--line);
  padding:6px 6px 7px;cursor:pointer;transition:.13s;position:relative;background:var(--bg2);text-align:left;
  border-top:0;border-left:0;font:inherit;color:inherit;display:block;width:100%}
.day:nth-child(7n){border-right:0}
.day:hover{background:var(--card-h)}
.day.out{background:rgba(0,0,0,.22);opacity:.5}
.day.today{background:rgba(124,140,255,.10)}
.day.sel{background:rgba(124,140,255,.20);box-shadow:inset 0 0 0 2px var(--ac)}
.dnum{font-size:12px;font-weight:700;color:var(--tx2);font-variant-numeric:tabular-nums;margin-bottom:4px;display:flex;align-items:center;gap:5px}
.day.today .dnum{color:var(--ac)}
.day.sun .dnum{color:#ff8a8a} .day.sat .dnum{color:#8ab4ff}
.pill{font-size:10px;line-height:1.5;padding:1.5px 5px;border-radius:4px;margin-bottom:2px;max-width:100%;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-weight:600;display:block}
.p-live{background:rgba(47,208,122,.20);color:#8ef0bb;border-left:2px solid var(--live)}
.p-soon{background:rgba(240,181,55,.17);color:#f7d68b;border-left:2px solid var(--soon)}
.p-done{background:rgba(107,114,145,.18);color:#a9afc7;border-left:2px solid var(--done)}
.more{font-size:9.5px;color:var(--tx3);padding-left:3px;font-weight:700}
.daypanel{margin-top:22px}
.daypanel h3{font-size:16px;font-weight:800;margin-bottom:12px;display:flex;align-items:center;gap:9px}
.daypanel h3 small{font-size:12px;color:var(--tx3);font-weight:600}

/* ---------- works ---------- */
.wgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:12px}
.wcard{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:15px 16px;
  transition:.16s;display:flex;flex-direction:column;gap:7px}
.wcard:hover{background:var(--card-h);border-color:var(--line2);transform:translateY(-2px)}
.wname{font-size:15px;font-weight:700;line-height:1.4}
.wsub{font-size:12px;color:var(--tx3);display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.wsub .n{color:var(--ac);font-weight:700}
.back{display:inline-flex;align-items:center;gap:6px;font-size:13px;color:var(--tx2);margin-bottom:14px;font-weight:600}
.back:hover{color:var(--tx)}
.whead{margin-bottom:20px;padding-bottom:18px;border-bottom:1px solid var(--line)}
.whead h2{font-size:clamp(21px,3.4vw,30px);font-weight:800;line-height:1.3}
.whead .wsub{margin-top:8px;font-size:13px}

footer{border-top:1px solid var(--line);padding:26px 0 40px;color:var(--tx3);font-size:12.5px}
footer a{color:var(--tx2);text-decoration:underline}

@media(max-width:820px){
  .stats{grid-template-columns:repeat(2,1fr)}
  .count{width:100%;margin-left:0}
  .tabs{width:100%;overflow-x:auto}
  .nav{overflow-x:auto} .nav a{padding:11px 14px;font-size:13px;white-space:nowrap}
  .day{min-height:74px;padding:4px 3px}
  .pill{font-size:0;padding:0;height:5px;margin-bottom:2px;border-radius:2px;border-left:0}
  .more{display:none}
  .legend{width:100%;margin-left:0}
}
'''

JS = r'''
const DATA = __PAYLOAD__;
const TODAY = new Date(); TODAY.setHours(0,0,0,0);
const ymd = s => { const [y,m,d]=s.split('-').map(Number); return new Date(y,m-1,d); };
const key = d => `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
const fmt = s => { const d=ymd(s); return `${d.getFullYear()}.${String(d.getMonth()+1).padStart(2,'0')}.${String(d.getDate()).padStart(2,'0')}`; };
const stat = e => { const s=ymd(e.start), t=ymd(e.end); return TODAY<s?'soon':TODAY>t?'done':'live'; };
const days = a => Math.round((a-TODAY)/86400000);
const esc = s => String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const LB = {live:'開催中', soon:'開催予定', done:'終了'};

const evs = DATA.events.map(e=>({...e, st:stat(e)}));

/* ---- header stats ---- */
document.getElementById('updated').textContent = DATA.meta.updated.replace(/-/g,'.');
document.getElementById('total').textContent = `全 ${evs.length} 件を掲載`;
for (const k of ['live','soon','done'])
  document.getElementById('n-'+k).textContent = evs.filter(e=>e.st===k).length;
document.getElementById('n-work').textContent = new Set(evs.map(e=>e.work)).size;

/* ---- region select ---- */
const RO = ['北海道','東北','関東','中部','関西','中国','四国','九州・沖縄','全国'];
const sel = document.getElementById('region');
[...new Set(evs.map(e=>e.region))].sort((a,b)=>RO.indexOf(a)-RO.indexOf(b))
  .forEach(r=>{ const o=document.createElement('option'); o.value=r; o.textContent='地域：'+r; sel.appendChild(o); });

/* ---- card ---- */
const mapURL = q => 'https://www.google.com/maps/search/?api=1&query=' + encodeURIComponent(q);
function mapRow(e){
  const m = e.map || [];
  if (!m.length) return '';
  const chips = m.length===1
    ? [`<a class="maplink" href="${mapURL(m[0].q)}" target="_blank" rel="noopener">地図で見る ↗</a>`]
    : m.map(x=>`<a class="maplink" href="${mapURL(x.q)}" target="_blank" rel="noopener">${esc(x.n)} ↗</a>`);
  return `<div><span class="ico">🗺</span><span class="maplinks">${chips.join('')}</span></div>`;
}
function cardHTML(e, opt={}){
  let note='';
  if (e.st==='live'){ const d=days(ymd(e.end)); note = d<=0?'<span class="left">本日最終日</span>':`<span class="left">残り ${d} 日</span>`; }
  if (e.st==='soon'){ const d=days(ymd(e.start)); note = `<span class="left">${d} 日後に開始</span>`; }
  const workLine = opt.hideWork ? '' :
    `<a class="work" href="#/work/${encodeURIComponent(e.work)}" onclick="event.stopPropagation()">${esc(e.work)} ›</a>`;
  return `<div class="card s-${e.st}">
    <div class="row1"><span class="badge b-${e.st}">${LB[e.st]}</span>${note}</div>
    <div>${workLine}<a class="ttl" href="${esc(e.url)}" target="_blank" rel="noopener">${esc(e.title)}</a></div>
    <div class="meta">
      <div><span class="ico">📅</span><span class="date">${fmt(e.start)} – ${fmt(e.end)}</span></div>
      <div><span class="ico">📍</span><span>${esc(e.venue)}</span></div>
      <div><span class="ico">🗾</span><span>${esc(e.pref)}・${esc(e.region)}</span></div>
      ${mapRow(e)}
    </div>
    <div class="tags">${e.tags.map(t=>`<span class="tag">${esc(t)}</span>`).join('')}</div>
  </div>`;
}

/* ================= LIST VIEW ================= */
let L = {s:'live', region:'', q:'', sort:'start'};
function renderList(){
  let list = evs.filter(e=>
    (L.s==='all' || e.st===L.s) &&
    (!L.region || e.region===L.region) &&
    (!L.q || (e.work+' '+e.title+' '+e.venue+' '+e.pref+' '+e.tags.join(' ')).toLowerCase().includes(L.q))
  );
  const cmp = {
    start:(a,b)=>a.start.localeCompare(b.start)||a.end.localeCompare(b.end),
    end:(a,b)=>a.end.localeCompare(b.end)||a.start.localeCompare(b.start),
    work:(a,b)=>a.work.localeCompare(b.work,'ja')
  }[L.sort];
  list.sort(cmp);
  if (L.s==='done' && L.sort==='start') list.reverse();
  document.getElementById('count').textContent = `${list.length} 件表示中`;
  document.getElementById('empty').hidden = list.length>0;
  document.getElementById('grid').innerHTML = list.map(e=>cardHTML(e)).join('');
}
document.getElementById('tabs').addEventListener('click', ev=>{
  const b = ev.target.closest('.tab'); if(!b) return;
  [...document.querySelectorAll('.tab')].forEach(t=>t.setAttribute('aria-selected', t===b));
  L.s = b.dataset.s; renderList();
});
sel.addEventListener('change', e=>{ L.region=e.target.value; renderList(); });
document.getElementById('sort').addEventListener('change', e=>{ L.sort=e.target.value; renderList(); });
document.getElementById('q').addEventListener('input', e=>{ L.q=e.target.value.trim().toLowerCase(); renderList(); });

/* ================= CALENDAR VIEW ================= */
const DOW = ['日','月','火','水','木','金','土'];
let cal = new Date(TODAY.getFullYear(), TODAY.getMonth(), 1);
let selDay = key(TODAY);

const byDay = new Map();
for (const e of evs){
  for (let d=ymd(e.start); d<=ymd(e.end); d.setDate(d.getDate()+1)){
    const k = key(d);
    if(!byDay.has(k)) byDay.set(k, []);
    byDay.get(k).push(e);
  }
}
for (const arr of byDay.values()) arr.sort((a,b)=>a.start.localeCompare(b.start));

function renderCal(){
  document.getElementById('cal-title').textContent = `${cal.getFullYear()}年 ${cal.getMonth()+1}月`;
  const first = new Date(cal.getFullYear(), cal.getMonth(), 1);
  const start = new Date(first); start.setDate(1 - first.getDay());
  const cells = [];
  for (let i=0;i<42;i++){
    const d = new Date(start); d.setDate(start.getDate()+i);
    const k = key(d), list = byDay.get(k) || [];
    const cls = ['day'];
    if (d.getMonth()!==cal.getMonth()) cls.push('out');
    if (k===key(TODAY)) cls.push('today');
    if (k===selDay) cls.push('sel');
    if (d.getDay()===0) cls.push('sun');
    if (d.getDay()===6) cls.push('sat');
    const pills = list.slice(0,3).map(e=>
      `<span class="pill p-${e.st}" title="${esc(e.title)}">${esc(e.work)}</span>`).join('');
    const more = list.length>3 ? `<span class="more">+${list.length-3} 件</span>` : '';
    cells.push(`<button class="${cls.join(' ')}" data-d="${k}" type="button">
      <span class="dnum">${d.getDate()}</span>${pills}${more}</button>`);
  }
  document.getElementById('cal-body').innerHTML = cells.join('');
  renderDayPanel();
}
function renderDayPanel(){
  const list = (byDay.get(selDay) || []).slice();
  const d = ymd(selDay);
  document.getElementById('day-title').innerHTML =
    `${d.getFullYear()}年${d.getMonth()+1}月${d.getDate()}日（${DOW[d.getDay()]}）<small>この日に開催しているイベント ${list.length} 件</small>`;
  document.getElementById('day-grid').innerHTML = list.length
    ? list.map(e=>cardHTML(e)).join('')
    : '<div class="empty"><b>この日は開催イベントがありません</b>カレンダーの色付きの日を選んでください。</div>';
}
document.getElementById('cal-body').addEventListener('click', ev=>{
  const b = ev.target.closest('.day'); if(!b) return;
  selDay = b.dataset.d;
  const d = ymd(selDay);
  if (d.getMonth()!==cal.getMonth()||d.getFullYear()!==cal.getFullYear()) cal = new Date(d.getFullYear(), d.getMonth(), 1);
  renderCal();
});
document.getElementById('prev').onclick = ()=>{ cal.setMonth(cal.getMonth()-1); renderCal(); };
document.getElementById('next').onclick = ()=>{ cal.setMonth(cal.getMonth()+1); renderCal(); };
document.getElementById('today-btn').onclick = ()=>{
  cal = new Date(TODAY.getFullYear(), TODAY.getMonth(), 1); selDay = key(TODAY); renderCal(); };

/* ================= WORKS VIEW ================= */
const works = [...new Set(evs.map(e=>e.work))].map(w=>{
  const list = evs.filter(e=>e.work===w).sort((a,b)=>a.start.localeCompare(b.start));
  const live = list.filter(e=>e.st==='live').length;
  const soon = list.filter(e=>e.st==='soon').length;
  const upcoming = list.find(e=>e.st!=='done');
  return {w, list, live, soon, upcoming};
});
function renderWorks(){
  const q = document.getElementById('wq').value.trim().toLowerCase();
  const mode = document.getElementById('wsort').value;
  let ws = works.filter(x=>!q || x.w.toLowerCase().includes(q));
  ws.sort(mode==='name'
    ? (a,b)=>a.w.localeCompare(b.w,'ja')
    : (a,b)=>(b.live+b.soon)-(a.live+a.soon) || b.list.length-a.list.length || a.w.localeCompare(b.w,'ja'));
  document.getElementById('wcount').textContent = `${ws.length} 作品`;
  document.getElementById('wgrid').innerHTML = ws.map(x=>{
    const st = x.live ? `<span class="badge b-live">開催中 ${x.live}</span>`
             : x.soon ? `<span class="badge b-soon">予定 ${x.soon}</span>`
             : `<span class="badge b-done">終了</span>`;
    const nxt = x.upcoming ? `${fmt(x.upcoming.start)} 〜` : `最終開催 ${fmt(x.list[x.list.length-1].end)}`;
    return `<a class="wcard" href="#/work/${encodeURIComponent(x.w)}">
      <div class="wname">${esc(x.w)}</div>
      <div class="wsub">${st}<span><span class="n">${x.list.length}</span> 件の開催</span></div>
      <div class="wsub"><span class="ico">📅</span><span class="date">${nxt}</span></div>
    </a>`;
  }).join('');
}
document.getElementById('wq').addEventListener('input', renderWorks);
document.getElementById('wsort').addEventListener('change', renderWorks);

function renderWorkDetail(name){
  const x = works.find(v=>v.w===name);
  const el = document.getElementById('wdetail');
  if(!x){ el.innerHTML = '<div class="empty"><b>作品が見つかりません</b></div>'; return; }
  const list = x.list.slice().sort((a,b)=>{
    const o={live:0,soon:1,done:2};
    return o[a.st]-o[b.st] || a.start.localeCompare(b.start);
  });
  const prefs = [...new Set(x.list.map(e=>e.pref))].join('・');
  el.innerHTML = `
    <a class="back" href="#/works">‹ 作品一覧にもどる</a>
    <div class="whead">
      <h2>${esc(x.w)}</h2>
      <div class="wsub">
        <span><span class="n">${x.list.length}</span> 件の開催情報</span><span>·</span>
        <span>開催中 ${x.live} 件／予定 ${x.soon} 件</span><span>·</span>
        <span>${esc(prefs)}</span>
      </div>
    </div>
    <div class="grid">${list.map(e=>cardHTML(e,{hideWork:true})).join('')}</div>`;
}

/* ================= ROUTER ================= */
const VIEWS = ['list','calendar','works','wdetail'];
function route(){
  const h = location.hash.replace(/^#\/?/, '') || 'list';
  const [v, arg] = [h.split('/')[0], decodeURIComponent(h.split('/').slice(1).join('/')||'')];
  let view = VIEWS.includes(v) ? v : 'list';
  if (v==='work'){ view='wdetail'; renderWorkDetail(arg); }
  else if (view==='works') renderWorks();
  else if (view==='calendar') renderCal();
  else renderList();
  VIEWS.forEach(x=>document.getElementById('v-'+x).hidden = (x!==view));
  document.getElementById('ctl-list').hidden = view!=='list';
  document.getElementById('ctl-works').hidden = view!=='works';
  document.getElementById('ctl').hidden = (view!=='list' && view!=='works');
  const navKey = view==='wdetail' ? 'works' : view;
  document.querySelectorAll('.nav a').forEach(a=>a.classList.toggle('on', a.dataset.v===navKey));
  window.scrollTo({top:0});
}
window.addEventListener('hashchange', route);
route();
'''

HTML = '''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<meta name="description" content="__DESC__">
__HEAD_EXTRA__
<style>__CSS__</style>
</head>
<body>
<header>
  <div class="wrap">
    <div class="brand"><div class="logo">🎪</div><b>ANIME POP UP TRACKER</b></div>
    <h1>全国の<em>アニメ POP UP</em>イベントを、<br>ひとつの画面で。</h1>
    <p class="lede">アニメ・マンガ関連のポップアップストア／期間限定ショップの開催情報をまとめました。一覧・カレンダー・作品別で探せます。</p>
    <p class="upd"><span class="dot"></span><span>最終更新 <span id="updated"></span></span><span>·</span><span id="total"></span></p>
    <div class="stats">
      <div class="stat live"><div class="n" id="n-live">0</div><div class="l">開催中</div></div>
      <div class="stat soon"><div class="n" id="n-soon">0</div><div class="l">開催予定</div></div>
      <div class="stat done"><div class="n" id="n-done">0</div><div class="l">終了</div></div>
      <div class="stat"><div class="n" id="n-work">0</div><div class="l">掲載作品数</div></div>
    </div>
    <nav class="nav">
      <a href="#/list" data-v="list"><span class="ic">📋</span>一覧</a>
      <a href="#/calendar" data-v="calendar"><span class="ic">🗓</span>カレンダー</a>
      <a href="#/works" data-v="works"><span class="ic">✨</span>作品から探す</a>
    </nav>
  </div>
</header>

<div class="ctl" id="ctl">
  <div class="wrap ctl-in" id="ctl-list">
    <div class="tabs" role="tablist" id="tabs">
      <button class="tab" role="tab" data-s="live" aria-selected="true">開催中</button>
      <button class="tab" role="tab" data-s="soon" aria-selected="false">開催予定</button>
      <button class="tab" role="tab" data-s="done" aria-selected="false">終了</button>
      <button class="tab" role="tab" data-s="all" aria-selected="false">すべて</button>
    </div>
    <select class="field" id="region"><option value="">地域：すべて</option></select>
    <select class="field" id="sort">
      <option value="start">開始日が近い順</option>
      <option value="end">終了日が近い順</option>
      <option value="work">作品名順</option>
    </select>
    <input class="field" id="q" type="search" placeholder="作品名・会場名で検索（例：ハイキュー、池袋）">
    <span class="count" id="count"></span>
  </div>
  <div class="wrap ctl-in" id="ctl-works" hidden>
    <select class="field" id="wsort">
      <option value="active">開催中・予定が多い順</option>
      <option value="name">作品名順（五十音）</option>
    </select>
    <input class="field" id="wq" type="search" placeholder="作品名で検索">
    <span class="count" id="wcount"></span>
  </div>
</div>

<main class="wrap">
  <section id="v-list">
    <div class="grid" id="grid"></div>
    <div class="empty" id="empty" hidden><b>該当するイベントがありません</b>絞り込み条件を変えてお試しください。</div>
  </section>

  <section id="v-calendar" hidden>
    <div class="cal-head">
      <button class="nav-btn" id="prev" type="button" aria-label="前の月">‹</button>
      <div class="cal-title" id="cal-title"></div>
      <button class="nav-btn" id="next" type="button" aria-label="次の月">›</button>
      <button class="nav-btn today-btn" id="today-btn" type="button">今日</button>
      <div class="legend">
        <span><i class="sw" style="background:#2fd07a"></i>開催中</span>
        <span><i class="sw" style="background:#f0b537"></i>開催予定</span>
        <span><i class="sw" style="background:#6b7291"></i>終了</span>
      </div>
    </div>
    <div class="cal">
      <div class="cal-dow"><div>日</div><div>月</div><div>火</div><div>水</div><div>木</div><div>金</div><div>土</div></div>
      <div class="cal-body" id="cal-body"></div>
    </div>
    <div class="daypanel">
      <h3 id="day-title"></h3>
      <div class="grid" id="day-grid"></div>
    </div>
  </section>

  <section id="v-works" hidden><div class="wgrid" id="wgrid"></div></section>
  <section id="v-wdetail" hidden><div id="wdetail"></div></section>
</main>

<footer class="wrap">
  <p>掲載情報は各公式サイト・コラボカフェ等の公開情報をもとにまとめています。最新の開催状況・入場方法は必ず公式サイトをご確認ください。</p>
  <p style="margin-top:8px">出典：<a href="https://collabo-cafe.com/events/category/pop-up-store/" target="_blank" rel="noopener">コラボカフェ</a> ／ 各作品公式サイト</p>
</footer>

<script>__JS__</script>
</body>
</html>
'''

out = (HTML.replace('__CSS__', CSS)
           .replace('__JS__', JS.replace('__PAYLOAD__', payload))
           .replace('__TITLE__', TITLE)
           .replace('__DESC__', DESC)
           .replace('__HEAD_EXTRA__', head_extra))
OUT_PATH.write_text(out, encoding='utf-8')
print(f'{OUT_PATH.name}: {len(out):,} bytes / {len(data["events"])} events / SITE_URL={SITE_URL or "(未設定)"}')

# --- sitemap.xml / robots.txt（SITE_URL が設定されているときだけ出力）---
if SITE_URL:
    lastmod = data['meta']['updated']
    (ROOT / 'sitemap.xml').write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f'  <url><loc>{SITE_URL}/</loc><lastmod>{lastmod}</lastmod>'
        '<changefreq>weekly</changefreq><priority>1.0</priority></url>\n'
        '</urlset>\n', encoding='utf-8')
    (ROOT / 'robots.txt').write_text(
        f'User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n', encoding='utf-8')
    print('sitemap.xml / robots.txt written')

