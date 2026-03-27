from langgraph.graph import END, START, StateGraph

from agents.nodes import node_ats_scorer, node_authenticity, node_jd_parser, node_profile, node_ranker, node_retrieval
from agents.state import CandidateResult, GraphState


def _build_graph():
    graph = StateGraph(GraphState)
    graph.add_node("node_jd_parser", node_jd_parser.run)
    graph.add_node("node_retrieval", node_retrieval.run)
    graph.add_node("node_ats_scorer", node_ats_scorer.run)
    graph.add_node("node_authenticity", node_authenticity.run)
    graph.add_node("node_profile", node_profile.run)
    graph.add_node("node_ranker", node_ranker.run)

    graph.add_edge(START, "node_jd_parser")
    graph.add_edge("node_jd_parser", "node_retrieval")
    graph.add_edge("node_retrieval", "node_ats_scorer")
    graph.add_edge("node_retrieval", "node_authenticity")
    graph.add_edge("node_ats_scorer", "node_profile")
    graph.add_edge("node_authenticity", "node_profile")
    graph.add_edge("node_profile", "node_ranker")
    graph.add_edge("node_ranker", END)
    return graph.compile()


compiled_graph = _build_graph()


def run_pipeline(jd_text: str, recruiter_id: str) -> list[CandidateResult]:
    final_state = compiled_graph.invoke({"jd_text": jd_text, "recruiter_id": recruiter_id})
    return final_state.get("ranked_profiles", [])
