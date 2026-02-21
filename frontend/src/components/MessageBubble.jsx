import React from "react";

export default function MessageBubble({ message }) {
  const isUser = message.role === "user";
  const timestamp = new Date(message.created_at);
  const timeStr = timestamp.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div className={`message-bubble-wrapper ${isUser ? "user" : "assistant"}`}>
      <div className={`message-bubble ${isUser ? "user" : "assistant"}`}>
        <div className="message-content">{message.content}</div>
        {message.audio_url && (
          <div className="message-audio">
            <audio controls src={message.audio_url} preload="none">
              Your browser does not support the audio element.
            </audio>
          </div>
        )}
      </div>
      <span className="message-timestamp">{timeStr}</span>
    </div>
  );
}
