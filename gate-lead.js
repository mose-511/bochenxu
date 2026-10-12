/* 博辰序 家长留资墙 v2 — 访问密码（站长随时可改）+ 省市区三级联动 + 孩子高中
   未持有效访问密码不可浏览；登记数据写入云端数据库 leads 表 */
(function () {
  'use strict';
  var PUB = {
    endpoint: 'https://bochenxu.app.workbuddy.host',
    publishableKey: 'wbpk_Fpg2xqmGc4MgJ42KU7tcbK_IWFSMPTZi0r4lpEk3AD4zt4xyJXvD2Hh'
  };
  var KEY = 'bcx_lead';
  var AREA_URL = 'lib/area-data.json';
  var GRADES = ['高三（2027届）','高二（2028届）','高一（2029届）','初三及以下','复读'];
  var SUBJECTS = ['物理+化学+生物','物理+化学+政治','物理+化学+地理','物理+生物+地理','物理+生物+政治','历史+政治+地理','历史+政治+生物','历史+地理+政治','历史+地理+生物','尚未选科'];
  var AREA = null; // {省:{市:[区县...]}}
  var cloud = null;

  function getCloud() {
    if (!cloud) cloud = window.WorkBuddyCloud.createWorkBuddyCloud({ endpoint: PUB.endpoint, publishableKey: PUB.publishableKey });
    return cloud;
  }
  function esc(s){ return String(s).replace(/[&<>"']/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]; }); }
  function opts(arr, first) {
    var h = first ? '<option value="" disabled selected>' + first + '</option>' : '';
    for (var i = 0; i < arr.length; i++) h += '<option value="' + esc(arr[i]) + '">' + esc(arr[i]) + '</option>';
    return h;
  }
  function unlock(data) {
    try { localStorage.setItem(KEY, JSON.stringify(data)); } catch (e) {}
    var g = document.getElementById('bcxGate');
    if (g) { g.style.opacity = '0'; setTimeout(function(){ g.remove(); }, 350); }
    document.documentElement.style.overflow = '';
  }

  function buildCSS() {
    var css = [
      '#bcxGate{position:fixed;inset:0;z-index:999999;background:linear-gradient(160deg,#071c33 0%,#0A2A4A 55%,#0E3A66 100%);display:flex;align-items:center;justify-content:center;padding:16px;transition:opacity .35s;overflow:auto}',
      '#bcxGate .bcx-card{width:100%;max-width:430px;background:#fff;border-radius:16px;padding:26px 24px 22px;box-shadow:0 18px 60px rgba(0,0,0,.45)}',
      '#bcxGate .bcx-brand{font-size:13px;letter-spacing:4px;color:#8A6D1F;font-weight:700;text-align:center}',
      '#bcxGate h1{margin:6px 0 4px;font-size:22px;color:#0A2A4A;text-align:center;letter-spacing:1px}',
      '#bcxGate .bcx-sub{margin:0 0 16px;font-size:13px;color:#5A7186;text-align:center;line-height:1.6}',
      '#bcxGate .bcx-sub b{color:#B8860B}',
      '#bcxGate label{display:block;font-size:13px;color:#3E5A73;margin:10px 0 4px;font-weight:600}',
      '#bcxGate .bcx-row{display:flex;gap:8px}',
      '#bcxGate .bcx-row>*{flex:1;min-width:0}',
      '#bcxGate input,#bcxGate select{width:100%;padding:10px 12px;border:1px solid #D5E0EB;border-radius:9px;font-size:15px;color:#13293D;background:#F8FBFD;outline:none;box-sizing:border-box;-webkit-appearance:none;appearance:none}',
      '#bcxGate select{background-image:url("data:image/svg+xml;charset=utf-8,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'10\' height=\'6\'%3E%3Cpath d=\'M1 1l4 4 4-4\' stroke=\'%237B93A8\' stroke-width=\'1.6\' fill=\'none\' stroke-linecap=\'round\'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 12px center}',
      '#bcxGate input:focus,#bcxGate select:focus{border-color:#1B5FA8;background:#fff;box-shadow:0 0 0 3px rgba(27,95,168,.12)}',
      '#bcxGate .bcx-btn{width:100%;margin-top:16px;padding:13px;border:none;border-radius:10px;background:linear-gradient(135deg,#C9A227,#B8860B);color:#fff;font-size:16px;font-weight:700;letter-spacing:2px;cursor:pointer}',
      '#bcxGate .bcx-btn:disabled{opacity:.6;cursor:wait}',
      '#bcxGate .bcx-err{display:none;margin-top:10px;padding:9px 12px;border-radius:8px;background:#FDECEC;color:#C0392B;font-size:13px;text-align:center}',
      '#bcxGate .bcx-tip{margin:12px 0 0;font-size:12px;color:#8AA0B4;text-align:center;line-height:1.7}',
      '#bcxGate .bcx-agree{display:flex;gap:8px;align-items:flex-start;margin-top:14px;font-size:12px;color:#5A7186;line-height:1.6;cursor:pointer;text-align:left}',
      '#bcxGate .bcx-agree input{width:auto;flex:none;margin-top:2px;-webkit-appearance:checkbox;appearance:checkbox;accent-color:#C9A227}',
      '#bcxGate .bcx-foot{margin-top:14px;padding-top:12px;border-top:1px solid #EDF2F7;font-size:12px;color:#9AB0C3;text-align:center}',
      '#bcxGate .bcx-done{text-align:center;padding:10px 0 4px}',
      '#bcxGate .bcx-done .ok{width:52px;height:52px;margin:0 auto 12px;border-radius:50%;background:#E8F5EE;display:flex;align-items:center;justify-content:center}',
      '@media (max-width:480px){#bcxGate{align-items:flex-start;padding-top:6vh}#bcxGate .bcx-card{padding:20px 16px 16px}}'
    ].join('\n');
    var style = document.createElement('style');
    style.textContent = css;
    document.head.appendChild(style);
  }

  function buildGate(notice) {
    buildCSS();
    var wrap = document.createElement('div');
    wrap.id = 'bcxGate';
    wrap.innerHTML =
      '<div class="bcx-card">' +
        '<div class="bcx-brand">博辰序 · BOCHENXU</div>' +
        '<h1>领取你的专属升学地图</h1>' +
        '<p class="bcx-sub">1403 所本科院校 × 31 省产业—专业速查。<br>凭<b>访问密码</b>进入 · 简单登记后免费使用全部工具。<br>信息仅用于升学规划联系。</p>' +
        '<div id="bcxPwdStep">' +
          (notice ? '<div class="bcx-err" style="display:block">' + esc(notice) + '</div>' : '') +
          '<label>访问密码（由孟老师发放）</label>' +
          '<input id="bcxPwd" type="text" placeholder="请输入访问密码" autocomplete="off">' +
          '<button id="bcxPwdGo" class="bcx-btn" type="button">验证密码 · 下一步</button>' +
          '<div id="bcxPwdErr" class="bcx-err"></div>' +
          '<p class="bcx-tip">没有密码？请联系孟老师获取：18931577792（微信同号）</p>' +
        '</div>' +
        '<div id="bcxFormStep" style="display:none">' +
          '<label>手机号</label>' +
          '<input id="bcxPhone" type="tel" inputmode="numeric" maxlength="11" placeholder="用于接收规划资讯，仅孟老师可见" autocomplete="tel">' +
          '<label>省份</label>' +
          '<select id="bcxProv"><option value="" disabled selected>请先选择省份</option></select>' +
          '<div class="bcx-row">' +
            '<div><label>城市</label><select id="bcxCity"><option value="" disabled selected>请先选省</option></select></div>' +
            '<div><label>区县</label><select id="bcxDist"><option value="" disabled selected>请先选市</option></select></div>' +
          '</div>' +
          '<label>孩子高中</label>' +
          '<input id="bcxSchool" type="text" maxlength="30" placeholder="如：唐山市第一中学（选填）">' +
          '<label>孩子年级</label>' +
          '<select id="bcxGrade">' + opts(GRADES, '请选择年级') + '</select>' +
          '<label>选科组合</label>' +
          '<select id="bcxSubj">' + opts(SUBJECTS, '请选择选科组合') + '</select>' +
          '<label class="bcx-agree"><input id="bcxAgree" type="checkbox"> <span>我已阅读并同意：登记信息（含孩子年级、学校）仅用于孟老师提供升学规划服务的联系，不向任何第三方提供</span></label>' +
          '<button id="bcxGo" class="bcx-btn" type="button">完成登记 · 进入网站</button>' +
          '<div id="bcxErr" class="bcx-err"></div>' +
          '<p class="bcx-tip">登记一次，本设备畅行。我们承诺不向任何第三方泄露您的信息。</p>' +
          '<div class="bcx-foot">已登记的家长无需重复填写 · 咨询：孟老师 18931577792</div>' +
        '</div>' +
        '<div id="bcxDone" class="bcx-done" style="display:none">' +
          '<div class="ok"><svg width="26" height="26" viewBox="0 0 24 24"><path d="M4 12.5l5 5L20 7" stroke="#1E9E5A" stroke-width="2.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg></div>' +
          '<h1 style="font-size:20px">登记成功</h1>' +
          '<p class="bcx-sub">正在进入博辰序升学决策地图…</p>' +
        '</div>' +
      '</div>';
    document.body.appendChild(wrap);
    document.documentElement.style.overflow = 'hidden';

    // ---- 第一步：访问密码 ----
    var pwdErr = document.getElementById('bcxPwdErr');
    function showFormStep() {
      document.getElementById('bcxPwdStep').style.display = 'none';
      document.getElementById('bcxFormStep').style.display = 'block';
      initArea();
    }
    function tryPwd(v, done) {
      if (!v) { pwdErr.textContent = '请输入访问密码'; pwdErr.style.display = 'block'; return; }
      pwdErr.style.display = 'none';
      var btn = document.getElementById('bcxPwdGo');
      btn.disabled = true; btn.textContent = '验证中…';
      getCloud().database.rpc('check_access_password', { p_code: v }).then(function (r) {
        btn.disabled = false; btn.textContent = '验证密码 · 下一步';
        var ok = !!(r && r.data === true);
        if (ok) done();
        else { pwdErr.textContent = '访问密码不正确（连续错误多次将临时锁定），请联系孟老师获取：18931577792'; pwdErr.style.display = 'block'; }
      }).catch(function () {
        btn.disabled = false; btn.textContent = '验证密码 · 下一步';
        pwdErr.textContent = '网络异常，请稍后重试'; pwdErr.style.display = 'block';
      });
    }
    document.getElementById('bcxPwdGo').addEventListener('click', function () {
      var v = document.getElementById('bcxPwd').value.trim();
      tryPwd(v, function () { showFormStep(); });
    });
    document.getElementById('bcxPwd').addEventListener('keydown', function (e) {
      if (e.key === 'Enter') document.getElementById('bcxPwdGo').click();
    });

    // ---- 第二步：三级联动 + 提交 ----
    function fill(sel, arr, first) {
      sel.innerHTML = opts(arr, first);
    }
    function initArea() {
      var pSel = document.getElementById('bcxProv');
      var cSel = document.getElementById('bcxCity');
      var dSel = document.getElementById('bcxDist');
      if (AREA) { fill(pSel, Object.keys(AREA), '请选择省份'); return; }
      var xhr = new XMLHttpRequest();
      xhr.open('GET', AREA_URL, true);
      xhr.onload = function () {
        try { AREA = JSON.parse(xhr.responseText); } catch (e) { AREA = null; }
        if (AREA) fill(pSel, Object.keys(AREA), '请选择省份');
        else { pSel.outerHTML = '<input id="bcxProv" type="text" placeholder="请输入省份（数据加载失败）">'; }
      };
      xhr.onerror = function () { pSel.outerHTML = '<input id="bcxProv" type="text" placeholder="请输入省份（数据加载失败）">'; };
      xhr.send();
    }
    document.addEventListener('change', function (e) {
      var t = e.target;
      if (t.id === 'bcxProv' && AREA) {
        var cities = Object.keys(AREA[t.value] || {});
        fill(document.getElementById('bcxCity'), cities, cities.length ? '请选择城市' : '该省无市数据');
        fill(document.getElementById('bcxDist'), [], '请先选市');
      } else if (t.id === 'bcxCity' && AREA) {
        var areas = (AREA[document.getElementById('bcxProv').value] || {})[t.value] || [];
        fill(document.getElementById('bcxDist'), areas, areas.length ? '请选择区县' : '该市无区县数据');
      }
    });

    var err = document.getElementById('bcxErr');
    function fail(msg) { err.textContent = msg; err.style.display = 'block'; }

    document.getElementById('bcxGo').addEventListener('click', function () {
      var btn = this;
      var phone = document.getElementById('bcxPhone').value.replace(/\s/g, '');
      var province = document.getElementById('bcxProv').value;
      var city = document.getElementById('bcxCity').value;
      var district = document.getElementById('bcxDist').value;
      var school = document.getElementById('bcxSchool').value.trim();
      var grade = document.getElementById('bcxGrade').value;
      var subject = document.getElementById('bcxSubj').value;
      var pwd = document.getElementById('bcxPwd') ? document.getElementById('bcxPwd').value.trim() : '';

      err.style.display = 'none';
      if (!/^1[3-9]\d{9}$/.test(phone)) return fail('请填写正确的 11 位手机号');
      if (!province) return fail('请选择省份');
      if (!city) return fail('请选择城市');
      if (!district) return fail('请选择区县');
      if (!grade) return fail('请选择孩子年级');
      if (!subject) return fail('请选择选科组合');
      if (!document.getElementById('bcxAgree').checked) return fail('请先勾选同意信息使用说明');

      btn.disabled = true; btn.textContent = '正在提交…';
      getCloud().database.from('leads').insert({
        phone: phone, province: province, city: city,
        district: district || null, school: school || null,
        grade: grade, subject: subject,
        ua: (navigator.userAgent || '').slice(0, 180)
      }).then(function (r) {
        if (r.error) {
          if (r.error.code === '23505') {
            document.getElementById('bcxFormStep').style.display = 'none';
            document.getElementById('bcxDone').style.display = 'block';
            setTimeout(function () { unlock({ phone: phone, pwd: pwd, ts: Date.now() }); }, 700);
            return;
          }
          btn.disabled = false; btn.textContent = '完成登记 · 进入网站';
          fail('提交失败，请检查网络后重试（' + (r.error.code || '未知错误') + '）');
          return;
        }
        document.getElementById('bcxFormStep').style.display = 'none';
        document.getElementById('bcxDone').style.display = 'block';
        setTimeout(function () { unlock({ phone: phone, pwd: pwd, ts: Date.now() }); }, 700);
      }).catch(function () {
        btn.disabled = false; btn.textContent = '完成登记 · 进入网站';
        fail('网络异常，请稍后重试');
      });
    });
  }

  function boot() {
    // 本地开发环境豁免（file://、localhost）：不构成线上安全漏洞——
    // 攻击者无法把线上域名的 Origin 变成本地；能本地打开的人本就持有文件
    var DEV = location.protocol === 'file:' || /^(localhost|127\.0\.0\.1)$/.test(location.hostname);
    if (DEV) return;
    var saved = null;
    try { saved = JSON.parse(localStorage.getItem(KEY) || 'null'); } catch (e) {}
    if (saved && saved.pwd) {
      // 已登记过：静默校验存档的访问密码（站长改密码后此处会失败 → 要求输新密码）
      getCloud().database.rpc('check_access_password', { p_code: saved.pwd }).then(function (r) {
        var ok = !!(r && r.data === true);
        if (ok) return; // 放行
        buildGate('访问密码已更新，请输入新密码（您已登记过资料，验证后直接进入）');
      }).catch(function () {
        // 安全策略：验证不通（含网络异常）一律弹墙，不放行——防拦截请求绕过密码门
        buildGate('网络连接异常，请检查网络后重新验证访问密码');
      });
      return;
    }
    if (saved && !saved.pwd) {
      // v1 老访客（无密码存档）：要求验证一次新密码
      buildGate('访问密码已更新，请输入新密码（您已登记过资料，验证后直接进入）');
      return;
    }
    buildGate();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
