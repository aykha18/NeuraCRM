import MessageBubble from "./MessageBubble";

export default function MessageList({ messages }: { messages: any[] }) {
  return (
    <div className="flex flex-col gap-2">
      {messages.map((msg) => (
        <MessageBubble key={msg.id} message={msg} />
      ))}
    </div>
  );
} 