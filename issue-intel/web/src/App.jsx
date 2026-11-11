import React, { useEffect, useState } from "react";
import { getRun, getTrace, listRuns, runAction, submitReview } from "./api.js";
import FixPage from "./FixPage.jsx";

function RunList({ onOpen }) {
  const [runs, setRuns] = useState([]);
  const [error, setError] = useState("");
  useEffect(() => {
    listRuns().then(setRuns).catch((e) => setError(String(e)));
  }, []);
  if (error) return <p className="error">{error}</p>;
  return (
    <table>
      <thead>
        <tr><th>Ticket</th><th>Trigger</th><th>Status</th><th>Cost</th><th></th></tr>
      </thead>
      <tbody>
        {runs.map((r) => (
          <tr key={r.id}>
            <td>{r.ticket}</td>
            <td>{r.trigger}</td>
            <td>{r.status}</td>
            <td>${r.cost_usd.toFixed(4)}</td>
            <td><button onClick={() => onOpen(r.id)}>Review</button></td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function Review({ runId, userId, onTrace }) {
  const [view, setView] = useState(null);
  const [error, setError] = useState("");
  const [result, setResult] = useState("");
  useEffect(() => {
    getRun(runId, userId).then(setView).catch((e) => setError(String(e)));
  }, [runId, userId]);
  if (error) return <p className="error">{error}</p>;
  if (!view) return <p>Loading…</p>;
  if (view.wrong_module_alert) {
    const alert = view.wrong_module_alert;
    return (
      <div>
        <h2>{view.ticket} — wrong module</h2>
        <p>Belongs to {alert.predicted_module} (confidence {alert.confidence}).</p>
        <button onClick={() => runAction(runId, userId, "request-access").then(() => setResult("Access requested."))}>
          Request access
        </button>
        <button onClick={() => runAction(runId, userId, "notify-owner").then((r) => setResult(`Notified ${r.notified}.`))}>
          Notify owning team
        </button>
        <p>{result}</p>
      </div>
    );
  }
  const decide = (decision) =>
    submitReview(runId, userId, { reviewer: `user-${userId}`, decision })
      .then((r) => setResult(JSON.stringify(r)))
      .catch((e) => setError(String(e)));
  return (
    <div>
      <h2>{view.ticket}</h2>
      <p>Status {view.status} · withheld claims {view.withheld}</p>
      <h3>Synthesis</h3>
      <pre>{view.answer_text || "(none)"}</pre>
      <h3>Evidence</h3>
      <ul>
        {view.evidence.map((e) => (
          <li key={e.id}><b>[{e.id}]</b> {e.kind}:{e.key} — {e.title} <i>{e.outcome}</i></li>
        ))}
      </ul>
      <div className="actions">
        <button onClick={() => decide("APPROVED")}>Approve and post</button>
        <button onClick={() => decide("NEED_INFO")}>Need info</button>
        <button onClick={() => decide("WRONG")}>Wrong</button>
        <button onClick={() => decide("NOTIFY_OWNER")}>Notify owner</button>
        <button onClick={onTrace}>Trace</button>
      </div>
      <p>{result}</p>
    </div>
  );
}

function Trace({ runId, userId }) {
  const [stages, setStages] = useState([]);
  const [open, setOpen] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => {
    getTrace(runId, userId).then(setStages).catch((e) => setError(String(e)));
  }, [runId, userId]);
  if (error) return <p className="error">{error}</p>;
  return (
    <table>
      <thead>
        <tr><th>Stage</th><th>Model</th><th>Tokens</th><th>Status</th><th></th></tr>
      </thead>
      <tbody>
        {stages.map((s) => (
          <React.Fragment key={s.stage}>
            <tr>
              <td>{s.stage}</td>
              <td>{s.model || "—"}</td>
              <td>{s.tokens_in}/{s.tokens_out}</td>
              <td>{s.status}{s.error ? ` (${s.error})` : ""}</td>
              <td>
                <button onClick={() => setOpen(open === s.stage ? null : s.stage)}>
                  {open === s.stage ? "Hide" : "Show"}
                </button>
              </td>
            </tr>
            {open === s.stage && (
              <tr><td colSpan="5"><pre>{JSON.stringify({ input: s.input, output: s.output }, null, 2)}</pre></td></tr>
            )}
          </React.Fragment>
        ))}
      </tbody>
    </table>
  );
}

export default function App() {
  const [userId, setUserId] = useState("1");
  const [view, setView] = useState({ name: "list", runId: null });
  const [fixRunId, setFixRunId] = useState("");
  return (
    <div className="app">
      <header>
        <h1>Issue Intel</h1>
        <label>Viewer id <input value={userId} onChange={(e) => setUserId(e.target.value)} /></label>
        <nav>
          <button onClick={() => setView({ name: "list", runId: null })}>Runs</button>
          <input placeholder="run id" value={fixRunId} onChange={(e) => setFixRunId(e.target.value)} />
          <button onClick={() => fixRunId && setView({ name: "fix", runId: fixRunId })}>Fix</button>
        </nav>
      </header>
      <main>
        {view.name === "list" && <RunList onOpen={(runId) => setView({ name: "review", runId })} />}
        {view.name === "review" && (
          <Review runId={view.runId} userId={userId} onTrace={() => setView({ name: "trace", runId: view.runId })} />
        )}
        {view.name === "trace" && <Trace runId={view.runId} userId={userId} />}
        {view.name === "fix" && <FixPage runId={view.runId} userId={userId} />}
      </main>
    </div>
  );
}
