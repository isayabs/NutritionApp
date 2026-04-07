import Header from "./components/Header";
import VisualizationCards from "./components/VisualizationCards";
import Filters from "./components/Filters";
import Pagination from "./components/Pagination";
import Footer from "./components/Footer";
import SecurityCompliance from "./components/SecurityCompliance";
import OAuth2FA from "./components/OAuth2FA";
import CloudCleanup from "./components/CloudCleanup";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col bg-gray-100 text-gray-900">
      <Header />

      <main className="flex-1 w-full px-12 py-6">
        <h2 className="text-2xl font-semibold mb-4">
          Explore Nutritional Insights
        </h2>

        <VisualizationCards />

        <div className="mt-6">
          <Filters />
        </div>

        <SecurityCompliance />
        <OAuth2FA />
        <CloudCleanup />

        <section className="mt-6">
          <h2 className="text-2xl font-semibold mb-4">Pagination</h2>
          <Pagination />
        </section>
      </main>

      <Footer />
    </div>
  );
}