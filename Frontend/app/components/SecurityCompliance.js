"use client";
import { useEffect, useState } from "react";

const StatusBadge = ({ status, message }) => {
  const colors = {
    secure: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
    warning:
      "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300",
    error: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
  };

  const dots = {
    secure: "bg-green-500",
    warning: "bg-yellow-500",
    error: "bg-red-500",
  };

  return (
    <span
      className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium ${colors[status]}`}
    >
      <span className={`w-2 h-2 rounded-full ${dots[status]}`} />
      {message}
    </span>
  );
};

export default function SecurityCompliance() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastRefresh, setLastRefresh] = useState(null);

  const fetchStatus = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/security/status");
      const json = await res.json();
      setData(json);
      setLastRefresh(new Date().toLocaleTimeString());
    } catch (err) {
      setError("Failed to reach backend");
    } finally {
      setLoading(false);
    }
  };

  // Fetch on mount and every 30 seconds
  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <section className="mt-8">
      <h2 className="text-2xl font-semibold mb-4">Security & Compliance</h2>

      <div className="bg-white dark:bg-gray-900 rounded-lg shadow p-6">
        {/* Header */}
        <div className="flex justify-between items-center mb-4">
          <p className="font-semibold text-gray-700 dark:text-gray-300">
            Live Security Status
          </p>
          <button
            onClick={fetchStatus}
            disabled={loading}
            className="text-sm bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 px-3 py-1 rounded disabled:opacity-50"
          >
            {loading ? "Checking..." : "🔄 Refresh"}
          </button>
        </div>

        {/* Error */}
        {error && <p className="text-red-500 text-sm mb-4">⚠ {error}</p>}

        {/* Status Grid */}
        {data && (
          <div className="space-y-4">
            <div className="flex justify-between items-center border-b dark:border-gray-700 pb-3">
              <span className="text-gray-600 dark:text-gray-400">
                Encryption
              </span>
              <StatusBadge {...data.encryption} />
            </div>
            <div className="flex justify-between items-center border-b dark:border-gray-700 pb-3">
              <span className="text-gray-600 dark:text-gray-400">
                Access Control
              </span>
              <StatusBadge {...data.access_control} />
            </div>
            <div className="flex justify-between items-center border-b dark:border-gray-700 pb-3">
              <span className="text-gray-600 dark:text-gray-400">
                Compliance
              </span>
              <StatusBadge {...data.compliance} />
            </div>
            <div className="flex justify-between items-center pb-3">
              <span className="text-gray-600 dark:text-gray-400">
                Server Uptime
              </span>
              <StatusBadge {...data.uptime} />
            </div>

            {/* Last checked */}
            <p className="text-xs text-gray-400 text-right">
              Last checked: {lastRefresh} · Auto-refreshes every 30s
            </p>
          </div>
        )}

        {/* Loading skeleton */}
        {loading && !data && (
          <div className="space-y-4 animate-pulse">
            {[...Array(4)].map((_, i) => (
              <div
                key={i}
                className="flex justify-between items-center border-b dark:border-gray-700 pb-3"
              >
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-32" />
                <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-24" />
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}