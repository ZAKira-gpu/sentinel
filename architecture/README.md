# Architecture

This directory contains the system architecture diagram for Elastic Sentinel.

## architecture.png

The architecture diagram will be generated on Day 7 (see execution plan).

**Planned diagram content:**

```
┌────────────────────────────────────────────────────────────────────┐
│                        ELASTIC SENTINEL                            │
│                  Autonomous Incident Investigator                  │
└────────────────────────────────────────────────────────────────────┘

  ┌─────────────────┐     ┌──────────────────────────────────────────┐
  │  Log Simulator  │────▶│         Elasticsearch                    │
  │                 │     │                                          │
  │  • API logs     │     │  • sentinel-api-logs     (index)         │
  │  • DB logs      │     │  • sentinel-db-logs      (index)         │
  │  • Deploy logs  │     │  • sentinel-deploy-logs  (index)         │
  └─────────────────┘     └──────────────────────────────────────────┘
                                          │
                                          ▼
                          ┌──────────────────────────────┐
                          │      Sentinel Agent           │
                          │   (ReAct Reasoning Loop)      │
                          │                               │
                          │  1. detect_anomaly (ES|QL)    │
                          │  2. search_api_logs           │
                          │  3. search_db_logs            │
                          │  4. search_deploy_logs        │
                          │  5. correlate_timeline        │
                          │  6. generate_report           │
                          └──────────────────────────────┘
                                          │
                                          ▼
                          ┌──────────────────────────────┐
                          │      Incident Report          │
                          │  • Root cause hypothesis      │
                          │  • Supporting evidence        │
                          │  • Recommended action         │
                          │  • Confidence score           │
                          └──────────────────────────────┘
```

Replace this file with `architecture.png` when the diagram is finalized on Day 7.
