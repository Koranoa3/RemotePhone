import { app, BrowserWindow, ipcMain } from 'electron';
import path from 'path';
import { createHostApi } from './api/hostApi';

let mainWindow: BrowserWindow | null;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1024,
        height: 769,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            contextIsolation: true,
            enableRemoteModule: false,
            nodeIntegration: false,
        },
    });

    mainWindow.loadFile(path.join(__dirname, '../public/window.html'));

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

app.on('ready', createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (mainWindow === null) {
        createWindow();
    }
});

// API integration
ipcMain.handle('api:host', async (event, method, ...args) => {
    const hostApi = createHostApi();
    return await hostApi[method](...args);
});