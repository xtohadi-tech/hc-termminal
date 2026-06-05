from pathlib import Path

BASE = Path('/data/data/com.termux/files/home/repos/hc-termminal/index.html')
text = BASE.read_text(encoding='utf-8')

# 1. Ensure new tabs exist
OLD_TABS = (
    '  <button class="tab-btn" onclick="sw(\'kalender\',this)">📅 KALENDER</button>\n</div>'
)
NEW_TABS = (
    '  <button class="tab-btn" onclick="sw(\'kalender\',this)">📅 KALENDER</button>\n'
    '  <button class="tab-btn" onclick="sw(\'route-score\',this)">📈 ROUTE SCORE</button>\n'
    '  <button class="tab-btn" onclick="sw(\'backtest\',this)">🧪 BACKTEST</button>\n</div>'
)
if OLD_TABS not in text:
    text = text.replace(
        '<button class="tab-btn" onclick="sw(\'kalender\',this)">📅 KALENDER</button>',
        '<button class="tab-btn" onclick="sw(\'kalender\',this)">📅 KALENDER</button>\n'
        '  <button class="tab-btn" onclick="sw(\'route-score\',this)">📈 ROUTE SCORE</button>\n'
        '  <button class="tab-btn" onclick="sw(\'backtest\',this)">🧪 BACKTEST</button>',
    )

# 2. Ensure tab switcher handles new tabs
SW_OLD = "  if(name==='kalender'&&!S.calEvents.length)loadCalendar();\n}\n"
SW_NEW = (
    "  if(name==='kalender'&&!S.calEvents.length)loadCalendar();\n"
    "  if(name==='route-score')renderRouteStrength();\n"
    "  if(name==='backtest')renderBacktestOutput();\n}\n"
)
if SW_OLD in text and "renderRouteStrength();" not in text:
    text = text.replace(SW_OLD, SW_NEW)

# 3. Ensure new sections exist after Kalender section
SECTIONS_MARKER = '<!-- KALENDER -->\n<div id="sec-kalender" class="sec">\n  <div class="lbl">Kalender Event Crypto</div>\n  <div class="cal-filter">\n'
EXTRA = (
    '\n'
    '<!-- ROUTE SCORE -->\n'
    '<div id="sec-route-score" class="sec">\n'
    '  <div class="lbl">Route Strength</div>\n'
    '  <div class="info-box">Skor kekuatan jalur arus (0-100).</div>\n'
    '  <div class="btn-row">\n'
    '    <button class="btn-sm" onclick="runRouteStrength()">↻ Hitung Route Score</button>\n'
    '    <span style="font-size:10px;color:var(--text3);margin-left:6px" id="route-score-update">Belum dihitung</span>\n'
    '  </div>\n'
    '  <div id="routeScoreOut"><div class="empty">Scan dulu di tab SCANNER</div></div>\n'
    '</div>\n'
    '\n'
    '<!-- BACKTEST -->\n'
    '<div id="sec-backtest" class="sec">\n'
    '  <div class="lbl">Quick Backtest</div>\n'
    '  <div class="info-box">Estimasi: kandidat berikutnya cenderung naik berdasarkan arah jalur saat ini.</div>\n'
    '  <div class="btn-row">\n'
    '    <button class="btn-sm" onclick="runBacktest()">↻ Jalankan Backtest</button>\n'
    '    <span style="font-size:10px;color:var(--text3);margin-left:6px" id="backtest-update">Belum dijalankan</div>\n'
    '  </div>\n'
    '  <div id="backtestOut"><div class="empty">Scan dulu, lalu jalankan backtest.</div></div>\n'
    '</div>\n'
)
if SECTIONS_MARKER in text and 'sec-route-score' not in text:
    text = text.replace(SECTIONS_MARKER, SECTIONS_MARKER + EXTRA)

# 4. Append JS helpers if missing
needle = "navigator.serviceWorker.register(swPath).catch(()=>{});"
if needle in text and "function buildRouteStrengthRows" not in text:
    extra_js = """
function getStrengthColor(score){return score>=75?'var(--green)':score>=50?'var(--yellow)':score>=30?'var(--orange)':'var(--text3)'}
function getStrengthLabel(score){return score>=75?'Kuat':score>=50?'Sedang':score>=30?'Lemah':'Idle'}
function buildRouteStrengthRows(){
  const allArus=getAllArus();const prices=S.arusPrices||{};
  const rows=allArus.map((row,idx)=>{
    let up=0,pctSum=0,chainWin=0;
    for(let i=0;i<row.length;i++){
      const d=prices[row[i]];const d24=S.d24[row[i]];
      if(d && d.c>0) up++;
      if(d && Number.isFinite(d.c)) pctSum += Math.abs(d.c);
      if(i>0 && d && prices[row[i-1]]){if(d.c>0 && prices[row[i-1]].c>0) chainWin++;}
      if(d24 && d24.c>0) up++;
    }
    const upRatio=row.length?up/row.length:0;const pctAvg=row.length?pctSum/row.length:0;const win=row.length>1?chainWin/(row.length-1):0;
    const score=Math.round(Math.min(100,Math.max(0,upRatio*40+Math.min(pctAvg,15)+win*40+(upRatio>0.7&&pctAvg>3?10:0))));
    return {id:`J${String(idx+1).padStart(2,'0')}`,route:row.join(' -> '),score,coins:row};
  });
  rows.sort((a,b)=>b.score-a.score||b.coins.length-a.coins.length);return rows;
}
function renderRouteStrength(){
  const el=document.getElementById('routeScoreOut');if(!el)return;
  if(!tickers.length){el.innerHTML='<div class=\"empty\">Scan dulu di tab SCANNER</div>';return;}
  if(!getAllArus().length){el.innerHTML='<div class=\"empty\">Belum ada data jalur.</div>';return;}
  const rows=buildRouteStrengthRows();let h='<div class=\"heat-grid\">';
  rows.slice(0,30).forEach(item=>{
    const color=getStrengthColor(item.score);const label=getStrengthLabel(item.score);
    const coinsHtml=item.coins.map((c,j)=>`<span class=\"${j===0?'ha':S.arusPrices?.[c]?.c>0?'hn':''}\">${c}</span>`).join('<span style=\"color:var(--border2)\">-></span>');
    h+=`<div class="heat-card ${item.score>=50?'active':item.score>=30?'warm':''}"><div class="heat-num">${item.id} - <span style=\"color:${color};font-weight:700\">${item.score}</span> - ${label}</div><div class="heat-coins\">${coinsHtml}</div></div>`;
  });
  h+='</div>';el.innerHTML=h;
  const u=document.getElementById('route-score-update');if(u)u.textContent='Update: '+new Date().toLocaleTimeString('id-ID');
}
function runRouteStrength(){
  if(typeof loadArusPrices==='function'&&(!Object.keys(S.arusPrices||{}).length||!getAllArus().length)){loadArusPrices().then(()=>{renderRouteStrength();showNotif('Route Score dihitung','success');}).catch(()=>showNotif('Gagal muat harga','warn'));return;}
  renderRouteStrength();showNotif('Route Score dihitung','success');
}
function renderBacktestOutput(){
  const el=document.getElementById('backtestOut');if(!el)return;
  if(!tickers.length){el.innerHTML='<div class=\"empty\">Scan dulu</div>';return;}
  const allArus=getAllArus();const activeSyms=new Set(tickers.slice(0,50).map(t=>t.symbol.replace('USDT','')));let rows=[];
  allArus.forEach((row,i)=>{
    const hits=row.filter(c=>activeSyms.has(c));if(hits.length<2)return;
    const idx=row.indexOf(hits[hits.length-1]);const next=row[idx+1];if(!next)return;
    const upCount=row.slice(0,idx+1).filter((c,ci)=>{if(ci===0)return true;const prev=row[ci-1];const a=S.d24[c],b=S.d24[prev];return a&&b&&a.c>0&&b.c>0;}).length;
    const consistency=Math.round((upCount/(idx+1))*100);
    rows.push({id:`J${String(i+1).padStart(2,'0')}`,route:row.join(' -> '),next,consistency});
  });
  if(!rows.length){el.innerHTML='<div class=\"empty\">Tidak ada jalur aktif.</div>';return;}
  let h='<div class=\"heat-grid\">';
  rows.slice(0,30).forEach(r=>{
    const color=r.consistency>=70?'var(--green)':r.consistency>=45?'var(--yellow)':'var(--orange)';
    const label=r.consistency>=70?'Konsisten':r.consistency>=45?'Sedang':'Tidak konsisten';
    h+=`<div class="heat-card ${r.consistency>=45?'active':'warm'}"><div class="heat-num">${r.id} - ${label} ${r.consistency}%</div><div class="heat-coins\">${r.route} -><span style=\"color:var(--accent)\">${r.next}</span></div></div>`;
  });
  h+='</div>';el.innerHTML=h;
  const u=document.getElementById('backtest-update');if(u)u.textContent='Update: '+new Date().toLocaleTimeString('id-ID');
}
function runBacktest(){renderBacktestOutput();showNotif('Backtest dijalankan','success');}
"""
    text = text.replace(needle + "\n  });\n}\n</script>", needle + "\n  });\n}\n" + extra_js + "</script>")

BASE.write_text(text, encoding='utf-8')
print('updated')
