from fastapi import FastAPI, Request, HTTPException
import aiohttp
from datetime import datetime
import json
from starlette_prometheus import PrometheusMiddleware, metrics

app = FastAPI()

# Add Prometheus middleware for metrics
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", metrics)

CLICKHOUSE_URL = "http://clickhouse.lugx.svc.cluster.local:8123"
TABLE_NAME = "web_analytics"


def convert_timestamp(iso_str: str) -> str:
    """Convert ISO 8601 (with Z) to 'YYYY-MM-DD HH:MM:SS'"""
    try:
        # Remove 'Z' and parse as UTC
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        # Fallback to now if invalid
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@app.post("/analytics")
async def log_event(request: Request):
    try:
        data = await request.json()

        # Validate required fields
        if "timestamp" not in data:
            raise ValueError("Missing timestamp")

        # Convert timestamp to ClickHouse-friendly format
        data["timestamp"] = convert_timestamp(data["timestamp"])

        # Serialize to JSON + newline
        payload = json.dumps(data) + "\n"

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{CLICKHOUSE_URL}?query=INSERT INTO {TABLE_NAME} FORMAT JSONEachRow",
                data=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 200:
                    text = await response.text()
                    raise HTTPException(status_code=500, detail=f"ClickHouse error: {text}")

        return {"status": "logged"}

    except Exception as e:
        return {"status": "failed", "error": str(e)}
