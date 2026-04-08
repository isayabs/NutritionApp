from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from data_analysis import (
    get_avg_protein_bar,
    get_macros_heatmap,
    get_top_protein_scatter,
    get_recipe_distribution_pie,
    get_highest_protein_diet,
    get_most_common_cuisine,
    get_recipes,
)

app = FastAPI(title="Nutrition Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://20.151.170.182:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Nutrition backend is running"}


@app.get("/api/data/highest-protein-diet")
def highest_protein_diet(
    diet: Optional[str] = None,
    search: Optional[str] = None,
):
    return {"data": get_highest_protein_diet(diet=diet, search=search)}


@app.get("/api/data/most-common-cuisine")
def most_common_cuisine(
    diet: Optional[str] = None,
    search: Optional[str] = None,
):
    return {"data": get_most_common_cuisine(diet=diet, search=search)}


@app.get("/api/chart/protein-bar")
def protein_bar(
    diet: Optional[str] = None,
    search: Optional[str] = None,
):
    return {"image": get_avg_protein_bar(diet=diet, search=search)}


@app.get("/api/chart/macros-heatmap")
def macros_heatmap(
    diet: Optional[str] = None,
    search: Optional[str] = None,
):
    return {"image": get_macros_heatmap(diet=diet, search=search)}


@app.get("/api/chart/top-protein-scatter")
def top_protein_scatter(
    diet: Optional[str] = None,
    search: Optional[str] = None,
):
    return {"image": get_top_protein_scatter(diet=diet, search=search)}


@app.get("/api/chart/recipe-distribution")
def recipe_distribution(
    diet: Optional[str] = None,
    search: Optional[str] = None,
):
    return {"image": get_recipe_distribution_pie(diet=diet, search=search)}

@app.get("/api/data/recipes")
def recipes(
    diet: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 20,
):
    return {"data": get_recipes(diet=diet, search=search, limit=limit)}