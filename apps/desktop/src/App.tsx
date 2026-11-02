import { FormEvent, KeyboardEvent, useState } from "react";
import { ChatMessage, sendChat } from "./api";

export default function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function submit(event: FormEvent<HTMLFormElement> | KeyboardEvent<HTMLTextAreaElement>) {
    event.preventDefault();
    const prompt = draft.trim();
    if (!prompt || busy) return;
    const next: ChatMessage[] = [...messages, { role: "user", content: prompt }];
    setMessages(next);
    setDraft("");
    setBusy(true);
    setError("");
    try {
      const result = await sendChat(next);
      setMessages([...next, { role: "assistant", content: result.content }]);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Arya could not reach the local AI service.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="shell">
      <aside className="sidebar">
        <div className="brand"><span className="orb">A</span><div><b>Arya</b><small>Personal AI workspace</small></div></div>
        <button className="new-chat" onClick={() => { setMessages([]); setError(""); }}>＋ New chat</button>
        <div className="side-label">WORKSPACE</div>
        <div className="nav-item active">◈　Assistant</div>
        <div className="nav-item muted">▤　Tasks <small>Coming next</small></div>
        <div className="nav-item muted">◇　Agents <small>Coming next</small></div>
        <div className="nav-item muted">⚙　Settings <small>Coming next</small></div>
        <div className="sidebar-foot">Windows-first · Hybrid AI</div>
      </aside>
      <section className="content">
        <header><div><div className="eyebrow">YOUR ASSISTANT</div><h1>How can I help?</h1></div><div className="status"><i /> Local service</div></header>
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
          {busy && <div className="thinking"><span /> Arya is thinking…</div>}
        </div>
        {error && <div className="error">{error} Check that the backend is running and a provider key is configured.</div>}
        <form className="composer" onSubmit={submit}>
          <textarea value={draft} onChange={event => setDraft(event.target.value)}
            onKeyDown={event => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); void submit(event); } }}
            placeholder="Message Arya…" rows={2} />
          <div className="composer-foot"><span>Enter to send · Shift + Enter for a new line</span>
            <button type="submit" disabled={busy || !draft.trim()}>{busy ? "Working…" : "Send ↑"}</button>
          </div>
        </form>
        <footer>AI can make mistakes. Verify important information and review actions before taking them.</footer>
      </section>
    </main>
  );
}