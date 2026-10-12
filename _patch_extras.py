# -*- coding: utf-8 -*-
"""
补丁脚本（幂等）：
1. 工具13-院校专业信息库.html → 复制进 results/ 并统一改名为「河北省院校录取查询系统」
   （title、页头 h1 两处显示名，内容数据不动）。
2. map.html 注入 OG 元数据（</head> 前）+ 底部常驻联系条（</body> 前）。
"""
import os, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(ROOT, "results")

# ---------- 1. 工具13 改名接入 ----------
SRC = r"D:/桌面/学情分析手册执行SOP手册/学生工具包/工具13-院校专业信息库.html"
DST = os.path.join(RESULTS, "河北省院校录取查询系统.html")

if os.path.isfile(SRC):
    with open(SRC, encoding="utf-8", errors="ignore") as fp:
        html = fp.read()
    old_title = "<title>工具13-院校专业信息库（河北2026·本科）</title>"
    new_title = "<title>河北省院校录取查询系统（河北2026·本科）</title>"
    old_h1 = '<h1>院校专业信息库 <span style="font-size:12px;color:#999;font-weight:400">河北 2026 · 本科</span></h1>'
    new_h1 = '<h1>河北省院校录取查询系统 <span style="font-size:12px;color:#999;font-weight:400">河北 2026 · 本科</span></h1>'
    n1 = html.count(old_title); n2 = html.count(old_h1)
    html = html.replace(old_title, new_title).replace(old_h1, new_h1)
    # 兜底：还有零散「院校专业信息库」字样也统一替换
    html = html.replace("工具13-院校专业信息库", "河北省院校录取查询系统").replace("院校专业信息库", "河北省院校录取查询系统")
    with open(DST, "w", encoding="utf-8") as fp:
        fp.write(html)
    print(f"tool13 -> {DST}")
    print(f"  title replaced: {n1}, h1 replaced: {n2}, size: {os.path.getsize(DST)}")
    leftover = html.count("信息库")
    print(f"  leftover '信息库': {leftover}")
else:
    print("SRC missing:", SRC)

# ---------- 2. map.html 注入 OG + 联系条 ----------
MAP = os.path.join(ROOT, "map.html")
with open(MAP, encoding="utf-8", errors="ignore") as fp:
    m = fp.read()
changed = False

OG_BLOCK = (
    '<meta property="og:type" content="website">\n'
    '<meta property="og:title" content="博辰序 · 全国各省本科院校分布地图">\n'
    '<meta property="og:description" content="1403 所本科院校 × 31 省产业-专业速查，点城市看产业，点院校看匹配专业。规划咨询：孟老师 18931577792。">\n'
    '<meta property="og:url" content="https://star-map-folder.app.workbuddy.host/map.html">\n'
    '<meta property="og:image" content="https://star-map-folder.app.workbuddy.host/og/map.png">\n'
    '<meta property="og:image:width" content="1200">\n'
    '<meta property="og:image:height" content="630">\n'
    '<meta property="og:site_name" content="博辰序">\n'
    '<meta name="twitter:card" content="summary_large_image">\n'
)
if 'property="og:type"' not in m and "</head>" in m:
    m = m.replace("</head>", OG_BLOCK + "</head>", 1)
    changed = True
    print("map.html: OG meta injected")

CONTACT_BLOCK = (
    '<div id="contactbar" style="position:fixed;left:0;right:0;bottom:0;z-index:9998;'
    'background:linear-gradient(90deg,#0A4E7E,#0E9AA7);color:#fff;padding:9px 46px 9px 18px;'
    'font-size:14px;line-height:1.5;font-family:\'Microsoft YaHei\',sans-serif;'
    'display:flex;align-items:center;justify-content:center;gap:14px;'
    'box-shadow:0 -4px 18px rgba(0,0,0,.18);">'
    '<span>升学规划咨询 · <b>孟老师</b></span>'
    '<a href="tel:18931577792" style="color:#fff;font-weight:800;font-size:17px;'
    'text-decoration:none;letter-spacing:.5px;">18931577792</a>'
    '<button onclick="document.getElementById(\'contactbar\').remove()" '
    'style="position:absolute;right:12px;top:50%;transform:translateY(-50%);'
    'background:none;border:none;color:#fff;font-size:16px;cursor:pointer;opacity:.8;">✕</button>'
    '</div>\n'
)
if "contactbar" not in m and "</body>" in m:
    # 注意：必须插在最后一个 </body> 前——str.replace 会命中压缩 JS 字符串里的 </body> 导致语法错误
    k = m.rfind("</body>")
    m = m[:k] + CONTACT_BLOCK + m[k:]
    changed = True
    print("map.html: contact bar injected")

if changed:
    with open(MAP, "w", encoding="utf-8") as fp:
        fp.write(m)
    print("map.html saved, size:", os.path.getsize(MAP))
else:
    print("map.html: nothing to do (already patched)")
