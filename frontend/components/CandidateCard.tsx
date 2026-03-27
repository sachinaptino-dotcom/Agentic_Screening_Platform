"use client";

import { Candidate } from "../lib/api";

type Props = {
  candidate: Candidate;
  expanded: boolean;
  onToggle: () => void;
};

export default function CandidateCard({ candidate, expanded, onToggle }: Props) {
  const atsScore = Math.max(0, Math.min(100, candidate.ats_score));
  const scoreBarWidth = `${atsScore}%`;

  const authenticityBadge =
    candidate.authenticity_flag === "pass"
      ? { label: "✓ Authentic", cls: "bg-green-50 text-green-700 border-green-200" }
      : candidate.authenticity_flag === "fail"
        ? { label: "⚠ Authenticity Risk", cls: "bg-red-50 text-red-700 border-red-200" }
        : { label: "No LinkedIn", cls: "bg-gray-50 text-gray-600 border-gray-200" };

  const linkedInBadge =
    candidate.linkedin_flag === "green"
      ? { label: "✓ LinkedIn Verified", cls: "bg-green-50 text-green-700 border-green-200" }
      : candidate.linkedin_flag === "red"
        ? { label: "⚠ LinkedIn Mismatch", cls: "bg-red-50 text-red-700 border-red-200" }
        : { label: "No LinkedIn", cls: "bg-gray-50 text-gray-600 border-gray-200" };

  return (
    <div className="rounded-xl border bg-white shadow-sm">
      <button onClick={onToggle} className="w-full p-4 text-left">
        <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
          <div className="min-w-0">
            <div className="flex items-center gap-3">
              <span className="inline-flex items-center rounded border bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700">
                Rank #{candidate.rank}
              </span>
              <div className="font-semibold truncate">{candidate.name}</div>
            </div>
            <div className="mt-1 text-sm text-gray-600">
              {candidate.email ? candidate.email : "No email"} {candidate.location ? `· ${candidate.location}` : ""}
            </div>
            <div className="mt-1 text-sm text-gray-800">
              <span className="font-medium text-gray-700">Job Profile:</span>{" "}
              <span className="text-gray-800">{candidate.job_title || "—"}</span>
            </div>
            <div className="mt-3">
              <div className="text-xs font-medium text-gray-700">ATS Score (out of 100)</div>
              <div className="mt-1 h-2 w-full rounded bg-gray-100">
                <div className="h-2 rounded bg-blue-600" style={{ width: scoreBarWidth }} />
              </div>
              <div className="mt-1 text-sm font-semibold">{atsScore}/100</div>
            </div>
          </div>

          <div className="flex flex-wrap gap-2 md:justify-end">
            <span className={`rounded-full border px-3 py-1 text-xs ${authenticityBadge.cls}`}>
              {authenticityBadge.label}
            </span>
            <span className={`rounded-full border px-3 py-1 text-xs ${linkedInBadge.cls}`}>
              {linkedInBadge.label}
            </span>
            <span className="rounded-full border bg-white px-3 py-1 text-xs text-gray-600">
              {expanded ? "Hide" : "View"}
            </span>
          </div>
        </div>
      </button>

      {expanded && (
        <div className="border-t p-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-3">
              <div>
                <div className="text-xs font-medium uppercase tracking-wide text-gray-500">
                  Job Profile / Applied Role
                </div>
                <div className="mt-1 text-sm font-semibold">{candidate.job_title || "—"}</div>
              </div>

              <div>
                <div className="text-xs font-medium uppercase tracking-wide text-gray-500">Skill Matched</div>
                <div className="mt-2 flex flex-wrap gap-2">
                  {(candidate.skills_matched || []).length ? (
                    candidate.skills_matched.map((s) => (
                      <span key={s} className="rounded-full bg-blue-50 px-3 py-1 text-xs text-blue-700">
                        {s}
                      </span>
                    ))
                  ) : (
                    <span className="text-sm text-gray-600">None</span>
                  )}
                </div>
              </div>

              <div>
                <div className="text-xs font-medium uppercase tracking-wide text-gray-500">
                  Skill Missmatched
                </div>
                <div className="mt-2 flex flex-wrap gap-2">
                  {(candidate.skills_not_matched || []).length ? (
                    candidate.skills_not_matched.map((s) => (
                      <span key={s} className="rounded-full bg-amber-50 px-3 py-1 text-xs text-amber-700">
                        {s}
                      </span>
                    ))
                  ) : (
                    <span className="text-sm text-gray-600">None</span>
                  )}
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <div>
                <div className="text-xs font-medium uppercase tracking-wide text-gray-500">Main Summary</div>
                <div className="mt-2 whitespace-pre-wrap text-sm text-gray-800">{candidate.main_summary || "—"}</div>
              </div>

              <div>
                <div className="text-xs font-medium uppercase tracking-wide text-gray-500">
                  LinkedIn Summary
                </div>
                <div className="mt-2 whitespace-pre-wrap text-sm text-gray-800">
                  {candidate.linkedin_summary || "—"}
                </div>
              </div>

              {candidate.authenticity_flag === "fail" && candidate.authenticity_notes && (
                <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                  <div className="font-semibold">Authenticity notes</div>
                  <div className="mt-1">{candidate.authenticity_notes}</div>
                </div>
              )}
            </div>
          </div>

          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <div className="rounded-lg border bg-white p-3">
              <div className="text-xs font-medium uppercase tracking-wide text-gray-500">PROS</div>
              <div className="mt-2 space-y-1">
                {(candidate.pros || []).length ? (
                  candidate.pros.map((p, i) => (
                    <div key={`${p}-${i}`} className="text-sm text-green-700">
                      - {p}
                    </div>
                  ))
                ) : (
                  <div className="text-sm text-gray-600">—</div>
                )}
              </div>
            </div>
            <div className="rounded-lg border bg-white p-3">
              <div className="text-xs font-medium uppercase tracking-wide text-gray-500">CONS</div>
              <div className="mt-2 space-y-1">
                {(candidate.cons || []).length ? (
                  candidate.cons.map((p, i) => (
                    <div key={`${p}-${i}`} className="text-sm text-amber-700">
                      - {p}
                    </div>
                  ))
                ) : (
                  <div className="text-sm text-gray-600">—</div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
