'use strict';
const fs = require('node:fs');
const path = require('node:path');
const { app, BrowserWindow, clipboard, dialog, ipcMain, screen, session, shell } = require('electron');
const { autoUpdater } = require('electron-updater');
const { runEngine } = require('./engine');

// Harus sama dengan build.appId di package.json: shortcut installer memakai AUMID ini.
const APP_ID = 'iyansanjaya.expcore.1.0';
// Urutan = urutan menu, kartu beranda, dan shortcut Alt+1..; alat dikelompokkan per `group` di menu Alat.
const MODULES = {
  bupot: {
    title: 'Bukti Potong 2026', tag: 'CORETAX', number: '01',
    group: 'Ekstraksi ke Excel', icon: 'ReceiptText', brief: 'BPPU Coretax',
    description: 'Dari bukti potong ke rekap Excel yang siap digunakan.',
    detail: 'Formulir BPPU · Nomor bukti, identitas, DPP & PPh',
    hint: 'Gunakan PDF Bukti Potong berformat BPPU dari Coretax.',
    output: '!Hasil_Rekap_Bupot.xlsx',
  },
  bupot2024: {
    title: 'Bukti Potong 2024', tag: 'PRA-CORETAX', number: '02',
    group: 'Ekstraksi ke Excel', icon: 'Receipt', brief: 'Formulir BPBS pra-Coretax',
    description: 'Rapikan bukti potong lama dalam satu rekap terstruktur.',
    detail: 'Formulir BPBS · Identitas, objek pajak & pemotong',
    hint: 'Gunakan PDF formulir BPBS (pra-Coretax), dengan bagian H.1–H.5.',
    output: '!Hasil_Rekap_Bupot_2024.xlsx',
  },
  pm: {
    title: 'Pajak Masukan', tag: 'FAKTUR PAJAK', number: '03',
    group: 'Ekstraksi ke Excel', icon: 'Invoice', brief: 'Faktur pajak',
    description: 'Satukan rincian faktur pajak, tanpa menyalin satu per satu.',
    detail: 'Faktur PDF · Pembeli, barang, DPP, PPN & netto',
    hint: 'Gunakan faktur dengan teks yang dapat diseleksi. Perhitungan PPN pada modul ini menggunakan tarif tetap 12%.',
    output: 'Hasil_Pajak_Masukan.xlsx',
  },
  rekening: {
    title: 'Rekening Koran', tag: 'BCA', number: '04',
    group: 'Ekstraksi ke Excel', icon: 'Bank', brief: 'e-Statement BCA Giro & Tahapan',
    description: 'Mutasi rekening per bulan, debit dan kredit terpisah.',
    detail: 'e-Statement Giro & Tahapan · Debit, kredit, saldo & ringkasan',
    hint: 'Gunakan e-Statement BCA (Rekening Giro atau Tahapan) yang teksnya dapat diseleksi. Setiap PDF menjadi '
      + 'satu sheet; total, jumlah transaksi, dan saldo dicocokkan dengan ringkasan di akhir PDF.',
    output: '!Hasil_Rekap_Rekening_Koran.xlsx',
  },
  rename: {
    title: 'Penamaan Bupot', tag: 'PENGELOLAAN PDF', number: '05',
    group: 'Kelola PDF', icon: 'Edit2', brief: 'Nama file BPPU, pratinjau & log CSV',
    description: 'Nama file yang konsisten. Dokumen lebih mudah ditemukan.',
    detail: 'BPPU Coretax · Nama pemotong atau dipotong, log audit CSV',
    hint: 'Periksa pratinjau sebelum menerapkan. PDF yang nama pada sumber terpilihnya kosong dilewati, tanpa memakai nama lain.',
    output: 'Log penamaan .csv',
    // Kunci = nilai --nama engine. Yang pertama adalah pilihan bawaan.
    nameSources: {
      pemotong: { title: 'Identitas Pemotong', detail: 'C.3 · Nama pemotong dan/atau pemungut PPh' },
      penerima: { title: 'Wajib Pajak yang Dipotong', detail: 'A.2 · Nama identitas wajib pajak yang dipotong' },
    },
  },
};

let win = null;
let job = null; // Kunci alat yang sedang diproses: satu pekerjaan sekaligus, navigasi tetap bebas.
let preview = null; // Penerapan nama hanya untuk folder dan sumber nama yang pratinjaunya selesai.
const outputs = {}; // Hanya hasil yang dibuat engine yang boleh dibuka renderer.
const update = { checking: false, version: null, downloading: false, downloaded: false };

function send(channel, data) {
  if (win && !win.isDestroyed()) win.webContents.send(channel, data);
}

function message(type, title, detail) {
  return dialog.showMessageBox(win, { type, title, message: title, detail, buttons: ['OK'], noLink: true });
}

async function confirm(title, detail, action) {
  const { response } = await dialog.showMessageBox(win, {
    type: 'question', title, message: title, detail, buttons: [action, 'Batal'],
    defaultId: 1, cancelId: 1, noLink: true,
  });
  return response === 0;
}

// Jalur dapat ditempel dari "Copy as path" Explorer, lengkap dengan tanda kutip.
function cleanFolder(value) {
  const folder = String(value ?? '').trim().replace(/^"(.*)"$/s, '$1').trim();
  return path.isAbsolute(folder) ? folder : '';
}

function isDirectory(folder) {
  try {
    return fs.statSync(folder).isDirectory();
  } catch {
    return false;
  }
}

function engineCommand(args) {
  if (app.isPackaged) return [path.join(process.resourcesPath, 'engine', 'expcore_engine.exe'), args];
  const root = path.join(__dirname, '..');
  return [path.join(root, '.venv', 'Scripts', 'python.exe'), [path.join(root, 'expcore_engine.py'), ...args]];
}

async function startJob(key, rawFolder, rawApply, rawSource) {
  if (job || !Object.hasOwn(MODULES, key)) return false;
  const apply = rawApply === true && key === 'rename';
  const source = key === 'rename' ? rawSource : null;
  if (key === 'rename' && !Object.hasOwn(MODULES.rename.nameSources, source)) return false;
  const folder = cleanFolder(rawFolder);
  if (!folder || !isDirectory(folder)) {
    await message('warning', 'Folder tidak ditemukan', 'Pilih folder yang tersedia di perangkat Anda.');
    return false;
  }
  if (apply) {
    if (preview?.folder !== folder || preview.source !== source) return false;
    const { title } = MODULES.rename.nameSources[source];
    const ok = await confirm('Terapkan penamaan?', `Nama PDF di folder sumber akan diubah memakai nama dari ${title}.\n\n`
      + 'Pastikan Anda telah memeriksa CSV pratinjau. Folder akan dipindai ulang; file baru atau yang '
      + 'berubah juga diperiksa. File dengan data tidak lengkap dilewati dan setiap perubahan dicatat '
      + 'dalam log CSV.', 'Terapkan nama');
    if (!ok) return false;
  } else if (key !== 'rename' && fs.existsSync(path.join(folder, MODULES[key].output))) {
    const ok = await confirm('Ganti rekap sebelumnya?', 'File hasil dengan nama yang sama sudah tersedia.\n'
      + 'Lanjutkan untuk menggantinya dengan rekap baru?', 'Ganti rekap');
    if (!ok) return false;
  }
  if (job) return false; // Dialog bersifat asinkron; tetap satu pekerjaan.
  job = key;
  delete outputs[key];
  if (key === 'rename') preview = null;
  send('job-event', { key, event: 'start' });
  const [command, args] = engineCommand([key, folder, ...(apply ? ['--apply'] : []), ...(source ? ['--nama', source] : [])]);
  runEngine(command, args, (event) => send('job-event', { key, ...event })).then(
    (result) => {
      if (result.path) {
        outputs[key] = key === 'rename' ? folder : result.path;
        if (key === 'rename' && !apply) preview = { folder, source };
      }
      job = null;
      send('job-event', { key, event: 'done', apply, hasOutput: Boolean(result.path), summary: result.summary });
    },
    (error) => {
      job = null;
      send('job-event', { key, event: 'error', message: error.message });
    },
  );
  return true;
}

async function openOutput(key) {
  const target = Object.hasOwn(outputs, key) ? outputs[key] : null;
  if (!target) return;
  const error = await shell.openPath(target);
  if (error) await message('error', 'Hasil tidak dapat dibuka', `${target}\n\n${error}`);
}

const NETWORK_ERROR = /net::ERR_|ENOTFOUND|ECONN|ETIMEDOUT|EAI_AGAIN/;
const errorText = (error) => `${error?.code ?? ''} ${error?.message ?? ''}`;

function describeUpdateError(error) {
  return NETWORK_ERROR.test(errorText(error))
    ? 'Tidak dapat terhubung. Periksa koneksi internet Anda.'
    : 'Layanan pembaruan sedang tidak tersedia.';
}

// Belum ada rilis, atau rilis terbaru belum memuat latest.yml (mis. rilis lama v2.x yang lebih tua):
// bukan gangguan, hanya belum ada pembaruan. Pesan aslinya bisa membungkus galat jaringan.
function noUpdateReady(error) {
  const text = errorText(error);
  return /ERR_UPDATER_(CHANNEL_FILE_NOT_FOUND|LATEST_VERSION_NOT_FOUND|NO_PUBLISHED_VERSIONS)/.test(text)
    && !NETWORK_ERROR.test(text);
}

async function checkForUpdate(manual) {
  if (!app.isPackaged) {
    if (manual) await message('info', 'Pembaruan ExpCore', 'Pembaruan hanya tersedia pada aplikasi yang terpasang.');
    return;
  }
  if (update.checking || update.downloading) return;
  if (update.downloaded) {
    send('update-event', { state: 'downloaded', version: update.version });
    return;
  }
  update.checking = true;
  send('update-event', { state: 'checking' });
  let result;
  try {
    result = await autoUpdater.checkForUpdates();
  } catch (error) {
    const none = noUpdateReady(error);
    send('update-event', { state: none ? 'current' : 'idle' });
    // Pemeriksaan otomatis yang gagal (mis. offline) tidak boleh mengganggu pengguna.
    if (manual && none) {
      await message('info', 'Pembaruan ExpCore',
        `Anda memakai ExpCore ${app.getVersion()}.\nBelum ada pembaruan yang siap dipasang.`);
    } else if (manual) {
      await message('warning', 'Pembaruan belum dapat diperiksa',
        `${describeUpdateError(error)}\nAplikasi tetap dapat digunakan.`);
    }
    return;
  } finally {
    update.checking = false;
  }
  if (result?.isUpdateAvailable) {
    update.version = result.updateInfo.version;
    send('update-event', { state: 'available', version: update.version, current: app.getVersion() });
  } else {
    send('update-event', { state: 'current' });
    if (manual) {
      await message('info', 'Pembaruan ExpCore',
        `Anda memakai ExpCore ${app.getVersion()}.\nTidak ada versi stabil yang lebih baru.`);
    }
  }
}

async function downloadUpdate() {
  if (!update.version || update.downloading || update.downloaded) return;
  update.downloading = true;
  send('update-event', { state: 'downloading', version: update.version, percent: 0 });
  try {
    await autoUpdater.downloadUpdate();
    update.downloaded = true;
    send('update-event', { state: 'downloaded', version: update.version });
  } catch (error) {
    send('update-event', { state: 'failed', version: update.version, message: describeUpdateError(error) });
  } finally {
    update.downloading = false;
  }
}

async function installUpdate() {
  if (!update.downloaded) return;
  if (job) {
    await message('info', 'Proses masih berjalan', 'Tunggu pemrosesan selesai sebelum memasang pembaruan.');
    return;
  }
  // Senyap, lalu buka kembali aplikasi. Installer per-mesin tetap meminta izin UAC.
  setImmediate(() => autoUpdater.quitAndInstall(true, true));
}

function setupUpdater() {
  autoUpdater.autoDownload = false; // Pengguna yang memutuskan kapan mengunduh dan memasang.
  autoUpdater.autoInstallOnAppQuit = false;
  autoUpdater.logger = null;
  autoUpdater.on('error', () => {}); // Ditangani lewat promise; tanpa listener EventEmitter melempar.
  autoUpdater.on('download-progress', (progress) => {
    send('update-event', { state: 'downloading', version: update.version, percent: Math.floor(progress.percent) });
  });
  if (app.isPackaged) setTimeout(() => checkForUpdate(false), 1800);
}

function handle(channel, listener) {
  ipcMain.handle(channel, (event, ...args) => {
    if (!win || event.sender !== win.webContents) throw new Error('Pengirim IPC tidak dikenal.');
    return listener(...args);
  });
}

function registerIpc() {
  handle('init', () => ({ version: app.getVersion(), modules: MODULES }));
  handle('pick-folder', async (current) => {
    const folder = cleanFolder(current);
    const result = await dialog.showOpenDialog(win, {
      title: 'Pilih folder PDF — subfolder ikut diproses',
      properties: ['openDirectory'],
      defaultPath: isDirectory(folder) ? folder : undefined,
    });
    return result.canceled ? null : result.filePaths[0];
  });
  handle('run-job', startJob);
  handle('open-output', openOutput);
  handle('copy-text', (text) => clipboard.writeText(String(text)));
  handle('check-update', () => checkForUpdate(true));
  handle('download-update', downloadUpdate);
  handle('install-update', installUpdate);
}

function createWindow() {
  const { width, height } = screen.getPrimaryDisplay().workAreaSize;
  win = new BrowserWindow({
    width: Math.max(960, Math.min(1180, width - 80)),
    height: Math.max(620, Math.min(800, height - 100)),
    minWidth: 960,
    minHeight: 620,
    title: `ExpCore ${app.getVersion()} — Toolkit PDF Coretax`,
    backgroundColor: '#f4f4f5',
    show: false,
    icon: app.isPackaged ? undefined : path.join(__dirname, '..', 'icon.ico'),
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      sandbox: true,
      contextIsolation: true,
      nodeIntegration: false,
      spellcheck: false,
      devTools: !app.isPackaged,
    },
  });
  win.removeMenu();
  win.on('page-title-updated', (event) => event.preventDefault());
  win.once('ready-to-show', () => win.show());
  win.on('close', (event) => {
    if (!job) return;
    event.preventDefault();
    message('info', 'Proses masih berjalan', 'Tunggu pemrosesan selesai sebelum menutup aplikasi '
      + 'agar hasil dan log tersimpan lengkap.');
  });
  win.on('closed', () => { win = null; });
  win.loadFile(path.join(__dirname, 'renderer', 'index.html'));
}

if (!app.requestSingleInstanceLock()) {
  app.quit();
} else {
  app.setAppUserModelId(APP_ID);
  app.on('second-instance', () => {
    if (!win) return;
    if (win.isMinimized()) win.restore();
    win.focus();
  });
  // Konten hanya dari paket aplikasi: tanpa navigasi, jendela baru, webview, atau izin perangkat.
  app.on('web-contents-created', (_event, contents) => {
    contents.setWindowOpenHandler(() => ({ action: 'deny' }));
    contents.on('will-navigate', (event) => event.preventDefault());
    contents.on('will-attach-webview', (event) => event.preventDefault());
  });
  app.on('window-all-closed', () => app.quit());
  app.whenReady().then(() => {
    session.defaultSession.setPermissionRequestHandler((_contents, _permission, callback) => callback(false));
    session.defaultSession.setPermissionCheckHandler(() => false);
    registerIpc();
    createWindow();
    setupUpdater();
  });
}
