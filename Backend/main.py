from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from data_analysis import (
    get_avg_protein_bar,
    get_macros_heatmap,
    get_top_protein_scatter,
    get_recipe_distribution_pie,
    get_highest_protein_diet,
    get_most_common_cuisine
)
import time
import psutil
from datetime import datetime, timezone

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://20.151.170.182:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

START_TIME = time.time()
# ─── Data Endpoints ───────────────────────────────────────────────────────────

@app.get("/api/data/highest-protein-diet")
def highest_protein_diet():
    return {"data": get_highest_protein_diet()}

@app.get("/api/data/most-common-cuisine")
def most_common_cuisine():
    return {"data": get_most_common_cuisine()}

# ─── Chart Endpoints ──────────────────────────────────────────────────────────

@app.get("/api/chart/protein-bar")
def protein_bar():
    return {"image": get_avg_protein_bar()}

@app.get("/api/chart/macros-heatmap")
def macros_heatmap():
    return {"image": get_macros_heatmap()}

@app.get("/api/chart/top-protein-scatter")
def top_protein_scatter():
    return {"image": get_top_protein_scatter()}

@app.get("/api/chart/recipe-distribution")
def recipe_distribution():
    return {"image": get_recipe_distribution_pie()}

@app.get("/api/security/status")
def security_status():
    uptime_seconds = int(time.time() - START_TIME)
    uptime_minutes = uptime_seconds // 60
    uptime_hours = uptime_minutes // 60

    return {
        "encryption": {
            "status": "warning",
            "message": "HTTP (No SSL)"
        },
        "access_control": {
            "status": "secure",
            "message": "CORS configured"
        },
        "compliance": {
            "status": "secure",
            "message": "GDPR Compliant"
        },
        "uptime": {
            "status": "secure",
            "message": f"{uptime_hours}h {uptime_minutes % 60}m {uptime_seconds % 60}s"
        },
        "last_checked": datetime.now(timezone.utc).isoformat()
    }