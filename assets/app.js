/* =======================================================================
   アニメ POP UP イベント情報サイト — 描画スクリプト

   データは HTML に埋め込まない。実行時に data/events.json を fetch して描画する。
   イベント情報の更新は data/events.json を差し替えるだけでよい。

   注意: fetch を使うため file:// で直接開くと動かない。
        ローカル確認は `python3 -m http.server 8000` などHTTP経由で。
   ======================================================================= */
'use strict';

const DATA_URL = 'data/events.json';

function bootFail(msg){
  const el = document.getElementById('loading');
  if (el) el.remove();
  const box = document.getElementById('loaderr');
  if (box){
    box.hidden = false;
    const m = document.getElementById('loaderr-msg');
    if (m) m.textContent = msg;
  }
  console.error('[events] 読み込み失敗:', msg);
}

(async function main(){

let DATA;
try {
  const res = await fetch(DATA_URL, {cache: 'no-cache'});
  if (!res.ok) throw new Error(`${DATA_URL} を取得できませんでした (HTTP ${res.status})`);
  DATA = await res.json();
} catch (err) {
  return bootFail(err && err.message ? err.message : String(err));
}
if (!DATA || !DATA.meta || !Array.isArray(DATA.events)) {
  return bootFail(`${DATA_URL} の形式が正しくありません（meta / events が見つかりません）`);
}
const loading = document.getElementById('loading');
if (loading) loading.remove();

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

})();
