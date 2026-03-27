from agents.state import CandidateResult


def run(state: dict) -> dict:
    candidates: list[CandidateResult] = state.get("candidates", []) or []
    sorted_candidates = sorted(
        candidates,
        key=lambda c: c.ats_score - (10 if c.authenticity_flag == "fail" else 0),
        reverse=True,
    )
    ranked: list[CandidateResult] = []
    for idx, candidate in enumerate(sorted_candidates, start=1):
        c = candidate.model_copy()
        c.rank = idx
        ranked.append(c)
    return {"ranked_profiles": ranked}
