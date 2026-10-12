# -*- coding: utf-8 -*-
"""从已验证的 china_full.json 生成 Hero 真实中国地图 SVG 片段。
输出 _heromap.frag，由 _gen_portal.py 读取嵌入首页。
数据源：2026-10-09-144city-industry-map/data/china_full.json（省级 FeatureCollection，35 features）。
"""
import json, io, math, os, urllib.parse

SRC = r'D:/workbuddy/2026-10-09-144city-industry-map/data/china_full.json'
OUT = '_heromap.frag'

# Hero 高校节点（真实经纬度；type: hub=重点橙色 / sub=普通）
# lab: (dx, dy, anchor) 标签偏移与对齐，用于密集区错开
UNIS = [
    ('华北电力大学', '保定', 115.53, 38.87, 'hub', (-8, 3.5, 'end')),
    ('燕山大学',     '秦皇岛', 119.35, 39.88, 'sub', (8, -6, 'start')),
    ('河北工业大学', '天津', 117.13, 39.16, 'sub', (8, 9, 'start')),
    ('四川大学',     '成都', 104.08, 30.65, 'hub', (0, 16, 'middle')),
    ('中山大学',     '广州', 113.29, 23.13, 'hub', (8, 3.5, 'start')),
    ('复旦大学',     '上海', 121.50, 31.30, 'hub', (8, 3.5, 'start')),
    ('哈尔滨工业大学', '哈尔滨', 126.63, 45.75, 'hub', (8, 3.5, 'start')),
]

# 站内有落地页的 31 省（跳 p/<全名>.html）；台湾/港澳无页不跳
HAVE_PAGE = {'北京市','天津市','河北省','山西省','内蒙古自治区','辽宁省','吉林省','黑龙江省',
             '上海市','江苏省','浙江省','安徽省','福建省','江西省','山东省','河南省','湖北省',
             '湖南省','广东省','广西壮族自治区','海南省','重庆市','四川省','贵州省','云南省',
             '西藏自治区','陕西省','甘肃省','青海省','宁夏回族自治区','新疆维吾尔自治区'}

d = json.load(io.open(SRC, encoding='utf-8'))

# ---- Mercator 投影 ----
def merc(lat):
    r = math.radians(lat)
    return math.log(math.tan(math.pi/4 + r/2))

LON0, LON1 = 73.4, 135.2
LAT0, LAT1 = 3.3, 53.65          # 含南海九段线（曾母暗沙 3.98N）
K = 470.0                        # 每弧度像素（约520px宽）
W = round((LON1-LON0)*math.pi/180*K)
H = round((merc(LAT1)-merc(LAT0))*K)

def px(lon, lat):
    x = (lon-LON0)*math.pi/180*K
    y = (merc(LAT1) - merc(lat)) * K
    return round(x, 1), round(y, 1)

def path_of(geom):
    polys = geom['coordinates'] if geom['type'] == 'MultiPolygon' else [geom['coordinates']]
    ds = []
    for poly in polys:
        for ring in poly:
            pts = [px(lon, lat) for lon, lat in ring]
            # 精简：相邻点几乎重合则丢弃
            simp = [pts[0]]
            for p in pts[1:]:
                if abs(p[0]-simp[-1][0]) >= 0.15 or abs(p[1]-simp[-1][1]) >= 0.15:
                    simp.append(p)
            ds.append('M' + 'L'.join(f'{a} {b}' for a, b in simp) + 'Z')
    return ''.join(ds)

g_prov, g_line = [], []
for f in d['features']:
    name = f['properties'].get('name') or ''
    dd = path_of(f['geometry'])
    if name:
        href = 'p/' + urllib.parse.quote(name) + '.html' if name in HAVE_PAGE else ''
        g_prov.append(f'<path class="hp" data-p="{name}" d="{dd}"{f" data-href=\"{href}\"" if href else ""}/>')
    else:
        # 九段线/南海诸岛：仅描边示意
        g_line.append(f'<path class="hp-line" d="{dd}"/>')

# ---- 高校节点 ----
g_uni = []
for nm, city, lon, lat, typ, (dx, dy, anchor) in UNIS:
    x, y = px(lon, lat)
    cls = 'hu hub' if typ == 'hub' else 'hu'
    g_uni.append(
        f'<g class="{cls}" data-u="{nm}" data-c="{city}">'
        f'<circle cx="{x}" cy="{y}" r="{4.2 if typ=="hub" else 3}"/>'
        f'<text x="{x+dx}" y="{y+dy}" text-anchor="{anchor}">{nm}</text></g>'
    )

frag = (
    f'<svg class="cnmap-svg" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="全国本科院校分布地图">\n'
    + '\n'.join(g_prov) + '\n' + '\n'.join(g_line) + '\n' + '\n'.join(g_uni)
    + '\n</svg>'
)
io.open(OUT, 'w', encoding='utf-8').write(frag)
print(f'W={W} H={H} paths={len(g_prov)} frag={os.path.getsize(OUT)} bytes')
