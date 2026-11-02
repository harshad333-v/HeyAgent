import { FormEvent, KeyboardEvent, useState } from "react";
import { ChatMessage, ChatProvider, openGeminiWeb, sendChat } from "./api";

export default function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [provider, setProvider] = useState<ChatProvider>("gemini");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [handoffNotice, setHandoffNotice] = useState("");

  async function submit(event: FormEvent<HTMLFormElement> | KeyboardEvent<HTMLTextAreaElement>) {
    event.preventDefault();
    const prompt = draft.trim();
    if (!prompt || busy) return;
    setBusy(true);
    setError("");
    setHandoffNotice("");
    try {
      if (provider === "gemini_web") {
        await openGeminiWeb(prompt);
        setDraft("");
        setHandoffNotice("Gemini Web opened and your prompt was copied to the clipboard. Paste it into Gemini. Arya does not automatically receive the website response.");
        return;
      }
      const next: ChatMessage[] = [...messages, { role: "user", content: prompt }];
      setMessages(next);
      setDraft("");
      const result = await sendChat(next, provider);
      setMessages([...next, { role: "assistant", content: result.content }]);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Arya could not complete the request.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="shell">
      <aside className="sidebar">
        <div className="brand"><span className="orb">A</span><div><b>Arya</b><small>Personal AI workspace</small></div></div>
        <button className="new-chat" onClick={() => { setMessages([]); setError(""); setHandoffNotice(""); }}>＋ New chat</button>
        <div className="side-label">WORKSPACE</div>
        <div className="nav-item active">◈　Assistant</div>
        <div className="nav-item muted">▤　Tasks <small>Coming next</small></div>
        <div className="nav-item muted">◇　Agents <small>Coming next</small></div>
        <div className="nav-item muted">⚙　Settings <small>Coming next</small></div>
        <div className="sidebar-foot">Windows-first · Hybrid AI</div>
      </aside>
      <section className="content">
        <header>
          <div><div className="eyebrow">YOUR ASSISTANT</div><h1>How can I help?</h1></div>
          <div className="provider-control">
            <label htmlFor="provider">Provider</label>
            <select id="provider" value={provider} onChange={event => {
              setProvider(event.target.value as ChatProvider);
              setError("");
              setHandoffNotice("");
            }}>
              <option value="gemini">Gemini API</option>
              <option value="openai">OpenAI API</option>
              <option value="gemini_web">Gemini Web (manual)</option>
            </select>
          </div>
        </header>
        <div className="conversation">
          {messages.length === 0 ? (
            <div className="welcome">
              <div className="welcome-orb">A</div><h2>Good to see you.</h2>
              <p>Ask Arya to explain, reason, plan or help you work through a problem.</p>
              <div className="suggestions">
                <button onClick={() => setDraft("Explain how a REST API works with an example.")}>Explain a concept <span>↗</span></button>
                <button onClick={() => setDraft("Help me plan my next coding project.")}>Plan a project <span>↗</span></button>
                <button onClick={() => setDraft("Review this code for bugs and edge cases: ")}>Review code <span>↗</span></button>
              </div>
            </div>
          ) : messages.map((message, index) => (
            <article className={message.role} key={index}>
              <div className="message-avatar">{message.role === "assistant" ? "A" : "Y"}</div>
              <div className="message-body"><b>{message.role === "assistant" ? "Arya" : "You"}</b><p>{message.content}</p></div>
            </article>
          ))}
          {busy && <div className="thinking"><span /> Arya is working…</div>}
        </div>
        {handoffNotice && <div className="handoff-notice">{handoffNotice}</div>}
        {error && <div className="error">{error} Check the selected provider configuration.</div>}
        <form className="composer" onSubmit={submit}>
          <textarea value={draft} onChange={event => setDraft(event.target.value)}
            onKeyDown={event => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); void submit(event); } }}
            placeholder={provider === "gemini_web" ? "Prompt to copy into Gemini Web…" : "Message Arya…"} rows={2} />
          <div className="composer-foot">
            <span>{provider === "gemini_web" ? "Opens Gemini Web and copies this prompt" : "Enter to send · Shift + Enter for a new line"}</span>
            <button type="submit" disabled={busy || !draft.trim()}>{busy ? "Working…" : provider === "gemini_web" ? "Open Gemini Web ↗" : "Send ↑"}</button>
          </div>
        </form>
        <footer>AI can make mistakes. Verify important information and review actions before taking them.</footer>
      </section>
    </main>
  );
}
