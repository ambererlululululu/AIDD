from __future__ import annotations
from rdkit import Chem
from chemistry.generator import generate_candidates, ALL_STRATEGIES, validate_smiles
from chemistry.molecules import OSIMERTINIB
from agents.prompts import (
    DESIGNER_SYSTEM, DESIGNER_ROUND,
    DESIGNER_STRATEGY_SYSTEM, DESIGNER_STRATEGY_ROUND,
)


class MolecularDesigner:
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.history = []
        self.generated_smiles = set()

    def _llm_propose_strategy(self, round_number: int, seed_smiles: str,
                              feedback: dict | None) -> dict:
        feedback_section = "这是第一轮，无上轮反馈。"
        if feedback:
            parts = []
            if feedback.get("top_issues"):
                parts.append(f"上轮主要问题: {', '.join(feedback['top_issues'][:3])}")
            if feedback.get("successful_strategies"):
                parts.append(f"成功策略: {', '.join(feedback['successful_strategies'])}")
            if feedback.get("avoid_strategies"):
                parts.append(f"应避免策略: {', '.join(feedback['avoid_strategies'])}")
            if feedback.get("prioritize"):
                parts.append(f"优先方向: {', '.join(feedback['prioritize'][:3])}")
            feedback_section = "\n".join(parts) if parts else "上轮无特别反馈。"

        system = DESIGNER_STRATEGY_SYSTEM.format(ref_smiles=seed_smiles)
        user = DESIGNER_STRATEGY_ROUND.format(
            round_number=round_number,
            feedback_section=feedback_section,
        )
        try:
            from agents.llm import chat_json
            result = chat_json(system, user, temperature=0.7, max_tokens=800)
            return result
        except Exception:
            return {}

    def _validate_llm_molecules(self, proposals: list[dict]) -> tuple[list[dict], list[dict]]:
        valid, invalid = [], []
        for p in proposals:
            smi = p.get("smiles", "")
            if not smi:
                continue
            if validate_smiles(smi):
                canon = Chem.MolToSmiles(Chem.MolFromSmiles(smi))
                valid.append({
                    "smiles": canon,
                    "name": p.get("name", f"LLM-{len(valid)+1}"),
                    "strategy": f"AI-{p.get('position', 'novel')}",
                    "region": p.get("position", ""),
                    "rationale": p.get("rationale", ""),
                })
            else:
                invalid.append({"smiles": smi, "name": p.get("name", ""), "error": "RDKit 无法解析"})
        return valid, invalid

    def _llm_design_notes(self, round_number: int, seed_smiles: str,
                          strategies: list[str], n_candidates: int,
                          feedback: dict | None, sar_reasoning: str = "") -> str:
        feedback_section = "这是第一轮，无上轮反馈。"
        if feedback:
            parts = []
            if feedback.get("top_issues"):
                parts.append(f"上轮主要问题: {', '.join(feedback['top_issues'][:3])}")
            if feedback.get("successful_strategies"):
                parts.append(f"成功策略: {', '.join(feedback['successful_strategies'])}")
            if feedback.get("prioritize"):
                parts.append(f"优先方向: {', '.join(feedback['prioritize'][:3])}")
            feedback_section = "\n".join(parts) if parts else "上轮无特别反馈。"

        if sar_reasoning:
            feedback_section += f"\n\nAI SAR 分析: {sar_reasoning}"

        user_msg = DESIGNER_ROUND.format(
            round_number=round_number,
            seed_smiles=seed_smiles,
            strategies=", ".join(strategies),
            n_candidates=n_candidates,
            feedback_section=feedback_section,
        )
        try:
            from agents.llm import chat
            return chat(DESIGNER_SYSTEM, user_msg, temperature=0.7, max_tokens=300)
        except Exception as e:
            return f"第 {round_number} 轮：基于 {', '.join(strategies)} 策略生成 {n_candidates} 个候选分子。"

    def generate_round(self, seed_smiles: str, round_number: int,
                       n_candidates: int = 8,
                       feedback: dict | None = None) -> dict:

        llm_strategy = self._llm_propose_strategy(round_number, seed_smiles, feedback)

        llm_smiles_attempts = llm_strategy.get("smiles_attempts", [])
        llm_valid, llm_invalid = self._validate_llm_molecules(llm_smiles_attempts)

        for m in llm_valid:
            self.generated_smiles.add(m["smiles"])

        preferred = llm_strategy.get("preferred_positions")
        avoid = llm_strategy.get("avoid_positions")
        if not preferred and feedback:
            preferred = feedback.get("prioritize_strategies")
        if not avoid and feedback:
            avoid = feedback.get("avoid_strategies")

        rule_needed = max(0, n_candidates - len(llm_valid))
        rule_candidates = []
        if rule_needed > 0:
            rule_candidates = generate_candidates(
                seed_smiles=seed_smiles,
                round_number=round_number,
                n_candidates=rule_needed + 4,
                preferred_strategies=preferred,
                avoid_strategies=avoid,
                exclude_smiles=self.generated_smiles,
            )

        if feedback and feedback.get("conditional_seeds"):
            for cond_smi in feedback["conditional_seeds"][:2]:
                extra = generate_candidates(
                    seed_smiles=cond_smi,
                    round_number=round_number,
                    n_candidates=4,
                    exclude_smiles=self.generated_smiles,
                )
                rule_candidates.extend(extra)

        candidates = llm_valid + rule_candidates
        seen = set()
        unique = []
        for c in candidates:
            if c["smiles"] not in seen and c["smiles"] not in self.generated_smiles:
                seen.add(c["smiles"])
                unique.append(c)
            elif c in llm_valid and c["smiles"] not in seen:
                seen.add(c["smiles"])
                unique.append(c)
        candidates = unique[:n_candidates]

        for c in candidates:
            self.generated_smiles.add(c["smiles"])

        strategies_used = list({c["strategy"] for c in candidates})
        sar_reasoning = llm_strategy.get("sar_reasoning", "")

        design_notes = self._llm_design_notes(
            round_number, seed_smiles, strategies_used,
            len(candidates), feedback, sar_reasoning,
        )

        ai_contribution = ""
        if llm_smiles_attempts:
            rate = len(llm_valid) / len(llm_smiles_attempts) * 100 if llm_smiles_attempts else 0
            ai_contribution = f"AI 提出 {len(llm_smiles_attempts)} 个 SMILES，{len(llm_valid)} 个有效（{rate:.0f}%）"

        result = {
            "round": round_number,
            "candidates": candidates,
            "design_notes": design_notes,
            "n_generated": len(candidates),
            "strategies_used": strategies_used,
            "llm_strategy": llm_strategy,
            "llm_proposed": len(llm_smiles_attempts),
            "llm_valid": len(llm_valid),
            "llm_invalid": llm_invalid,
            "ai_contribution": ai_contribution,
            "sar_reasoning": sar_reasoning,
        }

        self.history.append(result)
        return result
