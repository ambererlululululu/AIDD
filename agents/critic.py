from __future__ import annotations
from chemistry.evaluator import evaluate_candidate, generate_radar_data, compute_properties
from chemistry.molecules import OSIMERTINIB
from agents.prompts import CRITIC_SYSTEM, CRITIC_ROUND


class ADMETCritic:
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.history = []
        self._ref_props = compute_properties(OSIMERTINIB["smiles"])

    def _llm_summary(self, evaluations: list[dict], feedback: dict,
                     round_number: int) -> str:
        passed = [e for e in evaluations if e["verdict"] == "PASS"]
        failed = [e for e in evaluations if e["verdict"] == "FAIL"]
        conditional = [e for e in evaluations if e["verdict"] == "CONDITIONAL"]

        best = max(evaluations, key=lambda x: x.get("score", 0)) if evaluations else None

        user_msg = CRITIC_ROUND.format(
            round_number=round_number,
            n_evaluated=len(evaluations),
            n_passed=len(passed),
            n_conditional=len(conditional),
            n_failed=len(failed),
            avg_score=round(sum(e["score"] for e in evaluations) / max(len(evaluations), 1), 1),
            top_issues=", ".join(feedback.get("top_issues", ["无"])),
            best_name=best.get("name", "—") if best else "—",
            best_score=best.get("score", 0) if best else 0,
            successful_strategies=", ".join(feedback.get("successful_strategies", ["无"])),
        )
        try:
            from agents.llm import chat
            return chat(CRITIC_SYSTEM, user_msg, temperature=0.5, max_tokens=400)
        except Exception as e:
            return self._fallback_summary(evaluations, feedback, round_number, str(e))

    def _fallback_summary(self, evaluations, feedback, round_number, error=""):
        passed = [e for e in evaluations if e["verdict"] == "PASS"]
        parts = [
            f"第 {round_number} 轮：评估 {len(evaluations)} 个候选分子 — "
            f"{len(passed)} 个通过。"
        ]
        if passed:
            best = max(passed, key=lambda x: x["score"])
            parts.append(f"最佳: {best['name']}（{best['score']} 分）。")
        if feedback.get("top_issues"):
            parts.append(f"主要问题: {', '.join(feedback['top_issues'][:2])}。")
        if error:
            parts.append(f"（LLM 不可用: {error}）")
        return " ".join(parts)

    def evaluate_round(self, candidates: list[dict],
                       reference_smiles: str,
                       round_number: int) -> dict:

        evaluations = []
        for c in candidates:
            ev = evaluate_candidate(c["smiles"], reference_smiles)
            ev["name"] = c.get("name", "Unknown")
            ev["strategy"] = c.get("strategy", "")
            ev["region"] = c.get("region", "")
            ev["design_rationale"] = c.get("rationale", "")

            if self._ref_props and ev.get("properties"):
                ev["radar"] = generate_radar_data(ev["properties"], self._ref_props)

            evaluations.append(ev)

        passed = [e for e in evaluations if e["verdict"] == "PASS"]
        conditional = [e for e in evaluations if e["verdict"] == "CONDITIONAL"]
        failed = [e for e in evaluations if e["verdict"] == "FAIL"]

        feedback = self._build_feedback(evaluations, round_number)

        summary = self._llm_summary(evaluations, feedback, round_number)

        result = {
            "round": round_number,
            "evaluations": evaluations,
            "passed": passed,
            "conditional": conditional,
            "failed": failed,
            "summary": summary,
            "feedback": feedback,
            "stats": {
                "n_evaluated": len(evaluations),
                "n_passed": len(passed),
                "n_conditional": len(conditional),
                "n_failed": len(failed),
                "avg_score": round(sum(e["score"] for e in evaluations) / max(len(evaluations), 1), 1),
                "pass_rate": round(len(passed) / max(len(evaluations), 1), 2),
            },
        }

        self.history.append(result)
        return result

    def _build_feedback(self, evaluations: list[dict], round_number: int) -> dict:
        issue_counts = {}
        for ev in evaluations:
            for reason in ev.get("reasons", []):
                key = reason.split(":")[0].strip() if ":" in reason else reason[:40]
                issue_counts[key] = issue_counts.get(key, 0) + 1

        top_issues = sorted(issue_counts.keys(), key=lambda k: issue_counts[k], reverse=True)[:3]

        successful_strategies = set()
        for ev in evaluations:
            if ev["verdict"] == "PASS":
                successful_strategies.add(ev.get("strategy", ""))
        successful_strategies.discard("")

        avoid_strategies = set()
        for ev in evaluations:
            if ev["verdict"] == "FAIL" and ev["score"] < 30:
                avoid_strategies.add(ev.get("strategy", ""))
        avoid_strategies -= successful_strategies

        prioritize = []
        if any("MW" in i for i in top_issues):
            prioritize.append("Use smaller substituents to reduce MW")
        if any("LogP" in i for i in top_issues):
            prioritize.append("Add polar groups to reduce lipophilicity")
        if any("SA" in i for i in top_issues):
            prioritize.append("Simplify ring systems for easier synthesis")
        if any("QED" in i for i in top_issues):
            prioritize.append("Balance MW/LogP/TPSA for better drug-likeness")

        all_suggestions = []
        for ev in evaluations:
            all_suggestions.extend(ev.get("suggestions", []))

        conditional_seeds = [
            ev["smiles"] for ev in evaluations
            if ev["verdict"] == "CONDITIONAL" and ev.get("valid", True)
        ][:3]

        return {
            "round": round_number,
            "top_issues": top_issues,
            "successful_strategies": list(successful_strategies),
            "avoid_strategies": list(avoid_strategies),
            "prioritize_strategies": list(successful_strategies) if successful_strategies else None,
            "prioritize": prioritize,
            "suggestions": list(set(all_suggestions))[:5],
            "conditional_seeds": conditional_seeds,
        }
