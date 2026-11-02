export type ChatMessage = { role: "user" | "assistant"; content: string };
export type ChatProvider = "gemini" | "openai" | "gemini_web";

type AryaBridge = {
  chat: (messages: ChatMessage[], provider: "gemini" | "openai") =>
    Promise<{ provider: string; model: string; content: string }>;
  openGeminiWeb: (prompt: string) => Promise<void>;
};

declare global {
  interface Window { arya: AryaBridge }
}

export const sendChat = (messages: ChatMessage[], provider: "gemini" | "openai") =>
  window.arya.chat(messages, provider);

export const openGeminiWeb = (prompt: string) => window.arya.openGeminiWeb(prompt);
