"use client";
import { useState } from "react";
export default function Pagination() {
  const [page, setPage] = useState(1);

  return (
    <div className="my-6 flex items-center justify-center gap-2">
      <button
        onClick={() => setPage((p) => Math.max(p - 1, 1))}
        className="cursor-pointer rounded bg-gray-300 px-3 py-1 text-gray-900 hover:bg-gray-400 disabled:cursor-not-allowed disabled:opacity-60 dark:bg-gray-800 dark:text-gray-100 dark:hover:bg-gray-700"
        disabled={page === 1}
      >
        Previous
      </button>
      {[1, 2].map((p) => (
        <button
          key={p}
          onClick={() => setPage(p)}
          className={`cursor-pointer rounded border border-gray-300 px-3 py-1 text-gray-900 dark:border-gray-700 dark:text-gray-100 ${page === p ? "bg-blue-600 text-white dark:bg-blue-500" : "bg-gray-300 hover:bg-gray-400 dark:bg-gray-800 dark:hover:bg-gray-700"}`}
        >
          {p}
        </button>
      ))}
      <button
        onClick={() => setPage((p) => Math.min(p + 1, 2))}
        className="cursor-pointer rounded bg-gray-300 px-3 py-1 text-gray-900 hover:bg-gray-400 disabled:cursor-not-allowed disabled:opacity-60 dark:bg-gray-800 dark:text-gray-100 dark:hover:bg-gray-700"
        disabled={page === 2}
      >
        Next
      </button>
    </div>
  );
}
