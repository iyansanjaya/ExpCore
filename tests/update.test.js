'use strict';
// Alur pembaruan pada aplikasi hasil paket terhadap server update lokal (tanpa GitHub).
//   EXPCORE_APP=dist/win-unpacked/ExpCore.exe npm test
// Salinan win-unpacked dibuat di dist/e2e-update dengan app-update.yml yang menunjuk ke server lokal.
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
const http = require('node:http');
const os = require('node:os');
const path = require('node:path');
const { after, before, describe, it } = require('node:test');
const { _electron: electron } = require('playwright-core');

const ROOT = path.join(__dirname, '..');
const SOURCE = process.env.EXPCORE_APP ? path.dirname(path.resolve(ROOT, process.env.EXPCORE_APP)) : null;
const COPY = path.join(ROOT, 'dist', 'e2e-update');
const CACHE = path.join(process.env.LOCALAPPDATA ?? os.tmpdir(), 'expcore-updater-e2e');
const PAYLOAD = crypto.randomBytes(3 * 1024 * 1024);
const SHA512 = crypto.createHash('sha512').update(PAYLOAD).digest('base64');

const CORRUPT = Buffer.from(PAYLOAD).fill(0, 0, 1024);
const server = { mode: 'available', corrupt: false, requests: [] };
let httpServer;
let app;
let page;
let temp;

function latestYml(version, sha512 = SHA512) {
  const file = `ExpCore-Setup-${version}.exe`;
  return `version: ${version}\nfiles:\n  - url: ${file}\n    sha512: ${sha512}\n    size: ${PAYLOAD.length}\n`
    + `path: ${file}\nsha512: ${sha512}\nreleaseDate: '2026-10-01T00:00:00.000Z'\n`;
}

function handle(request, response) {
  server.requests.push(request.url);
  const url = request.url.split('?')[0];
  if (server.mode === 'down') {
    request.socket.destroy();
  } else if (url === '/latest.yml' && server.mode !== 'missing') {
    const version = server.mode === 'current' ? '3.0.0' : '3.0.1';
    response.end(latestYml(version));
  } else if (url === '/ExpCore-Setup-3.0.1.exe') {
    // Dikirim bertahap supaya status "Mengunduh… n%" dapat diamati.
    const body = server.corrupt ? CORRUPT : PAYLOAD;
    response.writeHead(200, { 'Content-Length': PAYLOAD.length, 'Content-Type': 'application/octet-stream' });
    let offset = 0;
    const timer = setInterval(() => {
      response.write(body.subarray(offset, offset + 256 * 1024));
      offset += 256 * 1024;
      if (offset >= PAYLOAD.length) {
        clearInterval(timer);
        response.end();
      }
    }, 40);
  } else {
    response.statusCode = 404;
    response.end();
  }
}

async function stubMain(answer = 0) {
  await app.evaluate(({ dialog }, response) => {
    globalThis.calls = { dialogs: [] };
    dialog.showMessageBox = async (_win, opts) => {
      globalThis.calls.dialogs.push(opts);
      return { response };
    };
  }, answer);
}

async function eventually(check, timeout = 20000) {
  const deadline = Date.now() + timeout;
  for (;;) {
    const value = await check();
    if (value) return value;
    if (Date.now() > deadline) throw new Error(`Kondisi tidak tercapai: ${check}`);
    await new Promise((resolve) => setTimeout(resolve, 50));
  }
}

// Polling berbasis interval, bukan requestAnimationFrame: rAF berhenti total bila jendela tes
// diminimalkan oleh aktivitas desktop, sehingga penantian berbasis rAF tidak pernah selesai.
const waitFor = (fn, arg, options = {}) => page.waitForFunction(fn, arg, { polling: 100, ...options });

const dialogs = () => app.evaluate(() => globalThis.calls.dialogs);
const bannerText = () => page.textContent('#update-text');
const waitBanner = (prefix) => waitFor((p) => !document.querySelector('#update-banner').hidden
  && document.querySelector('#update-text').textContent.startsWith(p), prefix, { timeout: 30000 });

async function manualCheck() {
  await stubMain();
  await page.click('#check-update');
  return eventually(async () => (await dialogs()).length && (await dialogs())[0]);
}

describe('Pembaruan aplikasi terpasang', { skip: !SOURCE && 'EXPCORE_APP belum diatur' }, () => {
  before(async () => {
    httpServer = http.createServer(handle);
    await new Promise((resolve) => httpServer.listen(0, '127.0.0.1', resolve));
    fs.rmSync(COPY, { recursive: true, force: true });
    fs.cpSync(SOURCE, COPY, { recursive: true });
    fs.writeFileSync(path.join(COPY, 'resources', 'app-update.yml'), 'provider: generic\n'
      + `url: http://127.0.0.1:${httpServer.address().port}/\nupdaterCacheDirName: expcore-updater-e2e\n`);
    fs.rmSync(CACHE, { recursive: true, force: true });
    temp = fs.mkdtempSync(path.join(os.tmpdir(), 'expcore-update-'));
    app = await electron.launch({ executablePath: path.join(COPY, 'ExpCore.exe'), args: [`--user-data-dir=${temp}`] });
    page = await app.firstWindow();
    await page.waitForSelector('body[data-ready="true"]');
  });

  after(async () => {
    await app?.close();
    httpServer?.close();
    fs.rmSync(temp, { recursive: true, force: true, maxRetries: 10, retryDelay: 200 });
    fs.rmSync(CACHE, { recursive: true, force: true });
    fs.rmSync(COPY, { recursive: true, force: true, maxRetries: 10, retryDelay: 200 });
  });

  it('pemeriksaan otomatis saat mulai menampilkan banner tanpa interaksi', async () => {
    await waitBanner('ExpCore 3.0.1 tersedia.');
    assert.equal(await bannerText(), 'ExpCore 3.0.1 tersedia.\nVersi Anda: 3.0.0');
    assert.equal(await page.textContent('#update-action'), 'Unduh update');
    assert.equal(await page.isEnabled('#check-update'), true);
    assert.ok(server.requests.some((url) => url.startsWith('/latest.yml')));
    assert.ok(!server.requests.some((url) => url.includes('.exe')), 'tidak mengunduh tanpa persetujuan');
  });

  it('pemeriksaan manual: versi terbaru, belum ada latest.yml, dan offline', async () => {
    server.mode = 'current';
    let dialog = await manualCheck();
    assert.equal(dialog.detail, 'Anda memakai ExpCore 3.0.0.\nTidak ada versi stabil yang lebih baru.');
    assert.equal(await page.isHidden('#update-banner'), true);

    // Rilis tanpa latest.yml (mis. v2.x lama di GitHub) bukan gangguan: cukup belum ada pembaruan.
    server.mode = 'missing';
    dialog = await manualCheck();
    assert.deepEqual([dialog.type, dialog.title, dialog.detail],
      ['info', 'Pembaruan ExpCore', 'Anda memakai ExpCore 3.0.0.\nBelum ada pembaruan yang siap dipasang.']);
    assert.equal(await page.isHidden('#update-banner'), true);

    server.mode = 'down';
    dialog = await manualCheck();
    assert.match(dialog.detail, /^Tidak dapat terhubung\. Periksa koneksi internet Anda\.\nAplikasi tetap dapat digunakan\.$/);
    assert.equal((await page.textContent('#check-update')).trim(), 'Periksa update');
    assert.equal(await page.isEnabled('#check-update'), true);
  });

  it('unduhan rusak ditolak, lalu Coba lagi berhasil dengan progres', async () => {
    server.mode = 'available';
    server.corrupt = true; // Isi berubah di jalan: checksum sha512 dari latest.yml wajib menolaknya.
    await stubMain();
    await page.click('#check-update');
    await waitBanner('ExpCore 3.0.1 tersedia.');
    await page.click('#update-action');
    await waitBanner('Unduhan ExpCore 3.0.1 gagal.');
    assert.equal(await page.textContent('#update-action'), 'Coba lagi');

    server.corrupt = false;
    await page.click('#update-action');
    await waitBanner('Mengunduh ExpCore 3.0.1…');
    assert.equal(await page.isDisabled('#update-action'), true);
    await waitBanner('ExpCore 3.0.1 siap dipasang.');
    assert.equal(await page.textContent('#update-action'), 'Pasang & mulai ulang');
    const downloaded = fs.readdirSync(path.join(CACHE, 'pending')).filter((name) => name.endsWith('.exe'));
    assert.equal(downloaded.length, 1);
    assert.ok(fs.readFileSync(path.join(CACHE, 'pending', downloaded[0])).equals(PAYLOAD));
  });

  it('Nanti menyembunyikan banner; pemeriksaan berikutnya tidak mengunduh ulang', async () => {
    await page.click('#update-later');
    assert.equal(await page.isHidden('#update-banner'), true);
    const before = server.requests.length;
    await page.click('#check-update');
    await waitBanner('ExpCore 3.0.1 siap dipasang.');
    assert.equal(server.requests.length, before);
  });

  it('pemasangan ditahan selama pekerjaan berjalan, lalu memanggil quitAndInstall', async () => {
    await app.evaluate(() => {
      globalThis.installs = [];
      process.mainModule.require('electron-updater').autoUpdater.quitAndInstall = (...args) => globalThis.installs.push(args);
    });
    const folder = path.join(temp, 'besar');
    const fixture = path.join(ROOT, 'tests', 'fixtures.py');
    require('node:child_process').execFileSync(path.join(ROOT, '.venv', 'Scripts', 'python.exe'), [fixture, folder]);
    for (let index = 0; index < 60; index += 1) fs.copyFileSync(path.join(folder, 'faktur.pdf'), path.join(folder, `${index}.pdf`));
    await stubMain();
    await page.keyboard.press('Alt+3');
    await page.fill('#page-pm .folder', folder);
    await page.click('#page-pm .run');
    await waitFor(() => document.querySelector('#page-pm [data-field="status"]').textContent === 'MEMPROSES');
    await page.click('#update-action');
    const [dialog] = await eventually(async () => (await dialogs()).length && dialogs());
    assert.equal(dialog.title, 'Proses masih berjalan');
    assert.deepEqual(await app.evaluate(() => globalThis.installs), []);
    await waitFor(() => document.querySelector('#page-pm [data-field="status"]').textContent === 'SELESAI', null, { timeout: 120000 });
    await page.click('#update-action');
    assert.deepEqual(await eventually(async () => (await app.evaluate(() => globalThis.installs)).length
      && app.evaluate(() => globalThis.installs)), [[true, true]]);
  });
});
