"use client";

import { useState, useEffect } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function CloudCleanup() {
  const [resourceGroups, setResourceGroups] = useState([]);
  const [selectedGroup, setSelectedGroup] = useState("");
  const [resources, setResources] = useState([]);
  const [loadingGroups, setLoadingGroups] = useState(true);
  const [loadingResources, setLoadingResources] = useState(false);
  const [cleaning, setCleaning] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [showConfirm, setShowConfirm] = useState(false);

  // Load resource groups on mount
  useEffect(() => {
    fetch(`${API}/api/cloud/resource-groups`)
      .then((res) => res.json())
      .then((data) => {
        setResourceGroups(data.resource_groups || []);
        setLoadingGroups(false);
      })
      .catch(() => {
        setError("Could not load resource groups");
        setLoadingGroups(false);
      });
  }, []);

  // Load resources when a group is selected
  useEffect(() => {
    if (!selectedGroup) {
      setResources([]);
      return;
    }
    setLoadingResources(true);
    setResult(null);
    setError(null);
    fetch(`${API}/api/cloud/resources/${selectedGroup}`)
      .then((res) => res.json())
      .then((data) => {
        setResources(data.resources || []);
        setLoadingResources(false);
      })
      .catch(() => {
        setError("Could not load resources");
        setLoadingResources(false);
      });
  }, [selectedGroup]);

  const handleCleanup = async () => {
    setShowConfirm(false);
    setCleaning(true);
    setResult(null);
    setError(null);
    try {
      const res = await fetch(`${API}/api/cloud/cleanup/${selectedGroup}`, {
        method: "DELETE",
      });
      const data = await res.json();
      setResult(data);
      setResources([]); // clear list after cleanup
    } catch {
      setError("Cleanup request failed");
    } finally {
      setCleaning(false);
    }
  };

  return (
    <section className="mt-8">
      <h2 className="text-2xl font-semibold mb-4">Cloud Resource Cleanup</h2>

      <div className="bg-white rounded-lg shadow p-4 dark:bg-gray-900 dark:text-gray-100">
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
          Ensure that cloud resources are efficiently managed and cleaned up
          post-deployment.
        </p>

        {/* Dropdown */}
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">
            Select Resource Group
          </label>
          {loadingGroups ? (
            <p className="text-sm text-gray-500">Loading resource groups...</p>
          ) : (
            <select
              className="border border-gray-300 rounded px-3 py-2 w-full dark:bg-gray-800 dark:border-gray-600"
              value={selectedGroup}
              onChange={(e) => setSelectedGroup(e.target.value)}
            >
              <option value="">-- Select a resource group --</option>
              {resourceGroups.map((g) => (
                <option key={g.name} value={g.name}>
                  {g.name} ({g.location})
                </option>
              ))}
            </select>
          )}
        </div>

        {/* Resource List */}
        {selectedGroup && (
          <div className="mb-4">
            <h3 className="text-sm font-medium mb-2">
              Resources in{" "}
              <span className="font-semibold">{selectedGroup}</span>
            </h3>
            {loadingResources ? (
              <p className="text-sm text-gray-500">Loading resources...</p>
            ) : resources.length === 0 ? (
              <p className="text-sm text-gray-500">No resources found.</p>
            ) : (
              <ul className="border border-gray-200 rounded divide-y dark:border-gray-700">
                {resources.map((r, i) => (
                  <li key={i} className="px-3 py-2 text-sm flex justify-between">
                    <span className="font-medium">{r.name}</span>
                    <span className="text-gray-500 text-xs">{r.type.split("/").pop()}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}

        {/* Confirm Dialog */}
        {showConfirm && (
          <div className="mb-4 border border-red-300 bg-red-50 rounded p-3 dark:bg-red-950 dark:border-red-700">
            <p className="text-sm text-red-700 dark:text-red-300 mb-2">
              Are you sure? This will delete all {resources.length} resource(s)
              in <strong>{selectedGroup}</strong>. This cannot be undone.
            </p>
            <div className="flex gap-2">
              <button
                onClick={handleCleanup}
                className="bg-red-500 text-white px-3 py-1 rounded text-sm"
              >
                Yes, delete all
              </button>
              <button
                onClick={() => setShowConfirm(false)}
                className="bg-gray-200 text-gray-800 px-3 py-1 rounded text-sm"
              >
                Cancel
              </button>
            </div>
          </div>
        )}

        {/* Result */}
        {result && (
          <div className={`mb-4 rounded p-3 text-sm ${result.status === "success" ? "bg-green-50 text-green-700 border border-green-300" : "bg-yellow-50 text-yellow-700 border border-yellow-300"}`}>
            <p className="font-medium">{result.message}</p>
            {result.cleaned?.length > 0 && (
              <ul className="mt-1 list-disc list-inside">
                {result.cleaned.map((r, i) => (
                  <li key={i}>{r.name} — {r.status}</li>
                ))}
              </ul>
            )}
            {result.errors?.length > 0 && (
              <ul className="mt-1 list-disc list-inside text-red-600">
                {result.errors.map((r, i) => (
                  <li key={i}>{r.name} — {r.error}</li>
                ))}
              </ul>
            )}
          </div>
        )}

        {error && (
          <div className="mb-4 rounded p-3 text-sm bg-red-50 text-red-700 border border-red-300">
            {error}
          </div>
        )}

        {/* Clean Up Button */}
        <button
          onClick={() => setShowConfirm(true)}
          disabled={!selectedGroup || cleaning || resources.length === 0}
          className="bg-red-500 text-white px-4 py-2 rounded disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {cleaning ? "Cleaning..." : "Clean Up Resources"}
        </button>
      </div>
    </section>
  );
}
