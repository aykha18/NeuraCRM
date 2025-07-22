import React, { useState } from 'react';

const ChatWindow = () => {
  const [messages, setMessages] = useState<string[]>([]);
  const [input, setInput] = useState('');

  const sendMessage = () => {
    if (!input.trim()) return;
    setMessages([...messages, input]);
    setInput('');
  };

  return (
    <div className="p-4 w-full max-w-md mx-auto">
      <div className="border rounded-lg p-2 h-64 overflow-y-auto mb-2 bg-white shadow">
        {messages.map((msg, i) => (
          <div key={i} className="p-1 border-b">{msg}</div>
        ))}
      </div>
      <div className="flex">
        <input
          className="flex-grow border rounded-l p-2"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message..."
        />
        <button onClick={sendMessage} className="bg-blue-500 text-white px-4 rounded-r">Send</button>
      </div>
    </div>
  );
};

export default ChatWindow;
