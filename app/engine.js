'use strict';
// Menjalankan engine Python (satu proses per pekerjaan) dan membaca protokol JSON per baris.
// Kontrak protokol: lihat docstring expcore_engine.py.
const { spawn } = require('node:child_process');
const readline = require('node:readline');

const STDERR_TAIL = 8000;

function lastLines(text, count = 8) {
  return text.trim().split(/\r?\n/).slice(-count).join('\n');
}

/**
 * onEvent menerima {event: 'log', message} atau {event: 'progress', done, total}.
 * Resolve {path, summary} saat engine selesai; reject Error berpesan siap tampil.
 */
function runEngine(command, args, onEvent) {
  return new Promise((resolve, reject) => {
    let child;
    try {
      child = spawn(command, args, { windowsHide: true, stdio: ['ignore', 'pipe', 'pipe'] });
    } catch (error) {
      reject(new Error(`Mesin pemroses tidak dapat dijalankan: ${error.message}`));
      return;
    }
    let result = null;
    let stderr = '';
    // stderr wajib dibaca terus; pipe penuh akan membuat engine berhenti menunggu.
    child.stderr.setEncoding('utf8');
    child.stderr.on('data', (chunk) => { stderr = (stderr + chunk).slice(-STDERR_TAIL); });
    readline.createInterface({ input: child.stdout, crlfDelay: Infinity }).on('line', (line) => {
      let data;
      try {
        data = JSON.parse(line);
      } catch {
        return;
      }
      if (data?.event === 'log' && typeof data.message === 'string') {
        onEvent({ event: 'log', message: data.message });
      } else if (data?.event === 'progress' && Number.isInteger(data.done) && Number.isInteger(data.total)) {
        onEvent({ event: 'progress', done: data.done, total: data.total });
      } else if (data?.event === 'done' && typeof data.summary === 'string'
                 && (data.path === null || typeof data.path === 'string')) {
        result = { path: data.path, summary: data.summary };
      } else if (data?.event === 'error' && typeof data.message === 'string') {
        result = new Error(data.message);
      }
    });
    child.on('error', (error) => reject(new Error(`Mesin pemroses tidak dapat dijalankan: ${error.message}`)));
    child.on('close', (code) => {
      if (result instanceof Error) reject(result);
      else if (result && code === 0) resolve(result);
      else {
        const detail = stderr.trim() ? `\n${lastLines(stderr)}` : '';
        reject(new Error(`Mesin pemroses berhenti tanpa hasil (kode ${code}).${detail}`));
      }
    });
  });
}

module.exports = { runEngine };
