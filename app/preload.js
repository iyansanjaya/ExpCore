'use strict';
// Satu-satunya jembatan renderer -> main. Renderer tidak memiliki akses Node.
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('expcore', {
  init: () => ipcRenderer.invoke('init'),
  pickFolder: (current) => ipcRenderer.invoke('pick-folder', current),
  runJob: (key, folder, apply = false, nameSource = null) => ipcRenderer.invoke('run-job', key, folder, apply, nameSource),
  openOutput: (key) => ipcRenderer.invoke('open-output', key),
  copyText: (text) => ipcRenderer.invoke('copy-text', text),
  checkUpdate: () => ipcRenderer.invoke('check-update'),
  downloadUpdate: () => ipcRenderer.invoke('download-update'),
  installUpdate: () => ipcRenderer.invoke('install-update'),
  onJobEvent: (callback) => ipcRenderer.on('job-event', (_event, data) => callback(data)),
  onUpdateEvent: (callback) => ipcRenderer.on('update-event', (_event, data) => callback(data)),
});
