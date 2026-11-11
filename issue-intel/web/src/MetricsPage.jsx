import React, { useEffect, useState } from "react";
import { getMetrics } from "./api.js";

const ROWS = [
  ["cost_per_resolved_case", "Cost per resolved case", (v) => `$${v.toFixed(4)}`],
  ["expensive_tier_share", "Share on the most expensive tier", (v) => `${(v * 100).toFixed(1)}%`],
  ["final_check_sendback_rate", "Final-check send-back rate", (v) => `${(v * 100).toFixed(1)}%`],
  ["quality_verify_filtered", "Filtered by quality_verify", (v) => String(v)],
  ["fix_acceptance_rate", "Fix acceptance rate", (v) => `${(v * 100).toFixed(1)}%`],
  ["leakage_errors", "Leakage errors", (v) => String(v)],
  ["runs_done", "Runs done", (v) => String(v)],
  ["n_calls", "Model calls (excl. shadow)", (v) => String(v)],
  ["total_cost_usd", "Total model cost", (v) => `$${v.toFixed(4)}`],
  ["active_routing_version", "Active routing version", (v) => (v === null ? "—" : `v${v}`)],
];

export default function MetricsPage() {
  const [metrics, setMetrics] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => {
    getMetrics().then(setMetrics).catch((e) => setError(String(e)));
  }, []);
  if (error) return <p className="error">{error}</p>;
  if (!metrics) return <p>Loading…</p>;
  return (
    <table>
      <thead>
        <tr><th>Metric</th><th>Value</th></tr>
      </thead>
      <tbody>
        {ROWS.map(([key, label, format]) => (
          <tr key={key}>
            <td>{label}</td>
            <td>{format(metrics[key])}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
