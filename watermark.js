/* 博辰序 全站溯源水印 — 防截屏外传（浏览器无法真正阻止系统截屏，
   采行业标准做法：满屏斜排水印，含品牌电话 + 本访客脱敏手机号，泄露可溯源到人）
   附：禁文字选中/右键/复制，PrintScreen 时尽力清空剪贴板 */
(function () {
  'use strict';

  function getVisitor() {
    try {
      var d = JSON.parse(localStorage.getItem('bcx_lead') || 'null');
      return d && d.phone ? String(d.phone) : '';
    } catch (e) { return ''; }
  }
  function mask(p) {
    return (p && p.length === 11) ? p.slice(0, 3) + '****' + p.slice(7) : p;
  }
  function today() {
    var t = new Date();
    function z(n) { return n < 10 ? '0' + n : '' + n; }
    return t.getFullYear() + '-' + z(t.getMonth() + 1) + '-' + z(t.getDate());
  }

  function paint() {
    var old = document.getElementById('bcxWm');
    if (old) old.remove();
    var phone = getVisitor();
    var line1 = '孟老师升学规划 18931577792';
    var line2 = phone ? ('访客 ' + mask(phone) + ' · ' + today()) : ('博辰序 · ' + today());

    var c = document.createElement('canvas');
    c.width = 340; c.height = 190;
    var x = c.getContext('2d');
    x.translate(c.width / 2, c.height / 2);
    x.rotate(-22 * Math.PI / 180);
    x.textAlign = 'center';
    x.fillStyle = 'rgba(105,122,138,0.16)';
    x.font = 'bold 16px "Microsoft YaHei","PingFang SC",sans-serif';
    x.fillText(line1, 0, -7);
    x.font = '12px "Microsoft YaHei","PingFang SC",sans-serif';
    x.fillText(line2, 0, 15);
    var url = c.toDataURL('image/png');

    var d = document.createElement('div');
    d.id = 'bcxWm';
    d.style.cssText = 'position:fixed;inset:0;z-index:2147483000;pointer-events:none;' +
      'background-image:url(' + url + ');background-repeat:repeat;' +
      'width:100vw;height:100vh;margin:0;padding:0;border:none;';
    (document.body || document.documentElement).appendChild(d);
  }

  // 防移除：水印层被删/改则自动重绘（开发者工具删除也会恢复）
  var mo = window.MutationObserver ? new MutationObserver(function () {
    if (!document.getElementById('bcxWm')) paint();
  }) : null;
  if (mo) {
    function watch() {
      if (document.getElementById('bcxWm')) mo.observe(document.body, { childList: true, subtree: false });
      else setTimeout(watch, 200);
    }
    watch();
  }

  function boot() {
    paint();
    // 尽力阻止网页内容被复制（不拦截输入框）
    var css = document.createElement('style');
    css.textContent = 'body{-webkit-user-select:none;user-select:none}input,textarea,select{-webkit-user-select:text;user-select:text}';
    document.head.appendChild(css);
    document.addEventListener('contextmenu', function (e) { e.preventDefault(); });
    document.addEventListener('copy', function (e) {
      if (e.target && /^(input|textarea)$/i.test(e.target.tagName)) return;
      e.preventDefault();
    });
    // PrintScreen 按下后尽力用空内容覆盖剪贴板（部分浏览器有效，纯尽力而为）
    document.addEventListener('keyup', function (e) {
      if (e.key === 'PrintScreen' && navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText('博辰序升学规划 · 内容受版权保护 · 咨询 18931577792').catch(function () {});
      }
    });
    // 登记成功后重绘（水印升级为含访客手机号）
    window.addEventListener('storage', function (e) { if (e.key === 'bcx_lead') paint(); });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
