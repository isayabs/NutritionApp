export default function OAuth2FA() {
  return (
    <section className="mt-8">
      <h2 className="text-2xl font-semibold mb-4">OAuth & 2FA Integration</h2>

      <div className="bg-white rounded-lg shadow p-4">
        <p className="font-semibold mb-3">Secure Login</p>

        <div className="flex gap-3 flex-wrap mb-4">
          <button className="bg-blue-600 text-white px-4 py-2 rounded">
            Login with Google
          </button>
          <button className="bg-blue-600 text-white px-4 py-2 rounded">
            Login with GitHub
          </button>
        </div>

        <label className="block text-sm font-medium mb-2">Enter 2FA Code</label>
        <input
          type="text"
          placeholder="Enter your 2FA code"
          className="w-full border border-gray-300 rounded px-3 py-2"
        />
      </div>
    </section>
  );
}