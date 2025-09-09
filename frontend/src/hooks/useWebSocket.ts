// import { useRef } from "react";

export default function useWebSocket({ onMessage }: { onMessage: (msg: any) => void }) {
  // Placeholder: no real socket yet
  const send = (msg: any) => {
    // In real use, send via WebSocket
    // For demo, echo back after 1s as if from 'Bot'
    setTimeout(() => {
      onMessage({ ...msg, id: Date.now() + 1, sender: "Bot", content: `Echo: ${msg.content}` });
    }, 1000);
  };
  return { send };
} 