import dayjs from "dayjs";

export default function MessageBubble({ message }: { message: any }) {
  const isMe = message.sender === "You";
  return (
    <div className={`flex ${isMe ? "justify-end" : "justify-start"}`}>
      <div className={`max-w-xs px-4 py-2 rounded-2xl shadow text-sm ${isMe ? "bg-blue-500 text-white" : "bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white"}`}>
        <div className="font-bold mb-1">{message.sender}</div>
        <div>{message.content}</div>
        <div className="text-xs text-right mt-1 opacity-60">{dayjs(message.timestamp).format("HH:mm")}</div>
      </div>
    </div>
  );
} 