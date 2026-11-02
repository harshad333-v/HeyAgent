export type ChatMessage = { role: "user" | "assistant"; content: string };

type AryaBridge = {
  chat: (messages: ChatMessage[]) => Promise<{ provider: string; model: string; content: string }>;
};

declare global {
  interface Window { arya: AryaBridge }
}

export const sendChat = (messages: ChatMessage[]) => window.arya.chat(messages);