# Arya desktop shell — development milestone

## Requirements

- Windows 11 x64
- Node.js 20+
- Python 3.11+
- A Gemini or OpenAI API key

## Setup

From the repository root:

\`\`\`powershell
python -m pip install -e .
cd apps/desktop
npm install
$env:GEMINI_API_KEY = "your-key"
# Or use OPENAI_API_KEY and set ARYA_DEFAULT_PROVIDER=openai
npm run dev
\`\`\`

Electron main generates a per-launch random local API token and keeps it out of renderer code. It reserves a loopback port, starts FastAPI, waits for authenticated health readiness, and exposes only the chat operation through the context-isolated preload. The local backend reads provider credentials from the process environment. Never commit API keys.

This is the first desktop-to-local-API-to-cloud-chat vertical slice. It is not yet a production installer and does not claim voice, computer-use, screen capture, agents, memory or background automation are complete. Packaged mode intentionally fails closed until the Python runtime is bundled and signed.