/**
 * api.js — Fetch calls to Flask backend
 */

const API_BASE = window.location.origin;

async function apiFetch(path, params = {}) {
  const url = new URL(API_BASE + path);
  Object.entries(params).forEach(([k, v]) => {
    if (v !== null && v !== undefined && v !== '') url.searchParams.set(k, v);
  });
  const res = await fetch(url.toString());
  if (!res.ok) throw new Error(`API error ${res.status}: ${path}`);
  return res.json();
}

const API = {
  status:         ()       => apiFetch('/api/status'),
  tasks:          (params) => apiFetch('/api/tasks', params),
  task:           (id)     => apiFetch(`/api/task/${id}`),
  resultsSummary: ()       => apiFetch('/api/results/summary'),
  resultsByType:  ()       => apiFetch('/api/results/by_type'),
  resultsByTier:  ()       => apiFetch('/api/results/by_tier'),
  resultsRuns:    (params) => apiFetch('/api/results/runs', params),
  leaderboard:    ()       => apiFetch('/api/leaderboard'),
  taskTypes:      ()       => apiFetch('/api/task_types'),
};

window.API = API;
