export default function SecurityCompliance() {
  return (
    <section className="mt-8">
      <h2 className="text-2xl font-semibold mb-4">Security & Compliance</h2>

      <div className="bg-white rounded-lg shadow p-4">
        <p className="font-semibold">Security Status</p>
        <p>
          Encryption: <span className="text-green-600">Enabled</span>
        </p>
        <p>Access Control: <span className="text-green-600">Secure</span></p>
        <p>
          Compliance: <span className="text-green-600">GDPR Compliant</span>
        </p>
      </div>
    </section>
  );
}