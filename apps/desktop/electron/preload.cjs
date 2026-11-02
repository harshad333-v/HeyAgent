const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("arya", Object.freeze({
  chat: (messages, provider) => ipcRenderer.invoke("arya:chat", messages, provider),
  openGeminiWeb: (prompt) => ipcRenderer.invoke("arya:open-gemini-web", prompt)
}));
