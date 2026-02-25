"use client";

import { useState } from "react";

export default function Home() {
  const [task, setTask] = useState("");
  const [plan, setPlan] = useState(null);
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState("");

  const runPlan = async () => {
    if (!task.trim()) return;
    setStatus("loading");
    setError("");
    setPlan(null);
    try {
      const res = await fetch("http://localhost:8000/plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ task })
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Planner failed");
      }
      const data = await res.json();
      setPlan(data);
      setStatus("done");
    } catch (err) {
      setStatus("error");
      setError(err.message || "Planner failed");
    }
  };

  return (
    <main className="page">
      <section className="card">
        <h1>MR.N Local Agent</h1>
        <p>Type a task and run it locally.</p>
        <div className="input-row">
          <input
            type="text"
            placeholder="Find price of DJI Mini 4 Pro"
            aria-label="Task"
            value={task}
            onChange={(event) => setTask(event.target.value)}
          />
          <button onClick={runPlan} disabled={status === "loading"}>
            {status === "loading" ? "Planning..." : "Run"}
          </button>
        </div>
        {error ? <div className="error">{error}</div> : null}
        <div className="hint">Planner output appears below.</div>

        {plan ? (
          <div className="plan">
            <h2>Planned Steps</h2>
            <ol>
              {plan.steps.map((step) => (
                <li key={step.id}>
                  <span className="step-type">{step.type}</span>
                  <span className="step-desc">{step.description}</span>
                </li>
              ))}
            </ol>
            <pre>{JSON.stringify(plan, null, 2)}</pre>
          </div>
        ) : null}
      </section>
    </main>
  );
}
