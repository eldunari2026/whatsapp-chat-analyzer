const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function checkHealth() {
  const res = await fetch(`${API_URL}/api/health`);
  if (!res.ok) throw new Error('Backend unreachable');
  return res.json();
}

export async function parseText(text) {
  const form = new FormData();
  form.append('text', text);
  const res = await fetch(`${API_URL}/api/parse/text`, { method: 'POST', body: form });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Parse failed' }));
    throw new Error(err.detail);
  }
  return res.json();
}

export async function parseFile(file) {
  const form = new FormData();
  form.append('file', file);
  const res = await fetch(`${API_URL}/api/parse/file`, { method: 'POST', body: form });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Parse failed' }));
    throw new Error(err.detail);
  }
  return res.json();
}

export async function analyzeText(text, filters = {}) {
  const form = new FormData();
  form.append('text', text);
  if (filters.participant) form.append('participant', filters.participant);
  if (filters.startDate) form.append('start_date', filters.startDate);
  if (filters.endDate) form.append('end_date', filters.endDate);

  const res = await fetch(`${API_URL}/api/analyze/text`, { method: 'POST', body: form });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Analysis failed' }));
    throw new Error(err.detail);
  }
  return res.json();
}

export async function analyzeFile(file, filters = {}) {
  const form = new FormData();
  form.append('file', file);
  if (filters.participant) form.append('participant', filters.participant);
  if (filters.startDate) form.append('start_date', filters.startDate);
  if (filters.endDate) form.append('end_date', filters.endDate);

  const res = await fetch(`${API_URL}/api/analyze/file`, { method: 'POST', body: form });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Analysis failed' }));
    throw new Error(err.detail);
  }
  return res.json();
}
