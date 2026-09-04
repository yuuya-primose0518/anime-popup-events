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

/* ---- 開催地 ----
   1レコードが複数の会場＝複数の都道府県を持ちうる。regions / prefs は配列。
   古い形式（region / pref のみ）のデータでも動くようにフォールバックする。 */
const RO = ['北海道','東北','関東','中部','関西','中国','四国','九州・沖縄','全国'];
const REGION_PREFS = {
  '北海道':   ['北海道'],
  '東北':     ['青森県','岩手県','宮城県','秋田県','山形県','福島県'],
  '関東':     ['茨城県','栃木県','群馬県','埼玉県','千葉県','東京都','神奈川県'],
  '中部':     ['新潟県','富山県','石川県','福井県','山梨県','長野県','岐阜県','静岡県','愛知県'],
  '関西':     ['三重県','滋賀県','京都府','大阪府','兵庫県','奈良県','和歌山県'],
  '中国':     ['鳥取県','島根県','岡山県','広島県','山口県'],
  '四国':     ['徳島県','香川県','愛媛県','高知県'],
  '九州・沖縄':['福岡県','佐賀県','長崎県','熊本県','大分県','宮崎県','鹿児島県','沖縄県'],
  '全国':     ['全国'],
};
const PO = RO.flatMap(r=>REGION_PREFS[r]);
const P2R = Object.fromEntries(RO.flatMap(r=>REGION_PREFS[r].map(p=>[p,r])));
const regionsOf = e => (Array.isArray(e.regions) && e.regions.length) ? e.regions : [e.region];
const prefsOf   = e => (Array.isArray(e.prefs)   && e.prefs.length)   ? e.prefs   : [e.pref];
/* 「全国」のイベントはどの地域で絞り込んでも出す */
const inRegion = (e,r) => !r || regionsOf(e).includes(r) || regionsOf(e).includes('全国');
const inPref   = (e,p) => !p || prefsOf(e).includes(p)   || prefsOf(e).includes('全国');

const sel  = document.getElementById('region');
const selP = document.getElementById('pref');
const ALL_REGIONS = [...new Set(evs.flatMap(regionsOf))].sort((a,b)=>RO.indexOf(a)-RO.indexOf(b));
ALL_REGIONS.forEach(r=>{ const o=document.createElement('option'); o.value=r; o.textContent='地域：'+r; sel.appendChild(o); });

/* 都道府県セレクトは、選択中の地域に含まれるものだけに絞る */
function fillPrefs(){
  const keep = selP.value;
  const list = [...new Set(evs.flatMap(prefsOf))]
    .filter(p => p && (!L.region || P2R[p]===L.region || p==='全国'))
    .sort((a,b)=>PO.indexOf(a)-PO.indexOf(b));
  selP.innerHTML = '<option value="">都道府県：すべて</option>' +
    list.map(p=>`<option value="${esc(p)}">都道府県：${esc(p)}</option>`).join('');
  if (list.includes(keep)) selP.value = keep; else { selP.value=''; L.pref=''; }
}

/* ---- キービジュアル ----
   img が空、または読み込みに失敗した場合は、作品名から決定的に生成した
   グラデーションにフォールバックする（onerror で img を取り除く）。
   collabo-cafe / AMNIBUS からのホットリンク。画像の複製・再配布はしない。 */
const hashOf = s => { let h = 0; for (let i=0;i<s.length;i++) h = (h*31 + s.charCodeAt(i)) | 0; return Math.abs(h); };
function visual(e, cls){
  const h  = hashOf(e.work);
  const h1 = h % 360, h2 = (h1 + 40 + (h >> 3) % 50) % 360;
  const bg = `linear-gradient(135deg,hsl(${h1} 42% 30%),hsl(${h2} 46% 18%))`;
  const im = e.img
    ? `<img src="${esc(e.img)}" alt="" loading="lazy" decoding="async" referrerpolicy="no-referrer" onerror="this.remove()">`
    : '';
  return `<div class="${cls||'vis'}" style="background:${bg}"><span class="vis-t">${esc(e.work)}</span>${im}</div>`;
}

/* ---- card ---- */
/* 開催地の表示：都道府県は4つまで並べ、超えたら「ほか N 県」。地域も並記する。 */
function areaLabel(e){
  const ps = prefsOf(e), rs = regionsOf(e);
  const head = ps.length<=4 ? ps.join('・') : ps.slice(0,4).join('・') + ` ほか${ps.length-4}県`;
  return rs.length===1 && ps.length===1 && ps[0]===rs[0] ? head : `${head}（${rs.join('／')}）`;
}
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
    ${visual(e)}
    <div class="row1"><span class="badge b-${e.st}">${LB[e.st]}</span>${note}</div>
    <div>${workLine}<a class="ttl" href="${esc(e.url)}" target="_blank" rel="noopener">${esc(e.title)}</a></div>
    <div class="meta">
      <div><span class="ico">📅</span><span class="date">${fmt(e.start)} – ${fmt(e.end)}</span></div>
      <div><span class="ico">📍</span><span>${esc(e.venue)}</span></div>
      <div><span class="ico">🗾</span><span>${esc(areaLabel(e))}</span></div>
      ${mapRow(e)}
    </div>
    <div class="tags">${e.tags.map(t=>`<span class="tag">${esc(t)}</span>`).join('')}</div>
  </div>`;
}

/* ================= LIST VIEW ================= */
let L = {s:'live', region:'', pref:'', q:'', sort:'start'};
/* フリーワードの対象：作品名・イベント名・会場名・全会場のマップ表示名・全都道府県・地域・タグ */
const haystack = e => (
  e.work+' '+e.title+' '+e.venue+' '+
  (e.map||[]).map(m=>m.n).join(' ')+' '+
  prefsOf(e).join(' ')+' '+regionsOf(e).join(' ')+' '+e.tags.join(' ')
).toLowerCase();
function renderList(){
  let list = evs.filter(e=>
    (L.s==='all' || e.st===L.s) &&
    inRegion(e, L.region) &&
    inPref(e, L.pref) &&
    (!L.q || haystack(e).includes(L.q))
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
sel.addEventListener('change', e=>{ L.region=e.target.value; fillPrefs(); renderList(); });
selP.addEventListener('change', e=>{ L.pref=e.target.value; renderList(); });
fillPrefs();
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
  // 作品索引のサムネイル：開催中／予定のもの優先で、img が入っている1件を代表にする
  const rep = list.find(e=>e.img && e.st!=='done') || list.find(e=>e.img) || list[0];
  return {w, list, live, soon, upcoming, rep};
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
      ${visual(x.rep, 'wvis')}
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
  const prefs = [...new Set(x.list.flatMap(prefsOf))].sort((a,b)=>PO.indexOf(a)-PO.indexOf(b)).join('・');
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
