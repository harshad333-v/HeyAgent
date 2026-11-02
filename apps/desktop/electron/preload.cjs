const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("arya", Object.freeze({
  chat: (messages) => ipcRenderer.invoke("arya:chat", messages)
}));