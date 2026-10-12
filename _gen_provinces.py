# -*- coding: utf-8 -*-
"""
生成「每省独立落地页 + sitemap + OG 分享卡片」提升收录与转发效果。
- p/<省>.html：每个省一张独立可抓取页面，内嵌该省产业-专业速查仪表盘 iframe，
  并列出该省相关升学工作成果，含 SEO meta + JSON-LD 结构化数据 + OG 元数据。
- sitemap.xml / robots.txt：列出门户、地图本体、全部落地页。
- og/<省>.png：1200x630 分享卡片，省名+产业关键词+孟老师品牌行（PIL 本地渲染）。
所有内容严格来自 results/ 真实文件名，不编造产业数据。
"""
import os, re, json, urllib.parse, datetime

# —— 百度统计接入点：把统计 ID 写入同目录 stats_id.txt 即自动启用 ——
_stats_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stats_id.txt")
STATS_ID = open(_stats_file, encoding="utf-8").read().strip() if os.path.exists(_stats_file) else ""
STATS_SNIPPET = ""
if STATS_ID:
    STATS_SNIPPET = ("<script>var _hmt=_hmt||[];(function(){var hm=document.createElement('script');"
                     "hm.src='https://hm.baidu.com/hm.js?" + STATS_ID + "';"
                     "var s=document.getElementsByTagName('script')[0];s.parentNode.insertBefore(hm,s);})();</script>")

ROOT = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(ROOT, "results")
P_DIR = os.path.join(ROOT, "p")
OG_DIR = os.path.join(ROOT, "og")
os.makedirs(P_DIR, exist_ok=True)
os.makedirs(OG_DIR, exist_ok=True)

BASE = "https://star-map-folder.app.workbuddy.host"

files = [f for f in os.listdir(RESULTS) if os.path.isfile(os.path.join(RESULTS, f))]
dash_re = re.compile(r"^(.+?)产业-本科专业(?:速查|总览)仪表盘\.html$")

PROV_ORDER = ["北京","天津","河北","山西","内蒙古","辽宁","吉林","黑龙江","上海","江苏",
              "浙江","安徽","福建","江西","山东","河南","湖北","湖南","广东","广西",
              "海南","重庆","四川","贵州","云南","西藏","陕西","甘肃","青海","宁夏","新疆"]
FULL = {"北京":"北京市","天津":"天津市","河北":"河北省","山西":"山西省","内蒙古":"内蒙古自治区",
        "辽宁":"辽宁省","吉林":"吉林省","黑龙江":"黑龙江省","上海":"上海市","江苏":"江苏省",
        "浙江":"浙江省","安徽":"安徽省","福建":"福建省","江西":"江西省","山东":"山东省",
        "河南":"河南省","湖北":"湖北省","湖南":"湖南省","广东":"广东省","广西":"广西壮族自治区",
        "海南":"海南省","重庆":"重庆市","四川":"四川省","贵州":"贵州省","云南":"云南省",
        "西藏":"西藏自治区","陕西":"陕西省","甘肃":"甘肃省","青海":"青海省","宁夏":"宁夏回族自治区",
        "新疆":"新疆维吾尔自治区"}

provinces, nation = [], []
for f in files:
    m = dash_re.match(f)
    if m:
        prov = m.group(1)
        (nation if prov == "全国" else provinces).append((prov, f))
def key(p):
    try: return PROV_ORDER.index(p[0])
    except ValueError: return 999
provinces.sort(key=key); nation.sort()

WORK_TITLE = {
    "中国1054个国家级产业集群全景解读与专业分析.html": "1054个国家级产业集群 · 解读与专业分析",
    "2026各省选调备考规划.html": "2026 各省选调备考规划",
    "2027河北选科专业对照表.html": "2027 河北选科专业对照表",
    "31省产业-本科专业择校指南网站.html": "31 省产业-本科专业择校指南",
    "31省高考报考逻辑详解.html": "31 省高考报考逻辑详解",
    "专业介绍查询系统.html": "专业介绍查询系统",
    "全国144城产业调研地图.html": "全国 144 城产业调研地图",
    "就业与教学质量报告决策参考380所.html": "就业与教学质量报告 · 380 所决策参考",
    "已审批更名大学全汇总.html": "已审批更名大学全汇总",
    "本科专业对应的研究生专业查询系统.html": "本科→研究生专业查询系统",
    "民营企业500强调研完整报告.html": "民营企业 500 强 · 调研完整报告",
    "河北高考九科合订本.html": "河北高考九科合订本",
    "河北高考投档数据_总查询台_2026vs2025.html": "河北高考投档数据总查询台 · 2026vs2025",
    "河北省院校录取查询系统.html": "河北省院校录取查询系统",
    "红宝书-全国分省特色院校全景梳理与决策参考(2026年6月版).docx": "全国分省特色院校全景红宝书（2026年6月版）",
    "职业本科院校择校手册.html": "职业本科院校择校手册",
}
def title_of(f): return WORK_TITLE.get(f, os.path.splitext(f)[0])
def enc(f): return "results/" + urllib.parse.quote(f)
def urlsafe(s): return urllib.parse.quote(s, safe="")

def extract_industries(prov_key):
    """从真实省仪表盘抽取主导产业关键词（不编造）。取首个 i:\"...\" 省域总览，
    去括号、截「——」前、按顿号/逗号切分，返回前 3 个。"""
    if prov_key == "全国":
        return []
    fn = os.path.join(RESULTS, f"{prov_key}产业-本科专业速查仪表盘.html")
    if not os.path.isfile(fn):
        return []
    try:
        txt = open(fn, encoding="utf-8", errors="ignore").read()
    except Exception:
        return []
    m = re.search(r'i:"([^"]{4,140})"', txt)
    if not m:
        return []
    s = m.group(1)
    s = re.sub(r'[（(][^）)]*[）)]', '', s)   # 去括号及注释
    s = s.split("——")[0]                       # 截断省总览说明
    parts = [p.strip() for p in re.split(r'[、，,；;]', s) if p.strip()]
    return parts[:3]

def draw_og_card(path, title, subtitle, tagline):
    """用 PIL 绘制 1200x630 OG 卡片（依赖系统 Noto Sans SC）。"""
    from PIL import Image, ImageDraw, ImageFont
    W, H = 1200, 630
    TOP = (10, 78, 126)
    BOT = (14, 154, 167)
    WHITE = (255, 255, 255)
    PALE = (216, 235, 247)
    CYAN = (140, 228, 237)
    FONT_DIR = "/c/Windows/Fonts"
    reg = os.path.join(FONT_DIR, "Noto Sans SC (TrueType).otf")
    bold = os.path.join(FONT_DIR, "Noto Sans SC Bold (TrueType).otf")
    if not os.path.isfile(bold):
        bold = reg
    def ft(path, size):
        try: return ImageFont.truetype(path, size)
        except Exception: return ImageFont.load_default()
    def lerp(a, b, t):
        return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
    img = Image.new("RGB", (W, H), TOP)
    d = ImageDraw.Draw(img)
    for y in range(H):
        d.line([(0, y), (W, y)], fill=lerp(TOP, BOT, y / H))
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([W - 520, -200, W + 240, 380], fill=WHITE)
    img = Image.blend(img, glow, 0.10)
    d = ImageDraw.Draw(img)
    d.text((80, 58), "博辰序 · BOCHENXU", font=ft(reg, 26), fill=PALE)
    n = len(title)
    size = 108 if n <= 4 else 96 if n <= 5 else 84 if n <= 6 else 74
    d.text((W // 2, H // 2 - 66), title, font=ft(bold, size), fill=WHITE, anchor="mm")
    d.text((W // 2, H // 2 + 18), subtitle, font=ft(reg, 38), fill=PALE, anchor="mm")
    if tagline:
        d.text((W // 2, H // 2 + 78), tagline, font=ft(reg, 32), fill=CYAN, anchor="mm")
    d.line([(80, H - 112), (W - 80, H - 112)], fill=(170, 200, 220))
    d.text((80, H - 82), "孟老师 · 升学规划咨询", font=ft(reg, 30), fill=WHITE)
    d.text((W - 80, H - 82), "18931577792", font=ft(bold, 36), fill=WHITE, anchor="rm")
    img.save(path, "PNG")

CSS = '''
:root{--bg:#E9F2F9;--blue:#0C5A8E;--blue2:#1E6FB8;--cyan:#0E9AA7;--ink:#16324C;--ink2:#3D5F7E;
  --line:rgba(127,168,201,.32);--card:#FFF;--shadow:0 6px 22px rgba(30,90,140,.10)}
*{box-sizing:border-box}html,body{margin:0;padding:0;background:var(--bg);color:var(--ink);
  font-family:"Microsoft YaHei","PingFang SC","Noto Sans SC",sans-serif}
a{text-decoration:none;color:inherit}.wrap{max-width:1100px;margin:0 auto;padding:0 22px}
.hero{background:linear-gradient(135deg,#0A4E7E,#1E6FB8 52%,#0E9AA7);color:#fff;padding:54px 0 44px}
.kick{letter-spacing:5px;font-size:12px;font-weight:700;opacity:.9}
.hero h1{margin:8px 0 6px;font-size:38px;font-weight:800}
.hero p{margin:0;font-size:16px;opacity:.95;max-width:760px;line-height:1.75}
.nav{display:flex;gap:12px;margin-top:24px;flex-wrap:wrap}
.nav a{background:#fff;color:var(--blue);font-weight:700;font-size:14px;padding:11px 22px;
  border-radius:24px;box-shadow:0 8px 22px rgba(0,0,0,.16);transition:.16s}
.nav a:hover{transform:translateY(-2px)}
.phone-bar{margin-top:18px}
.phone-bar a{display:inline-flex;align-items:center;gap:12px;background:rgba(255,255,255,.16);
  backdrop-filter:blur(6px);color:#fff;border:1px solid rgba(255,255,255,.35);border-radius:30px;
  padding:10px 22px;font-size:15px;transition:.16s}
.phone-bar a:hover{background:rgba(255,255,255,.26);transform:translateY(-2px)}
.phone-bar b{font-size:17px;letter-spacing:.5px}
section{padding:44px 0}.sec-title{font-size:24px;font-weight:800;margin:0 0 6px}
.sec-sub{color:var(--ink2);font-size:14.5px;margin:0 0 22px}
.frame{width:100%;height:calc(100vh - 240px);min-height:680px;border:1px solid var(--line);
  border-radius:14px;background:#fff;box-shadow:var(--shadow)}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:15px}
.card{background:var(--card);border:1px solid var(--line);border-radius:13px;padding:18px;
  box-shadow:var(--shadow);transition:.18s;display:flex;flex-direction:column;gap:9px}
.card:hover{transform:translateY(-3px);border-color:var(--blue2)}
.card-ic{width:26px;height:26px;color:var(--blue2)}
.card-t{font-size:15px;font-weight:700;line-height:1.5}
.card-go{margin-top:auto;font-size:13px;color:var(--blue2);font-weight:700}
.note{background:rgba(14,154,167,.08);border:1px solid var(--line);border-radius:12px;
  padding:15px 18px;font-size:13.5px;color:var(--ink2);line-height:1.7}
.provjump{display:flex;flex-wrap:wrap;gap:9px;margin-top:6px}
.provjump a{font-size:13px;font-weight:700;color:var(--blue2);border:1px solid var(--line);
  background:#fff;border-radius:20px;padding:7px 14px;transition:.15s}
.provjump a:hover{border-color:var(--blue2);background:#F1F7FC}
.provjump a.cur{background:var(--blue2);color:#fff;border-color:var(--blue2)}
.contact{background:#fff;border-top:1px solid var(--line)}
.contact-top{display:flex;align-items:center;justify-content:space-between;gap:24px;flex-wrap:wrap;padding:44px 0 28px}
.contact-top .sec-title{margin-bottom:6px}
.cta-phone{display:inline-flex;align-items:center;gap:10px;background:var(--blue);color:#fff;font-weight:800;font-size:22px;
  padding:16px 30px;border-radius:40px;box-shadow:0 10px 26px rgba(12,90,142,.25);transition:.18s}
.cta-phone:hover{background:#0A4E7E;transform:translateY(-2px)}
.contact-tags{display:flex;gap:10px;flex-wrap:wrap;padding-bottom:44px}
.cc-hook{margin-top:20px;background:linear-gradient(135deg,#FFF7E8,#FFEFD2);border:1px solid #F0D9A8;border-radius:14px;padding:14px 18px;font-size:13.5px;line-height:1.65;color:#5A4620;max-width:580px}
.cc-hook b{display:block;color:#8A6410;font-size:15px;margin-bottom:4px}
.contact-tags span{font-size:13px;font-weight:700;color:var(--blue2);background:#F0F7FC;border:1px solid var(--line);border-radius:20px;padding:8px 16px}
footer{background:#0E1B16;color:#9FB8AF;padding:34px 0;font-size:13px;line-height:1.8}
footer b{color:#D6E6DF}
footer a{color:#A8D6C8}
footer a:hover{color:#fff}
@media(max-width:860px){.grid{grid-template-columns:repeat(2,1fr)}.hero h1{font-size:30px}.frame{min-height:560px}}
@media(max-width:560px){.grid{grid-template-columns:1fr}.contact-top{flex-direction:column;align-items:flex-start}.cta-phone{font-size:18px;padding:14px 24px}}
'''
DOC_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M6 3h9l4 4v14H6z"/><path d="M15 3v4h4"/><path d="M9 12h7M9 16h7"/></svg>'
PHONE_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.56 12.56 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.56 12.56 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>'

# ---- 联系弹窗（微信二维码 + 电话，所有省页共用）----
MODAL_CSS = '''
.cmodal{position:fixed;inset:0;background:rgba(6,24,39,.62);display:none;align-items:center;justify-content:center;z-index:99;padding:20px}
.cmodal.on{display:flex}
.cmodal-box{background:#fff;border-radius:20px;max-width:360px;width:100%;padding:30px 28px 26px;text-align:center;position:relative;box-shadow:0 24px 64px rgba(6,24,39,.35)}
.cmodal-x{position:absolute;top:12px;right:14px;border:none;background:none;font-size:19px;color:#9FB4C4;cursor:pointer;line-height:1}
.cmodal-x:hover{color:#fff}
.cmodal-t{font-size:20px;font-weight:800;color:#072A40;margin-bottom:14px}
.cmodal-qr{width:238px;height:auto;border-radius:14px;border:1px solid rgba(255,255,255,.35);display:block;margin:0 auto}
.cmodal-wechat{font-size:13.5px;color:#3E5A70;margin:12px 0 14px}
.cmodal-tel{display:inline-flex;align-items:center;gap:8px;background:linear-gradient(135deg,#0A4E7E,#0E9AA7);color:#fff;text-decoration:none;font-weight:800;font-size:17px;padding:11px 24px;border-radius:26px}
.cmodal-tel svg{width:17px;height:17px}
.cmodal-sub{font-size:12.5px;color:#7A8B99;margin-top:12px}
'''

MODAL_HTML = '''
<div class="cmodal" id="cmodal" onclick="if(event.target===this)closeContact()">
  <div class="cmodal-box">
    <button class="cmodal-x" onclick="closeContact()" aria-label="关闭">✕</button>
    <div class="cmodal-t">咨询孟老师</div>
    <img class="cmodal-qr" src="../assets/qr-wechat.jpg" alt="微信扫码添加孟老师">
    <div class="cmodal-wechat">微信扫描二维码，添加孟老师为朋友（好友申请备注省份，优先发本省资料）</div>
    <a class="cmodal-tel" href="tel:18931577792">''' + PHONE_SVG + '''18931577792</a>
    <div class="cmodal-sub">高考志愿填报 · 产业选专业 · 院校择校 · 升学就业路径</div>
  </div>
</div>
<script>
function openContact(){document.getElementById('cmodal').classList.add('on');document.body.style.overflow='hidden';if(window._hmt){try{_hmt.push(['_trackEvent','contact','open','province'])}catch(e){}}}
function closeContact(){document.getElementById('cmodal').classList.remove('on');document.body.style.overflow='';}
document.addEventListener('keydown',function(e){if(e.key==='Escape')closeContact();});
</script>
'''

def related_works(prov_keyword, all_provs=False):
    out = []
    for f in files:
        if f in ("_ok.js",) or f.endswith(".md") or f.endswith(".json"):
            continue
        if all_provs:
            out.append(f)
        elif prov_keyword and prov_keyword in f:
            out.append(f)
    # 去重 + 友好排序（保留 WORK_TITLE 顺序优先）
    seen = set(); res = []
    for f in files:
        if f in seen: continue
        if (all_provs or (prov_keyword and prov_keyword in f)) and f not in ("_ok.js",) and not f.endswith((".md",".json")):
            res.append(f); seen.add(f)
    res.sort(key=lambda x: list(WORK_TITLE).index(x) if x in WORK_TITLE else 99)
    return res

def build_page(prov_full, prov_key, dash_file, is_nation=False):
    dash_url = "../" + enc(dash_file)
    rel = related_works(prov_key, all_provs=is_nation)
    kw = [] if is_nation else extract_industries(prov_key)
    kw2 = "、".join(kw[:2])
    kw3 = "、".join(kw[:3])
    if rel:
        cards = "\n".join(
            f'<a class="card" href="../{enc(f)}" target="_blank" rel="noopener">'
            f'<div class="card-ic">{DOC_ICON}</div><div class="card-t">{title_of(f)}</div>'
            f'<div class="card-go">打开 →</div></a>' for f in rel)
        sub_title = ("本页汇集全部升学工作成果，按服务场景归类。" if is_nation
                     else f"文件名命中「{prov_key}」的成果，点击直接打开（需联网）。")
        rel_section = (f'<section style="background:linear-gradient(180deg,#fff,#F1F7FC)\">\n'
            f'<div class="wrap"><h2 class="sec-title">{prov_full}相关升学工作成果</h2>\n'
            f'<p class="sec-sub">{sub_title}</p>\n'
            f'<div class="grid">\n{cards}\n</div></div></section>')
    else:
        rel_section = (f'<section style="background:linear-gradient(180deg,#fff,#F1F7FC)\">\n'
            f'<div class="wrap"><h2 class="sec-title">{prov_full}相关升学工作成果</h2>\n'
            f'<p class="sec-sub">该省暂无独立命名成果，可查看「31 省产业-本科专业择校指南」与「全国分省特色院校全景红宝书」。</p></div></section>')

    # 省份快速跳转条（仅省页；全国页跳过自身）
    if is_nation:
        jump = ""
    else:
        items = "".join(
            f'<a class="{"cur" if p==prov_key else ""}" href="{FULL.get(p,p)}.html">{FULL.get(p,p)}</a>'
            for p, _ in provinces)
        jump = (f'<section><div class="wrap"><h2 class="sec-title">切换其他省份</h2>\n'
                f'<p class="sec-sub">31 省产业-本科专业速查仪表盘，独立成页，便于检索与分享。</p>\n'
                f'<div class="provjump">{items}</div></div></section>')

    desc = (f"{prov_full}本科院校分布与产业-专业速查：支柱产业包括{kw3}等；打开{prov_full}产业-本科专业速查仪表盘，"
            f"查看支柱产业、匹配专业与报考提醒；并汇总该省相关升学工作成果。"
            if (not is_nation and kw) else
            (f"{prov_full}本科院校分布与产业-专业速查：打开{prov_full}产业-本科专业速查仪表盘，"
             f"查看支柱产业、匹配专业与报考提醒；并汇总该省相关升学工作成果。"
             if not is_nation else
             "全国本科院校产业-专业总览仪表盘与全部升学工作成果索引：一份把产业、专业、院校、报考链路打通的决策地图。"))
    page_title = (f"{prov_full}支柱产业与本科院校分布地图｜{kw2}等 | 博辰序"
                  if (not is_nation and kw) else
                  f"{prov_full} · 本科院校分布与产业-专业速查 | 博辰序")

    jsonld = ('<script type="application/ld+json">{"@context":"https://schema.org","@type":"WebPage",'
              f'"@id":"{BASE}/p/{urllib.parse.quote(prov_full)}.html",'
              f'"name":"{page_title.split(" | ")[0]}","description":{json.dumps(desc,ensure_ascii=False)},'
              f'"url":"{BASE}/p/{urllib.parse.quote(prov_full)}.html","isPartOf":{{"@type":"WebSite","name":"博辰序","url":"{BASE}/"}}}}</script>')

    og_url = f"{BASE}/p/{urllib.parse.quote(prov_full)}.html"
    og_img = f"{BASE}/og/{urllib.parse.quote(prov_full)}.png"
    tagline = " · ".join(kw[:3]) if kw else ("产业-专业-院校 报考决策地图" if not is_nation else "1403 所本科院校 · 31 省产业-专业总览")
    if len(tagline) > 24:
        tagline = tagline[:23] + "…"

    # 生成 OG 卡片
    og_path = os.path.join(OG_DIR, prov_full + ".png")
    try:
        draw_og_card(og_path, prov_full, "支柱产业与本科院校分布地图" if not is_nation else "本科院校产业-专业总览地图", tagline)
    except Exception as e:
        print("og skip", prov_full, e)

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<title>{page_title}</title>
<meta name="description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:title" content="{page_title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{og_url}">
<meta property="og:image" content="{og_img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:site_name" content="博辰序">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{og_img}">
{jsonld}
<style>{CSS}{MODAL_CSS}</style>
{STATS_SNIPPET}
</head>
<body>
<header class="hero">
  <div class="wrap">
    <div class="kick">博辰序 · BOCHENXU</div>
    <h1>{prov_full} · 产业-本科专业速查</h1>
    <p>{desc}</p>
    <div class="nav">
      <a href="../">← 返回门户</a>
      <a href="../map.html">打开交互地图</a>
    </div>
    <div class="phone-bar">
      <a href="tel:18931577792">{PHONE_SVG}<span>升学规划咨询</span><b>18931577792</b></a>
      <a href="#contact" onclick="openContact();return false" style="margin-left:10px"><span>微信扫码咨询</span></a>
    </div>
  </div>
</header>

<section>
  <div class="wrap">
    <h2 class="sec-title">{prov_full}产业-本科专业速查仪表盘</h2>
    <p class="sec-sub">支柱产业、匹配专业、报考提醒，一图看全。需在联网环境下加载。</p>
    <iframe class="frame" src="{dash_url}" title="{prov_full}产业-本科专业速查仪表盘" loading="lazy"></iframe>
  </div>
</section>

{rel_section}

{jump}

<section>
  <div class="wrap">
    <h2 class="sec-title">使用说明</h2>
    <div class="note">
      · 仪表盘为交互页面，需联网加载；其数据口径以原文件为准。<br>
      · 上方成果/地图链接均来自孟老师升学规划工具集（资料库节点「集合全部升学规划工具平台」）。<br>
      · 本页为内容展示用途，版权与相关权益归原作者所有。
    </div>
  </div>
</section>

<section class="contact">
  <div class="wrap">
    <div class="contact-top">
      <div>
        <h2 class="sec-title">升学规划咨询 · 联系孟老师</h2>
        <p class="sec-sub">产业、专业、院校、报考一站式规划，电话直接沟通更高效。</p>
      </div>
      <a class="cta-phone" href="tel:18931577792">{PHONE_SVG}18931577792</a>
    </div>
    <div style="margin-top:22px;background:#fff;border-radius:16px;padding:14px 14px 11px;display:inline-block;box-shadow:0 8px 24px rgba(7,42,64,.10)">
      <img src="../assets/qr-wechat.jpg" alt="微信扫码添加孟老师" style="width:178px;height:auto;border-radius:10px;display:block">
      <div style="font-size:12.5px;color:#3E5A70;margin-top:8px;font-weight:600">微信扫码，添加孟老师为朋友</div>
    </div>
    <div class="cc-hook"><b>{prov_full}家长专属</b>加微信备注「{prov_full}」，免费领本省本科院校分布与 2026 投档速查资料，并享一对一升学评估。</div>
    <div class="contact-tags">
      <span>高考志愿填报</span>
      <span>产业选专业</span>
      <span>院校择校</span>
      <span>升学就业路径</span>
    </div>
  </div>
</section>

<footer>
  <div class="wrap">
    <b>博辰序 · 全国各省本科院校分布地图</b><br>
    内容来自孟老师升学规划工具集（资料库节点「集合全部升学规划工具平台」）。<br>
    规划咨询：孟老师 · 电话 <a href="tel:18931577792">18931577792</a> · 本网站为内容展示用途，版权与相关权益归原作者所有。
  </div>
</footer>
{MODAL_HTML}
</body>
</html>
'''
    fn = os.path.join(P_DIR, prov_full + ".html")
    with open(fn, "w", encoding="utf-8") as fp:
        fp.write(html)
    return fn

made = []
for prov, dash in provinces:
    made.append(build_page(FULL.get(prov, prov), prov, dash, is_nation=False))
for prov, dash in nation:
    made.append(build_page("全国总览", "全国", dash, is_nation=True))

# ---- sitemap.xml ----
def loc(path):  # path like "/p/河北省.html"
    return BASE + "/" + "/".join(urllib.parse.quote(p, safe="") for p in path.split("/"))
today = datetime.date.today().isoformat()
urls = [("/index.html", "1.0"), ("/map.html", "0.9"), ("/tools.html", "0.8")]
for prov, _ in provinces:
    urls.append((f"/p/{FULL.get(prov,prov)}.html", "0.8"))
for prov, _ in nation:
    urls.append(("/p/全国总览.html", "0.8"))
sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for path, pri in urls:
    sitemap.append(f"  <url><loc>{loc(path)}</loc><lastmod>{today}</lastmod><priority>{pri}</priority></url>")
sitemap.append("</urlset>")
with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as fp:
    fp.write("\n".join(sitemap) + "\n")

# ---- robots.txt ----
with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as fp:
    fp.write(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")

print("landing pages:", len(made))
print("sitemap.xml entries:", len(urls))
print("robots.txt written")
