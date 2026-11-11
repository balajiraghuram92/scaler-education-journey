import React, { useState } from "react";
import {
  approvePr, getAttempt, getCandidate, getFinalCheck, getPr, listCandidates,
  mergePr, requestBackport, requestFix,
} from "./api.js";

export default function FixPage({ runId, userId }) {
  const [candidate, setCandidate] = useState(null);
  const [attempt, setAttempt] = useState(null);
  const [pr, setPr] = useState(null);
  const [check, setCheck] = useState(null);
  const [token, setToken] = useState("");
  const [msg, setMsg] = useState("");
  const [branches, setBranches] = useState("release/2024.3");

  const start = async () => {
    const c = await requestFix(runId);
    setCandidate(c);
    setMsg(`Candidate ${c.candidate_id}: ${c.status}. Wait for the worker, then Refresh.`);
  };
  const refresh = async () => {
    const list = await listCandidates();
    const mine = list.find((c) => c.run_id === runId);
    if (!mine) { setMsg("No candidate yet."); return; }
    setCandidate(mine);
    setMsg(`Candidate ${mine.id}: ${mine.status}`);
  };
  const loadAttempt = async (attemptId) => {
    const a = await getAttempt(attemptId);
    setAttempt(a);
    if (a.prs.length > 0) setPr(await getPr(a.prs[0].id));
    try { setCheck(await getFinalCheck(runId)); } catch { setCheck(null); }
  };
  void userId;
  return (
    <div>
      <h2>Fix for run {runId}</h2>
      <button onClick={start}>Request fix</button>
      <button onClick={refresh}>Refresh candidate</button>
      <p>{msg}</p>
      {candidate && candidate.id && (
        <AttemptLoader candidateId={candidate.candidate_id || candidate.id} onLoad={loadAttempt} />
      )}
      {attempt && (
        <div>
          <h3>Attempt {attempt.attempt_no} — {attempt.status}</h3>
          <p>Branch {attempt.branch} · tokens {attempt.tokens_in}/{attempt.tokens_out}</p>
          <h4>Test output</h4><pre>{attempt.test_output || "(none)"}</pre>
          <h4>Trace</h4><pre>{JSON.stringify(attempt.trace, null, 2)}</pre>
        </div>
      )}
      {pr && (
        <div>
          <h3>PR #{pr.id} — {pr.status}</h3>
          <p>{pr.title} · base {pr.base}</p>
          <h4>Diff</h4><pre>{pr.diff || "(none)"}</pre>
        </div>
      )}
      {check && <p>Final check: <b>{check.verdict}</b> — {check.reason}</p>}
      {pr && pr.status === "OPEN" && (
        <div className="actions">
          <button onClick={async () => {
            const r = await approvePr(pr.id, userId);
            setToken(r.token);
            setMsg("Approved; token minted. Merge to integrate.");
          }}>Approve</button>
          <button disabled={!token} onClick={async () => {
            const r = await mergePr(pr.id, userId, token);
            setMsg(`Merged: ${r.commit}`);
            setPr({ ...pr, status: "MERGED" });
          }}>Merge</button>
        </div>
      )}
      {pr && pr.status === "MERGED" && (
        <div className="actions">
          <input value={branches} onChange={(e) => setBranches(e.target.value)} />
          <button onClick={async () => {
            const r = await requestBackport(pr.id, branches.split(",").map((s) => s.trim()));
            setMsg(`Backport queued: ${JSON.stringify(r.branches)}`);
          }}>Backport</button>
        </div>
      )}
    </div>
  );
}

function AttemptLoader({ candidateId, onLoad }) {
  const [attempts, setAttempts] = useState([]);
  React.useEffect(() => {
    getCandidate(candidateId)
      .then((d) => setAttempts(d.attempts || []))
      .catch(() => setAttempts([]));
  }, [candidateId]);
  if (attempts.length === 0) return <p>No attempts yet.</p>;
  return (
    <div className="actions">
      {attempts.map((a) => (
        <button key={a.id} onClick={() => onLoad(a.id)}>Attempt {a.attempt_no} ({a.status})</button>
      ))}
    </div>
  );
}
