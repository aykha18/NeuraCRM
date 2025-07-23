import { useState } from "react";
import MessageList from "./MessageList";
import useWebSocket from "../hooks/useWebSocket";
import { Paperclip, Smile, Users } from "lucide-react";

// Slack-style sample messages
const sampleMessages = [
  { id: 1, sender: "Alex", content: "Hey team, the client just replied!", timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString() },
  { id: 2, sender: "Sam", content: "Awesome! What did they say?", timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2 + 60000).toISOString() },
  { id: 3, sender: "Alex", content: "They're ready to move forward with the proposal.", timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2 + 120000).toISOString() },
  { id: 4, sender: "Chris", content: "Great news! 🎉 I'll update the Kanban board.", timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2 + 180000).toISOString() },
  { id: 5, sender: "You", content: "Let me know if you need help with the docs.", timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2 + 240000).toISOString() },
  { id: 6, sender: "Sam", content: "Thanks! I'll ping you if anything comes up.", timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2 + 300000).toISOString() },
  { id: 7, sender: "Alex", content: "Should we schedule a call for tomorrow?", timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2 + 360000).toISOString() },
  { id: 8, sender: "You", content: "Yes, 2pm works for me.", timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2 + 420000).toISOString() },
  { id: 9, sender: "Chris", content: "Same here. Adding to the calendar now.", timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2 + 480000).toISOString() },
];

const channelUsers = [
  { name: "You", color: "bg-gradient-to-r from-pink-500 to-purple-500" },
  { name: "Alex", color: "bg-gradient-to-r from-blue-500 to-indigo-500" },
  { name: "Sam", color: "bg-gradient-to-r from-green-500 to-teal-500" },
  { name: "Chris", color: "bg-gradient-to-r from-yellow-500 to-orange-500" },
];
function getInitials(name: string) {
  return name.split(" ").map(n => n[0]).join("").toUpperCase();
}

export default function ChatWindow() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<any[]>(sampleMessages);
  const ws = useWebSocket({ onMessage: (msg: any) => setMessages((prev) => [...prev, msg]) });

  function sendMessage() {
    if (!input.trim()) return;
    const msg = { id: Date.now(), sender: "You", content: input, timestamp: new Date().toISOString() };
    setMessages((prev) => [...prev, msg]);
    ws.send && ws.send(msg);
    setInput("");
  }

  return (
    <div className="flex flex-col h-[600px] bg-white dark:bg-gray-900 rounded-2xl shadow border border-gray-200 dark:border-gray-800">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-800 rounded-t-2xl">
        <div className="flex items-center gap-3">
          <span className="font-bold text-lg text-gray-900 dark:text-white"># general</span>
          <span className="ml-2 text-xs text-gray-500 dark:text-gray-300 flex items-center gap-1"><Users className="w-4 h-4" /> {channelUsers.length} members</span>
        </div>
        <div className="flex -space-x-2">
          {channelUsers.map(u => (
            <span key={u.name} className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white border-2 border-white dark:border-gray-900 shadow ${u.color}`}>{getInitials(u.name)}</span>
          ))}
        </div>
      </div>
      {/* Message List */}
      <div className="flex-1 overflow-y-auto p-4">
        <MessageList messages={messages} />
      </div>
      {/* Input Area */}
      <div className="p-3 border-t border-gray-200 dark:border-gray-800 flex gap-2 items-center bg-gray-50 dark:bg-gray-800 rounded-b-2xl">
        <button className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 transition"><Paperclip className="w-5 h-5 text-gray-400" /></button>
        <input
          className="flex-1 rounded-full px-4 py-2 border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-900 dark:text-white"
          placeholder="Message #general"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => { if (e.key === "Enter") sendMessage(); }}
        />
        <button className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 transition"><Smile className="w-5 h-5 text-gray-400" /></button>
        <button
          className="px-4 py-2 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 text-white font-semibold shadow hover:from-blue-600 hover:to-purple-600 transition"
          onClick={sendMessage}
        >
          Send
        </button>
      </div>
    </div>
  );
} 