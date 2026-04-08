export default function CloudCleanup() {
  return (
    <section className="mt-8">
      <h2 className="text-2xl font-semibold mb-4">Cloud Resource Cleanup</h2>

      <div className="bg-white rounded-lg shadow p-4  dark:bg-gray-900 dark:text-gray-100">
        <p className="text-sm text-gray-600 mb-3">
          Ensure that cloud resources are efficiently managed and cleaned up
          post-deployment.
        </p>

        <button className="bg-red-500 text-white px-4 py-2 rounded">
          Clean Up Resources
        </button>
      </div>
    </section>
  );
}