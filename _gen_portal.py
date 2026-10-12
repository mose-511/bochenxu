# -*- coding: utf-8 -*-
# 博辰序 · 高考升学决策地图 —— 首页生成脚本（2026-10-11 v3 精修版）
# v3：Hero 右侧新增「全国高校资源网络」视觉；搜索下增加升学分析引导；
#     五步标题修正；16 项成果降级为「升学工具箱」6 入口，完整成果+31省入口迁至 tools.html。
# 数据逻辑不变：16项成果、31省入口、弹窗、统计、OG 全部保留（首页+工具总览页两处承载）。
import os, re, json, io, urllib.parse

# —— 百度统计接入点：把统计 ID 写入同目录 stats_id.txt 即自动启用 ——
_stats_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stats_id.txt")
STATS_ID = open(_stats_file, encoding="utf-8").read().strip() if os.path.exists(_stats_file) else ""
STATS_SNIPPET = ""
if STATS_ID:
    STATS_SNIPPET = ("<script>var _hmt=_hmt||[];(function(){var hm=document.createElement('script');"
                     "hm.src='https://hm.baidu.com/hm.js?" + STATS_ID + "';"
                     "var s=document.getElementsByTagName('script')[0];s.parentNode.insertBefore(hm,s);})();</script>")
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(ROOT, "results")
OG_DIR = os.path.join(ROOT, "og")
os.makedirs(OG_DIR, exist_ok=True)

BASE = "https://star-map-folder.app.workbuddy.host"

# ---- 读取 results 文件，分类 ----
files = [f for f in os.listdir(RESULTS) if os.path.isfile(os.path.join(RESULTS, f))]
dash_re = re.compile(r"^(.+?)产业-本科专业速查仪表盘\.html$")

prov_dashboards = []   # (prov, filename)
other_dashboards = []  # 全国总览等
works = []             # 成果 .html / .docx

PROV_ORDER = ["北京","天津","河北","山西","内蒙古","辽宁","吉林","黑龙江","上海","江苏",
              "浙江","安徽","福建","江西","山东","河南","湖北","湖南","广东","广西",
              "海南","重庆","四川","贵州","云南","西藏","陕西","甘肃","青海","宁夏","新疆"]

for f in files:
    m = dash_re.match(f)
    if m:
        prov = m.group(1)
        if prov == "全国":
            other_dashboards.append(f)
        else:
            prov_dashboards.append((prov, f))
    elif f == "全国产业-本科专业总览仪表盘.html":
        other_dashboards.append(f)
    elif f in ("_ok.js",) or f.endswith(".md") or f.startswith("1054个国家级产业集群解读与专业分析"):
        continue
    else:
        works.append(f)

def prov_key(p):
    try: return PROV_ORDER.index(p[0])
    except ValueError: return 999
prov_dashboards.sort(key=prov_key)
other_dashboards.sort()
works.sort()

# 成果友好名
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
    "红宝书-全国分省特色院校全景梳理与决策参考(2026年6月版).docx": "全国分省特色院校全景红宝书（2026年6月版 · docx）",
    "职业本科院校择校手册.html": "职业本科院校择校手册",
}
def work_title(f):
    return WORK_TITLE.get(f, os.path.splitext(f)[0])

def enc(f):
    return "results/" + urllib.parse.quote(f)

def urlsafe(s):
    return urllib.parse.quote(s, safe="")

# 短省名 → 落地页文件全名（p/ 目录文件为全名，如 河北省.html）
PROV_FULL = {"北京":"北京市","天津":"天津市","河北":"河北省","山西":"山西省","内蒙古":"内蒙古自治区",
    "辽宁":"辽宁省","吉林":"吉林省","黑龙江":"黑龙江省","上海":"上海市","江苏":"江苏省",
    "浙江":"浙江省","安徽":"安徽省","福建":"福建省","江西":"江西省","山东":"山东省",
    "河南":"河南省","湖北":"湖北省","湖南":"湖南省","广东":"广东省","广西":"广西壮族自治区",
    "海南":"海南省","重庆":"重庆市","四川":"四川省","贵州":"贵州省","云南":"云南省",
    "西藏":"西藏自治区","陕西":"陕西省","甘肃":"甘肃省","青海":"青海省","宁夏":"宁夏回族自治区",
    "新疆":"新疆维吾尔自治区"}

# 分组语义 SVG 图标（线性，24x24，currentColor）
ICONS = {
    "产业 · 专业映射": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><rect x="3" y="12" width="4" height="9"/><rect x="10" y="7" width="4" height="14"/><rect x="17" y="3" width="4" height="18"/></svg>',
    "选科 · 选专业": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><rect x="3" y="3" width="8" height="8" rx="1.5"/><rect x="13" y="3" width="8" height="8" rx="1.5"/><rect x="3" y="13" width="8" height="8" rx="1.5"/><rect x="13" y="13" width="8" height="8" rx="1.5"/></svg>',
    "志愿填报 · 报考决策": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 5h16l-6 7v6l-4 2v-8z"/></svg>',
    "院校认知 · 择校": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-5 9 5"/><path d="M5 10v8h14v-8"/><path d="M9 18v-5h6v5"/></svg>',
    "升学 · 就业路径": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M5 19V9l7-5 7 5v10"/><path d="M12 8v8"/><path d="M9 11l3 3 3-3"/></svg>',
    "备考 · 提分": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 20l4-1 9-9-3-3-9 9z"/><path d="M14 6l3 3"/></svg>',
}
PHONE_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.56 12.56 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.56 12.56 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>'
SEARCH_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4-4"/></svg>'

# ---- 按服务场景分组（依据成果功能属性归类，便于访客按需取用）----
GROUPS = [
    ("产业 · 专业映射", "把「产业在哪、对应什么专业」前置到志愿填报之前",
        ["中国1054个国家级产业集群全景解读与专业分析.html",
         "31省产业-本科专业择校指南网站.html",
         "全国144城产业调研地图.html"]),
    ("选科 · 选专业", "从科目组合对路到专业目录查询",
        ["2027河北选科专业对照表.html",
         "专业介绍查询系统.html"]),
    ("志愿填报 · 报考决策", "各省怎么报、投档数据怎么查",
        ["31省高考报考逻辑详解.html",
         "河北高考投档数据_总查询台_2026vs2025.html",
         "河北省院校录取查询系统.html"]),
    ("院校认知 · 择校", "更名、特色院校、职业本科一本清",
        ["已审批更名大学全汇总.html",
         "红宝书-全国分省特色院校全景梳理与决策参考(2026年6月版).docx",
         "职业本科院校择校手册.html"]),
    ("升学 · 就业路径", "考研、选调、就业质量一眼看",
        ["2026各省选调备考规划.html",
         "本科专业对应的研究生专业查询系统.html",
         "就业与教学质量报告决策参考380所.html",
         "民营企业500强调研完整报告.html"]),
    ("备考 · 提分", "河北九科合订，临门一脚",
        ["河北高考九科合订本.html"]),
]
grouped = set()
for _, _, fs in GROUPS:
    grouped.update(fs)
missing = [w for w in works if w not in grouped]
assert not missing, f"以下成果未分组：{missing}"

DOC_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M6 3h9l4 4v14H6z"/><path d="M15 3v4h4"/><path d="M9 12h7M9 16h7"/></svg>'
CHEV = '<svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg>'

# ---- 生成 HTML 片段 ----
def work_card(f):
    t = work_title(f)
    return (f'<a class="card" href="{enc(f)}" target="_blank" rel="noopener" '
            f'data-search="{t} {f}">\n'
            f'  <div class="card-ic">{DOC_ICON}</div>\n'
            f'  <div class="card-t">{t}</div>\n'
            f'  <div class="card-go">打开 →</div>\n'
            f'</a>')

def group_block(idx, name, desc, fs):
    cards = "\n".join(work_card(f) for f in fs)
    tag = f"0{idx}" if idx < 10 else str(idx)
    ic = ICONS.get(name, DOC_ICON)
    return (f'<div class="group">\n'
            f'  <div class="group-h" onclick="toggleGroup(this)">\n'
            f'    <span class="gic">{ic}</span>'
            f'<span class="tag">{tag}</span>'
            f'<span class="gname">{name}</span><span class="gdesc">{desc}</span>{CHEV}\n'
            f'  </div>\n'
            f'  <div class="grid">\n{cards}\n  </div>\n'
            f'</div>')

groups_html = "\n".join(group_block(i+1, n, d, fs) for i, (n, d, fs) in enumerate(GROUPS))

def prov_card(prov, f):
    full = PROV_FULL.get(prov, prov)  # 「全国总览」等保持原名
    return (f'<a class="pcard" href="p/{urlsafe(full)}.html" '
            f'data-search="{prov}">\n'
            f'  <span class="pdot"></span>{prov}\n'
            f'</a>')

prov_html = "\n".join(prov_card(p, f) for p, f in prov_dashboards)
other_html = "\n".join(prov_card("全国总览", f) for f in other_dashboards)

total_works = len(works)
total_prov = len(prov_dashboards)

# ---- 首页「升学工具箱」6 个最常用入口（全部对应真实文件/页面）----
TOOLBOX = [
    ("全国高校地图", "1403 所本科院校地理分布，点城市看产业、点院校看专业。", "map.html", False,
     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21V8l9-5 9 5v13"/><path d="M9 21v-6h6v6"/><path d="M3 21h18"/></svg>'),
    ("专业查询", "专业介绍、培养方向、开设院校，逐项看清再选。", "results/" + urllib.parse.quote("专业介绍查询系统.html"), True,
     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><rect x="3" y="3" width="8" height="8" rx="1.5"/><rect x="13" y="3" width="8" height="8" rx="1.5"/><rect x="3" y="13" width="8" height="8" rx="1.5"/><rect x="13" y="13" width="8" height="8" rx="1.5"/></svg>'),
    ("院校对比", "380 所院校就业与教学质量横向对照，择校有依据。", "results/" + urllib.parse.quote("就业与教学质量报告决策参考380所.html"), True,
     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M8 3v18M16 3v18"/><path d="M4 7h8M12 17h8"/><path d="M4 7l-1.5 2M20 17l1.5-2"/></svg>'),
    ("河北捡漏", "河北投档数据 2026vs2025 总查询，低分高就看位次变化。", "results/" + urllib.parse.quote("河北高考投档数据_总查询台_2026vs2025.html"), True,
     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19h16M6 19V9l4 3V7l4 3V5l4 4v10"/></svg>'),
    ("选科查询", "2027 河北选科与专业对照，高一选科不踩坑。", "results/" + urllib.parse.quote("2027河北选科专业对照表.html"), True,
     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 17l6-6-6-6"/><path d="M12 19h8"/></svg>'),
    ("招生规则", "31 省高考报考逻辑详解，各省规则一册通。", "results/" + urllib.parse.quote("31省高考报考逻辑详解.html"), True,
     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 5h16l-6 7v6l-4 2v-8z"/></svg>'),
]

def tbox_card(name, desc, href, blank, ic):
    tgt = ' target="_blank" rel="noopener"' if blank else ''
    return (f'<a class="tbox" href="{href}"{tgt}>\n'
            f'  <span class="tbox-ic">{ic}</span>\n'
            f'  <span class="tbox-tx"><b>{name}</b><small>{desc}</small></span>\n'
            f'</a>')

toolbox_html = "\n".join(tbox_card(*t) for t in TOOLBOX)

# ---- Hero 搜索索引（省 + 全部工具，静态注入；决策链节点从 DOM 读取）----
prov_items = [{"t": f"{p} {PROV_FULL.get(p,p)} 产业 专业 速查", "h": f"p/{urlsafe(PROV_FULL.get(p,p))}.html"} for p, _ in prov_dashboards]
prov_items += [{"t": "全国总览 产业 专业 仪表盘", "h": f"p/{urlsafe('全国总览')}.html"} for _ in other_dashboards]
tool_items = [{"t": work_title(f) + " " + f, "h": enc(f)} for f in works]
tool_items.append({"t": "高校地图 院校分布 找大学 1403所本科院校", "h": "map.html"})
prov_json = json.dumps(prov_items, ensure_ascii=False)
tool_json = json.dumps(tool_items, ensure_ascii=False)

# ---- 门户 OG 卡片 ----
def draw_og(path, title, subtitle, tagline):
    W, H = 1200, 630
    TOP = (7, 32, 63)      # 深蓝
    BOT = (13, 74, 130)    # 蓝
    WHITE = (255, 255, 255)
    PALE = (219, 234, 247)
    ORANGE = (255, 158, 84)
    reg = "/c/Windows/Fonts/Noto Sans SC (TrueType).otf"
    bold = "/c/Windows/Fonts/Noto Sans SC Bold (TrueType).otf"
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
    img = Image.blend(img, glow, 0.08)
    d = ImageDraw.Draw(img)
    d.text((80, 58), "博辰序 · BOCHENXU", font=ft(reg, 26), fill=PALE)
    n = len(title)
    size = 108 if n <= 4 else 96 if n <= 5 else 84 if n <= 6 else 74
    d.text((W // 2, H // 2 - 66), title, font=ft(bold, size), fill=WHITE, anchor="mm")
    d.text((W // 2, H // 2 + 18), subtitle, font=ft(reg, 38), fill=PALE, anchor="mm")
    if tagline:
        d.text((W // 2, H // 2 + 78), tagline, font=ft(reg, 32), fill=ORANGE, anchor="mm")
    d.line([(80, H - 112), (W - 80, H - 112)], fill=(120, 158, 196))
    d.text((80, H - 82), "孟老师 · 升学规划咨询", font=ft(reg, 30), fill=WHITE)
    d.text((W - 80, H - 82), "18931577792", font=ft(bold, 36), fill=WHITE, anchor="rm")
    img.save(path, "PNG")

draw_og(os.path.join(OG_DIR, "index.png"), "高考升学决策地图",
        "1403 所本科院校 × 31 省产业-专业速查",
        "院校 · 专业 · 城市 · 产业 · 就业 一站决策")
draw_og(os.path.join(OG_DIR, "map.png"), "高校探索地图 · 博辰序",
        "点城市看产业，点院校看匹配专业",
        "1403 所本科院校 地理分布 + 产业叠加")

CSS = '''
  :root{
    --navy:#0A2A4A; --navy2:#0E3A66; --blue:#1B5FA8; --blue-l:#2E7BC4;
    --ink:#13293D; --ink2:#3E5A73; --ink3:#7B93A8;
    --orange:#F97316; --orange-d:#EA580C; --orange-bg:#FFF3EA;
    --line:#DCE6F0; --bg:#F5F8FB; --card:#FFFFFF;
    --shadow:0 6px 22px rgba(13,42,74,.08);
  }
  *{box-sizing:border-box}
  html{scroll-behavior:smooth}
  html,body{margin:0;padding:0;background:var(--bg);color:var(--ink);
    font-family:"Microsoft YaHei","PingFang SC","Noto Sans SC",sans-serif;}
  a{text-decoration:none;color:inherit}
  .wrap{max-width:1160px;margin:0 auto;padding:0 22px}

  /* ===== 顶部导航 ===== */
  .nav{position:sticky;top:0;z-index:50;background:var(--navy);color:#fff;
    box-shadow:0 2px 14px rgba(7,26,47,.35)}
  .nav-in{max-width:1160px;margin:0 auto;padding:0 18px;display:flex;align-items:center;gap:10px;height:58px}
  .logo{display:flex;align-items:baseline;gap:8px;flex:none;margin-right:8px}
  .logo b{font-size:19px;letter-spacing:2px;color:#fff;font-weight:800}
  .logo span{font-size:10.5px;letter-spacing:2.5px;color:#8FB0D2}
  .nav-links{display:flex;align-items:center;gap:4px;overflow-x:auto;-webkit-overflow-scrolling:touch;
    scrollbar-width:none;flex:1;min-width:0;white-space:nowrap}
  .nav-links::-webkit-scrollbar{display:none}
  .nav-links a{flex:none;padding:7px 13px;border-radius:8px;font-size:14.5px;font-weight:600;color:#C9DAEC;transition:.15s}
  .nav-links a:hover{color:#fff;background:rgba(255,255,255,.10)}
  .nav-links a.nav-cta{color:#fff;background:var(--orange);font-weight:700;margin-left:6px}
  .nav-links a.nav-cta:hover{background:var(--orange-d)}

  /* ===== Hero ===== */
  .hero{background:linear-gradient(160deg,#071E36 0%,#0A2A4A 46%,#123E6B 100%);
    color:#fff;padding:64px 0 58px;position:relative;overflow:hidden}
  .hero::before{content:"";position:absolute;left:-100px;bottom:-160px;width:420px;height:420px;
    background:radial-gradient(circle,rgba(249,115,22,.10),transparent 70%);pointer-events:none}
  .hero .wrap{position:relative;z-index:1}
  .hero-grid{display:grid;grid-template-columns:1.04fr .96fr;gap:46px;align-items:center}
  .kick{letter-spacing:5px;font-size:12.5px;font-weight:700;color:#9DBBDA}
  .hero h1{margin:14px 0 8px;font-size:44px;line-height:1.22;letter-spacing:1px;font-weight:800;color:#fff}
  .hero h1 .hl{color:#FFB27A}
  .hero .sub{font-size:17px;font-weight:700;color:#D7E5F4;letter-spacing:1px;margin:0 0 10px}
  .hero p.desc{margin:0;font-size:15.5px;color:#B9CFE5;max-width:640px;line-height:1.8}
  .cta-row{display:flex;gap:14px;align-items:center;margin-top:26px;flex-wrap:wrap}
  .cta{display:inline-flex;align-items:center;gap:10px;white-space:nowrap;
    background:var(--orange);color:#fff;font-weight:800;font-size:16px;
    padding:13px 28px;border-radius:10px;box-shadow:0 10px 26px rgba(249,115,22,.35);transition:.18s}
  .cta:hover{background:var(--orange-d);transform:translateY(-2px)}
  .cta-outline{display:inline-flex;align-items:center;gap:10px;
    background:rgba(255,255,255,.08);color:#fff;font-weight:700;font-size:16px;
    padding:13px 24px;border-radius:10px;border:1px solid rgba(255,255,255,.38);transition:.18s}
  .cta-outline:hover{background:rgba(255,255,255,.16);transform:translateY(-2px)}
  .cta-outline svg{width:20px;height:20px}
  /* hero 搜索 */
  .hsearch{margin-top:26px;max-width:600px;position:relative}
  .hsearch-box{display:flex;align-items:center;gap:10px;background:#fff;border-radius:12px;
    padding:12px 18px;box-shadow:0 14px 40px rgba(4,18,33,.45)}
  .hsearch-box svg{width:20px;height:20px;color:var(--ink3);flex:none}
  .hsearch-box input{border:none;outline:none;flex:1;font-size:15.5px;color:var(--ink);
    background:transparent;font-family:inherit;min-width:0}
  .hsearch-box input::placeholder{color:#9BB0C2}
  .hsug{position:absolute;left:0;right:0;top:calc(100% + 8px);background:#fff;border-radius:12px;
    box-shadow:0 18px 48px rgba(4,18,33,.30);overflow:hidden;display:none;z-index:30}
  .hsug.on{display:block}
  .hsug a{display:flex;align-items:center;gap:10px;padding:11px 16px;font-size:14.5px;color:var(--ink);
    border-bottom:1px solid #F0F4F8}
  .hsug a:last-child{border-bottom:none}
  .hsug a:hover{background:#F3F8FD}
  .hsug .badge{flex:none;font-size:11px;font-weight:800;padding:3px 9px;border-radius:20px;letter-spacing:1px}
  .hsug .badge.p{background:#E8F1FA;color:var(--blue)}
  .hsug .badge.w{background:var(--orange-bg);color:var(--orange-d)}
  .hsug .badge.c{background:#FDF0E6;color:#C2570A}
  .hsug .badge.m{background:#EAF7EE;color:#1E7B43}
  .hsearch-hint{margin-top:10px;font-size:12.5px;color:#7E9CBA}
  .hsearch-hint b{color:#C9DAEC;font-weight:600}
  .hstart{margin-top:14px;padding-top:14px;border-top:1px solid rgba(255,255,255,.14);
    display:flex;align-items:center;gap:8px 16px;flex-wrap:wrap;font-size:13.5px;color:#A9C3DE;line-height:1.6}
  .hstart b{color:#DCE9F6;font-weight:700}
  .hstart .lnk{color:#FFB27A;font-weight:800;cursor:pointer;white-space:nowrap}
  .hstart .lnk:hover{color:#fff}

  /* ===== Hero 右侧：全国高校资源网络视觉 ===== */
  .hero-map{min-width:0}
  .hero-map{min-width:0}
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
  .hero-tip b{color:#FFB27A;font-weight:700}
  .trust-note{text-align:center;margin:26px 0 0;font-size:15px;color:var(--ink2)}
  .trust-note b{color:var(--ink);font-weight:800}
  .chain-cta{display:inline-flex;align-items:center;gap:8px;margin-top:18px;
    font-size:15.5px;font-weight:800;color:var(--orange-d)}
  .chain-cta:hover{color:var(--orange)}

  /* ===== sections ===== */
  section{padding:64px 0}
  .sec-title{font-size:26px;font-weight:800;color:var(--ink);margin:0 0 6px}
  .sec-sub{color:var(--ink2);font-size:15px;margin:0 0 26px;line-height:1.7}
  .sec-head{display:flex;align-items:flex-end;justify-content:space-between;gap:16px;flex-wrap:wrap;margin-bottom:24px}
  .sec-head .t{max-width:72%}
  .sec-head .sec-title{margin-bottom:4px}
  .sec-head .sec-sub{margin-bottom:0}

  /* ===== 四大核心入口 ===== */
  .feats{display:grid;grid-template-columns:repeat(4,1fr);gap:18px}
  .feat{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:24px 22px;
    box-shadow:var(--shadow);transition:.18s;display:flex;flex-direction:column}
  .feat:hover{transform:translateY(-4px);border-color:var(--blue-l);box-shadow:0 14px 34px rgba(13,42,74,.14)}
  .feat-ic{width:46px;height:46px;border-radius:12px;display:flex;align-items:center;justify-content:center;margin-bottom:14px}
  .feat-ic svg{width:24px;height:24px}
  .fi-blue{background:#E8F1FA;color:var(--blue)}
  .fi-orange{background:var(--orange-bg);color:var(--orange)}
  .fi-green{background:#EAF7EE;color:#1E7B43}
  .fi-navy{background:#E9EDF5;color:var(--navy)}
  .feat h3{margin:0 0 8px;font-size:18px;color:var(--ink)}
  .feat p{margin:0 0 18px;font-size:13.5px;color:var(--ink2);line-height:1.65;flex:1}
  .feat-go{display:inline-flex;align-items:center;gap:6px;font-size:14px;font-weight:800;color:var(--blue)}
  .feat.go-orange .feat-go{color:var(--orange-d)}
  .feat-go svg{width:15px;height:15px;transition:transform .15s}
  .feat:hover .feat-go svg{transform:translateX(3px)}

  /* ===== 信任数据卡 ===== */
  .trust{background:linear-gradient(180deg,#FFFFFF,#EFF5FB)}
  .tgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
  .tcard{background:var(--card);border:1px solid var(--line);border-radius:14px;text-align:center;
    padding:26px 12px;box-shadow:var(--shadow)}
  .tcard b{display:block;font-size:34px;font-weight:800;color:var(--navy);font-family:Georgia,"Microsoft YaHei",serif;line-height:1.1}
  .tcard b i{font-style:normal;font-size:16px;color:var(--orange);margin-left:2px}
  .tcard span{display:block;margin-top:8px;font-size:13.5px;color:var(--ink2)}

  /* ===== 专业×产业×就业 ===== */
  .chain{display:grid;grid-template-columns:1fr 34px 1fr 34px 1fr 34px 1fr;gap:0;align-items:stretch;margin-top:8px}
  .chain-node{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px 18px;
    box-shadow:var(--shadow);display:flex;flex-direction:column;transition:.18s}
  .chain-node:hover{border-color:var(--blue-l);transform:translateY(-3px)}
  .chain-node .lab{font-size:11.5px;font-weight:800;letter-spacing:2px;color:var(--orange-d);margin-bottom:8px}
  .chain-node .val{font-size:16px;font-weight:800;color:var(--ink);line-height:1.45;flex:1}
  .chain-node .val small{display:block;font-size:12.5px;font-weight:400;color:var(--ink2);margin-top:6px;line-height:1.6}
  .chain-node .lnk{margin-top:12px;font-size:12.5px;font-weight:700;color:var(--blue)}
  .chain-arrow{display:flex;align-items:center;justify-content:center;color:var(--orange)}
  .chain-arrow svg{width:22px;height:22px}
  .chain-note{margin-top:18px;font-size:13.5px;color:var(--ink2);background:var(--orange-bg);
    border-left:3px solid var(--orange);border-radius:0 10px 10px 0;padding:13px 16px;line-height:1.7}

  /* ===== 五步决策 ===== */
  .plan{background:linear-gradient(160deg,#071E36,#0E3A66);color:#fff}
  .plan .sec-title{color:#fff}
  .plan .sec-sub{color:#AFC8E2}
  .steps{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;margin-top:6px}
  .step{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.14);border-radius:14px;padding:20px 16px;position:relative}
  .step .no{font-size:12px;font-weight:800;color:#FFB27A;letter-spacing:1px}
  .step h4{margin:8px 0 6px;font-size:16.5px;color:#fff}
  .step p{margin:0;font-size:12.5px;color:#AFC8E2;line-height:1.65}
  .plan-foot{margin-top:30px;display:flex;align-items:center;gap:16px;flex-wrap:wrap}
  .plan-foot .hint{font-size:13px;color:#8FAECF;line-height:1.6}

  /* ===== 升学工具箱（首页只放 6 个最常用入口）===== */
  .tbgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:2px 30px;margin-top:4px}
  .tbox{display:flex;align-items:flex-start;gap:14px;padding:17px 10px;
    border-bottom:1px solid var(--line);transition:.15s}
  .tbox:hover{background:#fff;border-radius:12px;transform:translateY(-1px);
    box-shadow:0 8px 20px rgba(13,42,74,.08)}
  .tbox-ic{flex:none;width:34px;height:34px;border-radius:10px;background:#E8F1FA;color:var(--blue);
    display:flex;align-items:center;justify-content:center}
  .tbox-ic svg{width:19px;height:19px}
  .tbox-tx{min-width:0}
  .tbox-tx b{display:block;font-size:15.5px;font-weight:800;color:var(--ink)}
  .tbox-tx small{display:block;margin-top:3px;font-size:12.5px;color:var(--ink2);line-height:1.6}
  .viewall{display:inline-flex;align-items:center;gap:8px;margin-top:22px;
    font-size:15px;font-weight:800;color:var(--blue);transition:.15s}
  .viewall:hover{color:var(--navy)}
  .viewall svg{width:16px;height:16px}

  /* ===== 工具总览页（tools.html）共用样式 ===== */
  .grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
  .card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px;
    box-shadow:var(--shadow);transition:.18s;display:flex;flex-direction:column;gap:10px}
  .card:hover{transform:translateY(-3px);border-color:var(--blue-l);box-shadow:0 12px 30px rgba(13,42,74,.15)}
  .card-ic{width:30px;height:30px;color:var(--blue)}
  .card-t{font-size:15.5px;font-weight:700;color:var(--ink);line-height:1.5}
  .card-go{margin-top:auto;font-size:13px;color:var(--blue);font-weight:700}
  .group{margin-bottom:26px;border:1px solid var(--line);border-radius:16px;background:#fff;padding:18px 20px}
  .group-h{display:flex;align-items:center;gap:12px;margin:0 0 16px;flex-wrap:wrap;cursor:pointer;user-select:none}
  .group-h .gic{width:24px;height:24px;color:var(--blue);flex:none}
  .group-h .tag{font-size:12px;font-weight:800;color:#fff;background:var(--blue);
    padding:4px 11px;border-radius:20px;letter-spacing:1px}
  .group-h .gname{font-size:18px;font-weight:800;color:var(--ink)}
  .group-h .gdesc{font-size:13.5px;color:var(--ink2)}
  .group-h .chev{margin-left:auto;width:20px;height:20px;color:var(--ink3);transition:transform .2s}
  .group.collapsed .chev{transform:rotate(-90deg)}
  .group.collapsed .grid{display:none}
  .tools{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
  .search{display:flex;align-items:center;gap:8px;background:#fff;border:1px solid var(--line);
    border-radius:24px;padding:9px 16px;box-shadow:var(--shadow)}
  .search svg{width:16px;height:16px;flex:none;opacity:.55}
  .search input{border:none;outline:none;font-size:14px;width:190px;background:transparent;color:var(--ink);font-family:inherit}
  .btn{border:1px solid var(--blue);color:var(--blue);background:#fff;border-radius:24px;
    padding:9px 16px;font-size:13.5px;font-weight:700;cursor:pointer;transition:.15s;font-family:inherit}
  .btn:hover{background:var(--blue);color:#fff}
  .pgrid{display:grid;grid-template-columns:repeat(6,1fr);gap:12px}
  .pcard{background:var(--card);border:1px solid var(--line);border-radius:11px;padding:14px 10px;
    text-align:center;font-size:15px;font-weight:700;color:var(--ink);box-shadow:var(--shadow);
    transition:.18s;display:flex;align-items:center;justify-content:center;gap:7px}
  .pcard:hover{border-color:var(--blue);color:var(--blue);transform:translateY(-2px)}
  .pdot{width:8px;height:8px;border-radius:50%;background:var(--orange)}
  .pgrid .pcard:first-child{background:linear-gradient(135deg,var(--navy),var(--blue));color:#fff;border:none}
  .pgrid .pcard:first-child .pdot{background:#fff}
  .no-hit{color:var(--ink3);font-size:14px;padding:14px 2px;display:none}
  .note{background:#fff;border:1px solid var(--line);border-radius:12px;
    padding:16px 18px;font-size:13.5px;color:var(--ink2);line-height:1.7;margin-top:8px}
  .pagehead{background:linear-gradient(160deg,#071E36,#0E3A66);color:#fff;padding:44px 0 40px}
  .pagehead .kick{letter-spacing:5px;font-size:12.5px;font-weight:700;color:#9DBBDA}
  .pagehead h1{margin:12px 0 8px;font-size:32px;font-weight:800;color:#fff}
  .pagehead p{margin:0;font-size:14.5px;color:#B9CFE5;line-height:1.8}

  /* ===== 联系区 ===== */
  .contact{background:#fff;border-top:1px solid var(--line)}
  .contact-in{display:flex;align-items:center;justify-content:space-between;gap:32px;flex-wrap:wrap;padding:54px 0}
  .contact-in .t{max-width:540px}
  .contact-card{background:linear-gradient(160deg,var(--navy),var(--blue));color:#fff;border-radius:18px;
    padding:26px 30px;min-width:280px;box-shadow:0 14px 34px rgba(10,42,74,.28)}
  .cc-name{font-size:16px;opacity:.9;margin-bottom:4px}
  .cc-tel{display:flex;align-items:center;gap:10px;font-size:28px;font-weight:800;color:#fff;margin-bottom:8px}
  .cc-tel svg{width:24px;height:24px}
  .cc-sub{font-size:13px;opacity:.92}

  /* ===== footer ===== */
  footer{background:#071E36;color:#8FAECF;padding:38px 0;font-size:13px;line-height:1.8}
  footer b{color:#D8E6F4}
  footer a{color:#FFB27A}
  footer a:hover{color:#fff}

  /* ===== 移动端底部咨询条 ===== */
  .mbbar{display:none;position:fixed;left:0;right:0;bottom:0;z-index:60;
    background:#fff;border-top:1px solid var(--line);box-shadow:0 -6px 22px rgba(13,42,74,.12);
    padding:9px 14px calc(9px + env(safe-area-inset-bottom));gap:10px}
  .mbbar a{flex:1;display:flex;align-items:center;justify-content:center;gap:7px;
    border-radius:10px;padding:11px 8px;font-size:14.5px;font-weight:800}
  .mbbar .mb-tel{background:var(--navy);color:#fff}
  .mbbar .mb-wx{background:var(--orange);color:#fff}
  .mbbar svg{width:17px;height:17px;flex:none}

  /* ===== 响应式 ===== */
  @media(max-width:1080px){
    .hero-grid{grid-template-columns:1fr;gap:34px}
    .hero-map{max-width:430px;margin:0 auto;width:100%}
  }
  @media(max-width:980px){
    .feats{grid-template-columns:repeat(2,1fr)}
    .tgrid{grid-template-columns:repeat(2,1fr)}
    .steps{grid-template-columns:repeat(2,1fr)}
    .grid{grid-template-columns:repeat(2,1fr)}
    .pgrid{grid-template-columns:repeat(4,1fr)}
    .chain{grid-template-columns:1fr;gap:0}
    .chain-arrow{transform:rotate(90deg);height:34px}
    .hero h1{font-size:34px}
    .sec-head .t{max-width:100%}
    .contact-in{flex-direction:column;align-items:flex-start}
    .hero{padding:52px 0 46px}
    .tbgrid{grid-template-columns:repeat(2,1fr);gap:0 22px}
  }
  @media(max-width:640px){
    section{padding:46px 0}
    .hero h1{font-size:28px}
    .hero .sub{font-size:14.5px}
    .hero p.desc{font-size:14px}
    .hero-stats{gap:7px;margin-bottom:14px;justify-content:center}
    .hero-stats .st{padding:7px 11px}
    .hero-stats .st b{font-size:17px}
    .hero-stats .st span{font-size:11px}
    .hero-tip{font-size:12px}
    .trust-note{font-size:13.5px;margin-top:20px}
    .feats{grid-template-columns:repeat(2,1fr);gap:12px}
    .feat{padding:18px 14px}
    .feat h3{font-size:16px}
    .feat p{font-size:12.5px}
    .tbgrid{grid-template-columns:1fr;gap:0}
    .pgrid{grid-template-columns:repeat(3,1fr)}
    .grid{grid-template-columns:1fr}
    .tcard b{font-size:27px}
    .cta-row .cta,.cta-row .cta-outline{width:100%;justify-content:center}
    .hsearch-box{padding:11px 14px}
    .contact-card{min-width:auto;width:100%}
    /* 五步流程：横向滑动，一屏一步 */
    .steps{display:flex;overflow-x:auto;scroll-snap-type:x mandatory;gap:12px;
      padding-bottom:8px;-webkit-overflow-scrolling:touch}
    .step{flex:0 0 76%;scroll-snap-align:start}
    .pagehead h1{font-size:25px}
    body{padding-bottom:62px}  /* 防底部固定咨询条遮挡 */
    .mbbar{display:flex}
    .logo span{display:none}
  }
'''

# ---- 首页 JS：Hero 搜索（静态索引 + DOM 决策链）+ 弹窗 ----
JS_HOME = '''
  function openContact(){document.getElementById('cmodal').classList.add('on');document.body.style.overflow='hidden';if(window._hmt){try{_hmt.push(['_trackEvent','contact','open','portal'])}catch(e){}}}
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
})();
  function closeContact(){document.getElementById('cmodal').classList.remove('on');document.body.style.overflow='';}
  document.addEventListener('keydown',function(e){if(e.key==='Escape')closeContact();});

  /* ===== Hero 全站搜索：即时建议（省 + 全部工具 + 决策链 + 兜底高校地图）===== */
  (function(){
    var input = document.getElementById('heroq');
    var box = document.getElementById('hsug');
    if(!input || !box) return;
    var items = [];
    PROV_ITEMS.forEach(function(it){ items.push({t:it.t, h:it.h, k:'p', lab:'省速查'}); });
    TOOL_ITEMS.forEach(function(it){ items.push({t:it.t, h:it.h, k:'w', lab:'工具'}); });
    document.querySelectorAll('.chain-node[data-search]').forEach(function(n){
      items.push({t:n.getAttribute('data-search'), h:n.querySelector('.lnk').getAttribute('href'), k:'c', lab:'决策链'});
    });
    function esc(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
    function render(q){
      q = q.trim().toLowerCase();
      if(!q){ box.classList.remove('on'); box.innerHTML=''; return; }
      var hits = items.filter(function(it){ return it.t.toLowerCase().indexOf(q) !== -1; }).slice(0,8);
      var html = hits.map(function(it){
        return '<a href="'+it.h+'"><span class="badge '+it.k+'">'+it.lab+'</span>'+esc(it.t.split(' ')[0])+'</a>';
      }).join('');
      html += '<a href="map.html"><span class="badge m">地图</span>在高校地图中查看「'+esc(q)+'」相关院校</a>';
      box.innerHTML = html;
      box.classList.add('on');
    }
    input.addEventListener('input', function(e){ render(e.target.value); });
    input.addEventListener('focus', function(e){ if(e.target.value.trim()) render(e.target.value); });
    document.addEventListener('click', function(e){
      if(!box.contains(e.target) && e.target !== input) box.classList.remove('on');
    });
    input.addEventListener('keydown', function(e){
      if(e.key === 'Enter'){ location.href = 'map.html'; }
      if(e.key === 'Escape'){ box.classList.remove('on'); }
    });
  })();
'''

# ---- 工具总览页 JS：分组折叠 + 双搜索 + 弹窗 ----
JS_TOOLS = '''
  function toggleGroup(h){ h.closest('.group').classList.toggle('collapsed'); }
  function expandAll(btn){
    var gs = document.querySelectorAll('.group');
    var anyCollapsed = [].some.call(gs, function(g){ return g.classList.contains('collapsed'); });
    gs.forEach(function(g){ g.classList.toggle('collapsed', !anyCollapsed); });
    btn.textContent = anyCollapsed ? '全部收起' : '全部展开';
  }
  function filterCards(q, sel, parentSel){
    q = q.trim().toLowerCase();
    document.querySelectorAll(sel).forEach(function(c){
      var hit = c.getAttribute('data-search').toLowerCase().indexOf(q) !== -1;
      c.style.display = hit ? '' : 'none';
    });
    if(parentSel){
      document.querySelectorAll(parentSel).forEach(function(g){
        var any = [].some.call(g.querySelectorAll(sel), function(c){ return c.style.display !== 'none'; });
        g.style.display = any ? '' : 'none';
      });
    }
    var nh = document.getElementById('nh1');
    if(nh){
      var anyVisible = [].some.call(document.querySelectorAll(sel), function(c){ return c.style.display !== 'none'; });
      nh.style.display = anyVisible ? 'none' : 'block';
    }
  }
  var q1 = document.getElementById('q1');
  if(q1) q1.addEventListener('input', function(e){
    filterCards(e.target.value, '.card', '.group');
    document.querySelectorAll('.group').forEach(function(g){ g.classList.remove('collapsed'); });
  });
  var q2 = document.getElementById('q2');
  if(q2) q2.addEventListener('input', function(e){
    filterCards(e.target.value, '.pcard', null);
  });
  function openContact(){document.getElementById('cmodal').classList.add('on');document.body.style.overflow='hidden';if(window._hmt){try{_hmt.push(['_trackEvent','contact','open','tools'])}catch(e){}}}
  function closeContact(){document.getElementById('cmodal').classList.remove('on');document.body.style.overflow='';}
  document.addEventListener('keydown',function(e){if(e.key==='Escape')closeContact();});
'''

# ---- 联系弹窗（微信二维码 + 电话）----
MODAL_CSS = '''
  .cmodal{position:fixed;inset:0;background:rgba(6,24,39,.62);display:none;align-items:center;justify-content:center;z-index:99;padding:20px}
  .cmodal.on{display:flex}
  .cmodal-box{background:#fff;border-radius:20px;max-width:360px;width:100%;padding:30px 28px 26px;text-align:center;position:relative;box-shadow:0 24px 64px rgba(6,24,39,.35)}
  .cmodal-x{position:absolute;top:12px;right:14px;border:none;background:none;font-size:19px;color:#7A8B99;cursor:pointer;line-height:1}
  .cmodal-x:hover{color:#123}
  .cmodal-t{font-size:20px;font-weight:800;color:#0A2A4A;margin-bottom:14px}
  .cmodal-qr{width:238px;height:auto;border-radius:14px;border:1px solid #E3ECF2;display:block;margin:0 auto}
  .cmodal-wechat{font-size:13.5px;color:#4A6070;margin:12px 0 14px}
  .cmodal-tel{display:inline-flex;align-items:center;gap:8px;background:linear-gradient(135deg,#0A2A4A,#1B5FA8);color:#fff;text-decoration:none;font-weight:800;font-size:17px;padding:11px 24px;border-radius:26px}
  .cmodal-tel svg{width:17px;height:17px}
  .cmodal-sub{font-size:12.5px;color:#7A8B99;margin-top:12px}
'''

MODAL_HTML = '''
<div class="cmodal" id="cmodal" onclick="if(event.target===this)closeContact()">
  <div class="cmodal-box">
    <button class="cmodal-x" onclick="closeContact()" aria-label="关闭">✕</button>
    <div class="cmodal-t">咨询孟老师</div>
    <img class="cmodal-qr" src="assets/qr-wechat.jpg" alt="微信扫码添加孟老师">
    <div class="cmodal-wechat">微信扫描二维码，添加孟老师为朋友（好友申请备注省份，优先发本省资料）</div>
    <a class="cmodal-tel" href="tel:18931577792">''' + PHONE_SVG + '''18931577792</a>
    <div class="cmodal-sub">高考志愿填报 · 产业选专业 · 院校择校 · 升学就业路径</div>
  </div>
</div>
'''

# ---- Hero 右侧：全国高校资源网络视觉（风格化轮廓，非 GIS）----
HERO_MAP_SVG = (io.open('_heromap.frag', encoding='utf-8').read())
HERO_MAP_CAP = '''
<div class="hero-cap">全国高校资源网络 · 1403所本科院校分布</div>
<a class="hero-more" href="map.html">探索高校地图 →</a>
'''

desc = ("博辰序·高考升学决策地图：连接院校、专业、城市、产业和就业方向，帮助家庭建立科学升学选择逻辑。"
        "1403 所本科院校 × 31 省产业-专业速查。规划咨询：孟老师 18931577792。")
title = "博辰序 · 高考升学决策地图"
og_img = f"{BASE}/og/index.png"

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{BASE}/">
<meta property="og:image" content="{og_img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:site_name" content="博辰序">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{og_img}">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebSite","name":"博辰序·高考升学决策地图","url":"{BASE}/","description":"{desc}"}}</script>
<style>{CSS}{MODAL_CSS}</style>
{STATS_SNIPPET}
</head>
<body id="top">

<!-- 顶部导航 -->
<nav class="nav">
  <div class="nav-in">
    <div class="logo"><b>博辰序</b><span>BOCHENXU</span></div>
    <div class="nav-links">
      <a href="#top">首页</a>
      <a href="map.html">找大学</a>
      <a href="results/{urlsafe('专业介绍查询系统.html')}" target="_blank" rel="noopener">选专业</a>
      <a href="#future">看就业</a>
      <a href="tools.html">升学工具</a>
      <a class="nav-cta" href="#contact" onclick="openContact();return false">生成我的升学分析</a>
    </div>
  </div>
</nav>

<!-- 第一屏 Hero：品牌 + 核心价值 + 搜索 + 全国高校资源网络视觉 -->
<header class="hero">
  <div class="wrap">
    <div class="hero-grid">
      <div class="hero-txt">
        <div class="kick">博辰序 · BOCHENXU</div>
        <h1>孩子的未来，<br>从<span class="hl">选择大学</span>开始</h1>
        <div class="sub">博辰序 · 高考升学决策地图</div>
        <p class="desc">连接院校、专业、城市、产业和就业方向，帮助家庭建立科学升学选择逻辑。</p>
        <div class="cta-row">
          <a class="cta" href="map.html">开始探索高校 →</a>
          <a class="cta-outline" href="#plan" onclick="openContact();return false">{PHONE_SVG}生成升学分析</a>
        </div>
        <div class="hsearch">
          <div class="hsearch-box">{SEARCH_SVG}
            <input id="heroq" placeholder="搜索学校、专业或城市：华北电力大学 / 电气工程 / 河北高校" autocomplete="off">
          </div>
          <div class="hsug" id="hsug"></div>
          <div class="hsearch-hint">支持搜索 <b>学校名称</b> · <b>专业名称</b> · <b>城市 / 省份</b>，回车直达高校地图</div>
          <div class="hstart">
            <span>不知道从哪里开始？从孩子的<b>省份</b>、<b>选科</b>和<b>成绩</b>开始。</span>
            <a class="lnk" href="#plan" onclick="openContact();return false">免费生成我的升学方向 →</a>
          </div>
        </div>
      </div>
      <div class="hero-map">
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
      </div>
    </div>
  </div>
</header>

<!-- 第二屏：四大核心入口 -->
<section>
  <div class="wrap">
    <h2 class="sec-title">四大核心入口，覆盖升学决策全流程</h2>
    <p class="sec-sub">找大学 → 选专业 → 看就业 → 我的规划，一条清晰的决策路径，每一步都有数据可依。</p>
    <div class="feats">
      <div class="feat">
        <div class="feat-ic fi-blue"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21V8l9-5 9 5v13"/><path d="M9 21v-6h6v6"/><path d="M3 21h18"/></svg></div>
        <h3>找大学</h3>
        <p>全国 1403 所本科院校，一图探索。</p>
        <a class="feat-go" href="map.html">进入高校地图 <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>
      </div>
      <div class="feat">
        <div class="feat-ic fi-navy"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><rect x="3" y="3" width="8" height="8" rx="1.5"/><rect x="13" y="3" width="8" height="8" rx="1.5"/><rect x="3" y="13" width="8" height="8" rx="1.5"/><rect x="13" y="13" width="8" height="8" rx="1.5"/></svg></div>
        <h3>选专业</h3>
        <p>专业方向与未来发展，逐项看清。</p>
        <a class="feat-go" href="results/{urlsafe('专业介绍查询系统.html')}" target="_blank" rel="noopener">探索专业 <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>
      </div>
      <div class="feat">
        <div class="feat-ic fi-green"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><rect x="3" y="12" width="4" height="9"/><rect x="10" y="7" width="4" height="14"/><rect x="17" y="3" width="4" height="18"/></svg></div>
        <h3>看就业</h3>
        <p>产业趋势与职业方向，先定产业再定专业。</p>
        <a class="feat-go" href="#future">查看就业趋势 <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>
      </div>
      <div class="feat go-orange">
        <div class="feat-ic fi-orange">{PHONE_SVG}</div>
        <h3>我的规划</h3>
        <p>生成孩子的个人升学方向分析。</p>
        <a class="feat-go" href="#plan" onclick="openContact();return false">开始分析 <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>
      </div>
    </div>
  </div>
</section>

<!-- 第三屏：全国高校数据实力 -->
<section class="trust">
  <div class="wrap">
    <div class="tgrid">
      <div class="tcard"><b>31<i>省</i></b><span>全国省级行政区全覆盖</span></div>
      <div class="tcard"><b>1403<i>所</i></b><span>本科院校数据（含更名新设同步）</span></div>
      <div class="tcard"><b>300<i>+</i></b><span>城市高校与产业数据</span></div>
      <div class="tcard"><b>1000<i>+</i></b><span>家庭升学服务经验</span></div>
    </div>
    <p class="trust-note">用<b>真实高校数据</b>，辅助家庭做<b>科学升学选择</b>。</p>
  </div>
</section>

<!-- 第四屏：专业 × 产业 × 就业 -->
<section id="future">
  <div class="wrap">
    <h2 class="sec-title">不只看大学，更要看未来</h2>
    <p class="sec-sub">选择专业，不只是选择大学四年，更是在选择未来职业方向。</p>
    <div class="chain">
      <div class="chain-node" data-search="新能源产业 144城产业调研 产业集群">
        <div class="lab">产业</div>
        <div class="val">新能源产业<small>144 城产业调研 · 国家级产业集群全景</small></div>
        <a class="lnk" href="results/{urlsafe('全国144城产业调研地图.html')}" target="_blank" rel="noopener">查看产业地图 →</a>
      </div>
      <div class="chain-arrow"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg></div>
      <div class="chain-node" data-search="电气工程及其自动化 专业 选科">
        <div class="lab">专业</div>
        <div class="val">电气工程及其自动化<small>对应选科要求 · 考研方向 · 开设院校</small></div>
        <a class="lnk" href="results/{urlsafe('专业介绍查询系统.html')}" target="_blank" rel="noopener">查询专业详情 →</a>
      </div>
      <div class="chain-arrow"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg></div>
      <div class="chain-node" data-search="华北电力大学 高校 地图">
        <div class="lab">高校</div>
        <div class="val">华北电力大学<small>本科院校按地理分布探索</small></div>
        <a class="lnk" href="map.html">地图中找大学 →</a>
      </div>
      <div class="chain-arrow"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg></div>
      <div class="chain-node" data-search="国家电网 新能源企业 就业">
        <div class="lab">就业方向</div>
        <div class="val">国家电网、新能源企业<small>就业质量报告 · 380 所院校决策参考</small></div>
        <a class="lnk" href="results/{urlsafe('就业与教学质量报告决策参考380所.html')}" target="_blank" rel="noopener">查看就业数据 →</a>
      </div>
    </div>
    <div class="chain-note"><b>为什么这样看？</b>先看产业在哪、要什么人，再倒推学什么专业、去哪所大学——先定产业，再定专业。</div>
    <a class="chain-cta" href="#contact" onclick="openContact();return false">看看我的孩子适合哪些方向 →</a>
  </div>
</section>

<!-- 第五屏：五步走稳升学决策 -->
<section class="plan" id="plan">
  <div class="wrap">
    <h2 class="sec-title">五步，走稳升学决策</h2>
    <p class="sec-sub">认识孩子 → 定位方向 → 筛选大学 → 分析专业 → 制定志愿方案，不推销、不制造焦虑。</p>
    <div class="steps">
      <div class="step"><div class="no">STEP 1</div><h4>认识孩子</h4><p>成绩、兴趣、期望，先摸清底牌。</p></div>
      <div class="step"><div class="no">STEP 2</div><h4>定位方向</h4><p>产业趋势对照，圈定方向。</p></div>
      <div class="step"><div class="no">STEP 3</div><h4>筛选大学</h4><p>按分数段筛出目标院校。</p></div>
      <div class="step"><div class="no">STEP 4</div><h4>分析专业</h4><p>培养、考研、就业逐项核对。</p></div>
      <div class="step"><div class="no">STEP 5</div><h4>制定志愿方案</h4><p>冲稳保梯度方案落定。</p></div>
    </div>
    <div class="plan-foot">
      <a class="cta" href="#contact" onclick="openContact();return false">{PHONE_SVG}预约一次升学分析</a>
      <div class="hint">说明：工具区全部数据工具免费开放；一对一定制规划按需沟通，不强制、不捆绑。</div>
    </div>
  </div>
</section>

<!-- 第六屏：升学工具箱（6 个最常用入口，全部成果见工具总览页） -->
<section id="tools">
  <div class="wrap">
    <div class="sec-head">
      <div class="t">
        <h2 class="sec-title">升学工具箱</h2>
        <p class="sec-sub">围绕升学决策提供实用查询工具——最常用的 6 项放在这里。</p>
      </div>
    </div>
    <div class="tbgrid">
{toolbox_html}
    </div>
    <a class="viewall" href="tools.html">查看全部工具（{total_works} 项成果 + 31 省速查入口） <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>
  </div>
</section>

<!-- 第七屏：升学分析/咨询入口 -->
<section class="contact" id="contact">
  <div class="wrap contact-in">
    <div class="t">
      <h2 class="sec-title">升学规划咨询 · 联系孟老师</h2>
      <p class="sec-sub">认识孩子、定位方向、筛选大学、分析专业、制定志愿方案——每一步都可以聊。电话直接沟通，比在微信群里翻资料更快。</p>
    </div>
    <div class="contact-card">
      <div class="cc-name">孟老师</div>
      <a class="cc-tel" href="tel:18931577792">{PHONE_SVG}18931577792</a>
      <div class="cc-sub">高考志愿填报 · 产业选专业 · 院校择校 · 升学就业路径</div>
      <div style="margin-top:18px;background:#fff;border-radius:14px;padding:12px 12px 10px;display:inline-block">
        <img src="assets/qr-wechat.jpg" alt="微信扫码添加孟老师" style="width:172px;height:auto;border-radius:9px;display:block">
        <div style="font-size:12.5px;color:#4A6070;margin-top:8px;font-weight:600">微信扫码，添加孟老师为朋友</div>
      </div>
      <div style="margin-top:16px;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.28);border-radius:12px;padding:10px 14px;font-size:13px;line-height:1.55">加微信时备注您的省份（如「河北」），优先领取本省专属资料</div>
    </div>
  </div>
</section>

<footer>
  <div class="wrap">
    <b>博辰序 · 高考升学决策地图</b><br>
    内容来自孟老师升学规划工具集（资料库节点「集合全部升学规划工具平台」）。<br>
    规划咨询：孟老师 · 电话 <a href="tel:18931577792">18931577792</a> · 本网站为内容展示用途，版权与相关权益归原作者所有。
  </div>
</footer>

<!-- 移动端底部咨询条 -->
<div class="mbbar">
  <a class="mb-tel" href="tel:18931577792">{PHONE_SVG}电话咨询</a>
  <a class="mb-wx" href="#contact" onclick="openContact();return false">微信咨询孟老师</a>
</div>

{MODAL_HTML}
<script>var PROV_ITEMS = {prov_json};var TOOL_ITEMS = {tool_json};</script>
<script>{JS_HOME}</script>
</body>
</html>
'''

with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as fp:
    fp.write(html)
print("index.html generated (v3 精修版)")

# ================= 工具总览页 tools.html（16 项成果完整分组 + 31 省入口）=================
tools_desc = "博辰序升学工具箱：16 项升学工作成果与 31 省产业-本科专业速查仪表盘完整入口。"
tools_title = "升学工具箱 · 博辰序"
tools_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<title>{tools_title}</title>
<meta name="description" content="{tools_desc}">
<meta property="og:title" content="{tools_title}">
<meta property="og:description" content="{tools_desc}">
<meta property="og:image" content="{og_img}">
<style>{CSS}{MODAL_CSS}</style>
{STATS_SNIPPET}
</head>
<body id="top">

<nav class="nav">
  <div class="nav-in">
    <div class="logo"><b>博辰序</b><span>BOCHENXU</span></div>
    <div class="nav-links">
      <a href="/">返回首页</a>
      <a href="map.html">找大学</a>
      <a href="results/{urlsafe('专业介绍查询系统.html')}" target="_blank" rel="noopener">选专业</a>
      <a class="nav-cta" href="#top">升学工具箱</a>
    </div>
  </div>
</nav>

<div class="pagehead">
  <div class="wrap">
    <div class="kick">升学工具箱 · TOOLKIT</div>
    <h1>全部升学工具与成果</h1>
    <p>{total_works} 项升学工作成果，按服务场景归为 6 类；下方附 31 省产业-本科专业速查仪表盘入口。点击直接打开（需联网）。</p>
  </div>
</div>

<section id="tools">
  <div class="wrap">
    <div class="sec-head">
      <div class="t">
        <h2 class="sec-title">工作成果 · {total_works} 项</h2>
        <p class="sec-sub">按服务场景归类，点击分组标题可折叠/展开。</p>
      </div>
      <div class="tools">
        <div class="search">{SEARCH_SVG}
        <input id="q1" placeholder="搜索成果 / 关键词"></div>
        <button class="btn" onclick="expandAll(this)">全部展开</button>
      </div>
    </div>
    <div class="no-hit" id="nh1">没有匹配的成果，换个关键词试试。</div>
{groups_html}
  </div>
</section>

<section style="background:linear-gradient(180deg,#fff,#EFF5FB);padding-top:0">
  <div class="wrap" style="padding-top:0">
    <div class="sec-head" style="padding-top:8px">
      <div class="t">
        <h2 class="sec-title">31 省产业-本科专业速查仪表盘</h2>
        <p class="sec-sub">每省一张：支柱产业、匹配专业、报考提醒，一图看全。全国总览排在最前。</p>
      </div>
      <div class="tools">
        <div class="search">{SEARCH_SVG}
        <input id="q2" placeholder="筛选省份，如「河北」"></div>
      </div>
    </div>
    <div class="pgrid">
{other_html}
{prov_html}
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <h2 class="sec-title">使用与数据说明</h2>
    <div class="note">
      · <b>地图本体离线可看</b>：1403 所本科院校数据已内嵌，断网也能浏览地图。<br>
      · <b>联网项</b>：点校名跳百度百科、打开上方成果/仪表盘需联网。<br>
      · <b>数据口径</b>：院校数据含 2025–2026 更名/新设同步；成果内容来源于孟老师升学规划工具集，具体以原文件为准。<br>
      · <b>成果分组</b>：按成果服务功能场景归类（产业-专业映射 / 选科选专业 / 报考决策 / 院校择校 / 升学就业 / 备考提分），便于按需取用。<br>
      · 本页为完整工具总览，首页仅展示 6 个最常用入口。
    </div>
  </div>
</section>

<footer>
  <div class="wrap">
    <b>博辰序 · 高考升学决策地图</b><br>
    内容来自孟老师升学规划工具集（资料库节点「集合全部升学规划工具平台」）。<br>
    规划咨询：孟老师 · 电话 <a href="tel:18931577792">18931577792</a> · 本网站为内容展示用途，版权与相关权益归原作者所有。
  </div>
</footer>

<div class="mbbar">
  <a class="mb-tel" href="tel:18931577792">{PHONE_SVG}电话咨询</a>
  <a class="mb-wx" href="#top" onclick="openContact();return false">微信咨询孟老师</a>
</div>

{MODAL_HTML}
<script>{JS_TOOLS}</script>
</body>
</html>
'''

with open(os.path.join(ROOT, "tools.html"), "w", encoding="utf-8") as fp:
    fp.write(tools_html)
print("tools.html generated (完整成果总览)")
print("works:", total_works, "| groups:", len(GROUPS), "| province dashboards:", total_prov, "| other dashboards:", len(other_dashboards))
