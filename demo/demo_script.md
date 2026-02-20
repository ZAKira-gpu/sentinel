# 🎬 Elastic Sentinel — Demo Script

## Overview

This script guides you through recording a 3–5 minute demo video
for the Devpost submission. Follow each scene in order.

---

## 🎥 Scene 1 — Hook (0:00–0:30)

**What to show:** Terminal / IDE open with the project structure.

**What to say:**
> "What happens when your production system starts throwing thousands
> of errors at 2 AM and your on-call engineer is asleep?
> Elastic Sentinel answers that — autonomously."

**Actions:**
- Show the folder structure: `tree elastic-sentinel-agent`
- Briefly pan through `README.md`

---

## 🎥 Scene 2 — Simulate the Incident (0:30–1:30)

**What to show:** Running the log generator.

**What to say:**
> "First, we simulate a real-world incident.
> We have three services — API, Database, and a deployment pipeline.
> We inject an error spike caused by a bad deployment."

**Actions:**
```bash
cd elastic-sentinel-agent
python simulator/log_generator.py
```

Expected output:
```
✅ Connected to Elasticsearch
📋 Setting up indices...
⏱️  Simulating 60 minutes of logs...
   Deployment at   : 14:00 UTC
   Incident starts : 14:02 UTC
📤 Ingesting logs...
   📥 Ingested 2700 documents into 'sentinel-api-logs'
   📥 Ingested 2700 documents into 'sentinel-db-logs'
   📥 Ingested 2 documents into 'sentinel-deploy-logs'
🎉 Simulation complete!
```

---

## 🎥 Scene 3 — Kibana: Show the Spike (1:30–2:30)

**What to show:** Kibana Discover or Lens chart.

**What to say:**
> "In Kibana, you can see the error rate spike clearly.
> Before 14:00 — everything's normal.
> After the deployment — errors explode."

**Actions:**
- Open Kibana → Discover → `sentinel-api-logs`
- Add filter: `is_error: true`
- Switch to Lens chart grouped by 1-minute buckets
- Show the spike visually

---

## 🎥 Scene 4 — Run the Agent (2:30–3:30)

**What to show:** Agent running its reasoning loop.

**What to say:**
> "Now the agent kicks in. It runs a series of ES|QL queries,
> correlates the deployment event with the DB timeouts,
> and reasons about the root cause — all in seconds."

**Actions:**
```bash
python agent/sentinel_agent.py
```

Expected output (truncated):
```
🔍 [DETECT]   Spike ratio: 3.4x above baseline. Anomaly confirmed.
🔍 [API]      Top failing endpoint: /api/orders (87% error rate)
🔍 [DB]       Avg query time jumped from 12ms → 892ms
🔍 [DEPLOY]   Last deployment: deploy-82 at 14:00 UTC (Schema migration)
🧠 [REASON]   Causal chain: deploy-82 → schema lock → DB timeouts → API 503s
📋 [REPORT]   Writing incident report...
```

---

## 🎥 Scene 5 — Incident Report (3:30–4:30)

**What to show:** The generated `output/incident_report.json` and console summary.

**What to say:**
> "And here's the result — a structured incident report.
> Root cause identified. Recommended action clear.
> 87% confidence. In under 10 seconds."

**Actions:**
- Show the JSON file: `cat output/incident_report.json`
- Or run the pretty-print command:
  ```bash
  python agent/print_report.py
  ```

Show the output:
```
╔══════════════════════════════════════════════════════════╗
║           ELASTIC SENTINEL — INCIDENT REPORT             ║
╚══════════════════════════════════════════════════════════╝

Incident Summary:
  • Error spike detected at 14:02 UTC
  • Spike magnitude: 340% above baseline
  • Correlated with Deployment ID: deploy-82
  • DB timeout errors increased 300%

Root Cause:
  Schema migration in deploy-82 caused table lock on 'orders'.
  DB latency: 12ms → 892ms immediately post-deployment.

Recommended Action:
  Rollback deploy-82. Investigate migration_v3_schema.sql.

Confidence: 87%
```

---

## 🎥 Scene 6 — Architecture & Close (4:30–5:00)

**What to say:**
> "Elastic Sentinel shows how ES|QL, Elasticsearch, and an AI agent
> can work together to autonomously investigate incidents —
> faster than any human on-call rotation."

**Actions:**
- Show the `architecture/architecture.png` diagram
- End on the GitHub repo / Devpost link

---

## ✅ Recording Checklist

- [ ] Terminal font size large enough to read
- [ ] Kibana chart clearly shows the spike
- [ ] Agent output is visible and readable
- [ ] Incident report output is readable on screen
- [ ] Audio is clear (or subtitles added)
- [ ] Video is ≤ 5 minutes
