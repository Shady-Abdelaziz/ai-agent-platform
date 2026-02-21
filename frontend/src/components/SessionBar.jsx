import React from "react";

export default function SessionBar({
  agent,
  sessions,
  selectedSession,
  onSelectSession,
  onCreateSession,
  onDeleteSession,
}) {
  if (!agent) {
    return (
      <div className="session-bar">
        <span className="session-bar-placeholder">
          Select an agent to start chatting
        </span>
      </div>
    );
  }

  const handleSessionChange = (e) => {
    const sessionId = e.target.value;
    if (!sessionId) {
      onSelectSession(null);
      return;
    }
    const session = sessions.find(
      (s) => String(s.id) === String(sessionId)
    );
    onSelectSession(session || null);
  };

  const formatSessionLabel = (session) => {
    if (session.title) return session.title;
    const date = new Date(session.created_at);
    return `Session ${date.toLocaleDateString()} ${date.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    })}`;
  };

  return (
    <div className="session-bar">
      <div className="session-bar-left">
        <span className="session-agent-name">{agent.name}</span>
      </div>

      <div className="session-bar-center">
        <label className="session-label">Chat Sessions</label>
        <select
          className="session-select"
          value={selectedSession ? selectedSession.id : ""}
          onChange={handleSessionChange}
        >
          <option value="">-- Select a session --</option>
          {sessions.map((session) => (
            <option key={session.id} value={session.id}>
              {formatSessionLabel(session)}
            </option>
          ))}
        </select>
        {selectedSession && (
          <button
            className="btn-delete-session"
            onClick={() => {
              if (window.confirm("Delete this session and all its messages?")) {
                onDeleteSession(selectedSession.id);
              }
            }}
            title="Delete session"
          >
            &times;
          </button>
        )}
      </div>

      <div className="session-bar-right">
        <button className="btn-new-chat" onClick={onCreateSession}>
          + New Chat
        </button>
      </div>
    </div>
  );
}
