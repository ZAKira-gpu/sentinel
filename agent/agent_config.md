# 🤖 Elastic Sentinel — Agent Configuration

## Overview

The Sentinel Agent is a **tool-using ReAct-style agent** (Reason + Act loop).  
It receives an anomaly signal from ES|QL and iteratively gathers evidence
until it can produce a high-confidence incident report.

---

## Agent Identity

| Property | Value |
|---|---|
| Name | `elastic-sentinel-agent` |
| Version | `1.0.0` |
| Model | `gpt-4o` (or `claude-3-5-sonnet`) |
| Mode | ReAct (Reason → Act → Observe → Repeat) |
| Max iterations | 8 |
| Output | `output/incident_report.json` + console summary |

---

## System Prompt

```
You are Elastic Sentinel, an autonomous AI incident investigator.
Your job is to investigate a detected anomaly in a distributed system
by querying Elasticsearch logs across multiple services.

You have access to the following tools:
- detect_anomaly       → Run ES|QL anomaly detection query
- search_api_logs      → Full-text + filter search on API logs
- search_db_logs       → Search database query logs
- search_deploy_logs   → Find recent deployment events
- correlate_timeline   → Build a timeline from multiple log sources

Follow the ReAct loop:
  THOUGHT: What do I know? What do I need to find out next?
  ACTION:  Call exactly one tool.
  OBSERVATION: What did the tool return?
  ... repeat until confident ...
  CONCLUSION: Generate the incident report.

Always include a confidence score (0–100%) based on:
- Temporal correlation strength
- Number of correlated signals
- Presence of a clear triggering event

Be concise in your reasoning. Focus on facts from the logs.
```

---

## Tools Specification

### 1. `detect_anomaly`
- **Description**: Runs the ES|QL spike-detection query and returns error rate statistics.
- **Input**: `{ "window_minutes": int }`
- **Returns**: `{ "current_error_rate": float, "baseline_error_rate": float, "spike_ratio": float, "anomaly_detected": bool }`

### 2. `search_api_logs`
- **Description**: Search API logs by time range, status code, or keyword.
- **Input**: `{ "from": ISO8601, "to": ISO8601, "filter": { "status_code": int | null, "is_error": bool | null } }`
- **Returns**: Array of matching log entries (max 50)

### 3. `search_db_logs`
- **Description**: Search DB logs for timeouts and slow queries near a given window.
- **Input**: `{ "from": ISO8601, "to": ISO8601, "min_query_time_ms": int }`
- **Returns**: Array of DB log entries with query times

### 4. `search_deploy_logs`
- **Description**: Retrieve deployment events within a time range.
- **Input**: `{ "from": ISO8601, "to": ISO8601 }`
- **Returns**: Array of deployment events with IDs, versions, statuses

### 5. `correlate_timeline`
- **Description**: Given a list of timestamps and event types, build a unified, sorted timeline.
- **Input**: `{ "events": [ { "timestamp": ISO8601, "source": str, "message": str } ] }`
- **Returns**: Sorted timeline with causal chain hints

---

## Reasoning Steps (Expected Flow)

```
Step 1: DETECT
  → Call detect_anomaly
  → If spike_ratio < 2.0: no incident. Halt.
  → If spike_ratio >= 2.0: proceed.

Step 2: LOCATE (API)
  → Call search_api_logs for the spike window
  → Note: which endpoints failing? Which services?

Step 3: LOCATE (DB)
  → Call search_db_logs for same window
  → Check for timeout spikes, slow queries

Step 4: FIND TRIGGER
  → Call search_deploy_logs for 30 min before spike
  → Identify most recent deployment

Step 5: BUILD TIMELINE
  → Call correlate_timeline
  → Establish: deploy_time → spike_start → db_timeouts

Step 6: CONCLUDE
  → Write structured incident report
  → Assign confidence score
```

---

## Output Schema (incident_report.json)

```json
{
  "incident_id": "INC-YYYYMMDD-HHMMSS",
  "detected_at": "ISO8601",
  "summary": {
    "spike_detected_at": "ISO8601",
    "spike_ratio": 3.4,
    "affected_services": ["order-service", "payment-service"],
    "correlated_deployment_id": "deploy-82",
    "db_timeout_increase_pct": 300
  },
  "root_cause": {
    "hypothesis": "Schema migration introduced in deploy-82 caused table lock",
    "supporting_evidence": [
      "DB query time spiked from 12ms to 890ms at 14:02 UTC",
      "Deployment deploy-82 completed at 14:00 UTC",
      "All timeouts on 'orders' table"
    ]
  },
  "recommended_action": "Rollback deploy-82. Investigate migration_v3_schema.sql.",
  "confidence_pct": 87,
  "agent_iterations": 5
}
```
