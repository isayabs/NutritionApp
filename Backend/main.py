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

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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
