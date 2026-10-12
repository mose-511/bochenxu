# -*- coding: utf-8 -*-
"""
生成 OG 分享卡片（1200x630 PNG），用于百度/微信等链接预览显示「省名卡片」。
- og/<省全称>.png：每省一张，含省名 + 支柱产业关键词 + 孟老师品牌行。
- og/index.png：门户卡片。
- og/map.png：交互地图卡片。
全部本地用 PIL 渲染，零外部 API 依赖，中文字体用系统 Noto Sans SC。
"""
import os, re
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(ROOT, "results")
OG = os.path.join(ROOT, "og")
os.makedirs(OG, exist_ok=True)

FONT_DIR = "/c/Windows/Fonts"
REG = os.path.join(FONT_DIR, "Noto Sans SC (TrueType).otf")
BOLD = os.path.join(FONT_DIR, "Noto Sans SC Bold (TrueType).otf")
if not os.path.isfile(BOLD):
    BOLD = REG

def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

W, H = 1200, 630
TOP = (10, 78, 126)      # #0A4E7E
BOT = (14, 154, 167)     # #0E9AA7
WHITE = (255, 255, 255)
PALE = (216, 235, 247)
CYAN = (140, 228, 237)

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

def extract_industries(prov_key):
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
    s = re.sub(r'[（(][^）)]*[）)]', '', s)
    s = s.split("——")[0]
    parts = [p.strip() for p in re.split(r'[、，,；;]', s) if p.strip()]
    return parts[:3]

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def draw_card(path, title, subtitle, tagline):
    img = Image.new("RGB", (W, H), TOP)
    d = ImageDraw.Draw(img)
    for y in range(H):
        d.line([(0, y), (W, y)], fill=lerp(TOP, BOT, y / H))
    # 右上柔光
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([W - 520, -200, W + 240, 380], fill=WHITE)
    img = Image.blend(img, glow, 0.10)
    d = ImageDraw.Draw(img)
    # 品牌（左上）
    d.text((80, 58), "博辰序 · BOCHENXU", font=font(REG, 26), fill=PALE)
    # 省名（居中大字）
    n = len(title)
    size = 108 if n <= 4 else 96 if n <= 5 else 84 if n <= 6 else 74
    d.text((W // 2, H // 2 - 66), title, font=font(BOLD, size), fill=WHITE, anchor="mm")
    # 副标题
    d.text((W // 2, H // 2 + 18), subtitle, font=font(REG, 38), fill=PALE, anchor="mm")
    # 产业关键词
    if tagline:
        d.text((W // 2, H // 2 + 78), tagline, font=font(REG, 32), fill=CYAN, anchor="mm")
    # 底部联系行
    d.line([(80, H - 112), (W - 80, H - 112)], fill=(170, 200, 220))
    d.text((80, H - 82), "孟老师 · 升学规划咨询", font=font(REG, 30), fill=WHITE)
    d.text((W - 80, H - 82), "18931577792", font=font(BOLD, 36), fill=WHITE, anchor="rm")
    img.save(path, "PNG")

# ---- 门户卡片 ----
draw_card(os.path.join(OG, "index.png"),
          "全国各省本科院校分布地图",
          "1403 所本科院校 × 31 省产业-专业速查",
          "产业 · 专业 · 院校 · 报考 一站式决策地图")

# ---- 地图卡片 ----
draw_card(os.path.join(OG, "map.png"),
          "交互地图 · 博辰序",
          "点城市看产业，点院校看匹配专业",
          "1403 所本科院校 地理分布 + 产业叠加")

# ---- 每省 / 全国总览卡片 ----
made = []
for prov in PROV_ORDER:
    kw = extract_industries(prov)
    tag = " · ".join(kw) if kw else "产业-专业-院校 报考决策地图"
    if len(tag) > 24:
        tag = tag[:23] + "…"
    draw_card(os.path.join(OG, FULL[prov] + ".png"),
              FULL[prov], "支柱产业与本科院校分布地图", tag)
    made.append(FULL[prov])
# 全国总览
draw_card(os.path.join(OG, "全国总览.png"),
          "全国总览", "本科院校产业-专业总览地图",
          "1403 所本科院校 · 31 省产业-专业总览")
made.append("全国总览")

print("OG images:", len(made) + 2, "| folder:", OG)
print("sample:", os.path.exists(os.path.join(OG, "河北省.png")), os.path.exists(os.path.join(OG, "index.png")))
