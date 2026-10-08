// Antarmuka ruang kerja. Status pekerjaan berasal dari proses main (sumber kebenaran);
// renderer hanya menampilkan dan meneruskan permintaan pengguna lewat window.expcore.
// Dibundel esbuild ke ../dist/app.js (npm run build:renderer).
import '@fontsource-variable/inter/wght.css';
import { animate, inView, stagger } from 'motion';
import {
  ArrowRight, ArrowUpRight, ClipboardText, Copy, DocumentText, Download, Edit2, Eye, FilePdf, FolderOpen, Grid,
  InfoCircle, Layers, Lock, Refresh, ShieldCheck, Sparkles, TickCircle,
} from 'reicon';

const ICONS = {
  ArrowRight, ArrowUpRight, ClipboardText, Copy, DocumentText, Download, Edit2, Eye, FilePdf, FolderOpen, Grid,
  InfoCircle, Layers, Lock, Refresh, ShieldCheck, Sparkles, TickCircle,
};
const api = window.expcore;
const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const field = (root, name) => $(`[data-field="${name}"]`, root);
const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
const EASE = [0.22, 1, 0.36, 1];
const SPRING = { type: 'spring', stiffness: 420, damping: 34 };

// Pratinjau dekoratif pada kartu alat di beranda (statis, aria-hidden).
const PREVIEWS = {
  bupot: `
    <div class="rounded-xl border border-line bg-white p-3 shadow-soft">
      <div class="flex items-center justify-between text-[11px] font-semibold"><span>Membaca BPPU</span><span class="text-brand-600">72%</span></div>
      <div class="mt-2 h-1.5 rounded-full bg-surface-2"><div class="h-full w-[72%] rounded-full bg-gradient-to-r from-brand-500 to-indigo-500"></div></div>
      <div class="mt-2.5 flex justify-between text-[10.5px] text-ink-muted"><span>sub/januari.pdf</span><span>18 / 25 PDF</span></div>
    </div>
    <div class="mt-2.5 flex gap-2">
      <span class="rounded-lg bg-white px-2 py-1 text-[10.5px] font-medium text-ink-soft shadow-soft">Nomor bukti</span>
      <span class="rounded-lg bg-white px-2 py-1 text-[10.5px] font-medium text-ink-soft shadow-soft">DPP</span>
      <span class="rounded-lg bg-white px-2 py-1 text-[10.5px] font-medium text-ink-soft shadow-soft">PPh</span>
    </div>`,
  bupot2024: `
    <div class="space-y-1.5">
      <div class="flex items-center justify-between rounded-lg bg-white px-3 py-1.5 text-[11px] shadow-soft"><span class="font-medium">H.1 Nomor bukti</span><span class="size-2 rounded-full bg-emerald-500"></span></div>
      <div class="flex items-center justify-between rounded-lg bg-white px-3 py-1.5 text-[11px] shadow-soft"><span class="font-medium">A.3 Nama</span><span class="size-2 rounded-full bg-emerald-500"></span></div>
      <div class="flex items-center justify-between rounded-lg bg-white px-3 py-1.5 text-[11px] shadow-soft"><span class="font-medium">B.4 DPP &amp; tarif</span><span class="size-2 rounded-full bg-emerald-500"></span></div>
      <div class="flex items-center justify-between rounded-lg bg-white/70 px-3 py-1.5 text-[11px] text-ink-muted"><span>H.4–H.5 Sifat</span><span class="size-2 rounded-full bg-brand-300"></span></div>
    </div>`,
  pm: `
    <div class="overflow-hidden rounded-xl border border-line bg-white text-[10.5px] shadow-soft">
      <div class="grid grid-cols-[1.4fr_1fr_1fr] bg-lavender px-3 py-1.5 font-semibold text-brand-700"><span>Barang</span><span>DPP</span><span>PPN 12%</span></div>
      <div class="grid grid-cols-[1.4fr_1fr_1fr] px-3 py-1.5"><span class="h-2 w-3/4 self-center rounded-full bg-line"></span><span class="h-2 w-2/3 self-center rounded-full bg-line"></span><span class="h-2 w-1/2 self-center rounded-full bg-brand-100"></span></div>
      <div class="grid grid-cols-[1.4fr_1fr_1fr] px-3 py-1.5"><span class="h-2 w-2/3 self-center rounded-full bg-line"></span><span class="h-2 w-1/2 self-center rounded-full bg-line"></span><span class="h-2 w-1/2 self-center rounded-full bg-brand-100"></span></div>
      <div class="grid grid-cols-[1.4fr_1fr_1fr] px-3 py-1.5"><span class="h-2 w-4/5 self-center rounded-full bg-line"></span><span class="h-2 w-2/3 self-center rounded-full bg-line"></span><span class="h-2 w-1/3 self-center rounded-full bg-brand-100"></span></div>
    </div>`,
  rename: `
    <div class="rounded-xl border border-line bg-white px-3 py-2 text-[11px] text-ink-muted shadow-soft">2000000015.pdf</div>
    <div class="my-1.5 flex justify-center text-brand-500"><span class="grid size-5 place-items-center rounded-full bg-brand-100 text-[11px] font-bold">↓</span></div>
    <div class="rounded-xl border border-brand-200 bg-white px-3 py-2 text-[11px] font-medium shadow-soft">Pemotong - Nomor - Masa - Sifat.pdf</div>
    <div class="mt-2 text-center text-[10.5px] font-medium text-brand-700">Pratinjau dulu, terapkan kemudian</div>`,
};

const pages = { home: { page: $('#page-home'), title: 'Beranda', heading: $('#home-title') } };
const views = {};
let modules = {};
let current = 'home';
let busy = null;
let updateAction = null;

const timestamp = () => new Date().toLocaleTimeString('en-GB', { hour12: false });

function hydrateIcons(root) {
  for (const placeholder of $$('[data-icon]', root)) {
    const make = ICONS[placeholder.dataset.icon];
    if (!make) throw new Error(`Ikon tidak dikenal: ${placeholder.dataset.icon}`);
    placeholder.replaceWith(make({
      size: 24, weight: placeholder.dataset.weight || 'Outline', className: placeholder.className,
      attrs: { 'aria-hidden': 'true', focusable: 'false' },
    }));
  }
}

function reveal(elements, delay = 0) {
  if (reduceMotion || !elements.length) return;
  // Sembunyikan di frame yang sama: Motion baru memasang keyframe awal pada frame berikutnya.
  for (const element of elements) element.style.opacity = '0';
  animate(elements, { opacity: [0, 1], y: [14, 0] },
    { duration: 0.55, ease: EASE, delay: stagger(0.06, { startDelay: delay }) });
}

function moveIndicator(smooth = true) {
  const active = $(`.nav-item[data-page="${current}"]`);
  if (!active) return;
  animate('#nav-indicator', { x: active.offsetLeft, width: active.offsetWidth },
    smooth && !reduceMotion ? SPRING : { duration: 0 });
}

function navigate(key) {
  if (!pages[key]) return;
  const leaving = pages[current].page;
  const changed = current !== key;
  current = key;
  for (const button of $$('.nav-item')) {
    if (button.dataset.page === key) button.setAttribute('aria-current', 'page');
    else button.removeAttribute('aria-current');
  }
  for (const [name, entry] of Object.entries(pages)) entry.page.hidden = name !== key;
  moveIndicator(changed);
  if (views[key]?.logPending) scrollLogToEnd(views[key]);
  if (changed && key !== 'home') reveal($$('[data-reveal]', pages[key].page));
  if (changed && key === 'home' && !reduceMotion) {
    animate(pages.home.page, { opacity: [0, 1], y: [8, 0] }, { duration: 0.35, ease: EASE });
  }
  // Fokus di halaman yang baru disembunyikan akan hilang; pindahkan ke judul halaman tujuan.
  if (leaving !== pages[key].page && leaving.contains(document.activeElement)) pages[key].heading.focus();
}

function setStatus(view, state, label) {
  const changed = view.status.dataset.state !== state;
  view.status.dataset.state = state;
  view.statusLabel.textContent = label;
  if (changed && !reduceMotion) animate(view.status, { scale: [0.88, 1] }, { type: 'spring', stiffness: 520, damping: 26 });
}

function setProgress(view, ratio) {
  const percent = Math.round(ratio * 100);
  view.progress.classList.remove('indeterminate');
  view.bar.style.width = `${percent}%`;
  view.progress.setAttribute('aria-valuenow', String(percent));
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

function setBusyNav(key, isBusy) {
  const nav = views[key].nav;
  nav.setAttribute('aria-busy', String(isBusy));
  $('.busy-dot', nav).hidden = !isBusy;
}

function folderChanged(key) {
  const view = views[key];
  const filled = Boolean(view.input.value.trim());
  view.folderLabel.textContent = filled ? 'Folder sumber · dapat diketik atau dipilih' : 'Belum ada folder dipilih';
  setStatus(view, filled ? 'ready' : 'idle', filled ? 'SIAP DIPROSES' : 'MENUNGGU FOLDER');
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
      setStatus(view, 'running', 'MEMPROSES');
      view.summary.textContent = 'Memindai folder dan subfolder… Anda tetap dapat membuka halaman lain.';
      view.log.textContent = '';
      view.progress.classList.add('indeterminate');
      setBusyNav(data.key, true);
      view.activity.scrollIntoView({ block: 'nearest', behavior: reduceMotion ? 'auto' : 'smooth' });
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
      setBusyNav(data.key, false);
      setProgress(view, 1);
      setStatus(view, data.hasOutput ? 'done' : 'empty', data.hasOutput ? 'SELESAI' : 'TIDAK ADA HASIL');
      view.summary.textContent = data.summary;
      view.open.disabled = !data.hasOutput;
      view.previewReady = data.key === 'rename' && !data.apply && data.hasOutput;
      appendLog(data.key, data.summary);
      break;
    case 'error':
      busy = null;
      setBusyNav(data.key, false);
      view.progress.classList.remove('indeterminate');
      setStatus(view, 'error', 'PERLU DIPERIKSA');
      view.summary.textContent = 'Proses belum selesai. Periksa log lalu coba kembali.';
      appendLog(data.key, `GAGAL: ${data.message}`);
      break;
    default:
      return;
  }
  refreshControls();
}

function showUpdate(text, actionLabel, action) {
  const banner = $('#update-banner');
  $('#update-text').textContent = text;
  const button = $('#update-action');
  button.textContent = actionLabel;
  button.disabled = !action;
  updateAction = action;
  if (banner.hidden) {
    banner.hidden = false;
    if (!reduceMotion) animate(banner, { opacity: [0, 1], y: [-10, 0], scale: [0.98, 1] }, SPRING);
  }
}

function onUpdateEvent(data) {
  const check = $('#check-update');
  check.disabled = data.state === 'checking';
  $('.label', check).textContent = data.state === 'checking' ? 'Memeriksa…' : 'Periksa update';
  check.setAttribute('aria-label', data.state === 'checking' ? 'Memeriksa update' : 'Periksa update');
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
  const rename = key === 'rename';
  const navButton = document.createElement('button');
  navButton.type = 'button';
  navButton.className = 'nav-item';
  navButton.dataset.page = key;
  navButton.setAttribute('aria-keyshortcuts', `Alt+${index + 1}`);
  navButton.append(info.title);
  const dot = document.createElement('span');
  dot.className = 'busy-dot size-1.5 rounded-full bg-current animate-pulse-dot';
  dot.hidden = true;
  dot.setAttribute('aria-hidden', 'true');
  navButton.append(dot);
  $('#main-nav').append(navButton);

  const card = $('#tool-card').content.firstElementChild.cloneNode(true);
  for (const name of ['tag', 'number', 'title', 'detail']) field(card, name).textContent = info[name];
  $('.preview', card).innerHTML = PREVIEWS[key];
  $('.open-tool', card).dataset.page = key;
  $('.open-tool', card).setAttribute('aria-label', `Buka alat ${info.title}`);
  hydrateIcons(card);
  $('#tool-cards').append(card);

  const page = $('#tool-page').content.firstElementChild.cloneNode(true);
  for (const name of ['tag', 'number', 'title', 'description', 'hint']) field(page, name).textContent = info[name];
  page.id = `page-${key}`;
  page.hidden = true;
  field(page, 'output-label').textContent = rename ? 'Log audit' : 'Hasil Excel';
  field(page, 'output-name').textContent = rename ? 'Log_Penamaan_Bupot_*.csv' : info.output;
  field(page, 'output-icon').innerHTML = `<span data-icon="${rename ? 'ClipboardText' : 'Grid'}" data-weight="Filled" class="size-5"></span>`;
  field(page, 'output').innerHTML = rename
    ? '<span data-icon="Eye" class="size-4 text-brand-500"></span><span>Pratinjau → periksa CSV → terapkan</span>'
    : '<span data-icon="Download" class="size-4 text-brand-500"></span><span>Hasil Excel disimpan di folder sumber</span>';
  const view = {
    page,
    nav: navButton,
    input: $('.folder', page),
    browse: $('.browse', page),
    folderLabel: field(page, 'folder-label'),
    status: field(page, 'status'),
    statusLabel: $('[data-field="status"] [data-label]', page),
    summary: field(page, 'summary'),
    progress: $('.progress', page),
    bar: $('.progress .bar', page),
    log: $('.log', page),
    activity: $('.activity', page),
    copy: $('.copy', page),
    copyLabel: $('.copy [data-label]', page),
    open: $('.open', page),
    run: $('.run', page),
    apply: $('.apply', page),
    previewReady: false,
  };
  view.run.innerHTML = `${rename ? 'Pratinjau nama' : 'Mulai ekstraksi'} <span data-icon="ArrowRight" class="size-4"></span>`;
  view.apply.hidden = !rename;
  hydrateIcons(page);
  // Di tepi log, roda mouse diteruskan ke halaman. Scroll chaining bawaan tidak bisa diandalkan pada
  // DPI pecahan: batas gulir compositor dan main thread berbeda sepersekian piksel, sehingga satu
  // putaran roda habis di log yang sebenarnya sudah di ujung.
  view.log.addEventListener('wheel', (event) => {
    if (event.ctrlKey || !event.deltaY) return;
    const { log } = view;
    const atEnd = log.scrollTop >= log.scrollHeight - log.clientHeight - 2;
    if ((event.deltaY > 0 && atEnd) || (event.deltaY < 0 && log.scrollTop <= 2)) {
      event.preventDefault();
      $('.scroll', page).scrollBy({
        top: event.deltaY * (event.deltaMode === 1 ? 16 : 1), behavior: reduceMotion ? 'auto' : 'smooth',
      });
    }
  }, { passive: false });
  view.input.addEventListener('input', () => folderChanged(key));
  view.browse.addEventListener('click', () => browse(key));
  view.run.addEventListener('click', () => api.runJob(key, view.input.value, false));
  view.apply.addEventListener('click', () => api.runJob(key, view.input.value, true));
  view.open.addEventListener('click', () => api.openOutput(key));
  view.copy.addEventListener('click', async () => {
    await api.copyText(view.log.textContent);
    view.copyLabel.textContent = 'Disalin';
    clearTimeout(view.copyTimer);
    view.copyTimer = setTimeout(() => { view.copyLabel.textContent = 'Salin log'; }, 1600);
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
    // Page Up/Down menggulir halaman aktif walau fokus berada di navigasi.
    const scroll = $('.scroll', pages[current].page);
    event.preventDefault();
    scroll.scrollBy({ top: (event.key === 'PageDown' ? 1 : -1) * scroll.clientHeight * 0.9 });
  }
}

// Hero berjalan segera (tanpa menunggu IPC) agar tidak ada kedipan; keadaan awalnya disembunyikan CSS.
function revealHero() {
  if (reduceMotion) return;
  reveal($$('.hero [data-reveal]'), 0.05);
  $$('[data-float]').forEach((card, index) => {
    animate(card, { y: [0, -9] }, {
      duration: 3.4 + index * 0.5, delay: index * 0.35, repeat: Infinity, repeatType: 'mirror', ease: 'easeInOut',
    });
  });
}

// Bagian di bawah lipatan muncul saat digulir ke dalam pandangan (setelah kartu alat dibuat).
function revealSectionsInView() {
  if (reduceMotion) return;
  const scroll = $('.scroll', pages.home.page);
  for (const section of $$('.scroll > section', pages.home.page)) {
    const items = $$('[data-reveal]', section);
    if (items.length) inView(section, () => reveal(items), { root: scroll, amount: 0.12 });
  }
}

async function init() {
  const info = await api.init();
  modules = info.modules;
  $('#byline').textContent = `Versi ${info.version} · by Iyan Sanjaya`;
  Object.entries(modules).forEach(([key, module], index) => buildTool(key, module, index));
  revealSectionsInView();
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
  // Lebar item navigasi berubah saat font Inter selesai dimuat atau jendela diubah ukurannya.
  new ResizeObserver(() => moveIndicator(false)).observe($('#main-nav'));
  document.fonts.ready.then(() => moveIndicator(false));
  document.body.dataset.ready = 'true';
}

hydrateIcons(document);
revealHero();
init();
