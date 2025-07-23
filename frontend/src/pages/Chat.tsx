import ChatWindow from "../components/ChatWindow";

export default function Chat() {
  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-extrabold mb-4 text-gray-900 dark:text-white">Chat / Realtime Messaging</h1>
      <ChatWindow />
    </div>
  );
} 