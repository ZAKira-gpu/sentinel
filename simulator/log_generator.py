"""
Elastic Sentinel — Log Generator / Simulator
=============================================
Generates realistic API, Database, and Deployment logs,
then injects a simulated incident (error spike caused by a bad deployment).

Output: Pushes all logs into Elasticsearch indices.

Usage:
    python log_generator.py

Environment Variables (set in .env):
    ELASTIC_CLOUD_ID   - Your Elastic Cloud ID
    ELASTIC_API_KEY    - Your Elastic API Key
    ES_HOST            - Alternative: local ES host (e.g., http://localhost:9200)
"""

import os
import json
import random
import time
from datetime import datetime, timedelta, timezone
from faker import Faker
from elasticsearch import Elasticsearch, helpers
from dotenv import load_dotenv

# Load .env file from the project root (one level up from simulator/)
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────
fake = Faker()

# Elastic Serverless: https://PROJECT_ID.es.REGION.gcp.elastic-cloud.com
ELASTIC_URL     = os.getenv("ELASTIC_URL", "http://localhost:9200")
ELASTIC_API_KEY = os.getenv("ELASTIC_API_KEY")

API_INDEX        = "sentinel-api-logs"
DB_INDEX         = "sentinel-db-logs"
DEPLOY_INDEX     = "sentinel-deploy-logs"

# Incident parameters
INCIDENT_START_OFFSET_MINUTES = 30   # incident starts 30 min into simulation window
DEPLOYMENT_ID                  = "deploy-82"
INCIDENT_DURATION_MINUTES      = 20

# ──────────────────────────────────────────────
# Elasticsearch Client
# ──────────────────────────────────────────────
def get_es_client() -> Elasticsearch:
    """Connect using Elastic Serverless URL + API Key."""
    if ELASTIC_API_KEY:
        return Elasticsearch(
            ELASTIC_URL,
            api_key=ELASTIC_API_KEY,
        )
    # Fallback: unauthenticated local instance
    return Elasticsearch(ELASTIC_URL)


# ──────────────────────────────────────────────
# Log Generators
# ──────────────────────────────────────────────
ENDPOINTS = ["/api/users", "/api/orders", "/api/products", "/api/auth", "/api/payments"]
HTTP_METHODS = ["GET", "POST", "PUT", "DELETE"]
SERVICES = ["user-service", "order-service", "payment-service", "auth-service"]

def generate_api_log(timestamp: datetime, is_incident: bool = False) -> dict:
    """Generate a single API log entry."""
    status_code = (
        random.choices([500, 503, 502, 504], weights=[50, 20, 15, 15])[0]
        if is_incident and random.random() < 0.6
        else random.choices([200, 201, 400, 404, 500], weights=[70, 10, 10, 8, 2])[0]
    )
    latency = (
        random.randint(800, 3000) if is_incident and status_code >= 500
        else random.randint(10, 200)
    )
    return {
        "@timestamp":   timestamp.isoformat(),
        "type":         "api",
        "service":      random.choice(SERVICES),
        "method":       random.choice(HTTP_METHODS),
        "endpoint":     random.choice(ENDPOINTS),
        "status_code":  status_code,
        "latency_ms":   latency,
        "user_id":      fake.uuid4(),
        "request_id":   fake.uuid4(),
        "ip":           fake.ipv4(),
        "is_error":     status_code >= 500,
        "message":      (
            f"HTTP {status_code} — upstream timeout" if status_code >= 500
            else f"HTTP {status_code} — OK"
        ),
    }


DB_OPERATIONS = ["SELECT", "INSERT", "UPDATE", "DELETE"]
DB_TABLES = ["users", "orders", "products", "sessions", "payments"]

def generate_db_log(timestamp: datetime, is_incident: bool = False) -> dict:
    """Generate a single DB log entry."""
    query_time = (
        random.randint(500, 5000) if is_incident and random.random() < 0.7
        else random.randint(1, 30)
    )
    is_timeout = query_time > 3000
    return {
        "@timestamp":   timestamp.isoformat(),
        "type":         "database",
        "operation":    random.choice(DB_OPERATIONS),
        "table":        random.choice(DB_TABLES),
        "query_time_ms": query_time,
        "rows_affected": random.randint(0, 1000),
        "is_timeout":   is_timeout,
        "is_error":     is_timeout,
        "connection_pool_size": random.randint(5, 50),
        "message": (
            "Query timeout — possible schema lock" if is_timeout
            else "Query executed successfully"
        ),
    }


def generate_deployment_log(timestamp: datetime, deployment_id: str, status: str, note: str = "") -> dict:
    """Generate a deployment event log."""
    return {
        "@timestamp":    timestamp.isoformat(),
        "type":          "deployment",
        "deployment_id": deployment_id,
        "status":        status,          # STARTED | COMPLETED | FAILED | ROLLBACK
        "version":       "v3.2.1" if deployment_id == DEPLOYMENT_ID else "v3.2.0",
        "triggered_by":  "ci-pipeline",
        "environment":   "production",
        "note":          note,
        "is_error":      status in ("FAILED", "ROLLBACK"),
        "message":       f"Deployment {deployment_id} {status.lower()}. {note}".strip(),
    }


# ──────────────────────────────────────────────
# Index Setup
# ──────────────────────────────────────────────
COMMON_MAPPINGS = {
    "mappings": {
        "properties": {
            "@timestamp": {"type": "date"},
            "is_error":   {"type": "boolean"},
            "message":    {"type": "text"},
        }
    }
}

def setup_indices(es: Elasticsearch):
    for index in [API_INDEX, DB_INDEX, DEPLOY_INDEX]:
        if not es.indices.exists(index=index):
            es.indices.create(
                index=index,
                mappings={
                    "properties": {
                        "@timestamp": {"type": "date"},
                        "is_error":   {"type": "boolean"},
                        "message":    {"type": "text"},
                    }
                }
            )
            print(f"  ✅ Created index: {index}")
        else:
            print(f"  ℹ️  Index already exists: {index}")


# ──────────────────────────────────────────────
# Bulk Ingest
# ──────────────────────────────────────────────
def bulk_ingest(es: Elasticsearch, index: str, docs: list[dict]):
    actions = [{"_index": index, "_source": doc} for doc in docs]
    success, errors = helpers.bulk(es, actions, raise_on_error=False)
    if errors:
        print(f"  ⚠️  {len(errors)} errors while ingesting into {index}")
    print(f"  📥 Ingested {success} documents into '{index}'")


# ──────────────────────────────────────────────
# Main Simulation
# ──────────────────────────────────────────────
def simulate(window_minutes: int = 60, logs_per_minute: int = 30):
    """
    Simulate `window_minutes` worth of logs with an incident injected
    at INCIDENT_START_OFFSET_MINUTES.

    Args:
        window_minutes:  Total simulation time window in minutes.
        logs_per_minute: Average log entries per service per minute.
    """
    es = get_es_client()

    print("\n🛡️  Elastic Sentinel — Log Simulator")
    print("=" * 50)

    # Connection check
    print(f"\n  ELASTIC_URL     = {ELASTIC_URL}")
    print(f"  ELASTIC_API_KEY = {'SET ✅' if ELASTIC_API_KEY else 'NOT SET ❌'}\n")
    print("🔌 Connecting to Elasticsearch...")

    print("📋 Setting up indices...")
    setup_indices(es)

    base_time = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)
    incident_start = base_time + timedelta(minutes=INCIDENT_START_OFFSET_MINUTES)
    incident_end   = incident_start + timedelta(minutes=INCIDENT_DURATION_MINUTES)
    deployment_time = incident_start - timedelta(minutes=2)  # deploy 2 min before spike

    api_docs    = []
    db_docs     = []
    deploy_docs = []

    print(f"\n⏱️  Simulating {window_minutes} minutes of logs...")
    print(f"   Base time       : {base_time.strftime('%H:%M:%S UTC')}")
    print(f"   Deployment at   : {deployment_time.strftime('%H:%M:%S UTC')}")
    print(f"   Incident starts : {incident_start.strftime('%H:%M:%S UTC')}")
    print(f"   Incident ends   : {incident_end.strftime('%H:%M:%S UTC')}\n")

    # Deployment events
    deploy_docs.append(generate_deployment_log(
        deployment_time, DEPLOYMENT_ID, "STARTED",
        note="Schema migration v3 included"
    ))
    deploy_docs.append(generate_deployment_log(
        deployment_time + timedelta(minutes=1), DEPLOYMENT_ID, "COMPLETED",
        note="migration_v3_schema.sql applied"
    ))

    # Generate per-minute logs
    for minute in range(window_minutes):
        ts = base_time + timedelta(minutes=minute)
        in_incident = incident_start <= ts <= incident_end

        # Burst more errors during incident
        count = logs_per_minute * (3 if in_incident else 1)

        for _ in range(count):
            jitter = timedelta(seconds=random.randint(0, 59))
            api_docs.append(generate_api_log(ts + jitter, is_incident=in_incident))
            db_docs.append(generate_db_log(ts + jitter, is_incident=in_incident))

    # Ingest everything
    print("📤 Ingesting logs into Elasticsearch...")
    bulk_ingest(es, API_INDEX, api_docs)
    bulk_ingest(es, DB_INDEX, db_docs)
    bulk_ingest(es, DEPLOY_INDEX, deploy_docs)

    print("\n🎉 Simulation complete!")
    print(f"   Total API logs     : {len(api_docs)}")
    print(f"   Total DB logs      : {len(db_docs)}")
    print(f"   Total deploy events: {len(deploy_docs)}")
    print(f"\n   Incident window    : {incident_start.strftime('%H:%M')} — {incident_end.strftime('%H:%M')} UTC")
    print(f"   Linked deployment  : {DEPLOYMENT_ID}\n")


if __name__ == "__main__":
    simulate(window_minutes=60, logs_per_minute=30)
