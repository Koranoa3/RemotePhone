import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('api', {
    getSettings: () => ipcRenderer.invoke('get-settings'),
    setSettings: (settings) => ipcRenderer.invoke('set-settings', settings),
    getRegisteredDevices: () => ipcRenderer.invoke('get-registered-devices'),
    deleteRegisteredDevice: (uuid) => ipcRenderer.invoke('delete-registered-device', uuid),
    checkForUpdates: () => ipcRenderer.invoke('check-for-updates'),
    updateNow: () => ipcRenderer.invoke('update-now'),
});