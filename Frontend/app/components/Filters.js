/* eslint-disable @next/next/no-img-element */
"use client";
import { useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export default function Filters() {
  const [diet, setDiet] = useState("All Diet Types");
  const [search, setSearch] = useState("");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const buildQuery = () => {
    const params = new URLSearchParams();
    if (search.trim()) params.set("search", search.trim());
    if (diet !== "All Diet Types") params.set("diet", diet);
    const qs = params.toString();
    return qs ? `?${qs}` : "";
  };

  const handleGetInsights = () => {
    setLoading(true);
    setResults(null);
    fetch(`${API_URL}/api/data/highest-protein-diet${buildQuery()}`)
      .then(res => res.json())
      .then(json => {
        setResults({ type: "insights", data: json.data });
        setLoading(false);
      })
      .catch(() => { setResults({ type: "error" }); setLoading(false); });
  };

  const handleGetRecipes = () => {
    setLoading(true);
    setResults(null);
    fetch(`${API_URL}/api/data/most-common-cuisine${buildQuery()}`)
      .then(res => res.json())
      .then(json => {
        setResults({ type: "recipes", data: json.data });
        setLoading(false);
      })
      .catch(() => { setResults({ type: "error" }); setLoading(false); });
  };

  const handleGetClusters = () => {
    setLoading(true);
    setResults(null);
    fetch(`${API_URL}/api/chart/recipe-distribution${buildQuery()}`)
      .then(res => res.json())
      .then(json => {
        setResults({ type: "clusters", image: json.image });
        setLoading(false);
      })
      .catch(() => { setResults({ type: "error" }); setLoading(false); });
  };

  const filteredRecipes = results?.type === "recipes"
    ? results.data.filter(row => {
        const term = search.trim().toLowerCase();
        const matchesDiet = diet === "All Diet Types" || row.Diet_type?.toLowerCase() === diet.toLowerCase();
        const matchesSearch = !term ||
          row.Diet_type?.toLowerCase().includes(term) ||
          row.Most_common_cuisine?.toLowerCase().includes(term);
        return matchesDiet && matchesSearch;
      })
    : [];

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
          onKeyDown={(e) => { if (e.key === "Enter" && results) handleGetRecipes(); }}
        />
        <select
          value={diet}
          onChange={(e) => setDiet(e.target.value)}
          className="rounded border border-gray-300 bg-white px-4 py-3 text-gray-900 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-100"
        >
          <option>All Diet Types</option>
          <option>Vegan</option>
          <option>Keto</option>
        </select>
      </div>

      <h2 className="text-2xl font-semibold mt-5 mb-4">API Data Interaction</h2>
      <div className="flex gap-4">
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

      {/* Results display */}
      {loading && <p className="mt-4 text-gray-500 dark:text-gray-400">Loading...</p>}

      {results?.type === "error" && (
        <p className="text-red-500 mt-4">⚠ Failed to fetch. Is the backend running?</p>
      )}

      {results?.type === "insights" && (
        <div className="mt-4 rounded-lg bg-white p-4 text-gray-900 shadow dark:bg-gray-900 dark:text-gray-100">
          <h3 className="mb-2 text-lg font-semibold">Nutritional Insights</h3>
          <p className="text-gray-700 dark:text-gray-300">Highest protein diet: <strong>{results.data.diet_type}</strong></p>
          <p className="text-gray-700 dark:text-gray-300">Average protein: <strong>{results.data.avg_protein}g</strong></p>
        </div>
      )}

      {results?.type === "recipes" && (
        <div className="mt-4 rounded-lg bg-white p-4 text-gray-900 shadow dark:bg-gray-900 dark:text-gray-100">
          <h3 className="mb-2 text-lg font-semibold">Most Common Cuisine per Diet</h3>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200 text-left dark:border-gray-700">
                <th className="py-2">Diet Type</th>
                <th className="py-2">Most Common Cuisine</th>
              </tr>
            </thead>
            <tbody>
              {filteredRecipes.length > 0 ? (
                filteredRecipes.map((row, i) => (
                  <tr key={i} className="border-b border-gray-200 dark:border-gray-700">
                    <td className="py-2">{row.Diet_type}</td>
                    <td className="py-2">{row.Most_common_cuisine}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={2} className="py-4 text-center text-gray-500 dark:text-gray-400">
                    No results match your search.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {results?.type === "clusters" && (
        <div className="mt-4 rounded-lg bg-white p-4 text-gray-900 shadow dark:bg-gray-900 dark:text-gray-100">
          <h3 className="mb-2 text-lg font-semibold">Recipe Distribution</h3>
          <img
            src={`data:image/png;base64,${results.image}`}
            alt="Recipe Distribution"
            className="w-full rounded"
          />
        </div>
      )}
    </section>
  );
}