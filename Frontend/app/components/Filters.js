/* eslint-disable @next/next/no-img-element */
"use client";
import { useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://40.76.254.32:8000";

export default function Filters() {
  const [diet, setDiet] = useState("All Diet Types");
  const [search, setSearch] = useState("");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const buildQuery = (limit = 20) => {
    const params = new URLSearchParams();
    if (search.trim()) params.set("search", search.trim());
    if (diet !== "All Diet Types") params.set("diet", diet);
    params.set("limit", String(limit));
    const qs = params.toString();
    return qs ? `?${qs}` : "";
  };

  const handleGetInsights = () => {
    setLoading(true);
    setResults(null);
    fetch(`${API_URL}/api/data/nutritional-insights${buildQuery(20)}`)
      .then((res) => res.json())
      .then((json) => {
        setResults({ type: "insights", data: json.data || [] });
        setLoading(false);
      })
      .catch(() => {
        setResults({ type: "error" });
        setLoading(false);
      });
  };

  const handleGetRecipes = () => {
    setLoading(true);
    setResults(null);
    fetch(`${API_URL}/api/data/recipes${buildQuery(20)}`)
      .then((res) => res.json())
      .then((json) => {
        setResults({ type: "recipes", data: json.data || [] });
        setLoading(false);
      })
      .catch(() => {
        setResults({ type: "error" });
        setLoading(false);
      });
  };

  const handleGetClusters = () => {
    setLoading(true);
    setResults(null);
    fetch(`${API_URL}/api/data/clusters${buildQuery(50)}`)
      .then((res) => res.json())
      .then((json) => {
        setResults({ type: "clusters", data: json.data || {} });
        setLoading(false);
      })
      .catch(() => {
        setResults({ type: "error" });
        setLoading(false);
      });
  };

  return (
    <section className="my-6 space-y-4">
      <h2 className="text-2xl font-semibold mt-5 mb-4">
        Filters and Data Interaction
      </h2>

      <div className="flex flex-col sm:flex-row sm:items-center gap-4">
        <input
          type="text"
          placeholder="Search by Diet Type"
          className="w-full rounded border border-gray-300 bg-white p-2 text-gray-900 placeholder:text-gray-500 sm:w-auto dark:border-gray-700 dark:bg-gray-900 dark:text-gray-100 dark:placeholder:text-gray-400"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />

        <select
          value={diet}
          onChange={(e) => setDiet(e.target.value)}
          className="rounded border border-gray-300 bg-white px-4 py-3 text-gray-900 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-100"
        >
          <option>All Diet Types</option>
          <option>Paleo</option>
          <option>Keto</option>
          <option>Vegan</option>
          <option>Mediterranean</option>
          <option>Dash</option>
        </select>
      </div>

      <h2 className="text-2xl font-semibold mt-5 mb-4">API Data Interaction</h2>

      <div className="flex gap-4 flex-wrap">
        <button
          onClick={handleGetInsights}
          className="bg-blue-600 text-white px-4 py-2 rounded"
        >
          Get Nutritional Insights
        </button>

        <button
          onClick={handleGetRecipes}
          className="bg-green-600 text-white px-4 py-2 rounded"
        >
          Get Recipes
        </button>

        <button
          onClick={handleGetClusters}
          className="bg-purple-600 text-white px-4 py-2 rounded"
        >
          Get Clusters
        </button>
      </div>

      {loading && (
        <p className="mt-4 text-gray-500 dark:text-gray-400">Loading...</p>
      )}

      {results?.type === "error" && (
        <p className="text-red-500 mt-4">Failed to fetch. Is the backend running?</p>
      )}

      {results?.type === "insights" && (
        <div className="mt-4 rounded-lg bg-white p-4 text-gray-900 shadow dark:bg-gray-900 dark:text-gray-100 max-h-[500px] overflow-auto">
          <h3 className="mb-2 text-lg font-semibold">Nutritional Insights</h3>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200 text-left dark:border-gray-700">
                <th className="py-2">Diet Type</th>
                <th className="py-2">Recipe Name</th>
                <th className="py-2">Cuisine</th>
                <th className="py-2">Protein</th>
                <th className="py-2">Carbs</th>
                <th className="py-2">Fat</th>
              </tr>
            </thead>
            <tbody>
              {results.data.length > 0 ? (
                results.data.map((row, i) => (
                  <tr key={i} className="border-b border-gray-200 dark:border-gray-700">
                    <td className="py-2">{row.Diet_type}</td>
                    <td className="py-2">{row.Recipe_name}</td>
                    <td className="py-2">{row.Cuisine_type}</td>
                    <td className="py-2">{row["Protein(g)"]}</td>
                    <td className="py-2">{row["Carbs(g)"]}</td>
                    <td className="py-2">{row["Fat(g)"]}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="py-4 text-center text-gray-500 dark:text-gray-400">
                    No nutritional insights found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {results?.type === "recipes" && (
        <div className="mt-4 rounded-lg bg-white p-4 text-gray-900 shadow dark:bg-gray-900 dark:text-gray-100 max-h-[500px] overflow-auto">
          <h3 className="mb-2 text-lg font-semibold">Recipes</h3>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200 text-left dark:border-gray-700">
                <th className="py-2">Diet Type</th>
                <th className="py-2">Recipe Name</th>
                <th className="py-2">Cuisine</th>
              </tr>
            </thead>
            <tbody>
              {results.data.length > 0 ? (
                results.data.map((row, i) => (
                  <tr key={i} className="border-b border-gray-200 dark:border-gray-700">
                    <td className="py-2">{row.Diet_type}</td>
                    <td className="py-2">{row.Recipe_name}</td>
                    <td className="py-2">{row.Cuisine_type}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={3} className="py-4 text-center text-gray-500 dark:text-gray-400">
                    No recipes found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {results?.type === "clusters" && (
        <div className="mt-4 rounded-lg bg-white p-4 text-gray-900 shadow dark:bg-gray-900 dark:text-gray-100 max-h-[500px] overflow-auto">
          <h3 className="mb-4 text-lg font-semibold">Recipe Classification by Category</h3>

          {Object.keys(results.data).length > 0 ? (
            Object.entries(results.data).map(([category, items]) => (
              <div key={category} className="mb-6">
                <h4 className="font-semibold text-base mb-2 capitalize">
                  Category: {category}
                </h4>
                <ul className="list-disc pl-6 space-y-1">
                  {items.map((item, index) => (
                    <li key={index}>
                      {item.Recipe_name} ({item.Cuisine_type})
                    </li>
                  ))}
                </ul>
              </div>
            ))
          ) : (
            <p className="text-gray-500 dark:text-gray-400">No clusters found.</p>
          )}
        </div>
      )}
    </section>
  );
}