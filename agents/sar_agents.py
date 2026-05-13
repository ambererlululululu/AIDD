from __future__ import annotations
import json
import time
from agents.sar_prompts import (
    SA_SYSTEM_R1, SA_USER_R1, SA_SYSTEM_R2, SA_USER_R2,
    MPO_SYSTEM_R1, MPO_USER_R1, MPO_SYSTEM_R2, MPO_USER_R2,
    RISK_SYSTEM_R1, RISK_USER_R1, RISK_SYSTEM_R2, RISK_USER_R2,
    ADMET_SYSTEM_R1, ADMET_USER_R1, ADMET_SYSTEM_R2, ADMET_USER_R2,
    SYNTH_SYSTEM_R1, SYNTH_USER_R1, SYNTH_SYSTEM_R2, SYNTH_USER_R2,
    REACT_R1_PLAN, REACT_R1_INVESTIGATE, REACT_R1_CONCLUDE,
    REACT_R2_IDENTIFY, REACT_R2_VERIFY, REACT_R2_CHALLENGE,
    format_prompt, build_knowledge_block,
)


def _format_ref_props(ref_props: dict) -> str:
    return (
        f"MW={ref_props['mw']}, LogP={ref_props['logp']}, "
        f"TPSA={ref_props['tpsa']}, QED={ref_props['qed']:.3f}, "
        f"SA={ref_props['sa_score']:.2f}, HBD={ref_props['hbd']}, HBA={ref_props['hba']}"
    )


def _format_molecules(molecules: list[dict]) -> str:
    lines = []
    for m in molecules:
        p = m.get("properties", {})
        d = m.get("delta", {})
        b3d = m.get("binding_3d", {})
        bd = m.get("breakdown", {})
        line = (
            f"- {m['name']} [{m['position']}] "
            f"Score={m['score']}, Verdict={m['verdict']}\n"
            f"  MW={p.get('mw', 0)}, LogP={p.get('logp', 0):.2f}, "
            f"TPSA={p.get('tpsa', 0)}, QED={p.get('qed', 0):.3f}, "
            f"SA={p.get('sa_score', 0):.2f}\n"
            f"  ΔMW={d.get('mw', 0):+.1f}, ΔLogP={d.get('logp', 0):+.2f}, "
            f"ΔQED={d.get('qed', 0):+.3f}\n"
            f"  Similarity={m.get('similarity', 0):.3f}, "
            f"3D_binding={b3d.get('binding_proxy_score', 0):.3f}\n"
            f"  Score breakdown: "
            f"Lipinski={bd.get('lipinski', 0)}/{bd.get('lipinski_max', 20)}, "
            f"QED={bd.get('qed', 0)}/{bd.get('qed_max', 15)}, "
            f"SA={bd.get('sa', 0)}/{bd.get('sa_max', 10)}, "
            f"PAINS={bd.get('pains', 0)}/{bd.get('pains_max', 10)}, "
            f"Binding3D={bd.get('binding_3d', 0)}/{bd.get('binding_3d_max', 25)}"
        )
        lines.append(line)
    return "\n".join(lines)


_LANG_INSTRUCTION = {
    "en": "\n\nIMPORTANT: Reply entirely in English. Translate ALL section headers, labels, and content into English. Do not keep any Chinese text in your response.",
    "zh": "",
}


class SARAgent:
    def __init__(self, name: str, system_r1: str, user_r1: str,
                 system_r2: str, user_r2: str):
        self.name = name
        self.system_r1 = system_r1
        self.user_r1 = user_r1
        self.system_r2 = system_r2
        self.user_r2 = user_r2
        self.traces: list[dict] = []
        self.lang = "zh"
        self.project_config: dict | None = None
        self.knowledge_context: str = ""

    def _sys(self, prompt: str) -> str:
        filled = format_prompt(prompt, self.project_config)
        if self.knowledge_context:
            filled += f"\n\n{self.knowledge_context}"
        return filled + _LANG_INSTRUCTION.get(self.lang, "")

    def _compound_name(self) -> str:
        if self.project_config and "reference" in self.project_config:
            return self.project_config["reference"].get("name", "C34")
        return "C34"

    def _build_r1_msg(self, molecules: list[dict], ref_props: dict,
                      focus: str = "", user_context: str = "") -> str:
        ref_str = _format_ref_props(ref_props)
        mol_str = _format_molecules(molecules)
        user_tpl = format_prompt(self.user_r1, self.project_config)
        user_msg = user_tpl.format(
            n_molecules=len(molecules),
            ref_props=ref_str,
            molecules_data=mol_str,
            compound_name=self._compound_name(),
        )
        if focus:
            user_msg += f"\n\n用户分析重点：{focus}"
        if user_context:
            user_msg += f"\n\n用户补充背景：\n{user_context}"
        return user_msg

    def analyze(self, molecules: list[dict], ref_props: dict,
                focus: str = "", user_context: str = "") -> str:
        user_msg = self._build_r1_msg(molecules, ref_props, focus, user_context)
        t0 = time.time()
        try:
            from agents.llm import chat
            result = chat(self._sys(self.system_r1), user_msg, temperature=0.6, max_tokens=1200)
        except Exception as e:
            result = f"[{self.name} 分析不可用: {e}]"
        self.traces.append({
            "round": 1, "agent": self.name,
            "input_summary": f"{len(molecules)} molecules",
            "output": result,
            "duration": round(time.time() - t0, 2),
        })
        return result

    def _stream_llm(self, system_prompt: str, user_msg: str,
                    round_num: int, input_summary: str,
                    max_tokens: int = 1200):
        t0 = time.time()
        full_text = ""
        try:
            from agents.llm import chat_stream
            for chunk in chat_stream(self._sys(system_prompt), user_msg,
                                     temperature=0.6, max_tokens=max_tokens):
                full_text += chunk
                yield chunk
        except Exception as e:
            full_text = f"[{self.name} 不可用: {e}]"
            yield full_text
        self.traces.append({
            "round": round_num, "agent": self.name,
            "input_summary": input_summary,
            "output": full_text,
            "duration": round(time.time() - t0, 2),
        })

    def analyze_stream(self, molecules: list[dict], ref_props: dict,
                       focus: str = "", user_context: str = ""):
        user_msg = self._build_r1_msg(molecules, ref_props, focus, user_context)
        yield from self._stream_llm(self.system_r1, user_msg, 1,
                                    f"{len(molecules)} molecules", 1200)

    def _build_r2_msg(self, own_r1: str, other_analyses: dict[str, str],
                      user_guidance: str = "") -> str:
        raise NotImplementedError

    def challenge(self, own_r1: str, other_analyses: dict[str, str],
                  user_guidance: str = "") -> str:
        raise NotImplementedError

    def challenge_stream(self, own_r1: str, other_analyses: dict[str, str],
                         user_guidance: str = ""):
        user_msg = self._build_r2_msg(own_r1, other_analyses, user_guidance)
        yield from self._stream_llm(self.system_r2, user_msg, 2,
                                    "cross-challenge", 900)

    def _collect_stream(self, system_prompt: str, user_msg: str,
                        max_tokens: int = 800):
        full_text = ""
        for chunk in self._stream_llm(system_prompt, user_msg, 0, "", max_tokens):
            full_text += chunk
            yield chunk
        self.traces.pop()
        yield {"__full_text__": full_text}

    def react_analyze_stream(self, molecules: list[dict], ref_props: dict,
                             full_knowledge: str,
                             focus: str = "", user_context: str = ""):
        r1_user = self._build_r1_msg(molecules, ref_props, focus, user_context)
        sys = self._sys(self.system_r1)

        step_names_zh = ["规划", "调查", "结论"]
        step_names_en = ["Plan", "Investigate", "Conclude"]

        # Step 1: Plan (no knowledge)
        yield {"__react_step__": 1, "name_zh": step_names_zh[0], "name_en": step_names_en[0]}
        plan_prompt = sys + "\n\n" + REACT_R1_PLAN
        plan_text = ""
        for item in self._collect_stream(plan_prompt, r1_user, 400):
            if isinstance(item, dict):
                plan_text = item["__full_text__"]
            else:
                yield item
        yield {"__react_step_done__": 1, "text": plan_text}

        # Step 2: Investigate (full knowledge)
        yield {"__react_step__": 2, "name_zh": step_names_zh[1], "name_en": step_names_en[1]}
        inv_user = REACT_R1_INVESTIGATE.format(
            plan_output=plan_text, full_knowledge=full_knowledge,
        )
        inv_text = ""
        for item in self._collect_stream(sys, inv_user, 800):
            if isinstance(item, dict):
                inv_text = item["__full_text__"]
            else:
                yield item
        yield {"__react_step_done__": 2, "text": inv_text}

        # Step 3: Conclude
        yield {"__react_step__": 3, "name_zh": step_names_zh[2], "name_en": step_names_en[2]}
        conc_user = REACT_R1_CONCLUDE.format(investigate_output=inv_text) + "\n\n" + r1_user
        t0 = time.time()
        conc_text = ""
        for chunk in self._stream_llm(sys, conc_user, 1, f"{len(molecules)} molecules (react)", 1200):
            conc_text += chunk
            yield chunk
        yield {"__react_step_done__": 3, "text": conc_text}
        yield {"__full_text__": conc_text}

    def react_challenge_stream(self, own_r1: str, other_analyses: dict[str, str],
                               full_knowledge: str,
                               user_guidance: str = ""):
        sys = self._sys(self.system_r2)

        step_names_zh = ["识别分歧", "验证证据", "质疑"]
        step_names_en = ["Identify", "Verify", "Challenge"]

        others_text = "\n\n".join(f"{k}：\n{v}" for k, v in other_analyses.items())

        # Step 1: Identify disagreements
        yield {"__react_step__": 1, "name_zh": step_names_zh[0], "name_en": step_names_en[0]}
        id_user = REACT_R2_IDENTIFY.format(own_r1=own_r1, others_r1=others_text)
        if user_guidance:
            id_user += f"\n\n用户补充指令：{user_guidance}"
        id_text = ""
        for item in self._collect_stream(sys, id_user, 400):
            if isinstance(item, dict):
                id_text = item["__full_text__"]
            else:
                yield item
        yield {"__react_step_done__": 1, "text": id_text}

        # Step 2: Verify with evidence
        yield {"__react_step__": 2, "name_zh": step_names_zh[1], "name_en": step_names_en[1]}
        ver_user = REACT_R2_VERIFY.format(
            identify_output=id_text, full_knowledge=full_knowledge,
        )
        ver_text = ""
        for item in self._collect_stream(sys, ver_user, 600):
            if isinstance(item, dict):
                ver_text = item["__full_text__"]
            else:
                yield item
        yield {"__react_step_done__": 2, "text": ver_text}

        # Step 3: Challenge
        yield {"__react_step__": 3, "name_zh": step_names_zh[2], "name_en": step_names_en[2]}
        ch_user = REACT_R2_CHALLENGE.format(verify_output=ver_text)
        ch_user += f"\n\n你的第一轮分析：\n{own_r1}"
        ch_text = ""
        for chunk in self._stream_llm(sys, ch_user, 2, "react-challenge", 800):
            ch_text += chunk
            yield chunk
        yield {"__react_step_done__": 3, "text": ch_text}
        yield {"__full_text__": ch_text}


class StructureActivityAgent(SARAgent):
    def __init__(self):
        super().__init__(
            "结构-活性分析", SA_SYSTEM_R1, SA_USER_R1, SA_SYSTEM_R2, SA_USER_R2,
        )

    def _build_r2_msg(self, own_r1: str, other_analyses: dict[str, str],
                      user_guidance: str = "") -> str:
        user_msg = self.user_r2.format(
            own_analysis=own_r1,
            mpo_analysis=other_analyses.get("多参数优化", ""),
            risk_analysis=other_analyses.get("风险评估", ""),
        )
        if user_guidance:
            user_msg += f"\n\n用户补充指令：{user_guidance}"
        return user_msg

    def challenge(self, own_r1: str, other_analyses: dict[str, str],
                  user_guidance: str = "") -> str:
        user_msg = self._build_r2_msg(own_r1, other_analyses, user_guidance)
        t0 = time.time()
        try:
            from agents.llm import chat
            result = chat(self._sys(self.system_r2), user_msg, temperature=0.6, max_tokens=900)
        except Exception as e:
            result = f"[{self.name} 质疑不可用: {e}]"
        self.traces.append({
            "round": 2, "agent": self.name,
            "input_summary": "cross-challenge with MPO + Risk",
            "output": result,
            "duration": round(time.time() - t0, 2),
        })
        return result


class MPOAgent(SARAgent):
    def __init__(self):
        super().__init__(
            "多参数优化", MPO_SYSTEM_R1, MPO_USER_R1, MPO_SYSTEM_R2, MPO_USER_R2,
        )

    def _build_r2_msg(self, own_r1: str, other_analyses: dict[str, str],
                      user_guidance: str = "") -> str:
        user_msg = self.user_r2.format(
            own_analysis=own_r1,
            sa_analysis=other_analyses.get("结构-活性分析", ""),
            risk_analysis=other_analyses.get("风险评估", ""),
        )
        if user_guidance:
            user_msg += f"\n\n用户补充指令：{user_guidance}"
        return user_msg

    def challenge(self, own_r1: str, other_analyses: dict[str, str],
                  user_guidance: str = "") -> str:
        user_msg = self._build_r2_msg(own_r1, other_analyses, user_guidance)
        t0 = time.time()
        try:
            from agents.llm import chat
            result = chat(self._sys(self.system_r2), user_msg, temperature=0.6, max_tokens=900)
        except Exception as e:
            result = f"[{self.name} 质疑不可用: {e}]"
        self.traces.append({
            "round": 2, "agent": self.name,
            "input_summary": "cross-challenge with SA + Risk",
            "output": result,
            "duration": round(time.time() - t0, 2),
        })
        return result


class RiskAgent(SARAgent):
    def __init__(self):
        super().__init__(
            "风险评估", RISK_SYSTEM_R1, RISK_USER_R1, RISK_SYSTEM_R2, RISK_USER_R2,
        )

    def _build_r2_msg(self, own_r1: str, other_analyses: dict[str, str],
                      user_guidance: str = "") -> str:
        user_msg = self.user_r2.format(
            own_analysis=own_r1,
            sa_analysis=other_analyses.get("结构-活性分析", ""),
            mpo_analysis=other_analyses.get("多参数优化", ""),
        )
        if user_guidance:
            user_msg += f"\n\n用户补充指令：{user_guidance}"
        return user_msg

    def challenge(self, own_r1: str, other_analyses: dict[str, str],
                  user_guidance: str = "") -> str:
        user_msg = self._build_r2_msg(own_r1, other_analyses, user_guidance)
        t0 = time.time()
        try:
            from agents.llm import chat
            result = chat(self._sys(self.system_r2), user_msg, temperature=0.6, max_tokens=900)
        except Exception as e:
            result = f"[{self.name} 质疑不可用: {e}]"
        self.traces.append({
            "round": 2, "agent": self.name,
            "input_summary": "cross-challenge with SA + MPO",
            "output": result,
            "duration": round(time.time() - t0, 2),
        })
        return result


class ADMETAgent(SARAgent):
    def __init__(self):
        super().__init__(
            "ADMET预测", ADMET_SYSTEM_R1, ADMET_USER_R1, ADMET_SYSTEM_R2, ADMET_USER_R2,
        )

    def _build_r2_msg(self, own_r1: str, other_analyses: dict[str, str],
                      user_guidance: str = "") -> str:
        others_str = "\n\n".join(f"{k}：\n{v}" for k, v in other_analyses.items())
        user_msg = self.user_r2.format(
            own_analysis=own_r1,
            other_analyses=others_str,
        )
        if user_guidance:
            user_msg += f"\n\n用户补充指令：{user_guidance}"
        return user_msg

    def challenge(self, own_r1: str, other_analyses: dict[str, str],
                  user_guidance: str = "") -> str:
        user_msg = self._build_r2_msg(own_r1, other_analyses, user_guidance)
        t0 = time.time()
        try:
            from agents.llm import chat
            result = chat(self._sys(self.system_r2), user_msg, temperature=0.6, max_tokens=900)
        except Exception as e:
            result = f"[{self.name} 质疑不可用: {e}]"
        self.traces.append({
            "round": 2, "agent": self.name,
            "input_summary": "cross-challenge with all agents",
            "output": result,
            "duration": round(time.time() - t0, 2),
        })
        return result


class SynthFeasibilityAgent(SARAgent):
    def __init__(self):
        super().__init__(
            "合成可行性", SYNTH_SYSTEM_R1, SYNTH_USER_R1, SYNTH_SYSTEM_R2, SYNTH_USER_R2,
        )

    def _build_r2_msg(self, own_r1: str, other_analyses: dict[str, str],
                      user_guidance: str = "") -> str:
        others_str = "\n\n".join(f"{k}：\n{v}" for k, v in other_analyses.items())
        user_msg = self.user_r2.format(
            own_analysis=own_r1,
            other_analyses=others_str,
        )
        if user_guidance:
            user_msg += f"\n\n用户补充指令：{user_guidance}"
        return user_msg

    def challenge(self, own_r1: str, other_analyses: dict[str, str],
                  user_guidance: str = "") -> str:
        user_msg = self._build_r2_msg(own_r1, other_analyses, user_guidance)
        t0 = time.time()
        try:
            from agents.llm import chat
            result = chat(self._sys(self.system_r2), user_msg, temperature=0.6, max_tokens=900)
        except Exception as e:
            result = f"[{self.name} 质疑不可用: {e}]"
        self.traces.append({
            "round": 2, "agent": self.name,
            "input_summary": "cross-challenge with all agents",
            "output": result,
            "duration": round(time.time() - t0, 2),
        })
        return result
