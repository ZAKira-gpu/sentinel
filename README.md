# 🛡️ Elastic Sentinel — Autonomous Incident Investigator Agent

> An AI agent that detects error spikes, investigates logs across services, finds the root cause, and generates an incident report — automatically.

---

## 🎯 What It Does

Elastic Sentinel monitors your distributed system's logs in near real-time. When an anomaly is detected (e.g., a sudden spike in 5xx errors), the agent:

1. **Detects** the anomaly using an ES|QL query against Elasticsearch
2. **Searches** correlated logs across API, Database, and Deployment services
3. **Reasons** about the root cause by correlating events temporally
4. **Generates** a structured incident report with confidence score

---

## 🏗️ Architecture

```
Simulated Logs  →  Elasticsearch  →  Agent (ES|QL Queries)  →  Incident Report
  (3 services)       (indexed)          (reasoning loop)         (structured JSON)
```

![Architecture Diagram](architecture/architecture.png)

---

## 🧱 Components

| Component | Path | Description |
|---|---|---|
| Log Simulator | `simulator/log_generator.py` | Generates realistic API, DB, and deployment logs with injected incident |
| Anomaly Query | `queries/anomaly_detection.esql` | ES|QL query to detect error rate spikes |
| Agent Config | `agent/agent_config.md` | Agent tools, reasoning steps, and LLM prompt design |
| Incident Workflow | `workflows/incident_workflow.json` | Step-by-step workflow the agent follows |
| Demo Script | `demo/demo_script.md` | Walkthrough for live demo / video recording |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Elasticsearch 8.x (Elastic Cloud free trial or local)
- `pip install elasticsearch faker`

### 1. Configure your Elasticsearch connection
```bash
cp .env.example .env
# Fill in your ELASTIC_CLOUD_ID and ELASTIC_API_KEY
```

### 2. Generate and ingest logs
```bash
python simulator/log_generator.py
```

### 3. Run the agent
```bash
python agent/sentinel_agent.py
```

### 4. View the incident report
The agent outputs a structured JSON report to `output/incident_report.json` and prints a human-readable summary to the console.

---

## 📊 Sample Incident Report Output

```
╔══════════════════════════════════════════════════════════╗
║           ELASTIC SENTINEL — INCIDENT REPORT             ║
╚══════════════════════════════════════════════════════════╝

Incident Summary:
  • Error spike detected at 14:02 UTC
  • Spike magnitude: 340% above baseline
  • Correlated with Deployment ID: deploy-82
  • DB timeout errors increased 300% post-deployment

Root Cause:
  Likely schema migration issue introduced in deploy-82.
  DB query latency spiked from ~12ms to ~890ms immediately
  after the deployment event at 14:00 UTC.

Recommended Action:
  Rollback deployment deploy-82 immediately.
  Investigate migration script: migration_v3_schema.sql

Confidence: 87%
```

---

## 📅 Build Timeline

| Day | Goal |
|-----|------|
| 1 | Setup Elastic + ingest logs |
| 2 | Simulate incident |
| 3 | Build anomaly detection query |
| 4 | Build search tools |
| 5 | Connect Agent |
| 6 | Add reasoning & structured report |
| 7 | Polish + architecture diagram |
| 8 | Record demo + Devpost submission |

---

## 🛠️ Tech Stack

- **Language**: Python 3.10+
- **Search & Analytics**: Elasticsearch 8.x + ES|QL
- **AI / LLM**: Elastic Agent Builder (or OpenAI GPT-4o)
- **Log Simulation**: Python `faker` library
- **Output**: JSON + Markdown incident report

---

## 📄 License

MIT — see [LICENSE](LICENSE)
