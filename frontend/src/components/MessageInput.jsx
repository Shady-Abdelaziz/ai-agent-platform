import React, { useState } from "react";
import useAudioRecorder from "../hooks/useAudioRecorder.js";

export default function MessageInput({ onSendMessage, onSendVoice, disabled }) {
  const [text, setText] = useState("");
  const { isRecording, startRecording, stopRecording } = useAudioRecorder();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!text.trim() || disabled) return;
    onSendMessage(text.trim());
    setText("");
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleVoiceToggle = async () => {
    if (disabled) return;

    if (isRecording) {
      const blob = await stopRecording();
      if (blob && blob.size > 0) {
        onSendVoice(blob);
      }
    } else {
      try {
        await startRecording();
      } catch (err) {
        alert("Could not access microphone. Please check permissions.");
      }
    }
  };

  return (
    <form className="message-input-bar" onSubmit={handleSubmit}>
      <input
        type="text"
        className="message-input"
        placeholder="Type your message or use voice..."
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
      />
      <button
        type="submit"
        className="btn-send"
        disabled={!text.trim() || disabled}
      >
        Send
      </button>
      <button
        type="button"
        className={`btn-mic ${isRecording ? "recording" : ""}`}
        onClick={handleVoiceToggle}
        disabled={disabled}
        title={isRecording ? "Stop recording" : "Start recording"}
      >
        {isRecording ? (
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <rect x="6" y="6" width="12" height="12" rx="2" />
          </svg>
        ) : (
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
            <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
          </svg>
        )}
      </button>
    </form>
  );
}
