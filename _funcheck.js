/* 星图站功能实测 v3：首页精修版（Hero地图视觉/工具箱/五步）+ tools.html + 省页 + 地图页 */
const { chromium } = require('playwright-core');

const BASE = 'https://star-map-folder.app.workbuddy.host';
const EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';

(async () => {
  const browser = await chromium.launch({ executablePath: EDGE, headless: true });
  const page = await browser.newPage({ viewport: { width: 1366, height: 768 } });
  const errors = [];
  page.on('pageerror', e => errors.push('[pageerror] ' + e.message.slice(0, 160)));
  page.on('console', m => { if (m.type() === 'error') errors.push('[console] ' + m.text().slice(0, 160)); });

  const R = [];
  const ok = (name, cond) => R.push((cond ? 'PASS' : 'FAIL') + '  ' + name);

  // ---- 1. 首页（v3 精修版）----
  await page.goto(BASE + '/', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(1500);
  ok('首页加载无JS报错(累积前)', errors.length === 0);
  const heroH1 = await page.textContent('.hero h1');
  ok('Hero 主标题(孩子的未来…)', heroH1.includes('孩子的未来'));
  const heroMap = await page.evaluate(() => {
    const svg = document.querySelector('.hero-map svg.cnmap-svg');
    return svg && svg.querySelectorAll('.hp[data-p]').length >= 34 &&
           svg.querySelectorAll('.hu circle').length >= 7 &&
           document.querySelector('.hero-cap') && document.querySelector('.hero-cap').textContent.includes('1403');
  });
  ok('Hero 真实中国地图(34省path+7高校节点+图注)', heroMap);
  const navOk = await page.evaluate(() => {
    const ls = [...document.querySelectorAll('.nav-links a')].map(a => a.textContent.trim());
    return ['首页','找大学','选专业','看就业','升学工具'].every(t => ls.includes(t)) &&
           ls.includes('生成我的升学分析') && !ls.includes('规划服务');
  });
  ok('顶部导航5项+行动按钮「生成我的升学分析」', navOk);
  // Hero 搜索：输入"电气"应弹出建议
  await page.fill('#heroq', '电气');
  await page.waitForTimeout(300);
  const sugOn = await page.evaluate(() => document.getElementById('hsug').classList.contains('on'));
  const sugN = await page.evaluate(() => document.querySelectorAll('#hsug a').length);
  ok('Hero搜索即时建议弹出(电气)', sugOn && sugN > 1);
  await page.fill('#heroq', '河北');
  await page.waitForTimeout(300);
  const sugProv = await page.evaluate(() => {
    const a = document.querySelector('#hsug a');
    return a && a.textContent.includes('河北');
  });
  ok('Hero搜索省份直达建议(河北)', sugProv);
  await page.fill('#heroq', '');
  // 引导 + 升学分析入口
  const hstartOk = await page.evaluate(() => {
    const t = document.querySelector('.hstart').innerText;
    return t.includes('不知道从哪里开始') && t.includes('省份') && t.includes('选科') && t.includes('成绩') &&
           !!document.querySelector('.hstart .lnk');
  });
  ok('搜索下引导语+「开始我的升学分析」入口', hstartOk);
  // 四功能卡
  const featsOk = await page.evaluate(() => {
    const hs = [...document.querySelectorAll('.feat h3')].map(h => h.textContent.trim());
    return ['找大学','选专业','看就业','我的规划'].every(t => hs.includes(t));
  });
  ok('四大核心入口卡片', featsOk);
  // 信任数据卡
  const trustOk = await page.evaluate(() => {
    const t = document.querySelector('.trust').innerText;
    return t.includes('31') && t.includes('1403') && t.includes('300') && t.includes('1000');
  });
  ok('信任数据卡(31省/1403所/300+/1000+)', trustOk);
  // 产业×专业×就业链条
  const chainOk = await page.evaluate(() => {
    const t = document.getElementById('future').innerText;
    return t.includes('新能源产业') && t.includes('电气工程及其自动化') && t.includes('华北电力大学') && t.includes('国家电网');
  });
  ok('专业×产业×就业链条示例', chainOk);
  // 五步
  const stepsOk = await page.evaluate(() => {
    const sec = document.getElementById('plan');
    return sec.querySelector('.sec-title').textContent.includes('五步，走稳升学决策') &&
           sec.querySelectorAll('.step').length === 5 &&
           sec.innerText.includes('STEP 5');
  });
  ok('五步标题+5个STEP完整', stepsOk);
  // 升学工具箱：6 入口 + 查看全部
  const toolboxOk = await page.evaluate(() => {
    const boxes = [...document.querySelectorAll('.tbox b')].map(b => b.textContent.trim());
    const want = ['全国高校地图','专业查询','院校对比','河北捡漏','选科查询','招生规则'];
    return boxes.length === 6 && want.every(w => boxes.includes(w));
  });
  ok('升学工具箱6个最常用入口', toolboxOk);
  const viewAll = await page.evaluate(() => {
    const a = document.querySelector('a.viewall');
    return a && a.getAttribute('href') === 'tools.html' && a.textContent.includes('查看全部工具');
  });
  ok('「查看全部工具」入口指向 tools.html', viewAll);
  // 移动端底部咨询条
  const mbbarOk = await page.evaluate(() => !!document.querySelector('.mbbar'));
  ok('移动端底部咨询条存在(样式控制显隐)', mbbarOk);
  // 首页「找大学」卡
  await page.click('.feat a[href="map.html"]');
  await page.waitForURL('**/map.html', { timeout: 30000 }).catch(() => {});
  ok('「找大学」卡片跳转高校地图', page.url().includes('map.html'));

  // ---- 2. 首页 hero 按钮 + 弹窗 ----
  await page.goto(BASE + '/', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(1200);
  await page.click('a.cta-outline');
  await page.waitForTimeout(300);
  const modalOn2 = await page.evaluate(() => document.getElementById('cmodal').classList.contains('on'));
  ok('首页「生成升学分析」按钮弹出二维码弹窗', modalOn2);
  const qrVisible2 = await page.evaluate(() => { const i = document.querySelector('#cmodal img'); return i && i.naturalWidth > 0; });
  ok('首页弹窗二维码图加载成功', qrVisible2);
  await page.evaluate(() => closeContact());
  await page.click('.hstart .lnk');
  await page.waitForTimeout(300);
  const modalOn3 = await page.evaluate(() => document.getElementById('cmodal').classList.contains('on'));
  ok('「开始我的升学分析」入口打开弹窗', modalOn3);

  // ---- 3. tools.html（16 项成果 + 31 省）----
  await page.goto(BASE + '/tools.html', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(1200);
  const toolsCount = await page.evaluate(() => document.querySelectorAll('.card').length);
  ok('tools.html 全部16项成果卡片', toolsCount === 16);
  const provCount = await page.evaluate(() => document.querySelectorAll('.pcard').length);
  ok('tools.html 31省+全国总览入口(32)', provCount === 32);
  // 点击河北卡片
  await page.click('a.pcard[data-search="河北"]');
  await page.waitForURL('**/p/%E6%B2%B3%E5%8C%97%E7%9C%81.html', { timeout: 15000 }).catch(() => {});
  ok('tools页点击河北卡跳转省页', page.url().includes('p/%E6%B2%B3%E5%8C%97%E7%9C%81.html'));

  // ---- 4. 省页弹窗 ----
  await page.waitForTimeout(800);
  await page.evaluate(() => openContact());
  await page.waitForTimeout(300);
  const modalOn1 = await page.evaluate(() => document.getElementById('cmodal').classList.contains('on'));
  const qrVisible1 = await page.evaluate(() => { const i = document.querySelector('#cmodal img'); return i && i.naturalWidth > 0; });
  ok('省页「咨询孟老师」弹窗打开', modalOn1);
  ok('省页弹窗二维码图加载成功', qrVisible1);
  await page.evaluate(() => closeContact());

  // ---- 5. 移动端视口 390×844 ----
  const mob = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await mob.goto(BASE + '/', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await mob.waitForTimeout(1200);
  const navNoWrap = await mob.evaluate(() => {
    const nav = document.querySelector('.nav-in');
    return nav.scrollHeight <= 70;
  });
  ok('移动端导航单行不换行', navNoWrap);
  const heroOrder = await mob.evaluate(() => {
    const t = document.querySelector('.hero-txt').getBoundingClientRect();
    const m = document.querySelector('.hero-map').getBoundingClientRect();
    return m.top >= t.top;  // 地图视觉在文字下方
  });
  ok('移动端 Hero 地图在文字下方', heroOrder);
  const featsCols = await mob.evaluate(() =>
    getComputedStyle(document.querySelector('.feats')).gridTemplateColumns.split(' ').length === 2);
  ok('移动端四大入口 2×2', featsCols);
  const trustCols = await mob.evaluate(() =>
    getComputedStyle(document.querySelector('.tgrid')).gridTemplateColumns.split(' ').length === 2);
  ok('移动端数据卡片 2×2', trustCols);
  const stepsScroll = await mob.evaluate(() => {
    const s = document.querySelector('.steps');
    return s.scrollWidth > s.clientWidth;  // 五步横向可滑动
  });
  ok('移动端五步流程横向可滑动', stepsScroll);
  const barVisible = await mob.evaluate(() => {
    const b = document.querySelector('.mbbar');
    return getComputedStyle(b).display === 'flex';
  });
  ok('移动端底部咨询条显示', barVisible);
  const bodyPad = await mob.evaluate(() => parseFloat(getComputedStyle(document.body).paddingBottom) >= 60);
  ok('移动端 body 底部留白防遮挡', bodyPad);
  const heroBtns = await mob.evaluate(() => {
    const btn = document.querySelector('.hero .cta');
    return btn.getBoundingClientRect().height < 60;
  });
  ok('移动端按钮高度正常(非竖排文字)', heroBtns);
  await mob.close();

  // ---- 6. 地图页 ----
  await page.goto(BASE + '/map.html', { waitUntil: 'domcontentloaded', timeout: 90000 });
  await page.waitForTimeout(9000);
  const mapErrors = errors.filter(e => !e.includes('favicon'));
  ok('地图页无JS报错', mapErrors.length === 0);
  const canvasOk = await page.evaluate(() => !!document.querySelector('canvas'));
  ok('地图 canvas 已渲染', canvasOk);
  const barOk = await page.evaluate(() => !!document.getElementById('mcontactbar'));
  ok('地图页底部联系条存在', barOk);
  await page.evaluate(() => openMapContact());
  await page.waitForTimeout(300);
  const modalOk = await page.evaluate(() => document.getElementById('mcontactmodal').style.display === 'flex');
  const qrVisible3 = await page.evaluate(() => { const i = document.querySelector('#mcontactmodal img'); return i && i.naturalWidth > 0; });
  ok('地图页「微信扫码咨询」弹窗打开', modalOk);
  ok('地图页弹窗二维码图加载成功', qrVisible3);

  console.log('===== 功能实测结果 =====');
  R.forEach(r => console.log(r));
  console.log('===== JS 报错 (' + errors.length + ') =====');
  errors.slice(0, 10).forEach(e => console.log(e));
  await browser.close();
  process.exit(R.some(r => r.startsWith('FAIL')) ? 1 : 0);
})().catch(e => { console.error('SCRIPT ERROR:', e.message); process.exit(2); });
