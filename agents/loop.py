from __future__ import annotations
from dataclasses import dataclass, field
from agents.designer import MolecularDesigner
from agents.critic import ADMETCritic
from chemistry.molecules import OSIMERTINIB


@dataclass
class RoundResult:
    round_number: int
    designer_output: dict
    critic_output: dict
    conversation: list[dict] = field(default_factory=list)


@dataclass
class LoopSummary:
    total_generated: int
    total_passed: int
    total_conditional: int
    total_failed: int
    best_candidates: list[dict]
    round_stats: list[dict]
    all_passed: list[dict]


class AdversarialLoop:
    def __init__(self, n_rounds: int = 3, n_candidates: int = 8,
                 seed_smiles: str | None = None, llm_client=None):
        self.n_rounds = n_rounds
        self.n_candidates = n_candidates
        self.seed_smiles = seed_smiles or OSIMERTINIB["smiles"]
        self.designer = MolecularDesigner(llm_client=llm_client)
        self.critic = ADMETCritic(llm_client=llm_client)
        self.round_results: list[RoundResult] = []
        self.all_passed: list[dict] = []
        self.round_stats: list[dict] = []

    def run_round(self, round_number: int, feedback: dict | None = None) -> RoundResult:
        designer_output = self.designer.generate_round(
            seed_smiles=self.seed_smiles,
            round_number=round_number,
            n_candidates=self.n_candidates,
            feedback=feedback,
        )

        critic_output = self.critic.evaluate_round(
            candidates=designer_output["candidates"],
            reference_smiles=self.seed_smiles,
            round_number=round_number,
        )

        self.all_passed.extend(critic_output["passed"])

        self.round_stats.append({
            "round": round_number,
            "avg_score": critic_output["stats"]["avg_score"],
            "pass_rate": critic_output["stats"]["pass_rate"],
            "n_passed": critic_output["stats"]["n_passed"],
            "n_total": critic_output["stats"]["n_evaluated"],
        })

        conversation = [
            {
                "speaker": "Designer",
                "role": "Agent A",
                "round": round_number,
                "message": designer_output["design_notes"],
                "detail": f"Generated {designer_output['n_generated']} candidates using: {', '.join(designer_output['strategies_used'])}",
            },
            {
                "speaker": "Critic",
                "role": "Agent B",
                "round": round_number,
                "message": critic_output["summary"],
                "detail": "; ".join(critic_output["feedback"]["prioritize"][:2]) if critic_output["feedback"]["prioritize"] else "No specific improvement suggestions.",
            },
        ]

        result = RoundResult(
            round_number=round_number,
            designer_output=designer_output,
            critic_output=critic_output,
            conversation=conversation,
        )
        self.round_results.append(result)
        return result

    def run_all(self):
        feedback = None
        for r in range(1, self.n_rounds + 1):
            result = self.run_round(r, feedback)
            feedback = result.critic_output["feedback"]
            yield result

    def get_summary(self) -> LoopSummary:
        total_gen = sum(r.designer_output["n_generated"] for r in self.round_results)
        total_pass = len(self.all_passed)
        total_cond = sum(len(r.critic_output["conditional"]) for r in self.round_results)
        total_fail = sum(len(r.critic_output["failed"]) for r in self.round_results)

        best = sorted(self.all_passed, key=lambda x: x["score"], reverse=True)[:5]

        return LoopSummary(
            total_generated=total_gen,
            total_passed=total_pass,
            total_conditional=total_cond,
            total_failed=total_fail,
            best_candidates=best,
            round_stats=self.round_stats,
            all_passed=self.all_passed,
        )
