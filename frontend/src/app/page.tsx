import Header from "@/src/components/Header";
import Footer from "@/src/components/Footer";
import HealthBot from "@/src/components/HealthBot";

export default function Home() {
  return (
    <div className="min-h-screen bg-slate-50">
      <Header />

      <main className="mx-auto max-w-6xl px-6 py-10">
        <div className="mx-auto max-w-3xl">
          <div className="mb-10 text-center">
            <p className="mb-3 text-sm font-semibold uppercase tracking-wider text-slate-500">
              AI-powered health education
            </p>

            <h1 className="text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
              Understand your health,
              <br />
              one topic at a time.
            </h1>

            <p className="mx-auto mt-5 max-w-2xl text-lg leading-8 text-slate-600">
              HealthBot researches health information,
              explains it in simple language, and checks
              your understanding with a short quiz.
            </p>
          </div>

          <HealthBot />
        </div>
      </main>

      <Footer />
    </div>
  );
}