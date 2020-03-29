// Modules to control application life and create native browser window
const {app, BrowserWindow, ipcMain} = require('electron')
const path = require('path')
const {EyeOS, SpeechToText} = require('./wrapper')
 
require('electron-reload')(__dirname, {
  electron: path.join(__dirname, '../', 'node_modules', '.bin', 'electron'),
  hardResetMethod: 'exit'
});

const isDev = require("electron-is-dev")

let mainWindow

function createWindow () {
  // Create the browser window.
  mainWindow = new BrowserWindow({
    width:1000,
    height: 700,
    minWidth: 1000,
    minHeight: 700,
    webPreferences: {
      nodeIntegration: true,
      preload: path.join(__dirname, 'preload.js')
    }
  })

  // and load the index.html of the app.
  mainWindow.loadURL(isDev ? 'http://localhost:3000' : `file://${path.join(__dirname, "..eyeos-frontend/build/index.html")}`)

  // Open the DevTools.
  // mainWindow.webContents.openDevTools()
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.whenReady().then(createWindow)

// Quit when all windows are closed.
app.on('window-all-closed', function () {
  // On macOS it is common for applications and their menu bar
  // to stay active until the user quits explicitly with Cmd + Q
  if (process.platform !== 'darwin') app.quit()
})

app.on('activate', function () {
  // On macOS it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (BrowserWindow.getAllWindows().length === 0) createWindow()
})

var eyeOS = new EyeOS(false)

ipcMain.handle('eyeOS-on', (event, arg) => {
  return {on: eyeOS.isOn, typing: eyeOS.typing};
})

ipcMain.handle('start-eyeOS', (event, arg) => {
  console.log("starting eyeOS");
  if(!eyeOS.isOn)
    eyeOS.start(event)
})

ipcMain.handle('stop-eyeOS', (event, arg) => {
  console.log('stopping eyeOS')
  if(eyeOS.isOn)
    eyeOS.kill(event)
})

ipcMain.handle('change-mode-eyeOS', (event, arg) => {
  if(eyeOS.isOn) {
    console.log('restarting in mode ' + (arg) ? "typing" : "notyping");
    eyeOS.restart(arg.typing, event);
  } else {
    eyeOS.typing = arg.typing;
    eyeOS.start(event);
  }
})