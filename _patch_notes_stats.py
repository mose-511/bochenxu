# -*- coding: utf-8 -*-
"""给 map.html 注入：① 弹窗备注省份提示 ② 二维码弹窗点击统计 ③ 百度统计接入点。
全部幂等：重复运行不会重复注入。统计片段仅当 stats_id.txt 有 ID 时注入。"""
import os, io

BASE = os.path.dirname(os.path.abspath(__file__))
MAP = os.path.join(BASE, "map.html")
s = io.open(MAP, encoding="utf-8", errors="ignore").read()
orig = s

# ① 弹窗文案加备注省份提示
OLD_TXT = "微信扫描二维码，添加孟老师为朋友"
NEW_TXT = "微信扫描二维码，添加孟老师为朋友（好友申请备注省份，优先发本省资料）"
if OLD_TXT in s and NEW_TXT not in s:
    s = s.replace(OLD_TXT, NEW_TXT)
    print("map: modal note added")
elif NEW_TXT in s:
    print("map: modal note already present")

# ② openMapContact 加统计埋点（弹窗打开事件）
OLD_FN = "function openMapContact(){var m=document.getElementById('mcontactmodal');m.style.display='flex';document.body.style.overflow='hidden';}"
NEW_FN = ("function openMapContact(){var m=document.getElementById('mcontactmodal');m.style.display='flex';"
          "document.body.style.overflow='hidden';if(window._hmt){try{_hmt.push(['_trackEvent','contact','open','map'])}catch(e){}}}")
if OLD_FN in s:
    s = s.replace(OLD_FN, NEW_FN)
    print("map: open tracking added")
elif NEW_FN in s:
    print("map: open tracking already present")
else:
    print("map: WARNING - openMapContact not found, skip tracking")

# ③ 百度统计片段（写入 stats_id.txt 后重跑本脚本生效）
if "hm.baidu.com/hm.js?" not in s:
    stats_file = os.path.join(BASE, "stats_id.txt")
    sid = open(stats_file, encoding="utf-8").read().strip() if os.path.exists(stats_file) else ""
    if sid:
        snip = ("<script>var _hmt=_hmt||[];(function(){var hm=document.createElement('script');"
                "hm.src='https://hm.baidu.com/hm.js?" + sid + "';"
                "var s=document.getElementsByTagName('script')[0];s.parentNode.insertBefore(hm,s);})();</script>\n")
        # </head> 在文件前部，第一处即真 head（压缩 JS 在 body 内）
        i = s.find("</head>")
        if i > 0:
            s = s[:i] + snip + s[i:]
            print("map: baidu stats injected (id=%s...)" % sid[:4])
        else:
            print("map: WARNING - </head> not found")
    else:
        print("map: stats_id.txt empty, stats snippet skipped")
else:
    print("map: stats already present")

if s != orig:
    io.open(MAP, "w", encoding="utf-8").write(s)
    print("map.html updated")
else:
    print("map.html unchanged")
