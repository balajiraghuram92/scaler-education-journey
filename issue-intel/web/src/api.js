const BASE = import.meta.env.VITE_API_URL || "http://localhost:8010";

export function headers(userId) {
  return { "Content-Type": "application/json", "x-user-id": String(userId) };
}

export async function listRuns() {
  const res = await fetch(`${BASE}/runs`);
  if (!res.ok) throw new Error(`list runs: ${res.status}`);
  return res.json();
}

export async function getRun(runId, userId) {
  const res = await fetch(`${BASE}/runs/${runId}`, { headers: headers(userId) });
  if (!res.ok) throw new Error(`get run: ${res.status}`);
  return res.json();
}

export async function getTrace(runId, userId) {
  const res = await fetch(`${BASE}/runs/${runId}/trace`, { headers: headers(userId) });
  if (!res.ok) throw new Error(`get trace: ${res.status}`);
  return res.json();
}

export async function submitReview(runId, userId, payload) {
  const res = await fetch(`${BASE}/runs/${runId}/review`, {
    method: "POST",
    headers: headers(userId),
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`review: ${res.status}`);
  return res.json();
}

export async function runAction(runId, userId, action) {
  const res = await fetch(`${BASE}/runs/${runId}/${action}`, {
    method: "POST",
    headers: headers(userId),
  });
  if (!res.ok) throw new Error(`${action}: ${res.status}`);
  return res.json();
}

export async function requestFix(runId) {
  const res = await fetch(`${BASE}/runs/${runId}/request-fix`, { method: "POST" });
  if (!res.ok) throw new Error(`request-fix: ${res.status}`);
  return res.json();
}

export async function listCandidates() {
  const res = await fetch(`${BASE}/fixes/candidates`);
  if (!res.ok) throw new Error(`candidates: ${res.status}`);
  return res.json();
}

export async function getCandidate(candidateId) {
  const res = await fetch(`${BASE}/fixes/candidates/${candidateId}`);
  if (!res.ok) throw new Error(`candidate: ${res.status}`);
  return res.json();
}

export async function getAttempt(attemptId) {
  const res = await fetch(`${BASE}/fixes/attempts/${attemptId}`);
  if (!res.ok) throw new Error(`attempt: ${res.status}`);
  return res.json();
}

export async function getPr(prId) {
  const res = await fetch(`${BASE}/prs/${prId}`);
  if (!res.ok) throw new Error(`pr: ${res.status}`);
  return res.json();
}

export async function approvePr(prId, userId) {
  const res = await fetch(`${BASE}/prs/${prId}/approve`, {
    method: "POST",
    headers: headers(userId),
    body: JSON.stringify({ approver: `user-${userId}` }),
  });
  if (!res.ok) throw new Error(`approve: ${res.status}`);
  return res.json();
}

export async function mergePr(prId, userId, token) {
  const res = await fetch(`${BASE}/prs/${prId}/merge`, {
    method: "POST",
    headers: headers(userId),
    body: JSON.stringify({ token, approver: `user-${userId}` }),
  });
  if (!res.ok) throw new Error(`merge: ${res.status}`);
  return res.json();
}

export async function getFinalCheck(runId) {
  const res = await fetch(`${BASE}/runs/${runId}/final-check`);
  if (!res.ok) throw new Error(`final-check: ${res.status}`);
  return res.json();
}

export async function requestBackport(prId, branches) {
  const res = await fetch(`${BASE}/prs/${prId}/request-backport`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ branches }),
  });
  if (!res.ok) throw new Error(`backport: ${res.status}`);
  return res.json();
}
