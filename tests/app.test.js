'use strict';
// E2E aplikasi Electron + engine Python (mode pengembangan). Dialog native, shell.openPath,
// dan pemilih folder di-stub di proses main; PDF yang diproses adalah fixture sintetis.
//   npm test                 -> semua tes, skala tampilan 1
//   EXPCORE_SCALE=1.5 npm test
//   EXPCORE_APP=dist/win-unpacked/ExpCore.exe npm test   -> aplikasi hasil paket + engine Nuitka
const assert = require('node:assert/strict');
const { execFileSync } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { after, afterEach, before, beforeEach, describe, it } = require('node:test');
const { _electron: electron } = require('playwright-core');

const ROOT = path.join(__dirname, '..');
const PYTHON = path.join(ROOT, '.venv', 'Scripts', 'python.exe');
const SCALE = process.env.EXPCORE_SCALE;
const PACKAGED = process.env.EXPCORE_APP ? path.resolve(ROOT, process.env.EXPCORE_APP) : null;
const BPPU_NAME = 'ADIRA DINAMIKA MULTI FINANCE TBK - 25004WOBY - 01-2025 - TIDAK FINAL - NORMAL.pdf';
const BPPU_A2_NAME = 'MITRACOLL SARANA JAYA - 25004WOBY - 01-2025 - TIDAK FINAL - NORMAL.pdf';
// Urutan MODULES = urutan menu Alat dan shortcut Alt+1..5.
const TOOLS = ['bupot', 'bupot2024', 'pm', 'rekening', 'rename'];
const TITLES = { bupot: 'Bukti Potong 2026', bupot2024: 'Bukti Potong 2024', pm: 'Pajak Masukan',
  rekening: 'Rekening Koran', rename: 'Penamaan Bupot' };

let app;
let page;
let temp;

function fixtures(name, copies = 1) {
  const folder = path.join(temp, name);
  execFileSync(PYTHON, [path.join(ROOT, 'tests', 'fixtures.py'), path.join(folder, 'sub')]);
  for (let index = 1; index < copies; index += 1) {
    for (const file of ['bppu.pdf', 'bpbs.pdf', 'faktur.pdf']) {
      fs.copyFileSync(path.join(folder, 'sub', file), path.join(folder, `${index}-${file}`));
    }
  }
  return folder;
}

// Polling berbasis interval, bukan requestAnimationFrame: rAF berhenti total bila jendela tes
// diminimalkan oleh aktivitas desktop, sehingga penantian berbasis rAF tidak pernah selesai.
const waitFor = (fn, arg, options = {}) => page.waitForFunction(fn, arg, { polling: 100, ...options });

const tool = (key) => `#page-${key}`;
const focused = () => page.evaluate(() => document.activeElement.dataset.page || document.activeElement.id
  || document.activeElement.textContent);

// Buka alat lewat menu Alat di header (klik tombol, lalu klik alatnya).
async function openTool(key) {
  await page.click('#tools-trigger');
  await page.click(`.menu-item[data-page="${key}"]`);
}
const status = (key) => page.textContent(`${tool(key)} [data-field="status"]`);

async function stubMain({ answer = 0, pick = null } = {}) {
  await app.evaluate(({ dialog, shell }, options) => {
    globalThis.calls = { dialogs: [], opened: [], picks: [] };
    dialog.showMessageBox = async (_win, opts) => {
      globalThis.calls.dialogs.push(opts);
      return { response: options.answer };
    };
    dialog.showOpenDialog = async (_win, opts) => {
      globalThis.calls.picks.push(opts);
      return options.pick ? { canceled: false, filePaths: [options.pick] } : { canceled: true, filePaths: [] };
    };
    shell.openPath = async (target) => {
      globalThis.calls.opened.push(target);
      return '';
    };
  }, { answer, pick });
}

const calls = () => app.evaluate(() => globalThis.calls);

// IPC bersifat asinkron: tunggu sampai efek di proses main benar-benar terjadi.
async function eventually(check, timeout = 10000) {
  const deadline = Date.now() + timeout;
  for (;;) {
    const value = await check();
    if (value) return value;
    if (Date.now() > deadline) throw new Error(`Kondisi tidak tercapai: ${check}`);
    await new Promise((resolve) => setTimeout(resolve, 50));
  }
}

async function setFolder(key, folder) {
  await page.keyboard.press(`Alt+${TOOLS.indexOf(key) + 1}`);
  await page.fill(`${tool(key)} .folder`, folder);
}

// Engine butuh >= 1 detik untuk mulai, jadi status MEMPROSES selalu teramati sebelum hasil.
async function runTo(key, expected, button = '.run', timeout = 60000) {
  const selector = `${tool(key)} [data-field="status"]`;
  await page.click(`${tool(key)} ${button}`);
  await waitFor((s) => document.querySelector(s).textContent === 'MEMPROSES', selector, { timeout });
  await waitFor(([s, wanted]) => document.querySelector(s).textContent === wanted,
    [selector, expected], { timeout });
}

// Roda mouse di titik tengah bagian elemen yang terlihat dalam area gulir halaman aktif.
async function wheelOver(selector, deltaY) {
  // Posisi dihitung ulang bila halaman masih bergeser (animasi gulir OS pada DPI pecahan) sehingga titik
  // tidak lagi berada di atas target; roda hanya diputar saat titik benar-benar mengenai target.
  for (let attempt = 0; attempt < 10; attempt += 1) {
    const point = await wheelPoint(selector);
    if (await page.evaluate(([target, p]) => Boolean(document.elementFromPoint(p.x, p.y)?.closest(target)), [selector, point])) {
      await page.evaluate((p) => { window.__lastWheel = p; }, { x: point.x, y: point.y });
      await page.mouse.move(point.x, point.y);
      await page.mouse.wheel(0, deltaY);
      await page.waitForTimeout(150);
      return;
    }
    await page.waitForTimeout(100);
  }
  assert.fail(`${selector} terus bergeser; titik roda tidak mengenai target`);
}

async function wheelPoint(selector) {
  const point = await page.evaluate((target) => {
    const element = document.querySelector(target).getBoundingClientRect();
    const view = document.querySelector(target).closest('.scroll').getBoundingClientRect();
    const top = Math.max(element.top, view.top);
    const bottom = Math.min(element.bottom, view.bottom);
    return { x: element.left + element.width / 2, y: (top + bottom) / 2, visible: bottom - top,
      element: element.toJSON(), view: view.toJSON(), inner: [innerWidth, innerHeight, devicePixelRatio],
      scrollTop: document.querySelector(target).closest('.scroll').scrollTop };
  }, selector);
  if (!(point.visible > 8)) {
    const win = await app.evaluate(({ BrowserWindow }) => {
      const w = BrowserWindow.getAllWindows()[0];
      return { content: w.getContentSize(), bounds: w.getBounds() };
    });
    assert.fail(`${selector} tidak terlihat untuk roda mouse: ${JSON.stringify({ ...point, win })}`);
  }
  return point;
}

// Posisi gulir halaman alat di mana log terlihat, tetapi halaman masih dapat digulir lebih jauh.
function logBaseline(key) {
  return page.evaluate((name) => {
    const scroll = document.querySelector(`#page-${name} .scroll`);
    const log = document.querySelector(`#page-${name} .log`);
    const offset = log.getBoundingClientRect().top - scroll.getBoundingClientRect().top + scroll.scrollTop;
    const max = scroll.scrollHeight - scroll.clientHeight;
    return Math.max(0, Math.min(Math.round(offset - scroll.clientHeight * 0.6), max - 40));
  }, key);
}

async function setSize(width, height) {
  // Jendela tes tampil di desktop sungguhan; jendela yang dimaksimalkan (mis. Win+Up) mengabaikan setContentSize.
  await app.evaluate(({ BrowserWindow }, size) => {
    const window = BrowserWindow.getAllWindows()[0];
    if (window.isMaximized()) window.unmaximize();
    if (window.isMinimized()) window.restore();
    window.setContentSize(...size);
  }, [width, height]);
  await waitFor((size) => window.innerWidth === size[0] && window.innerHeight === size[1], [width, height],
    { timeout: 10000 }).catch(async (error) => {
    const state = await app.evaluate(({ BrowserWindow, screen }) => {
      const w = BrowserWindow.getAllWindows()[0];
      return { content: w.getContentSize(), bounds: w.getBounds(), min: w.getMinimumSize(), maximized: w.isMaximized(),
        minimized: w.isMinimized(), focused: w.isFocused(), display: screen.getDisplayMatching(w.getBounds()).workArea };
    });
    const inner = await page.evaluate(() => [innerWidth, innerHeight, devicePixelRatio, document.visibilityState]);
    throw new Error(`setSize(${width}, ${height}) gagal: ${JSON.stringify({ ...state, inner })}\n${error.message}`);
  });
}

// Profil terpisah: tidak bentrok dengan ExpCore terpasang maupun instance tes sebelumnya.
const launchArgs = () => [`--user-data-dir=${path.join(temp, 'profil')}`,
  ...(SCALE ? [`--force-device-scale-factor=${SCALE}`] : []), ...(PACKAGED ? [] : [ROOT])];
const launch = () => electron.launch({ args: launchArgs(), cwd: ROOT, executablePath: PACKAGED ?? undefined });

before(async () => {
  temp = fs.mkdtempSync(path.join(os.tmpdir(), 'expcore-e2e-'));
  app = await launch();
  page = await app.firstWindow();
  page.errors = [];
  page.on('pageerror', (error) => page.errors.push(error.message));
  page.on('console', (message) => message.type() === 'error' && page.errors.push(message.text()));
  await page.waitForSelector('body[data-ready="true"]');
  // Riwayat ukuran jendela untuk artefak kegagalan (window manager dapat mengubahnya terlambat).
  await page.evaluate(() => {
    window.__resizes = [];
    addEventListener('resize', () => window.__resizes.push([Math.round(performance.now()), innerWidth, innerHeight]));
  });
});

after(async () => {
  // Jendela menolak ditutup selama engine berjalan; tunggu dulu agar close() tidak menggantung.
  await page?.waitForFunction(() => ![...document.querySelectorAll('[data-field="status"]')]
    .some((el) => el.textContent === 'MEMPROSES'), null, { timeout: 120000 }).catch(() => {});
  await app?.close();
  fs.rmSync(temp, { recursive: true, force: true, maxRetries: 10, retryDelay: 200 });
});

describe('ExpCore Electron', () => {
  // Jendela tes tampil di desktop sungguhan; bila diminimalkan dari luar, pulihkan sebelum tes berikutnya.
  beforeEach(async (t) => {
    const restored = await app.evaluate(({ BrowserWindow }) => {
      const window = BrowserWindow.getAllWindows()[0];
      if (!window?.isMinimized()) return false;
      window.restore();
      return true;
    });
    if (restored) {
      t.diagnostic('jendela tes sempat diminimalkan dari luar aplikasi; dipulihkan');
      await waitFor(() => document.visibilityState === 'visible', null, { timeout: 5000 });
    }
  });

  // Tes gagal meninggalkan bukti: screenshot dan keadaan jendela/UI di folder artefak (tidak ikut dihapus).
  afterEach(async (t) => {
    if (t.passed || !page) return;
    const dir = path.join(os.tmpdir(), 'expcore-e2e-artefak');
    fs.mkdirSync(dir, { recursive: true });
    const base = path.join(dir, `${new Date().toISOString().replace(/[:.]/g, '-')}-${t.name.slice(0, 40).replace(/[^\w-]+/g, '_')}`);
    await page.screenshot({ path: `${base}.png` }).catch(() => {});
    const state = await page.evaluate(() => ({
      visible: [...document.querySelectorAll('[id^="page-"]')].filter((el) => !el.hidden).map((el) => el.id),
      statuses: Object.fromEntries([...document.querySelectorAll('.tool')].map((el) => [el.id, el.querySelector('[data-field="status"]').textContent])),
      inner: [innerWidth, innerHeight, devicePixelRatio], visibility: document.visibilityState, focus: document.hasFocus(),
    })).catch((error) => ({ error: error.message }));
    const win = await app.evaluate(({ BrowserWindow }) => {
      const w = BrowserWindow.getAllWindows()[0];
      return w && { bounds: w.getBounds(), focused: w.isFocused(), minimized: w.isMinimized(), maximized: w.isMaximized() };
    }).catch((error) => ({ error: error.message }));
    const resizes = await page.evaluate(() => ({ now: Math.round(performance.now()), last: (window.__resizes ?? []).slice(-12) }))
      .catch((error) => ({ error: error.message }));
    fs.writeFileSync(`${base}.json`, JSON.stringify({ state, win, resizes, errors: page.errors }, null, 2));
    t.diagnostic(`artefak kegagalan: ${base}.png / .json`);
  });

  it('membuka jendela dengan identitas, lima halaman, dan tanpa error', async () => {
    const window = await app.browserWindow(page);
    assert.match(await window.evaluate((w) => w.getTitle()), /^ExpCore \d+\.\d+\.\d+ — Toolkit PDF Coretax$/);
    const version = await app.evaluate(({ app: electronApp }) => electronApp.getVersion());
    assert.equal(await page.textContent('#byline'), `Versi ${version} · by Iyan Sanjaya`);
    // Header: Beranda + tombol Alat; kelima alat ada di menu Alat (tertutup saat mulai).
    assert.equal(await page.locator('.nav-item').count(), 2);
    assert.equal(await page.locator('.tool-card').count(), 5);
    assert.deepEqual(await page.$$eval('.menu-item [data-field="title"]', (els) => els.map((el) => el.textContent)),
      TOOLS.map((key) => TITLES[key]));
    assert.equal(await page.isHidden('#tools-menu'), true);
    assert.equal(await page.getAttribute('#tools-trigger', 'aria-expanded'), 'false');
    // Kartu kelima (sendirian di baris terakhir) melebar dua kolom.
    const [first, last] = await page.$$eval('.tool-card', (els) => [els[0], els.at(-1)].map((el) => el.getBoundingClientRect().width));
    assert.ok(last > first * 1.9, `kartu terakhir ${last} vs ${first}`);
    // Semua placeholder ikon diganti SVG Reicon; ikon dekoratif disembunyikan dari pembaca layar.
    assert.equal(await page.locator('[data-icon]').count(), 0);
    const icons = await page.$$eval('svg.reicon', (els) => els.map((el) => el.getAttribute('aria-hidden')));
    assert.ok(icons.length > 40 && icons.every((hidden) => hidden === 'true'), `ikon: ${icons.length}`);
    // Font Inter dibundel lokal (tanpa jaringan) dan benar-benar dipakai.
    await page.evaluate(() => document.fonts.ready);
    assert.ok(await page.evaluate(() => document.fonts.check('500 16px "Inter Variable"')));
    assert.deepEqual(await window.evaluate((w) => w.getMinimumSize()), [960, 620]);
    assert.equal(await window.evaluate((w) => w.isMenuBarVisible()), false);
    assert.deepEqual(page.errors, []);
    assert.equal(await app.evaluate(({ app: electronApp }) => electronApp.isPackaged), Boolean(PACKAGED));
    // AUMID jendela harus sama dengan appId installer agar shortcut dan taskbar menyatu.
    const appId = JSON.parse(fs.readFileSync(path.join(ROOT, 'package.json'), 'utf8')).build.appId;
    assert.ok(fs.readFileSync(path.join(ROOT, 'app', 'main.js'), 'utf8').includes(`const APP_ID = '${appId}';`));
  });

  it('navigasi lewat menu Alat, kartu beranda, dan Alt+0..5', async () => {
    const expectPage = async (key) => {
      assert.equal(await page.isVisible(key === 'home' ? '#page-home' : tool(key)), true, key);
      assert.equal(await page.locator('[id^="page-"]:visible').count(), 1);
      const current = key === 'home' ? '.nav-item[data-page="home"]' : `.menu-item[data-page="${key}"]`;
      assert.equal(await page.getAttribute(current, 'aria-current'), 'page');
      assert.equal(await page.locator('[aria-current="page"]').count(), 1);
      // Tombol Alat menampilkan alat aktif dan menutup daftarnya setelah memilih.
      assert.equal(await page.textContent('#tools-trigger .current'), key === 'home' ? '' : `· ${TITLES[key]}`);
      assert.equal(await page.getAttribute('#tools-trigger', 'aria-expanded'), 'false');
      if (key !== 'home') assert.equal(await page.textContent(`${tool(key)} h1`), TITLES[key]);
      // Pill indikator (Motion) berhenti tepat di bawah Beranda atau tombol Alat.
      await waitFor((selector) => {
        const pill = document.querySelector('#nav-indicator').getBoundingClientRect();
        const item = document.querySelector(selector).getBoundingClientRect();
        return Math.abs(pill.left - item.left) < 1 && Math.abs(pill.width - item.width) < 1;
      }, key === 'home' ? '.nav-item[data-page="home"]' : '#tools-trigger', { timeout: 3000 });
    };
    await openTool('pm');
    await expectPage('pm');
    // Item menu yang dipilih ikut tersembunyi; fokus pindah ke judul halaman tujuan.
    assert.equal(await focused(), 'Pajak Masukan');
    await page.keyboard.press('Alt+0');
    await expectPage('home');
    await page.click('.open-tool[data-page="rename"]');
    await expectPage('rename');
    assert.equal(await focused(), 'Penamaan Bupot');
    for (const [index, key] of [[1, 'bupot'], [2, 'bupot2024'], [3, 'pm'], [4, 'rekening'], [5, 'rename'], [0, 'home']]) {
      await page.keyboard.press(`Alt+${index}`);
      await expectPage(key);
    }

    // Regresi: navigasi cepat dulu membuat pegas indikator mewarisi kecepatan lompatan instan (lebar
    // hingga ribuan px, meluap keluar jendela). Pantau setiap frame: lebar indikator tidak boleh melebihi
    // tujuan terlebarnya (+5% ayunan pegas) dan dokumen tidak pernah meluap.
    await page.evaluate(() => {
      const watch = { on: true, pill: 0, target: 0, overflow: 0 };
      window.__pill = watch;
      const tick = () => {
        const width = (selector) => document.querySelector(selector).getBoundingClientRect().width;
        watch.pill = Math.max(watch.pill, width('#nav-indicator'));
        watch.target = Math.max(watch.target, width('#tools-trigger'), width('.nav-item[data-page="home"]'));
        watch.overflow = Math.max(watch.overflow, document.documentElement.scrollWidth - innerWidth);
        if (watch.on) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    });
    for (let round = 0; round < 4; round += 1) {
      for (const digit of [1, 0, 4, 2, 0, 5, 3, 0]) await page.keyboard.press(`Alt+${digit}`);
    }
    await page.waitForTimeout(700);
    const watch = await page.evaluate(() => { window.__pill.on = false; return window.__pill; });
    assert.ok(watch.pill <= watch.target * 1.05 + 1 && watch.overflow <= 0, JSON.stringify(watch));
    await expectPage('home');
  });

  it('menu Alat: grup, klik di luar, Esc, panah, Enter, Tab keluar, dan muat di jendela minimum', async () => {
    const expanded = () => page.getAttribute('#tools-trigger', 'aria-expanded');
    await page.keyboard.press('Alt+0');
    assert.deepEqual(await page.$$eval('#tools-menu ul', (lists) => lists.map((list) => [list.getAttribute('aria-label'),
      [...list.querySelectorAll('.menu-item')].map((item) => item.dataset.page)])),
    [['Ekstraksi ke Excel', ['bupot', 'bupot2024', 'pm', 'rekening']], ['Kelola PDF', ['rename']]]);
    // Klik membuka, klik di luar menutup, klik tombol lagi juga menutup.
    await page.click('#tools-trigger');
    assert.equal(await expanded(), 'true');
    assert.equal(await page.isVisible('#tools-menu'), true);
    await page.click('.brand'); // Di luar navigasi dan tidak tertutup panel.
    assert.equal(await expanded(), 'false');
    assert.equal(await page.isHidden('#tools-menu'), true);
    await page.click('#tools-trigger');
    await page.click('#tools-trigger');
    assert.equal(await expanded(), 'false');

    // Enter pada tombol membuka dan memfokuskan alat pertama; panah berputar; Home/End; Esc kembali ke tombol.
    await page.focus('#tools-trigger');
    await page.keyboard.press('Enter');
    assert.equal(await focused(), 'bupot');
    for (const [key, expected] of [['ArrowUp', 'rename'], ['ArrowDown', 'bupot'], ['End', 'rename'], ['Home', 'bupot'],
      ['ArrowDown', 'bupot2024']]) {
      await page.keyboard.press(key);
      assert.equal(await focused(), expected, key);
    }
    await page.keyboard.press('Escape');
    assert.equal(await expanded(), 'false');
    assert.equal(await focused(), 'tools-trigger');

    // Panah bawah membuka tepat di alat aktif; Enter memilih dan fokus pindah ke judul halaman.
    await page.keyboard.press('Alt+3');
    await page.focus('#tools-trigger');
    await page.keyboard.press('ArrowDown');
    assert.equal(await focused(), 'pm');
    assert.equal(await page.isVisible('.menu-item[data-page="pm"] .menu-check'), true, 'alat aktif bertanda centang');
    await page.keyboard.press('ArrowDown');
    await page.keyboard.press('Enter');
    assert.equal(await expanded(), 'false');
    assert.equal(await page.isVisible(tool('rekening')), true);
    assert.equal(await focused(), 'Rekening Koran');

    // Tab keluar dari daftar menutupnya.
    await page.focus('#tools-trigger');
    await page.keyboard.press('ArrowUp');
    assert.equal(await focused(), 'rename');
    await page.keyboard.press('Tab');
    assert.equal(await expanded(), 'false');
    assert.equal(await focused(), 'check-update');

    // Panel tidak keluar jendela pada ukuran minimum, juga dengan judul alat terpanjang di tombol.
    await setSize(960, 620);
    await page.keyboard.press('Alt+1');
    await page.click('#tools-trigger');
    const box = await page.$eval('#tools-menu', (el) => el.getBoundingClientRect().toJSON());
    assert.ok(box.left >= 0 && box.right <= 960 && box.bottom <= 620, JSON.stringify(box));
    await page.keyboard.press('Escape');
    assert.deepEqual(page.errors, []);
  });

  it('tata letak responsif tanpa overflow pada ukuran minimum dan lebar', async () => {
    for (const [width, height] of [[960, 620], [1180, 800], [960, 700], [1400, 900], [960, 620]]) {
      await setSize(width, height);
      for (const key of ['home', ...TOOLS]) {
        await page.keyboard.press(`Alt+${['home', ...TOOLS].indexOf(key)}`);
        const metrics = await page.evaluate((name) => {
          const pageElement = document.querySelector(`#page-${name}`);
          const scroll = pageElement.querySelector('.scroll');
          const box = (selector) => pageElement.querySelector(selector)?.getBoundingClientRect().toJSON();
          return {
            docOverflow: document.documentElement.scrollWidth - window.innerWidth,
            scrollOverflow: scroll.scrollWidth - scroll.clientWidth,
            scrollable: scroll.scrollHeight > scroll.clientHeight,
            run: box('.run'), apply: box('.apply'), log: box('.log'),
            viewport: [window.innerWidth, window.innerHeight],
            title: getComputedStyle(document.querySelector('#home-title')).fontSize,
            columns: getComputedStyle(document.querySelector('.tool-cards')).gridTemplateColumns.split(' ').length,
            header: ['.brand', '#main-nav', '.header-actions'].map((s) => document.querySelector(s).getBoundingClientRect().toJSON()),
            labels: [...document.querySelectorAll('.header-actions .label')].map((el) => el.getClientRects().length > 0),
            // Bukti bila meluap: elemen yang melewati tepi kanan jendela beserta transform-nya.
            culprits: [...document.querySelectorAll('body *')].filter((el) => el.getClientRects().length
              && el.getBoundingClientRect().right > window.innerWidth + 0.5).slice(0, 6)
              .map((el) => `${el.tagName}#${el.id}.${String(el.className).slice(0, 40)} right=${el.getBoundingClientRect().right
                .toFixed(1)} transform=${getComputedStyle(el).transform} opacity=${getComputedStyle(el).opacity}`),
          };
        }, key);
        const label = `${key} @ ${width}x${height}`;
        assert.ok(metrics.docOverflow <= 0,
          `${label}: horizontal overflow dokumen ${metrics.docOverflow}px ${JSON.stringify(metrics.culprits)}`);
        assert.ok(metrics.scrollOverflow <= 0, `${label}: horizontal overflow halaman`);
        const [brand, nav, actions] = metrics.header;
        assert.ok(brand.right <= nav.left && nav.right <= actions.left && actions.right <= metrics.viewport[0],
          `${label}: header bertumpuk ${JSON.stringify(metrics.header)}`);
        // Header ringkas: label tombol update dan badge privasi selalu tampil, juga di lebar minimum.
        assert.deepEqual(metrics.labels, [true, true], label);
        if (key === 'home') {
          assert.equal(metrics.title, metrics.viewport[0] < 1100 ? '40px' : '50px', label);
          assert.equal(metrics.columns, 2, label);
        } else {
          for (const button of key === 'rename' ? [metrics.run, metrics.apply] : [metrics.run]) {
            assert.ok(button.bottom <= metrics.viewport[1] && button.right <= metrics.viewport[0],
              `${label}: tombol aksi harus selalu terlihat`);
          }
          assert.ok(metrics.log.height >= 120, `${label}: log terlalu pendek`);
        }
      }
    }
  });

  it('roda mouse: kartu menggulir halaman, log panjang menggulir sendiri, ujung log meneruskan', async (t) => {
    await setSize(960, 620);
    await page.keyboard.press('Alt+2');
    const scroll = `${tool('bupot2024')} .scroll`;
    const log = `${tool('bupot2024')} .log`;
    const top = (selector) => page.$eval(selector, (el) => el.scrollTop);
    // Scroll roda di Windows dianimasikan; tunggu hasilnya alih-alih jeda tetap, lalu catat lamanya.
    const scrolled = async (selector, label, from = 0) => {
      const started = Date.now();
      while (Date.now() - started < 2000) {
        // > 1 px: posisi gulir dibulatkan ke piksel perangkat (mis. 218 -> 218,4 pada skala 125%).
        if (await top(selector) > from + 1) {
          if (Date.now() - started > 150) t.diagnostic(`${label}: bergulir setelah ${Date.now() - started} ms`);
          return true;
        }
        await page.waitForTimeout(25);
      }
      const state = await page.evaluate(([target, point]) => {
        const hit = document.elementFromPoint(point.x, point.y);
        const el = document.querySelector(target);
        return { hit: hit && `${hit.tagName}.${hit.className}`, visibility: document.visibilityState, focus: document.hasFocus(),
          inner: [innerWidth, innerHeight], scrollTop: el.scrollTop, max: el.scrollHeight - el.clientHeight };
      }, [selector, await page.evaluate(() => window.__lastWheel ?? { x: 0, y: 0 })]);
      const win = await app.evaluate(({ BrowserWindow }) => {
        const w = BrowserWindow.getAllWindows()[0];
        return { bounds: w.getBounds(), focused: w.isFocused(), minimized: w.isMinimized(), visible: w.isVisible() };
      });
      t.diagnostic(`${label} GAGAL: ${JSON.stringify({ ...state, win })}`);
      return false;
    };
    // Mulai dari keadaan diam: animasi gestur sebelumnya selesai dan posisi kembali ke titik awal.
    const reset = async (selector, value = 0) => {
      await page.waitForTimeout(300);
      await page.$eval(selector, (el, v) => { el.scrollTop = v; }, value);
      await page.waitForTimeout(300);
    };
    for (const target of [`${tool('bupot2024')} .hint`, `${tool('bupot2024')} .browse`, `${tool('bupot2024')} .folder`]) {
      await reset(scroll);
      await wheelOver(target, 120);
      assert.ok(await scrolled(scroll, target), `roda mouse di atas ${target} harus menggulir halaman`);
    }
    // Log pendek tidak menahan roda mouse. Baseline dihitung ulang sebelum setiap langkah karena
    // window manager Windows dapat mengubah geometri jendela tes setelah setSize.
    let base = await logBaseline('bupot2024');
    await reset(scroll, base);
    await wheelOver(log, 120);
    assert.ok(await scrolled(scroll, 'log pendek', base), 'log pendek menahan scroll halaman');
    // Log panjang: hanya log yang bergulir; di ujungnya halaman ikut bergulir.
    await page.$eval(log, (el) => el.append('baris log\n'.repeat(80)));
    await reset(log);
    base = await logBaseline('bupot2024');
    await reset(scroll, base);
    await wheelOver(log, 120);
    assert.ok(await scrolled(log, 'log panjang'), 'log panjang tidak bergulir');
    await page.waitForTimeout(400);
    assert.ok(Math.abs(await top(scroll) - base) < 1, 'log dan halaman bergulir bersamaan');
    // Pengguna menggulir log sampai ujung, lalu memutar roda lagi pada gestur baru.
    await wheelOver(log, 120 * 40);
    await waitFor((selector) => {
      // Di ujung bila mencoba menggulir lebih jauh tidak mengubah posisi (aman untuk DPI pecahan).
      const el = document.querySelector(selector);
      const top = el.scrollTop;
      el.scrollTop = top + 100000;
      const moved = el.scrollTop - top;
      el.scrollTop = top;
      return Math.abs(moved) < 0.5;
    }, log, { timeout: 3000 });
    base = await logBaseline('bupot2024');
    await reset(scroll, base);
    await page.waitForTimeout(300); // Gestur baru, bukan lanjutan gestur yang terkunci pada log.
    await wheelOver(log, 120);
    assert.ok(await scrolled(scroll, 'ujung log', base), 'ujung log menahan scroll halaman');
    await page.$eval(log, (el) => { el.textContent = ''; });
    await reset(scroll);
  });

  it('isian folder mengatur label, status, dan tombol', async () => {
    await page.keyboard.press('Alt+1');
    assert.equal(await page.isDisabled(`${tool('bupot')} .run`), true);
    await page.fill(`${tool('bupot')} .folder`, 'C:\\contoh');
    assert.equal(await status('bupot'), 'SIAP DIPROSES');
    assert.equal(await page.textContent(`${tool('bupot')} [data-field="folder-label"]`), 'Folder sumber · dapat diketik atau dipilih');
    assert.equal(await page.isEnabled(`${tool('bupot')} .run`), true);
    await page.fill(`${tool('bupot')} .folder`, '   ');
    assert.equal(await status('bupot'), 'MENUNGGU FOLDER');
    assert.equal(await page.isDisabled(`${tool('bupot')} .run`), true);
  });

  it('folder yang tidak ada ditolak sebelum engine berjalan', async () => {
    await stubMain();
    for (const folder of [path.join(temp, 'tidak-ada'), 'relatif\\folder']) {
      await setFolder('bupot', folder);
      assert.equal(await page.evaluate((f) => window.expcore.runJob('bupot', f), folder), false);
    }
    const { dialogs } = await calls();
    assert.deepEqual(dialogs.map((d) => d.title), ['Folder tidak ditemukan', 'Folder tidak ditemukan']);
    assert.equal(await status('bupot'), 'SIAP DIPROSES');
  });

  it('folder tanpa PDF berakhir PERLU DIPERIKSA dengan alasan di log', async () => {
    const empty = path.join(temp, 'kosong');
    fs.mkdirSync(empty);
    await setFolder('bupot', empty);
    await runTo('bupot', 'PERLU DIPERIKSA');
    assert.match(await page.textContent(`${tool('bupot')} .log`), /\d\d:\d\d:\d\d {3}GAGAL: Tidak ada PDF di folder/);
    assert.equal(await page.isDisabled(`${tool('bupot')} .open`), true);
    assert.equal(await page.isEnabled(`${tool('bupot')} .run`), true, 'kontrol pulih setelah gagal');
  });

  for (const [key, output, summary] of [
    ['bupot', '!Hasil_Rekap_Bupot.xlsx', 'Selesai — 1 baris, 3 PDF dilewati.'],
    ['bupot2024', '!Hasil_Rekap_Bupot_2024.xlsx', 'Selesai — 1 baris, 3 PDF dilewati.'],
    ['pm', 'Hasil_Pajak_Masukan.xlsx', 'Selesai — 1 baris, 3 PDF dilewati.'],
    ['rekening', '!Hasil_Rekap_Rekening_Koran.xlsx',
      'Selesai — 1 rekening koran, 5 transaksi, 0 perlu dicek, 3 PDF dilewati.'],
  ]) {
    it(`ekstraksi ${key}: PDF -> Excel, ringkasan, log, dan Buka hasil`, async () => {
      const folder = fixtures(`Ekstraksi ${key} — Ünïcode`);
      // Jalur dari "Copy as path" Explorer (bertanda kutip dan berspasi) tetap diterima.
      await setFolder(key, ` "${folder}" `);
      await stubMain();
      await runTo(key, 'SELESAI');
      assert.ok(fs.statSync(path.join(folder, output)).size > 0);
      assert.equal(await page.textContent(`${tool(key)} [data-field="summary"]`), summary);
      const log = await page.textContent(`${tool(key)} .log`);
      assert.match(log, /^\d\d:\d\d:\d\d {3}Memproses 4 file …\n/);
      assert.match(log, /Membaca sub[\\/]bppu\.pdf/);
      assert.ok(log.trimEnd().endsWith(summary), log);
      assert.equal(await page.getAttribute(`${tool(key)} .progress`, 'aria-valuenow'), '100');
      await page.click(`${tool(key)} .open`);
      assert.deepEqual(await eventually(async () => (await calls()).opened.length && (await calls()).opened),
        [path.join(folder, output)]);
      assert.equal(await page.textContent('#tools-trigger .current'), `· ${await page.textContent(`${tool(key)} h1`)}`);
    });
  }

  it('rekap lama hanya diganti setelah konfirmasi', async () => {
    const folder = path.join(temp, 'Ekstraksi bupot — Ünïcode');
    const output = path.join(folder, '!Hasil_Rekap_Bupot.xlsx');
    fs.writeFileSync(output, 'rekap lama');
    await setFolder('bupot', folder);
    await stubMain({ answer: 1 });
    assert.equal(await page.evaluate((f) => window.expcore.runJob('bupot', f), folder), false);
    assert.equal(fs.readFileSync(output, 'utf8'), 'rekap lama');
    const [dialog] = (await calls()).dialogs;
    assert.equal(dialog.title, 'Ganti rekap sebelumnya?');
    assert.deepEqual([dialog.buttons, dialog.defaultId, dialog.cancelId], [['Ganti rekap', 'Batal'], 1, 1]);
    await stubMain({ answer: 0 });
    await runTo('bupot', 'SELESAI');
    assert.notEqual(fs.readFileSync(output, 'utf8'), 'rekap lama');
  });

  it('penamaan: pratinjau wajib, konfirmasi, penerapan, dan reset saat folder berubah', async () => {
    const folder = fixtures('penamaan');
    await setFolder('rename', folder);
    await stubMain({ answer: 1 });
    assert.equal(await page.isDisabled(`${tool('rename')} .apply`), true);
    assert.equal(await page.evaluate((f) => window.expcore.runJob('rename', f, true), folder), false,
      'main menolak penerapan tanpa pratinjau');
    assert.deepEqual((await calls()).dialogs, []);

    await runTo('rename', 'SELESAI');
    assert.match(await page.textContent(`${tool('rename')} [data-field="summary"]`), /^Pratinjau selesai — 1 siap\/berhasil/);
    assert.ok(fs.existsSync(path.join(folder, 'sub', 'bppu.pdf')), 'pratinjau tidak mengubah nama');
    assert.equal(await page.isEnabled(`${tool('rename')} .apply`), true);

    // Mengubah folder membatalkan pratinjau (juga di sisi main).
    await page.fill(`${tool('rename')} .folder`, `${folder}\\sub`);
    assert.equal(await page.isDisabled(`${tool('rename')} .apply`), true);
    assert.equal(await page.isDisabled(`${tool('rename')} .open`), true);
    await page.fill(`${tool('rename')} .folder`, folder);
    assert.equal(await page.isDisabled(`${tool('rename')} .apply`), true);

    await runTo('rename', 'SELESAI');
    await page.click(`${tool('rename')} .apply`); // Batal pada konfirmasi.
    const dialogs = await eventually(async () => (await calls()).dialogs.length && (await calls()).dialogs);
    assert.equal(dialogs.at(-1).title, 'Terapkan penamaan?');
    assert.deepEqual(dialogs.at(-1).buttons, ['Terapkan nama', 'Batal']);
    assert.ok(fs.existsSync(path.join(folder, 'sub', 'bppu.pdf')));

    await stubMain({ answer: 0 });
    await runTo('rename', 'SELESAI', '.apply');
    assert.match(await page.textContent(`${tool('rename')} [data-field="summary"]`), /^Penerapan selesai — 1 siap\/berhasil/);
    assert.ok(fs.existsSync(path.join(folder, 'sub', BPPU_NAME)));
    assert.ok(!fs.existsSync(path.join(folder, 'sub', 'bppu.pdf')));
    assert.equal(await page.isDisabled(`${tool('rename')} .apply`), true, 'penerapan baru perlu pratinjau baru');
    await page.click(`${tool('rename')} .open`);
    assert.deepEqual(await eventually(async () => (await calls()).opened.length && (await calls()).opened), [folder],
      'Buka hasil membuka folder PDF');
    const logs = fs.readdirSync(folder).filter((name) => name.startsWith('Log_Penamaan_Bupot_'));
    assert.equal(logs.filter((name) => name.includes('_Penerapan_')).length, 1, logs.join());
  });

  it('penamaan: sumber nama C.3 atau A.2, pratinjau terikat pada sumbernya', async () => {
    const folder = fixtures('sumber nama');
    const radio = (value) => `${tool('rename')} .name-source input[value="${value}"]`;
    await setFolder('rename', folder);
    await stubMain({ answer: 0 });
    // Bawaan: Identitas Pemotong (C.3); pilihan berupa radio asli yang dapat dipilih dengan panah.
    assert.equal(await page.isChecked(radio('pemotong')), true);
    assert.deepEqual(await page.$$eval(`${tool('rename')} .name-source .source-option`, (els) => els.map((el) => el.textContent)),
      ['Identitas PemotongC.3 · Nama pemotong dan/atau pemungut PPh',
        'Wajib Pajak yang DipotongA.2 · Nama identitas wajib pajak yang dipotong']);
    await page.focus(radio('pemotong'));
    await page.keyboard.press('ArrowRight');
    assert.equal(await page.isChecked(radio('penerima')), true);

    await runTo('rename', 'SELESAI');
    assert.equal(await page.isEnabled(`${tool('rename')} .apply`), true);
    // Mengganti sumber membatalkan pratinjau, di renderer maupun di main.
    await page.click(`${tool('rename')} .source-option:has(input[value="pemotong"])`);
    assert.equal(await page.isDisabled(`${tool('rename')} .apply`), true);
    assert.equal(await status('rename'), 'SIAP DIPROSES');
    assert.equal(await page.evaluate((f) => window.expcore.runJob('rename', f, true, 'pemotong'), folder), false,
      'pratinjau A.2 tidak berlaku untuk penerapan C.3');
    assert.equal(await page.evaluate((f) => window.expcore.runJob('rename', f, false, 'lainnya'), folder), false,
      'sumber nama tidak dikenal ditolak');
    assert.deepEqual((await calls()).dialogs, []);
    assert.ok(fs.existsSync(path.join(folder, 'sub', 'bppu.pdf')));

    await page.click(`${tool('rename')} .source-option:has(input[value="penerima"])`);
    await runTo('rename', 'SELESAI');
    const csvName = fs.readdirSync(folder).filter((name) => name.includes('_Pratinjau_')).sort().at(-1);
    const csvText = fs.readFileSync(path.join(folder, csvName), 'utf8');
    assert.ok(csvText.includes(`SIAP,sub,bppu.pdf,${BPPU_A2_NAME}`), csvText);
    assert.match(await page.textContent(`${tool('rename')} .log`), /Pratinjau: memeriksa 4 PDF … \(nama dari Wajib Pajak yang Dipotong \(A\.2\)\)/);
    await runTo('rename', 'SELESAI', '.apply');
    const [dialog] = (await calls()).dialogs;
    assert.match(dialog.detail, /memakai nama dari Wajib Pajak yang Dipotong\./);
    assert.ok(fs.existsSync(path.join(folder, 'sub', BPPU_A2_NAME)));
    assert.ok(!fs.existsSync(path.join(folder, 'sub', 'bppu.pdf')) && !fs.existsSync(path.join(folder, 'sub', BPPU_NAME)));
  });

  it('selama memproses: kontrol terkunci, navigasi bebas, satu pekerjaan, jendela tidak ditutup', async () => {
    const folder = fixtures('besar', 40);
    await setFolder('pm', folder);
    await stubMain();
    await page.click(`${tool('pm')} .run`);
    await waitFor(() => document.querySelector('#page-pm [data-field="summary"]').textContent.startsWith('Memeriksa PDF'), null, { timeout: 60000 });
    assert.equal(await status('pm'), 'MEMPROSES');
    // Alat yang sibuk ditandai aria-busy dan titik berdenyut di menu; tombol Alat juga bertitik saat menu tertutup.
    assert.equal(await page.getAttribute('.menu-item[data-page="pm"]', 'aria-busy'), 'true');
    assert.equal(await page.isVisible('#tools-trigger .busy-dot'), true);
    await page.click('#tools-trigger');
    assert.equal(await page.isVisible('.menu-item[data-page="pm"] .busy-dot'), true);
    assert.equal(await page.textContent('.menu-item[data-page="pm"] [data-field="title"]'), 'Pajak Masukan');
    await page.keyboard.press('Escape');
    assert.ok(await page.$$eval('.folder, .browse, .run, .apply, .name-source input', (els) => els.every((el) => el.disabled)));
    await page.keyboard.press('Alt+1');
    assert.equal(await page.isVisible(tool('bupot')), true, 'navigasi tetap aktif');
    assert.equal(await page.evaluate((f) => window.expcore.runJob('bupot', f), folder), false, 'pekerjaan kedua ditolak');
    await app.evaluate(({ BrowserWindow }) => BrowserWindow.getAllWindows()[0].close());
    const closing = await eventually(async () => (await calls()).dialogs.length && (await calls()).dialogs);
    assert.deepEqual(closing.map((d) => d.title), ['Proses masih berjalan']);
    assert.equal(await app.evaluate(({ BrowserWindow }) => BrowserWindow.getAllWindows().length), 1);
    // Event progres pertama bernilai 0; tunggu langkah berikutnya sebelum memeriksa.
    await waitFor(() => Number(document.querySelector('#page-pm .progress').getAttribute('aria-valuenow')) > 0,
      null, { timeout: 60000 });
    const progress = Number(await page.getAttribute(`${tool('pm')} .progress`, 'aria-valuenow'));
    assert.ok(progress < 100 && await status('pm') === 'MEMPROSES', `progres determinan saat berjalan: ${progress}`);
    await waitFor(() => document.querySelector('#page-pm [data-field="status"]').textContent === 'SELESAI', null, { timeout: 120000 });
    assert.equal(await page.textContent(`${tool('pm')} [data-field="summary"]`), 'Selesai — 40 baris, 81 PDF dilewati.');
    assert.equal(await page.getAttribute('.menu-item[data-page="pm"]', 'aria-busy'), 'false');
    assert.equal(await page.isHidden('#tools-trigger .busy-dot'), true);
    assert.equal(await page.$eval('.menu-item[data-page="pm"] .busy-dot', (el) => el.hidden), true);
    // Pekerjaan selesai saat halaman lain aktif: kembali ke alat menampilkan baris log terakhir.
    await page.keyboard.press('Alt+3');
    assert.ok(await page.$eval(`${tool('pm')} .log`, (el) => {
      // Di ujung bila mencoba menggulir lebih jauh tidak mengubah posisi (aman untuk DPI pecahan).
      const top = el.scrollTop;
      el.scrollTop = top + 100000;
      const moved = el.scrollTop - top;
      el.scrollTop = top;
      return el.scrollHeight > el.clientHeight && Math.abs(moved) < 0.5;
    }), 'log tidak berada di baris terakhir');
    // Log panjang yang digulir otomatis ke ujung tidak boleh menahan roda mouse (termasuk DPI pecahan).
    await setSize(960, 620);
    const base = await logBaseline('pm');
    await page.$eval(`${tool('pm')} .scroll`, (el, value) => { el.scrollTop = value; }, base);
    await page.waitForTimeout(600);
    await wheelOver(`${tool('pm')} .log`, 120);
    assert.ok(await eventually(async () => await page.$eval(`${tool('pm')} .scroll`, (el) => el.scrollTop) > base + 1, 2000)
      .catch(() => false), 'ujung log otomatis menahan scroll halaman');
    assert.ok(await page.$$eval('.folder, .browse', (els) => els.every((el) => !el.disabled)));
  });

  it('salin log, Ctrl+O, Page Down, dan aktivasi tombol lewat keyboard', async () => {
    const saved = await app.evaluate(({ clipboard }) => clipboard.readText());
    try {
      await page.keyboard.press('Alt+3');
      await page.click(`${tool('pm')} .copy`);
      assert.equal(await page.textContent(`${tool('pm')} .copy`), 'Disalin');
      const copied = await app.evaluate(({ clipboard }) => clipboard.readText());
      assert.equal(copied, await page.textContent(`${tool('pm')} .log`));
      assert.match(copied, /Selesai — 40 baris/);
      await waitFor(() => document.querySelector('#page-pm .copy').textContent === 'Salin log', null, { timeout: 3000 });
    } finally {
      await app.evaluate(({ clipboard }, text) => clipboard.writeText(text), saved);
    }

    const picked = fixtures('dipilih');
    await stubMain({ pick: picked });
    await page.keyboard.press('Alt+2');
    await page.focus('#tools-trigger');
    await page.keyboard.press('Control+O');
    await waitFor((f) => document.querySelector('#page-bupot2024 .folder').value === f, picked);
    assert.equal((await calls()).picks[0].properties[0], 'openDirectory');
    assert.equal(await status('bupot2024'), 'SIAP DIPROSES');

    await setSize(960, 620);
    await page.focus('#tools-trigger');
    await page.keyboard.press('PageDown');
    assert.ok(await page.$eval(`${tool('bupot2024')} .scroll`, (el) => el.scrollTop) > 0, 'Page Down menggulir halaman');
    await page.keyboard.press('PageUp');
    assert.equal(await page.$eval(`${tool('bupot2024')} .scroll`, (el) => el.scrollTop), 0);

    await page.focus(`${tool('bupot2024')} .folder`);
    await page.keyboard.press('Tab');
    assert.equal(await page.evaluate(() => document.activeElement.textContent.trim()), 'Pilih folder');
    // Fokus keyboard terlihat: cincin ungu (box-shadow ring), bukan sekadar perubahan warna halus.
    await waitFor(() => /0px 0px 0px 4px/.test(getComputedStyle(document.activeElement).boxShadow), null,
      { timeout: 2000 });
    await page.keyboard.press('Enter');
    await eventually(async () => (await calls()).picks.length === 2);
  });

  it('pemeriksaan update pada mode pengembangan memberi penjelasan', { skip: Boolean(PACKAGED) }, async () => {
    await stubMain();
    await page.click('#check-update');
    const dialogs = await eventually(async () => (await calls()).dialogs.length && (await calls()).dialogs);
    assert.deepEqual(dialogs.map((d) => d.detail), ['Pembaruan hanya tersedia pada aplikasi yang terpasang.']);
    assert.equal(await page.isHidden('#update-banner'), true);
  });

  it('renderer terisolasi: tanpa Node, jendela baru, atau navigasi keluar', async () => {
    assert.deepEqual(await page.evaluate(() => [typeof require, typeof process, typeof window.expcore.runJob]),
      ['undefined', 'undefined', 'function']);
    assert.equal(await page.evaluate(() => window.open('https://example.com')), null);
    await page.evaluate(() => { window.location.href = 'https://example.com'; });
    await page.waitForTimeout(300);
    assert.match(page.url(), /index\.html$/);
    assert.equal(app.windows().length, 1);
    assert.deepEqual(page.errors, []);
  });

  it('animasi beranda: hero bergerak, setiap bagian muncul penuh saat digulir', async () => {
    await page.keyboard.press('Alt+0');
    await setSize(1180, 800);
    // Kartu hero melayang terus (Motion); animasi lain sudah selesai sejak awal.
    assert.ok(await page.evaluate(() => document.getAnimations().length) >= 3, 'animasi melayang tidak berjalan');
    const scroll = '#page-home .scroll';
    const max = await page.$eval(scroll, (el) => el.scrollHeight - el.clientHeight);
    for (let y = 0; y <= max; y += 250) {
      await page.$eval(scroll, (el, value) => { el.scrollTop = value; }, y);
      await page.waitForTimeout(80);
    }
    await page.$eval(scroll, (el) => { el.scrollTop = el.scrollHeight; });
    await waitFor(() => [...document.querySelectorAll('#page-home [data-reveal]')]
      .every((el) => Number(getComputedStyle(el).opacity) > 0.999), null, { timeout: 5000 });
    assert.equal(await page.locator('#page-home [data-reveal]').count(), 14); // termasuk lima kartu alat
    await page.$eval(scroll, (el) => { el.scrollTop = 0; });
  });

  it('gerak dikurangi: konten langsung tampil tanpa animasi', async () => {
    const profile = path.join(temp, 'profil-gerak');
    const calm = await electron.launch({
      args: [`--user-data-dir=${profile}`, ...(PACKAGED ? [] : [ROOT])], cwd: ROOT, executablePath: PACKAGED ?? undefined,
    });
    try {
      const calmPage = await calm.firstWindow();
      await calmPage.waitForSelector('body[data-ready="true"]');
      // Preferensi sistem dibaca saat halaman dimuat: emulasikan lalu muat ulang.
      await calmPage.emulateMedia({ reducedMotion: 'reduce' });
      await calmPage.reload();
      await calmPage.waitForSelector('body[data-ready="true"]');
      assert.equal(await calmPage.evaluate(() => matchMedia('(prefers-reduced-motion: reduce)').matches), true);
      assert.ok(await calmPage.$$eval('#page-home [data-reveal]', (els) => els.every((el) => getComputedStyle(el).opacity === '1')));
      // Tanpa gerakan: tidak ada animasi Motion (WAAPI) maupun animasi CSS; transisi warna tetap boleh.
      const moving = () => calmPage.evaluate(() => document.getAnimations()
        .filter((a) => a.constructor.name !== 'CSSTransition' || /transform|translate|scale|opacity/.test(a.transitionProperty))
        .map((a) => a.constructor.name + ':' + (a.animationName || a.transitionProperty || '')));
      assert.deepEqual(await moving(), []);
      await calmPage.keyboard.press('Alt+1');
      assert.deepEqual(await moving(), []);
      assert.equal(await calmPage.isVisible('#page-bupot .folder'), true);
    } finally {
      await calm.close();
    }
  });

  it('instance kedua tidak membuka jendela baru', async () => {
    const second = await launch().catch((error) => error);
    if (!(second instanceof Error)) {
      await new Promise((resolve) => setTimeout(resolve, 1500));
      assert.equal(second.windows().length, 0);
      await second.close().catch(() => {});
    }
    assert.equal(app.windows().length, 1);
    assert.equal(await app.evaluate(({ app: electronApp }) => electronApp.getPath('userData')), path.join(temp, 'profil'));
  });
});
