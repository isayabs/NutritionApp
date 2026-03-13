import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg') # must be before pyplot for cloud deployment
import seaborn as sns
import io
import base64

# Load the dataset
def load_data():
    # Handle missing data (fill missing values with mean)
    df = pd.read_csv("All_Diets.csv")
    df['Protein(g)'] = df['Protein(g)'].fillna(df['Protein(g)'].mean())
    df['Carbs(g)'] = df['Carbs(g)'].fillna(df['Carbs(g)'].mean())
    df['Fat(g)'] = df['Fat(g)'].fillna(df['Fat(g)'].mean())
    # Add new metrics (Protein-to-Carbs ratio and Carbs-to-Fat ratio)
    df['Protein_to_Carbs_ratio'] = df['Protein(g)'] / df['Carbs(g)']
    df['Carbs_to_Fat_ratio'] = df['Carbs(g)'] / df['Fat(g)']
    return df

    print("\nMissing values handled (filled with mean).")

#Helper
def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', facecolor='#0a0a0a')
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close(fig)
    return encoded

# Calculate the average macronutrient content for each diet type
def get_avg_macros():
    df = load_data()
    avg_macros = df.groupby('Diet_type')[['Protein(g)', 'Carbs(g)', 'Fat(g)']].mean()
    return avg_macros.reset_index().round(2).to_dict(orient='records')

    print("\nAverage macronutrients by diet type:")


# Find the top 5 protein-rich recipes for each diet type
def get_top_protein():
    df = load_data()
    top_protein = df.sort_values('Protein(g)', ascending=False).groupby('Diet_type').head(5)
    return top_protein[['Diet_type', 'Recipe_name', 'Protein(g)', 'Carbs(g)', 'Cuisine_type']].round(2).to_dict(orient='records')

    print("\nTop 5 protein-rich recipes per diet:")


# Diet type with highest average protein
def get_highest_protein_diet():
    df = load_data()
    avg_macros = df.groupby('Diet_type')[['Protein(g)', 'Carbs(g)', 'Fat(g)']].mean()
    highest_protein_diet = avg_macros['Protein(g)'].idxmax()
    return {"diet_type": highest_protein_diet, "avg_protein": round(avg_macros.loc[highest_protein_diet, 'Protein(g)'], 2)}

    print(f"\nDiet type with highest average protein: {highest_protein_diet}")

# Most common cuisines per diet
def get_most_common_cuisine():
    df = load_data()
    result = df.groupby('Diet_type')['Cuisine_type'].agg(lambda x: x.value_counts().index[0])
    return result.reset_index().rename(columns={'Cuisine_type': 'Most_common_cuisine'}).to_dict(orient='records')

    print("\nMost common cuisine per diet type:")

#Chart functions
#Bar Chart
def get_avg_protein_bar():
    df = load_data()
    avg_macros = df.groupby('Diet_type')[['Protein(g)', 'Carbs(g)', 'Fat(g)']].mean()
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        x=avg_macros.index,
        y=avg_macros['Protein(g)'],
        hue=avg_macros.index,
        legend=False,
        palette='viridis',
        ax=ax
    )
    ax.set_title('Average Protein by Diet Type', fontsize=16, color='white')
    ax.set_ylabel('Protein (g)', color='white')
    ax.set_xlabel('Diet Type', color='white')
    ax.tick_params(colors='white')
    plt.xticks(rotation=45, color='white')
    fig.patch.set_facecolor('#0a0a0a')
    ax.set_facecolor('#0a0a0a')
    ax.spines[:].set_color('#333')

    return fig_to_base64(fig)

# Heatmap: Average Macronutrients by Diet Type
def get_macros_heatmap():
    df = load_data()
    avg_macros = df.groupby('Diet_type')[['Protein(g)', 'Carbs(g)', 'Fat(g)']].mean()

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(
        avg_macros,
        annot=True,
        fmt=".1f",
        cmap='coolwarm',
        ax=ax,
        linewidths=0.5,
        linecolor='#1a1a1a'
    )
    ax.set_title('Average Macronutrients by Diet Type', fontsize=16, color='white')
    ax.tick_params(colors='white')
    fig.patch.set_facecolor('#0a0a0a')
    ax.set_facecolor('#0a0a0a')

    return fig_to_base64(fig)


# Scatter plot: Top 5 protein-rich recipes per diet
def get_top_protein_scatter():
    df = load_data()
    top_protein = df.sort_values('Protein(g)', ascending=False).groupby('Diet_type').head(5)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(
        data=top_protein,
        x='Carbs(g)',
        y='Protein(g)',
        hue='Diet_type',
        style='Cuisine_type',
        s=100,
        ax=ax
    )
    ax.set_title('Top 5 Protein-Rich Recipes per Diet', fontsize=16, color='white')
    ax.set_xlabel('Carbs (g)', color='white')
    ax.set_ylabel('Protein (g)', color='white')
    ax.tick_params(colors='white')
    ax.legend(bbox_to_anchor=(1.05, 1), loc=2, facecolor='#1a1a1a', labelcolor='white')
    fig.patch.set_facecolor('#0a0a0a')
    ax.set_facecolor('#0a0a0a')
    ax.spines[:].set_color('#333')
    
    return fig_to_base64(fig)

#Pie Chart Plot
def get_recipe_distribution_pie():
    df = load_data()
    distribution = df['Diet_type'].value_counts()

    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(
        distribution.values,
        labels=distribution.index,
        autopct='%1.1f%%',
        colors=sns.color_palette('viridis', len(distribution)),
        startangle=140,
        wedgeprops={'linewidth': 1.5, 'edgecolor': '#0a0a0a'}
    )

    # Style the text
    for text in texts:
        text.set_color('white')
        text.set_fontsize(12)
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(10)

    ax.set_title('Recipe Distribution by Diet Type', fontsize=16, color='white', pad=20)
    fig.patch.set_facecolor('#0a0a0a')
    ax.set_facecolor('#0a0a0a')

    return fig_to_base64(fig)
