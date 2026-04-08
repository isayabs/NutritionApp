import base64
import io
import os

import matplotlib
matplotlib.use("Agg")  # must be before pyplot

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


CSV_PATH = os.path.join(os.path.dirname(__file__), "All_Diets.csv")


def load_data():
    df = pd.read_csv(CSV_PATH)

    # Clean text columns
    df["Diet_type"] = df["Diet_type"].astype(str).str.strip()
    df["Recipe_name"] = df["Recipe_name"].astype(str).str.strip()
    df["Cuisine_type"] = df["Cuisine_type"].astype(str).str.strip()

    # Clean numeric columns
    numeric_cols = ["Protein(g)", "Carbs(g)", "Fat(g)"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].fillna(df[col].mean())

    # Avoid divide by zero
    df["Protein_to_Carbs_ratio"] = df["Protein(g)"] / df["Carbs(g)"].replace(0, pd.NA)
    df["Carbs_to_Fat_ratio"] = df["Carbs(g)"] / df["Fat(g)"].replace(0, pd.NA)

    return df


def apply_filters(df, diet=None, search=None):
    filtered = df.copy()

    if diet and diet.strip().lower() != "all diet types":
        filtered = filtered[
            filtered["Diet_type"].str.lower() == diet.strip().lower()
        ]

    if search and search.strip():
        term = search.strip().lower()
        filtered = filtered[
            filtered["Diet_type"].str.lower().str.contains(term, na=False)
            | filtered["Recipe_name"].str.lower().str.contains(term, na=False)
            | filtered["Cuisine_type"].str.lower().str.contains(term, na=False)
        ]

    return filtered


def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", facecolor="#0a0a0a")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()
    plt.close(fig)
    return encoded


def get_avg_macros(diet=None, search=None):
    df = apply_filters(load_data(), diet, search)
    if df.empty:
        return []

    avg_macros = df.groupby("Diet_type")[["Protein(g)", "Carbs(g)", "Fat(g)"]].mean()
    return avg_macros.reset_index().round(2).to_dict(orient="records")


def get_top_protein(diet=None, search=None):
    df = apply_filters(load_data(), diet, search)
    if df.empty:
        return []

    top_protein = (
        df.sort_values("Protein(g)", ascending=False)
        .groupby("Diet_type")
        .head(5)
    )

    return top_protein[
        ["Diet_type", "Recipe_name", "Protein(g)", "Carbs(g)", "Cuisine_type"]
    ].round(2).to_dict(orient="records")


def get_highest_protein_diet(diet=None, search=None):
    df = apply_filters(load_data(), diet, search)
    if df.empty:
        return {"diet_type": "No matching data", "avg_protein": 0}

    avg_macros = df.groupby("Diet_type")[["Protein(g)", "Carbs(g)", "Fat(g)"]].mean()
    highest_protein_diet = avg_macros["Protein(g)"].idxmax()

    return {
        "diet_type": highest_protein_diet,
        "avg_protein": round(avg_macros.loc[highest_protein_diet, "Protein(g)"], 2),
    }


def get_most_common_cuisine(diet=None, search=None):
    df = apply_filters(load_data(), diet, search)
    if df.empty:
        return []

    result = df.groupby("Diet_type")["Cuisine_type"].agg(
        lambda x: x.mode().iloc[0] if not x.mode().empty else "Unknown"
    )

    return (
        result.reset_index()
        .rename(columns={"Cuisine_type": "Most_common_cuisine"})
        .to_dict(orient="records")
    )


def get_avg_protein_bar(diet=None, search=None):
    df = apply_filters(load_data(), diet, search)
    if df.empty:
        fig, ax = plt.subplots(figsize=(8, 4))
        fig.patch.set_facecolor("#0a0a0a")
        ax.set_facecolor("#0a0a0a")
        ax.text(0.5, 0.5, "No matching data", ha="center", va="center", color="white")
        ax.axis("off")
        return fig_to_base64(fig)

    avg_macros = df.groupby("Diet_type")[["Protein(g)", "Carbs(g)", "Fat(g)"]].mean()

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        x=avg_macros.index,
        y=avg_macros["Protein(g)"],
        hue=avg_macros.index,
        legend=False,
        palette="viridis",
        ax=ax,
    )
    ax.set_title("Average Protein by Diet Type", fontsize=16, color="white")
    ax.set_ylabel("Protein (g)", color="white")
    ax.set_xlabel("Diet Type", color="white")
    ax.tick_params(colors="white")
    plt.xticks(rotation=45, color="white")
    fig.patch.set_facecolor("#0a0a0a")
    ax.set_facecolor("#0a0a0a")
    for spine in ax.spines.values():
        spine.set_color("#333")

    return fig_to_base64(fig)


def get_macros_heatmap(diet=None, search=None):
    df = apply_filters(load_data(), diet, search)
    if df.empty:
        fig, ax = plt.subplots(figsize=(8, 4))
        fig.patch.set_facecolor("#0a0a0a")
        ax.set_facecolor("#0a0a0a")
        ax.text(0.5, 0.5, "No matching data", ha="center", va="center", color="white")
        ax.axis("off")
        return fig_to_base64(fig)

    avg_macros = df.groupby("Diet_type")[["Protein(g)", "Carbs(g)", "Fat(g)"]].mean()

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(
        avg_macros,
        annot=True,
        fmt=".1f",
        cmap="coolwarm",
        ax=ax,
        linewidths=0.5,
        linecolor="#1a1a1a",
    )
    ax.set_title("Average Macronutrients by Diet Type", fontsize=16, color="white")
    ax.tick_params(colors="white")
    fig.patch.set_facecolor("#0a0a0a")
    ax.set_facecolor("#0a0a0a")

    return fig_to_base64(fig)


def get_top_protein_scatter(diet=None, search=None):
    df = apply_filters(load_data(), diet, search)
    if df.empty:
        fig, ax = plt.subplots(figsize=(8, 4))
        fig.patch.set_facecolor("#0a0a0a")
        ax.set_facecolor("#0a0a0a")
        ax.text(0.5, 0.5, "No matching data", ha="center", va="center", color="white")
        ax.axis("off")
        return fig_to_base64(fig)

    top_protein = (
        df.sort_values("Protein(g)", ascending=False)
        .groupby("Diet_type")
        .head(5)
    )

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(
        data=top_protein,
        x="Carbs(g)",
        y="Protein(g)",
        hue="Diet_type",
        style="Cuisine_type",
        s=100,
        ax=ax,
    )
    ax.set_title("Top 5 Protein-Rich Recipes per Diet", fontsize=16, color="white")
    ax.set_xlabel("Carbs (g)", color="white")
    ax.set_ylabel("Protein (g)", color="white")
    ax.tick_params(colors="white")
    ax.legend(bbox_to_anchor=(1.05, 1), loc=2, facecolor="#1a1a1a", labelcolor="white")
    fig.patch.set_facecolor("#0a0a0a")
    ax.set_facecolor("#0a0a0a")
    for spine in ax.spines.values():
        spine.set_color("#333")

    return fig_to_base64(fig)


def get_recipe_distribution_pie(diet=None, search=None):
    df = apply_filters(load_data(), diet, search)
    if df.empty:
        fig, ax = plt.subplots(figsize=(8, 4))
        fig.patch.set_facecolor("#0a0a0a")
        ax.set_facecolor("#0a0a0a")
        ax.text(0.5, 0.5, "No matching data", ha="center", va="center", color="white")
        ax.axis("off")
        return fig_to_base64(fig)

    distribution = df["Diet_type"].value_counts()

    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(
        distribution.values,
        labels=distribution.index,
        autopct="%1.1f%%",
        colors=sns.color_palette("viridis", len(distribution)),
        startangle=140,
        wedgeprops={"linewidth": 1.5, "edgecolor": "#0a0a0a"},
    )

    for text in texts:
        text.set_color("white")
        text.set_fontsize(12)

    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_fontsize(10)

    ax.set_title("Recipe Distribution by Diet Type", fontsize=16, color="white", pad=20)
    fig.patch.set_facecolor("#0a0a0a")
    ax.set_facecolor("#0a0a0a")

    return fig_to_base64(fig)

def get_recipes(diet=None, search=None, limit=20):
    df = apply_filters(load_data(), diet, search)

    if df.empty:
        return []

    recipes = df[
        ["Diet_type", "Recipe_name", "Cuisine_type", "Protein(g)", "Carbs(g)", "Fat(g)"]
    ].copy()

    return recipes.head(limit).round(2).to_dict(orient="records")