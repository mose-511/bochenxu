# -*- coding: utf-8 -*-
"""第三轮追加：Hero 换成真实中国地图（_heromap.frag），替换旧简化轮廓。"""
import io, re

p = '_gen_portal.py'
s = io.open(p, encoding='utf-8').read()
frag = io.open('_heromap.frag', encoding='utf-8').read()

# ---- 1. 替换 HERO_MAP_SVG 常量（从定义行到闭合 ''' ）----
m = re.search(r"HERO_MAP_SVG = '''.*?'''", s, re.S)
assert m, 'HERO_MAP_SVG block not found'
new_const = (
    "HERO_MAP_SVG = (io.open('_heromap.frag', encoding='utf-8').read())\n"
    "HERO_MAP_CAP = '''\n"
    '<div class="hero-cap">全国高校资源网络 · 1403所本科院校分布</div>\n'
    '<a class="hero-more" href="map.html">探索高校地图 →</a>\n'
    "'''"
)
s = s[:m.start()] + new_const + s[m.end():]

# ---- 2. CSS：删旧 .cnmap 系列样式，加真实地图样式 ----
old_css = re.search(r"  \.cnmap\{[^}]*\}.*?\.hero-tip b\{color:#FFB27A;font-weight:700\}", s, re.S)
assert old_css, 'old cnmap css not found'
new_css = '''  .hero-map{min-width:0}
  .hero-map .stage{position:relative;max-width:520px;margin:0 auto}
  .cnmap-svg{width:100%;display:block;overflow:visible}
  /* 省份：低对比底色 + 细边界，hover 高亮 */
  .cnmap-svg .hp{fill:rgba(232,240,248,.10);stroke:rgba(255,255,255,.28);stroke-width:.7;
    stroke-linejoin:round;transition:fill .16s;cursor:pointer}
  .cnmap-svg .hp:hover{fill:rgba(255,178,122,.22);stroke:rgba(255,178,122,.65)}
  .cnmap-svg .hp-line{fill:none;stroke:rgba(255,255,255,.30);stroke-width:.7;pointer-events:none}
  /* 高校节点 */
  .cnmap-svg .hu{cursor:pointer}
  .cnmap-svg .hu circle{fill:#7FB3E8;stroke:#0B2B4E;stroke-width:1}
  .cnmap-svg .hu.hub circle{fill:#FFB27A;stroke:#0B2B4E;stroke-width:1.2}
  .cnmap-svg .hu.hub circle::after{content:""}
  .cnmap-svg .hu text{fill:rgba(255,255,255,.90);font-size:11.5px;font-weight:600;
    font-family:"Microsoft YaHei","PingFang SC","Noto Sans SC",sans-serif;paint-order:stroke;
    stroke:rgba(7,26,48,.85);stroke-width:2.5;pointer-events:none}
  .cnmap-svg .hu:hover circle{fill:#FFB27A;filter:drop-shadow(0 0 5px rgba(255,178,122,.6))}
  /* 悬停提示 */
  .hmtip{position:fixed;z-index:99;pointer-events:none;display:none;
    background:#0F3458;color:#fff;border:1px solid rgba(255,178,122,.4);
    padding:7px 11px;border-radius:8px;font-size:12.5px;line-height:1.5;
    box-shadow:0 8px 22px rgba(2,12,26,.5)}
  .hmtip b{color:#FFB27A}
  .hmtip small{display:block;color:#A9C3DE;font-size:11.5px}
  .hero-cap{margin-top:10px;text-align:center;font-size:12px;color:#7E9CBA;letter-spacing:1.5px}
  .hero-more{display:table;margin:10px auto 0;padding:9px 22px;border-radius:9px;
    background:rgba(255,255,255,.08);border:1px solid rgba(255,178,122,.45);
    color:#FFB27A;font-size:13.5px;font-weight:700;letter-spacing:.5px;transition:.16s}
  .hero-more:hover{background:rgba(255,178,122,.16)}
  .hero-stats{display:flex;justify-content:flex-end;gap:8px;margin:0 0 14px;flex-wrap:wrap}
  .hero-stats .st{background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.16);
    border-radius:9px;padding:9px 14px;text-align:center}
  .hero-stats .st b{font-size:20px;font-weight:800;color:#fff;font-family:Georgia,"Microsoft YaHei",serif;line-height:1}
  .hero-stats .st b i{font-style:normal;font-size:12px;color:#FFB27A;margin-left:1px}
  .hero-stats .st span{font-size:12px;color:#A9C3DE}
  .hero-tip{margin-top:12px;text-align:center;font-size:12.5px;color:#8FB0D2}
  .hero-tip b{color:#FFB27A;font-weight:700}'''
s = s[:old_css.start()] + new_css + s[old_css.end():]

# ---- 3. hero 区块结构：SVG 包进 stage，统计标签靠右上，提示文案更新 ----
old_map = re.search(
    r'      <div class="hero-map">\n'
    r'        <div class="hero-stats">\n'
    r'          <div class="st"><b>1403<i>所</i></b><span>全国本科院校</span></div>\n'
    r'          <div class="st"><b>31<i>省</i></b><span>全覆盖</span></div>\n'
    r'          <div class="st"><b>300<i>\+</i></b><span>城市高校数据</span></div>\n'
    r'        </div>\n'
    r'\{HERO_MAP_SVG\}\n'
    r'        <div class="hero-tip">[^<]*点击<b>省份名称</b>[^<]*</div>\n'
    r'      </div>', s)
assert old_map, 'hero-map usage not found'
new_map = '''      <div class="hero-map">
        <div class="hero-stats">
          <div class="st"><b>1403<i>所</i></b><span>全国本科院校</span></div>
          <div class="st"><b>31<i>省</i></b><span>全国覆盖</span></div>
          <div class="st"><b>300<i>+</i></b><span>城市高校数据</span></div>
        </div>
        <div class="stage" id="hmapstage">
{HERO_MAP_SVG}
        </div>
        <div class="hero-tip">悬停查看<b>省份</b>与<b>高校</b>，点击直达</div>
{HERO_MAP_CAP}
      </div>'''
s = s[:old_map.start()] + new_map + s[old_map.end():]

# ---- 4. JS：地图交互（tooltip + 点击跳转），锚定门户版 openContact（带 portal 埋点）----
old_js = "function openContact(){document.getElementById('cmodal').classList.add('on');document.body.style.overflow='hidden';if(window._hmt){try{_hmt.push(['_trackEvent','contact','open','portal'])}catch(e){}}}"
assert old_js in s, 'portal openContact not found'
new_js = old_js + '''
/* ---- Hero 真实地图交互 ---- */
(function(){
  var stage = document.getElementById('hmapstage');
  if(!stage) return;
  var tip = document.createElement('div');
  tip.className = 'hmtip';
  document.body.appendChild(tip);
  function move(e){
    var x = e.clientX + 14, y = e.clientY + 14;
    if(x + 190 > window.innerWidth) x = e.clientX - 200;
    tip.style.left = x + 'px'; tip.style.top = y + 'px';
  }
  stage.addEventListener('mouseover', function(e){
    var prov = e.target.closest('.hp[data-p]');
    var uni  = e.target.closest('.hu');
    if(prov){
      tip.innerHTML = '<b>' + prov.getAttribute('data-p') + '</b><small>点击查看该省高校地图</small>';
      tip.style.display = 'block'; move(e);
    } else if(uni){
      tip.innerHTML = '<b>' + uni.getAttribute('data-u') + '</b><small>' + uni.getAttribute('data-c') + ' · 点击进入高校地图</small>';
      tip.style.display = 'block'; move(e);
    }
  });
  stage.addEventListener('mousemove', function(e){
    if(tip.style.display === 'block') move(e);
  });
  stage.addEventListener('mouseout', function(e){
    if(e.target.closest('.hp') || e.target.closest('.hu')) tip.style.display = 'none';
  });
  stage.addEventListener('click', function(e){
    var prov = e.target.closest('.hp[data-href]');
    var uni  = e.target.closest('.hu');
    if(prov){ location.href = prov.getAttribute('data-href'); }
    else if(uni){ location.href = 'map.html'; }
  });
})();'''
s = s.replace(old_js, new_js)

io.open(p, 'w', encoding='utf-8').write(s)
print('patched: HERO_MAP_SVG + CSS + markup + JS')
