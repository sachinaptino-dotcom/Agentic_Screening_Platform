"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import AuthGuard from "../../components/AuthGuard";
import { useAuth } from "../../components/AuthProvider";
import { apiPostForm } from "../../lib/api";


type UploadResult = { name: string; message: string; extra?: string };

export default function UploadPage() {
  const router = useRouter();
  const { token } = useAuth();
  const [resumeResults, setResumeResults] = useState<UploadResult[]>([]);
  const [linkedinResults, setLinkedinResults] = useState<UploadResult[]>([]);

  async function uploadMany(files: FileList | null, endpoint: string, target: "resume" | "linkedin") {
    if (!files || !token) return;
    for (const file of Array.from(files)) {
      const fd = new FormData();
      fd.append("file", file);
      const res = await apiPostForm(endpoint, fd, token);
      if (target === "resume") {
        setResumeResults((prev) => [...prev, { name: file.name, message: "✓ Uploaded", extra: `${res.candidate_name} | ${res.skills_found?.join(", ") || ""}` }]);
      } else {
        setLinkedinResults((prev) => [...prev, { name: file.name, message: "✓ Uploaded", extra: res.candidate_name }]);
      }
    }
  }

  return (
    <AuthGuard>
      <main className="mx-auto mt-8 max-w-6xl space-y-6 p-4">
        <h1 className="text-2xl font-semibold">Upload Resumes and LinkedIn PDFs</h1>
        <div className="grid gap-6 md:grid-cols-2">
          <section className="rounded-xl border bg-white p-4">
            <h2 className="mb-2 text-lg font-medium">Resume Upload</h2>
            <input type="file" accept="application/pdf" multiple onChange={(e) => uploadMany(e.target.files, "/upload/resume", "resume")} />
            <div className="mt-3 space-y-2">
              {resumeResults.map((r, i) => (
                <div key={`${r.name}-${i}`} className="rounded border p-2 text-sm">
                  <div>{r.name} <span className="text-green-700">{r.message}</span></div>
                  <div className="text-gray-600">{r.extra}</div>
                </div>
              ))}
            </div>
          </section>
          <section className="rounded-xl border bg-white p-4">
            <h2 className="mb-2 text-lg font-medium">LinkedIn Upload</h2>
            <input type="file" accept="application/pdf" multiple onChange={(e) => uploadMany(e.target.files, "/upload/linkedin", "linkedin")} />
            <p className="mt-2 text-sm text-gray-600">Match LinkedIn by candidate name - upload must be same person's profile.</p>
            <div className="mt-3 space-y-2">
              {linkedinResults.map((r, i) => (
                <div key={`${r.name}-${i}`} className="rounded border p-2 text-sm">
                  <div>{r.name} <span className="text-green-700">{r.message}</span></div>
                  <div className="text-gray-600">{r.extra}</div>
                </div>
              ))}
            </div>
          </section>
        </div>
        <button className="rounded bg-blue-600 px-4 py-2 text-white" onClick={() => router.push("/results")}>
          All done - Run ATS
        </button>
      </main>
    </AuthGuard>
  );
}
