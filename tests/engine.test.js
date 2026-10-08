'use strict';
// Kontrak app/engine.js terhadap proses engine palsu (Node) — tanpa Python atau Electron.
const assert = require('node:assert/strict');
const test = require('node:test');
const { runEngine } = require('../app/engine');

function fake(script) {
  const events = [];
  const promise = runEngine(process.execPath, ['-e', script], (event) => events.push(event));
  return { events, promise };
}

test('meneruskan log/progres berurutan lalu resolve hasil', async () => {
  const { events, promise } = fake(String.raw`
    const out = (o) => process.stdout.write(JSON.stringify(o) + '\r\n');
    out({ event: 'log', message: 'Memproses 2 file \u2026 \u00dcn\u00efcode' });
    out({ event: 'progress', done: 0, total: 2 });
    out({ event: 'progress', done: 1, total: 2 });
    out({ event: 'done', path: 'C:\\hasil\\!Hasil.xlsx', summary: 'Selesai \u2014 2 baris.' });`);
  assert.deepEqual(await promise, { path: 'C:\\hasil\\!Hasil.xlsx', summary: 'Selesai — 2 baris.' });
  assert.deepEqual(events, [
    { event: 'log', message: 'Memproses 2 file … Ünïcode' },
    { event: 'progress', done: 0, total: 2 },
    { event: 'progress', done: 1, total: 2 },
  ]);
});

test('hasil tanpa file (path null) tetap resolve', async () => {
  const { promise } = fake(`console.log(JSON.stringify({ event: 'done', path: null, summary: 'Tidak ada data.' }))`);
  assert.deepEqual(await promise, { path: null, summary: 'Tidak ada data.' });
});

test('event error menjadi pesan penolakan', async () => {
  const { promise } = fake(`
    console.log(JSON.stringify({ event: 'error', message: 'Folder tidak ditemukan.' }));
    process.exit(1);`);
  await assert.rejects(promise, { message: 'Folder tidak ditemukan.' });
});

test('crash tanpa event akhir melaporkan kode dan ekor stderr', async () => {
  const { promise } = fake(`
    console.error('baris lama\\n'.repeat(20) + 'ModuleNotFoundError: pdfplumber');
    process.exit(3);`);
  await assert.rejects(promise, (error) => {
    assert.match(error.message, /^Mesin pemroses berhenti tanpa hasil \(kode 3\)\./);
    assert.match(error.message, /ModuleNotFoundError: pdfplumber$/);
    assert.ok(error.message.split('\n').length <= 9, 'hanya beberapa baris terakhir');
    return true;
  });
});

test('event done dengan kode keluar bukan nol dianggap gagal', async () => {
  const { promise } = fake(`
    console.log(JSON.stringify({ event: 'done', path: null, summary: 'x' }));
    process.exit(5);`);
  await assert.rejects(promise, /kode 5/);
});

test('baris bukan JSON dan bentuk event tidak sah diabaikan', async () => {
  const { events, promise } = fake(`
    console.log('bukan json');
    console.log(JSON.stringify({ event: 'progress', done: '1', total: 2 }));
    console.log(JSON.stringify({ event: 'log', message: 42 }));
    console.log(JSON.stringify({ event: 'lainnya' }));
    console.log(JSON.stringify({ event: 'done', path: 7, summary: 'x' }));
    console.log(JSON.stringify(null));
    console.log(JSON.stringify({ event: 'log', message: 'sah' }));
    console.log(JSON.stringify({ event: 'done', path: null, summary: 'ok' }));`);
  assert.deepEqual(await promise, { path: null, summary: 'ok' });
  assert.deepEqual(events, [{ event: 'log', message: 'sah' }]);
});

test('stderr besar tidak membuat engine macet', async () => {
  const { promise } = fake(`
    const chunk = 'x'.repeat(1024) + '\\n';
    for (let i = 0; i < 4096; i++) process.stderr.write(chunk);
    console.log(JSON.stringify({ event: 'done', path: null, summary: 'ok' }));`);
  assert.deepEqual(await promise, { path: null, summary: 'ok' });
});

test('program engine yang tidak ada ditolak dengan pesan jelas', async () => {
  const promise = runEngine('C:\\tidak-ada\\expcore_engine.exe', [], () => {});
  await assert.rejects(promise, /^Error: Mesin pemroses tidak dapat dijalankan: .*ENOENT/);
});
