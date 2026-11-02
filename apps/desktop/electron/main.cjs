const { app, BrowserWindow, ipcMain } = require("electron");
const { spawn } = require("node:child_process");
const { randomBytes } = require("node:crypto");
const path = require("node:path");

let mainWindow;
let backend;
let localToken;
const isDev = !app.isPackaged;
const apiBase = "http://127.0.0.1:8765";

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1180, height: 800, minWidth: 760, minHeight: 600,
    backgroundColor: "#0d1017", title: "Arya",
    webPreferences: {
      preload: path.join(__dirname, "preload.cjs"),
      contextIsolation: true, nodeIntegration: false, sandbox: true, webSecurity: true
    }
  });
  if (isDev) mainWindow.loadURL("http://127.0.0.1:5173");
  else mainWindow.loadFile(path.join(__dirname, "../dist/index.html"));
}

function startBackend() {
  localToken = randomBytes(32).toString("base64url");
  const repoRoot = path.resolve(__dirname, "../../..");
  backend = spawn(process.env.ARYA_PYTHON || "python", [
    "-m", "uvicorn", "backend.app.api.main:app", "--host", "127.0.0.1", "--port", "8765"
  ], {
    cwd: repoRoot, windowsHide: true, stdio: "ignore",
    env: {
      ...process.env,
      ARYA_LOCAL_API_TOKEN: localToken,
      ARYA_ALLOWED_ORIGINS: "app://arya",
      ARYA_DATABASE_PATH: path.join(app.getPath("userData"), "data", "arya.sqlite3")
    }
  });
  backend.on("exit", () => { backend = undefined; });
}

async function callApi(route, body) {
  if (!localToken) throw new Error("Arya local service is not available.");
  const response = await fetch(apiBase + route, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Origin": "app://arya",
      "Authorization": "Bearer " + localToken
    },
    body: JSON.stringify(body)
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.detail || payload.error || "Local API request failed.");
  return payload;
}

ipcMain.handle("arya:chat", async (_event, messages) => {
  if (!Array.isArray(messages) || messages.length < 1 || messages.length > 40) {
    throw new Error("Invalid chat history.");
  }
  const safe = messages.map(message => {
    if (!message || !["user", "assistant"].includes(message.role) ||
        typeof message.content !== "string" || message.content.length > 12000) {
      throw new Error("Invalid chat message.");
    }
    return { role: message.role, content: message.content };
  });
  return callApi("/v1/chat/completions", { messages: safe });
});

app.whenReady().then(() => { startBackend(); createWindow(); });
app.on("window-all-closed", () => { if (process.platform !== "darwin") app.quit(); });
app.on("before-quit", () => {
  if (backend && !backend.killed) backend.kill();
  localToken = undefined;
});