const { app, BrowserWindow, ipcMain } = require("electron");
const { spawn } = require("node:child_process");
const { randomBytes } = require("node:crypto");
const net = require("node:net");
const path = require("node:path");

let mainWindow;
let backend;
let localToken;
let apiBase;
const isDev = !app.isPackaged;

function reserveLoopbackPort() {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.once("error", reject);
    server.listen(0, "127.0.0.1", () => {
      const address = server.address();
      const port = typeof address === "object" && address ? address.port : 0;
      server.close(error => error ? reject(error) : resolve(port));
    });
  });
}

async function waitForBackend() {
  const deadline = Date.now() + 20000;
  while (Date.now() < deadline) {
    if (!backend || backend.exitCode !== null) {
      throw new Error("Arya backend process exited during startup.");
    }
    try {
      const response = await fetch(apiBase + "/health", {
        headers: { "Origin": "app://arya", "Authorization": "Bearer " + localToken },
        signal: AbortSignal.timeout(750)
      });
      if (response.ok) return;
    } catch { /* service is still starting */ }
    await new Promise(resolve => setTimeout(resolve, 250));
  }
  throw new Error("Arya backend did not become ready within 20 seconds.");
}

async function startBackend() {
  if (app.isPackaged) {
    throw new Error("Packaged backend runtime is not configured yet. Use the development setup.");
  }
  const port = await reserveLoopbackPort();
  apiBase = "http://127.0.0.1:" + port;
  localToken = randomBytes(32).toString("base64url");
  const repoRoot = path.resolve(__dirname, "../../..");
  backend = spawn(process.env.ARYA_PYTHON || "python", [
    "-m", "uvicorn", "backend.app.api.main:app", "--host", "127.0.0.1", "--port", String(port)
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
  await waitForBackend();
}

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

async function callApi(route, body) {
  if (!localToken || !apiBase) throw new Error("Arya local service is not available.");
  const response = await fetch(apiBase + route, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Origin": "app://arya",
      "Authorization": "Bearer " + localToken
    },
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(60000)
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.detail || payload.error || "Local API request failed.");
  return payload;
}

ipcMain.handle("arya:chat", async (event, messages) => {
  if (event.senderFrame?.url !== "http://127.0.0.1:5173/") throw new Error("Untrusted renderer frame.");
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

app.whenReady().then(async () => {
  try {
    await startBackend();
    createWindow();
  } catch (error) {
    console.error("Arya startup failed:", error);
    app.quit();
  }
});
app.on("window-all-closed", () => { if (process.platform !== "darwin") app.quit(); });
app.on("before-quit", () => {
  if (backend && !backend.killed) backend.kill();
  localToken = undefined;
  apiBase = undefined;
});