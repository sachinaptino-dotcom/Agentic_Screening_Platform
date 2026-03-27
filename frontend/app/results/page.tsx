"use client";

import { useState } from "react";

import AuthGuard from "../../components/AuthGuard";
import CandidateCard from "../../components/CandidateCard";
import { useAuth } from "../../components/AuthProvider";
import { Candidate, apiPostForm } from "../../lib/api";


export default function ResultsPage() {
  const { token } = useAuth();
  const [jdFile, setJdFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<Candidate[]>([]);
  const [openIndex, setOpenIndex] = useState(0);

  async function runPipeline() {
    if (!jdFile || !token) return;
    const fd = new FormData();
    fd.append("file", jdFile);
    setLoading(true);
    try {
      const res = await apiPostForm("/jobs/run", fd, token);
      setResults(res.ranked_profiles || []);
      setOpenIndex(0);
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthGuard>
      <main className="mx-auto mt-8 max-w-6xl space-y-6 p-4">
        <section className="rounded-xl border bg-white p-4">
          <h1 className="mb-3 text-xl font-semibold">JD Upload</h1>
          <input type="file" accept="application/pdf" onChange={(e) => setJdFile(e.target.files?.[0] || null)} />
          <button disabled={!jdFile || loading} onClick={runPipeline} className="ml-3 rounded bg-blue-600 px-4 py-2 text-white disabled:opacity-60">
            {loading ? "Running pipeline... this takes 20-40 seconds." : "Run ATS Pipeline"}
          </button>
        </section>
        <section className="space-y-3">
          {results.map((candidate, index) => (
            <CandidateCard
              key={`${candidate.name}-${index}`}
              candidate={candidate}
              expanded={openIndex === index}
              onToggle={() => setOpenIndex(index)}
            />
          ))}
        </section>
      </main>
    </AuthGuard>
  );
}
