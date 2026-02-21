import React, { useState, useEffect, useCallback } from "react";
import AgentSidebar from "./components/AgentSidebar.jsx";
import SessionBar from "./components/SessionBar.jsx";
import ChatArea from "./components/ChatArea.jsx";
import MessageInput from "./components/MessageInput.jsx";
import {
  fetchAgents,
  createAgent,
  updateAgent,
  deleteAgent,
  fetchSessions,
  createSession,
  deleteSession,
  fetchMessages,
  sendMessage,
  sendVoice,
} from "./api.js";

export default function App() {
  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);
  const [messages, setMessages] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // ── Load agents on mount ──────────────────────────────

  const loadAgents = useCallback(async () => {
    try {
      const data = await fetchAgents();
      setAgents(data);
    } catch (err) {
      console.error("Failed to load agents:", err);
      setError("Failed to load agents");
    }
  }, []);

  useEffect(() => {
    loadAgents();
  }, [loadAgents]);

  // ── Load sessions when agent changes ──────────────────

  const loadSessions = useCallback(async (agentId) => {
    try {
      const data = await fetchSessions(agentId);
      setSessions(data);
      return data;
    } catch (err) {
      console.error("Failed to load sessions:", err);
      setSessions([]);
      return [];
    }
  }, []);

  useEffect(() => {
    if (selectedAgent) {
      loadSessions(selectedAgent.id);
      setSelectedSession(null);
      setMessages(null);
    } else {
      setSessions([]);
      setSelectedSession(null);
      setMessages(null);
    }
  }, [selectedAgent, loadSessions]);

  // ── Load messages when session changes ────────────────

  const loadMessages = useCallback(async (agentId, sessionId) => {
    try {
      const data = await fetchMessages(agentId, sessionId);
      setMessages(data);
    } catch (err) {
      console.error("Failed to load messages:", err);
      setMessages([]);
    }
  }, []);

  useEffect(() => {
    if (selectedAgent && selectedSession) {
      loadMessages(selectedAgent.id, selectedSession.id);
    } else {
      setMessages(null);
    }
  }, [selectedAgent, selectedSession, loadMessages]);

  // ── Agent handlers ────────────────────────────────────

  const handleSelectAgent = (agent) => {
    setSelectedAgent(agent);
    setError(null);
  };

  const handleCreateAgent = async (data) => {
    try {
      const newAgent = await createAgent(data);
      await loadAgents();
      setSelectedAgent(newAgent);
    } catch (err) {
      console.error("Failed to create agent:", err);
      setError("Failed to create agent");
    }
  };

  const handleUpdateAgent = async (id, data) => {
    try {
      const updated = await updateAgent(id, data);
      await loadAgents();
      if (selectedAgent && selectedAgent.id === id) {
        setSelectedAgent(updated);
      }
    } catch (err) {
      console.error("Failed to update agent:", err);
      setError("Failed to update agent");
    }
  };

  const handleDeleteAgent = async (id) => {
    try {
      await deleteAgent(id);
      if (selectedAgent && selectedAgent.id === id) {
        setSelectedAgent(null);
      }
      await loadAgents();
    } catch (err) {
      console.error("Failed to delete agent:", err);
      setError("Failed to delete agent");
    }
  };

  // ── Session handlers ──────────────────────────────────

  const handleSelectSession = (session) => {
    setSelectedSession(session);
  };

  const handleCreateSession = async () => {
    if (!selectedAgent) return;
    try {
      const newSession = await createSession(selectedAgent.id, {});
      const updatedSessions = await loadSessions(selectedAgent.id);
      // Select the newly created session
      const found = updatedSessions.find((s) => s.id === newSession.id);
      setSelectedSession(found || newSession);
    } catch (err) {
      console.error("Failed to create session:", err);
      setError("Failed to create session");
    }
  };

  const handleDeleteSession = async (sessionId) => {
    if (!selectedAgent) return;
    try {
      await deleteSession(selectedAgent.id, sessionId);
      if (selectedSession && selectedSession.id === sessionId) {
        setSelectedSession(null);
        setMessages(null);
      }
      await loadSessions(selectedAgent.id);
    } catch (err) {
      console.error("Failed to delete session:", err);
      setError("Failed to delete session");
    }
  };

  // ── Message handlers ──────────────────────────────────

  const handleSendMessage = async (content) => {
    if (!selectedAgent || !selectedSession) return;
    setLoading(true);
    setError(null);
    try {
      await sendMessage(selectedAgent.id, selectedSession.id, content);
      await loadMessages(selectedAgent.id, selectedSession.id);
    } catch (err) {
      console.error("Failed to send message:", err);
      setError("Failed to send message");
    } finally {
      setLoading(false);
    }
  };

  const handleSendVoice = async (audioBlob) => {
    if (!selectedAgent || !selectedSession) return;
    setLoading(true);
    setError(null);
    try {
      const response = await sendVoice(
        selectedAgent.id,
        selectedSession.id,
        audioBlob
      );
      // If the response contains an audio_url on the assistant message, play it
      const audioUrl =
        response?.assistant_message?.audio_url || response?.audio_url;
      if (audioUrl) {
        try {
          const audio = new Audio(audioUrl);
          audio.play();
        } catch (playErr) {
          console.warn("Could not auto-play audio response:", playErr);
        }
      }
      await loadMessages(selectedAgent.id, selectedSession.id);
    } catch (err) {
      console.error("Failed to send voice:", err);
      setError("Failed to send voice message");
    } finally {
      setLoading(false);
    }
  };

  // ── Render ────────────────────────────────────────────

  const canSendMessage = selectedAgent && selectedSession && !loading;

  return (
    <div className="app-container">
      <AgentSidebar
        agents={agents}
        selectedAgent={selectedAgent}
        onSelectAgent={handleSelectAgent}
        onCreateAgent={handleCreateAgent}
        onUpdateAgent={handleUpdateAgent}
        onDeleteAgent={handleDeleteAgent}
      />

      <main className="main-area">
        <SessionBar
          agent={selectedAgent}
          sessions={sessions}
          selectedSession={selectedSession}
          onSelectSession={handleSelectSession}
          onCreateSession={handleCreateSession}
          onDeleteSession={handleDeleteSession}
        />

        {error && (
          <div className="error-banner">
            <span>{error}</span>
            <button
              className="error-dismiss"
              onClick={() => setError(null)}
            >
              &times;
            </button>
          </div>
        )}

        <ChatArea messages={messages} loading={loading} />

        <MessageInput
          onSendMessage={handleSendMessage}
          onSendVoice={handleSendVoice}
          disabled={!canSendMessage}
        />
      </main>
    </div>
  );
}
