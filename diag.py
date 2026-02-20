import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

url = os.getenv("ELASTIC_URL", "NOT SET")
key = os.getenv("ELASTIC_API_KEY", "NOT SET")

print(f"ELASTIC_URL     = {url}")
print(f"ELASTIC_API_KEY = {key[:20]}..." if key != "NOT SET" else "ELASTIC_API_KEY = NOT SET")
print()

try:
    es = Elasticsearch(url, api_key=key)
    info = es.info()
    print(f"SUCCESS: {info}")
except Exception as e:
    print(f"FULL ERROR: {type(e).__name__}: {e}")
