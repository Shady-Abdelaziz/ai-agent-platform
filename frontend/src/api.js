const API_BASE = "/api";

async function request(url, options = {}) {
  const res = await fetch(url, options);
  if (!res.ok) {
    const errorBody = await res.text();
    throw new Error(
      `API error ${res.status}: ${errorBody || res.statusText}`
    );
  }
  if (res.status === 204) return null;
  return res.json();
}

// ── Agents ──────────────────────────────────────────────

export function fetchAgents() {
  return request(`${API_BASE}/agents`);
}

export function createAgent(data) {
  return request(`${API_BASE}/agents`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export function updateAgent(id, data) {
  return request(`${API_BASE}/agents/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export function deleteAgent(id) {
  return request(`${API_BASE}/agents/${id}`, {
    method: "DELETE",
  });
}

// ── Sessions ────────────────────────────────────────────

export function fetchSessions(agentId) {
  return request(`${API_BASE}/agents/${agentId}/sessions`);
}

export function createSession(agentId, data = {}) {
  return request(`${API_BASE}/agents/${agentId}/sessions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export function deleteSession(agentId, sessionId) {
  return request(`${API_BASE}/agents/${agentId}/sessions/${sessionId}`, {
    method: "DELETE",
  });
}

// ── Messages ────────────────────────────────────────────

export function fetchMessages(agentId, sessionId) {
  return request(
    `${API_BASE}/agents/${agentId}/sessions/${sessionId}/messages`
  );
}

export function sendMessage(agentId, sessionId, content) {
  return request(
    `${API_BASE}/agents/${agentId}/sessions/${sessionId}/messages`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content }),
    }
  );
}

// ── Voice ───────────────────────────────────────────────

export function sendVoice(agentId, sessionId, audioBlob) {
  const formData = new FormData();
  formData.append("audio", audioBlob, "recording.webm");
  return request(
    `${API_BASE}/agents/${agentId}/sessions/${sessionId}/voice`,
    {
      method: "POST",
      body: formData,
    }
  );
}
