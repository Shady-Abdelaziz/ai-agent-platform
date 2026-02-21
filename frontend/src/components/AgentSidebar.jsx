import React, { useState, useEffect } from "react";

export default function AgentSidebar({
  agents,
  selectedAgent,
  onSelectAgent,
  onCreateAgent,
  onUpdateAgent,
  onDeleteAgent,
}) {
  const [name, setName] = useState("");
  const [prompt, setPrompt] = useState("");
  const [editingId, setEditingId] = useState(null);

  // When editing is initiated, populate the form
  useEffect(() => {
    if (editingId) {
      const agent = agents.find((a) => a.id === editingId);
      if (agent) {
        setName(agent.name);
        setPrompt(agent.system_prompt || agent.prompt || "");
      }
    }
  }, [editingId, agents]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim()) return;

    if (editingId) {
      await onUpdateAgent(editingId, { name: name.trim(), prompt: prompt.trim() });
      setEditingId(null);
    } else {
      await onCreateAgent({ name: name.trim(), prompt: prompt.trim() });
    }
    setName("");
    setPrompt("");
  };

  const handleCancel = () => {
    setEditingId(null);
    setName("");
    setPrompt("");
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h2>Agents</h2>
      </div>

      <div className="agent-list">
        {agents.map((agent) => (
          <div
            key={agent.id}
            className={`agent-item ${
              selectedAgent && selectedAgent.id === agent.id ? "active" : ""
            }`}
            onClick={() => onSelectAgent(agent)}
          >
            <div className="agent-item-info">
              <span className="agent-name">{agent.name}</span>
            </div>
            <div className="agent-item-actions">
              <button
                className="btn-edit"
                onClick={(e) => {
                  e.stopPropagation();
                  setEditingId(agent.id);
                }}
                title="Edit agent"
              >
                Edit
              </button>
              <button
                className="btn-delete-small"
                onClick={(e) => {
                  e.stopPropagation();
                  if (window.confirm(`Delete agent "${agent.name}"?`)) {
                    onDeleteAgent(agent.id);
                  }
                }}
                title="Delete agent"
              >
                &times;
              </button>
            </div>
          </div>
        ))}
        {agents.length === 0 && (
          <p className="no-agents">No agents yet. Create one below.</p>
        )}
      </div>

      <form className="agent-form" onSubmit={handleSubmit}>
        <h3>{editingId ? "Edit Agent" : "New Agent"}</h3>
        <input
          type="text"
          placeholder="Agent name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="input-field"
          required
        />
        <textarea
          placeholder="System prompt (instructions for the agent)"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          className="textarea-field"
          rows={3}
        />
        <div className="form-buttons">
          <button
            type="submit"
            className={editingId ? "btn-update" : "btn-create"}
          >
            {editingId ? "Update Agent" : "Create Agent"}
          </button>
          {editingId && (
            <button type="button" className="btn-cancel" onClick={handleCancel}>
              Cancel
            </button>
          )}
        </div>
      </form>
    </aside>
  );
}
