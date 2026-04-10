"use client";
import { useEffect, useState } from "react";

function ChartImage({ endpoint, title }) {
  const [image, setImage] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(endpoint)
      .then(res => res.json())
      .then(json => { setImage(json.image); setLoading(false); })
      .catch(() => { setError("Failed to load"); setLoading(false); });
  }, [endpoint]);

  if (loading) return <p className="text-sm text-gray-400 mt-4">Loading {title}...</p>;
  if (error) return <p className="text-sm text-red-400 mt-4">⚠ {error}</p>;

  return (
    <img
      src={`data:image/png;base64,${image}`}
      alt={title}
      className="mt-4 w-full rounded"
    />
  );
}

const cards = [
  {
    title: "Bar Chart",
    description: "Average macronutrient content by diet type.",
    endpoint: "/api/chart/protein-bar",
  },
  {
    title: "Scatter Plot",
    description: "Nutrient relationships (e.g., protein vs carbs).",
    endpoint: "/api/chart/top-protein-scatter",
  },
  {
    title: "Heatmap",
    description: "Nutrient correlations.",
    endpoint: "/api/chart/macros-heatmap",
  },
  {
    title: "Pie Chart",
    description: "Recipe distribution by diet type.",
    endpoint: "/api/chart/recipe-distribution",
  },
];

export default function VisualizationCards() {
  return (
    <section className="my-6 grid grid-cols-1 lg:grid-cols-4 md:grid-cols-2 gap-6">
      {cards.map((card) => (
        <div
          key={card.title}
          className="rounded-lg bg-white p-4 text-gray-900 shadow-lg dark:bg-gray-900 dark:text-gray-100"
        >
          <h3 className="mb-2 font-semibold">{card.title}</h3>
          <p className="text-sm text-gray-600 dark:text-gray-300">{card.description}</p>
          <ChartImage endpoint={card.endpoint} title={card.title} />
        </div>
      ))}
    </section>
  );
}