# -*- coding: utf-8 -*-
"""
map.html 联系条修复 + 重注入（幂等）：
1. 摘除历史上误注入进压缩 JS 字符串字面量里的旧联系条（导致 ECharts 语法错误），还原原字符串。
2. 在真正的 </body>（rfind）前注入：底部联系条（电话 + 微信咨询）+ 微信二维码弹窗。
"""
import io, os

ROOT = os.path.dirname(os.path.abspath(__file__))
MAP = os.path.join(ROOT, "map.html")
s = io.open(MAP, encoding="utf-8").read()

# ---------- 1. 修复历史误注入 ----------
i = s.find('<div id="contactbar"')
if i != -1:
    e = s.find(",b=window.open()", i)
    assert e != -1, "anchor ',b=window.open()' not found"
    s = s[:i] + "</body>'" + s[e:]
    print("repaired: removed misplaced contactbar inside minified JS")
else:
    print("repair: nothing misplaced found")

# ---------- 2. 幂等清理旧注入块（若有）----------
TAG = '<div id="mcontactbar"'
while TAG in s:
    i = s.find(TAG)
    e = s.find("<!--/mcontactbar-->", i)
    e = e + len("<!--/mcontactbar-->") if e != -1 else i
    s = s[:i] + s[e:]
    print("removed old mcontactbar block")

# ---------- 3. 注入新联系条 + 二维码弹窗 ----------
BLOCK = '''
<div id="mcontactbar" style="position:fixed;left:0;right:0;bottom:0;z-index:9998;background:linear-gradient(90deg,#0A4E7E,#0E9AA7);color:#fff;padding:10px 52px 10px 18px;font-size:14px;line-height:1.5;font-family:'Microsoft YaHei',sans-serif;display:flex;align-items:center;justify-content:center;gap:16px;box-shadow:0 -4px 18px rgba(0,0,0,.18);flex-wrap:wrap;">
  <span>升学规划咨询 · <b>孟老师</b></span>
  <a href="tel:18931577792" style="color:#fff;font-weight:800;font-size:17px;text-decoration:none;letter-spacing:.5px;">18931577792</a>
  <button onclick="openMapContact()" style="background:rgba(255,255,255,.18);border:1px solid rgba(255,255,255,.55);color:#fff;font-size:13px;font-weight:700;padding:6px 14px;border-radius:18px;cursor:pointer;">微信扫码咨询</button>
  <button onclick="document.getElementById('mcontactbar').remove()" style="position:absolute;right:12px;top:50%;transform:translateY(-50%);background:none;border:none;color:#fff;font-size:16px;cursor:pointer;opacity:.8;">✕</button>
</div>
<div id="mcontactmodal" style="position:fixed;inset:0;background:rgba(6,24,39,.62);display:none;align-items:center;justify-content:center;z-index:9999;padding:20px;" onclick="if(event.target===this)closeMapContact()">
  <div style="background:#fff;border-radius:20px;max-width:360px;width:100%;padding:30px 28px 26px;text-align:center;position:relative;box-shadow:0 24px 64px rgba(6,24,39,.35);">
    <button onclick="closeMapContact()" aria-label="关闭" style="position:absolute;top:12px;right:14px;border:none;background:none;font-size:19px;color:#7A8B99;cursor:pointer;line-height:1;">✕</button>
    <div style="font-size:20px;font-weight:800;color:#0A2E4E;margin-bottom:14px;">咨询孟老师</div>
    <img src="assets/qr-wechat.jpg" alt="微信扫码添加孟老师" style="width:238px;height:auto;border-radius:14px;border:1px solid #E3ECF2;display:block;margin:0 auto;">
    <div style="font-size:13.5px;color:#4A6070;margin:12px 0 14px;">微信扫描二维码，添加孟老师为朋友</div>
    <a href="tel:18931577792" style="display:inline-flex;align-items:center;gap:8px;background:linear-gradient(135deg,#0A4E7E,#0E9AA7);color:#fff;text-decoration:none;font-weight:800;font-size:17px;padding:11px 24px;border-radius:26px;">📞 18931577792</a>
    <div style="font-size:12.5px;color:#7A8B99;margin-top:12px;">高考志愿填报 · 产业选专业 · 院校择校 · 升学就业路径</div>
  </div>
</div>
<script>
function openMapContact(){var m=document.getElementById('mcontactmodal');m.style.display='flex';document.body.style.overflow='hidden';}
function closeMapContact(){var m=document.getElementById('mcontactmodal');m.style.display='none';document.body.style.overflow='';}
document.addEventListener('keydown',function(e){if(e.key==='Escape')closeMapContact();});
</script>
<!--/mcontactbar-->
'''

k = s.rfind("</body>")
s = s[:k] + BLOCK + s[k:]
io.open(MAP, "w", encoding="utf-8").write(s)
print("map.html: contact bar + QR modal injected before real </body>, size:", os.path.getsize(MAP))
