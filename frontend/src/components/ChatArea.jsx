import React, { useEffect, useRef } from "react";
import MessageBubble from "./MessageBubble.jsx";

export default function ChatArea({ messages, loading }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, loading]);

  if (!messages && !loading) {
    return (
      <div className="chat-area chat-area-empty">
        <div className="empty-state">
          <div className="empty-state-icon">&#128172;</div>
          <h3>No conversation yet</h3>
          <p>Select an agent and a session to start chatting, or create a new chat.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-area">
      <div className="messages-container">
        {messages && messages.length === 0 && !loading && (
          <div className="empty-state">
            <p>No messages yet. Send a message to start the conversation.</p>
          </div>
        )}
        {messages &&
          messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} />
          ))}
        {loading && (
          <div className="loading-indicator">
            <div className="typing-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
