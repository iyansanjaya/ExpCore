'use strict';
// Antarmuka ruang kerja. Status pekerjaan berasal dari proses main (sumber kebenaran);
// renderer hanya menampilkan dan meneruskan permintaan pengguna lewat window.expcore.
const api = window.expcore;
const $ = (selector, root = document) => root.querySelector(selector);
const field = (root, name) => $(`[data-field="${name}"]`, root);

const pages = { home: { page: $('#page-home'), title: 'Beranda', heading: $('#home-title') } };
const views = {};
let modules = {};
let current = 'home';
let busy = null;
let updateAction = null;

const timestamp = () => new Date().toLocaleTimeString('en-GB', { hour12: false });

function navigate(key) {
  if (!pages[key]) return;
  const leaving = pages[current].page;
  current = key;
  $('#breadcrumb').textContent = `Ruang kerja  /  ${pages[key].title}`;
  for (const button of document.querySelectorAll('.nav-item')) {
    if (button.dataset.page === key) button.setAttribute('aria-current', 'page');
    else button.removeAttribute('aria-current');
  }
  for (const [name, entry] of Object.entries(pages)) entry.page.hidden = name !== key;
  if (views[key]?.logPending) scrollLogToEnd(views[key]);
  // Fokus di halaman yang baru disembunyikan akan hilang; pindahkan ke judul halaman tujuan.
  if (leaving !== pages[key].page && leaving.contains(document.activeElement)) pages[key].heading.focus();
}

function setProgress(view, ratio) {
  view.progress.classList.remove('indeterminate');
  view.bar.style.width = `${Math.round(ratio * 100)}%`;
  view.progress.setAttribute('aria-valuenow', String(Math.round(ratio * 100)));
}

function scrollLogToEnd(view) {
  // Halaman tersembunyi tidak dapat digulir; tunda sampai halamannya ditampilkan (navigate).
  view.logPending = view.page.hidden;
  // Bukan scrollHeight: pada DPI pecahan posisi itu melewati batas compositor sepersekian piksel,
  // sehingga putaran roda berikutnya habis di log alih-alih diteruskan ke halaman.
  view.log.scrollTop = view.log.scrollHeight - view.log.clientHeight;
}

function appendLog(key, message) {
  views[key].log.append(`${timestamp()}   ${message}\n`);
  scrollLogToEnd(views[key]);
}

function refreshControls() {
  for (const [key, view] of Object.entries(views)) {
    const ready = Boolean(view.input.value.trim()) && !busy;
    view.input.disabled = Boolean(busy);
    view.browse.disabled = Boolean(busy);
    view.run.disabled = !ready;
    if (key === 'rename') view.apply.disabled = !(ready && view.previewReady);
  }
}

function folderChanged(key) {
  const view = views[key];
  const filled = Boolean(view.input.value.trim());
  view.folderLabel.textContent = filled ? 'Folder sumber · dapat diketik atau dipilih' : 'Belum ada folder dipilih';
  view.status.textContent = filled ? 'SIAP DIPROSES' : 'MENUNGGU FOLDER';
  view.summary.textContent = filled ? 'Semua PDF dalam folder dan subfolder akan diperiksa.' : 'Pilih folder untuk memulai.';
  setProgress(view, 0);
  view.open.disabled = true; // Hasil lama tidak berlaku untuk folder lain.
  view.previewReady = false;
  refreshControls();
}

async function browse(key) {
  if (busy) return;
  const view = views[key];
  const folder = await api.pickFolder(view.input.value);
  if (folder && !busy) {
    view.input.value = folder;
    folderChanged(key);
  }
}

function onJobEvent(data) {
  const view = views[data.key];
  if (!view) return;
  switch (data.event) {
    case 'start':
      busy = data.key;
      view.open.disabled = true;
      view.previewReady = false;
      view.status.textContent = 'MEMPROSES';
      view.summary.textContent = 'Memindai folder dan subfolder… Anda tetap dapat membuka halaman lain.';
      view.log.textContent = '';
      view.progress.classList.add('indeterminate');
      view.nav.textContent = `${modules[data.key].title}  ···`;
      view.activity.scrollIntoView({ block: 'nearest' });
      break;
    case 'log':
      appendLog(data.key, data.message);
      return;
    case 'progress':
      setProgress(view, data.total ? data.done / data.total : 0);
      view.summary.textContent = `Memeriksa PDF ${data.done + 1} dari ${data.total}…`;
      return;
    case 'done':
      busy = null;
      view.nav.textContent = modules[data.key].title;
      setProgress(view, 1);
      view.status.textContent = data.hasOutput ? 'SELESAI' : 'TIDAK ADA HASIL';
      view.summary.textContent = data.summary;
      view.open.disabled = !data.hasOutput;
      view.previewReady = data.key === 'rename' && !data.apply && data.hasOutput;
      appendLog(data.key, data.summary);
      break;
    case 'error':
      busy = null;
      view.nav.textContent = modules[data.key].title;
      view.progress.classList.remove('indeterminate');
      view.status.textContent = 'PERLU DIPERIKSA';
      view.summary.textContent = 'Proses belum selesai. Periksa log lalu coba kembali.';
      appendLog(data.key, `GAGAL: ${data.message}`);
      break;
    default:
      return;
  }
  refreshControls();
}

function showUpdate(text, actionLabel, action) {
  $('#update-text').textContent = text;
  const button = $('#update-action');
  button.textContent = actionLabel;
  button.disabled = !action;
  updateAction = action;
  $('#update-banner').hidden = false;
}

function onUpdateEvent(data) {
  const check = $('#check-update');
  check.disabled = data.state === 'checking';
  check.textContent = data.state === 'checking' ? 'Memeriksa…' : 'Periksa update';
  switch (data.state) {
    case 'available':
      showUpdate(`ExpCore ${data.version} tersedia.\nVersi Anda: ${data.current}`, 'Unduh update', api.downloadUpdate);
      break;
    case 'downloading':
      showUpdate(`Mengunduh ExpCore ${data.version}… ${data.percent}%`, 'Mengunduh…', null);
      break;
    case 'downloaded':
      showUpdate(`ExpCore ${data.version} siap dipasang.\nAplikasi akan ditutup lalu diperbarui.`,
        'Pasang & mulai ulang', api.installUpdate);
      break;
    case 'failed':
      showUpdate(`Unduhan ExpCore ${data.version} gagal.\n${data.message}`, 'Coba lagi', api.downloadUpdate);
      break;
    case 'current':
      $('#update-banner').hidden = true;
      break;
    default:
  }
}

function buildTool(key, info, index) {
  const navButton = document.createElement('button');
  navButton.type = 'button';
  navButton.className = 'nav-item';
  navButton.dataset.page = key;
  navButton.textContent = info.title;
  navButton.setAttribute('aria-keyshortcuts', `Alt+${index + 1}`);
  $('#nav-tools').append(navButton);

  const card = $('#tool-card').content.firstElementChild.cloneNode(true);
  for (const name of ['tag', 'number', 'title', 'detail']) field(card, name).textContent = info[name];
  $('.open-tool', card).dataset.page = key;
  $('.open-tool', card).setAttribute('aria-label', `Buka alat ${info.title}`);
  $('#tool-cards').append(card);

  const page = $('#tool-page').content.firstElementChild.cloneNode(true);
  for (const name of ['tag', 'title', 'description', 'hint']) field(page, name).textContent = info[name];
  if (key === 'bupot') field(page, 'tag').classList.add('orange');
  page.id = `page-${key}`;
  page.hidden = true;
  const rename = key === 'rename';
  field(page, 'output').textContent = rename
    ? 'Pratinjau → periksa CSV → terapkan'
    : `Hasil Excel di folder sumber\n${info.output}`;
  const view = {
    page,
    nav: navButton,
    input: $('.folder', page),
    browse: $('.browse', page),
    folderLabel: field(page, 'folder-label'),
    status: field(page, 'status'),
    summary: field(page, 'summary'),
    progress: $('.progress', page),
    bar: $('.progress .bar', page),
    log: $('.log', page),
    activity: $('.activity', page),
    copy: $('.copy', page),
    open: $('.open', page),
    run: $('.run', page),
    apply: $('.apply', page),
    previewReady: false,
  };
  view.run.textContent = rename ? 'Pratinjau nama  →' : 'Mulai ekstraksi  →';
  view.apply.hidden = !rename;
  view.input.addEventListener('input', () => folderChanged(key));
  view.browse.addEventListener('click', () => browse(key));
  view.run.addEventListener('click', () => api.runJob(key, view.input.value, false));
  view.apply.addEventListener('click', () => api.runJob(key, view.input.value, true));
  view.open.addEventListener('click', () => api.openOutput(key));
  view.copy.addEventListener('click', async () => {
    await api.copyText(view.log.textContent);
    view.copy.textContent = 'Disalin ✓';
    clearTimeout(view.copyTimer);
    view.copyTimer = setTimeout(() => { view.copy.textContent = 'Salin log'; }, 1600);
  });
  $('.content').append(page);
  views[key] = view;
  pages[key] = { page, title: info.title, heading: $('h1', page) };
}

function onKeyDown(event) {
  const keys = Object.keys(pages);
  if (event.altKey && !event.ctrlKey && /^Digit[0-9]$/.test(event.code)) {
    const key = keys[Number(event.code.slice(5))];
    if (key) {
      event.preventDefault();
      navigate(key);
    }
  } else if (event.ctrlKey && !event.altKey && event.code === 'KeyO' && views[current]) {
    event.preventDefault();
    browse(current);
  } else if ((event.key === 'PageDown' || event.key === 'PageUp') && !event.target.closest('input, .log')) {
    // Page Up/Down menggulir halaman aktif walau fokus berada di sidebar.
    const scroll = $('.scroll', pages[current].page);
    event.preventDefault();
    scroll.scrollBy({ top: (event.key === 'PageDown' ? 1 : -1) * scroll.clientHeight * 0.9 });
  }
}

async function init() {
  const info = await api.init();
  modules = info.modules;
  $('#byline').textContent = `v${info.version}   /   by Iyan Sanjaya`;
  Object.entries(modules).forEach(([key, module], index) => buildTool(key, module, index));
  document.addEventListener('click', (event) => {
    const target = event.target.closest('[data-page]');
    if (target) navigate(target.dataset.page);
  });
  document.addEventListener('keydown', onKeyDown);
  $('#check-update').addEventListener('click', () => api.checkUpdate());
  $('#update-action').addEventListener('click', () => updateAction?.());
  $('#update-later').addEventListener('click', () => { $('#update-banner').hidden = true; });
  api.onJobEvent(onJobEvent);
  api.onUpdateEvent(onUpdateEvent);
  navigate('home');
  refreshControls();
  document.body.dataset.ready = 'true';
}

init();
