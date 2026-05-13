from __future__ import annotations
import queue
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from agents.sar_agents import (
    StructureActivityAgent, MPOAgent, RiskAgent,
    ADMETAgent, SynthFeasibilityAgent,
)
from agents.sar_prompts import (
    CONVERGENCE_SYSTEM, format_prompt, build_knowledge_block, load_full_knowledge,
)


AGENT_ROLES = {
    "结构-活性分析": "关注 SAR 趋势",
    "多参数优化": "关注属性平衡",
    "风险评估": "关注安全和可行性",
    "ADMET预测": "关注代谢、吸收和毒性风险",
    "合成可行性": "关注合成路线和成本",
}

STRATEGY_AGENTS = {
    "focused": [StructureActivityAgent, MPOAgent],
    "standard": [StructureActivityAgent, MPOAgent, RiskAgent],
    "comprehensive": [StructureActivityAgent, MPOAgent, RiskAgent, ADMETAgent, SynthFeasibilityAgent],
}


@dataclass
class RoundOutput:
    round_number: int
    agent_outputs: dict[str, str]
    duration: float = 0.0


@dataclass
class DeliberationResult:
    rounds: list[RoundOutput] = field(default_factory=list)
    convergence: str = ""
    all_traces: list[dict] = field(default_factory=list)
    total_duration: float = 0.0


def _load_knowledge(project_id: str) -> str:
    knowledge_path = Path("data/projects") / project_id / "knowledge.md"
    if knowledge_path.exists():
        return knowledge_path.read_text(encoding="utf-8")
    return ""


class Deliberation:
    def __init__(self, lang: str = "zh", project_config: dict | None = None,
                 strategy: str = "standard", project_id: str = "c34-egfr"):
        agent_classes = STRATEGY_AGENTS.get(strategy, STRATEGY_AGENTS["standard"])

        knowledge_md = _load_knowledge(project_id)
        knowledge_block = build_knowledge_block(project_config, knowledge_md)

        self.agents = []
        for cls in agent_classes:
            agent = cls()
            agent.lang = lang
            agent.project_config = project_config
            agent.knowledge_context = knowledge_block
            self.agents.append(agent)

        self.lang = lang
        self.project_config = project_config
        self.strategy = strategy
        self.project_id = project_id
        self._r1_outputs: dict[str, str] = {}
        self._r2_outputs: dict[str, str] = {}
        self._full_knowledge: str | None = None

    def run_round1(self, molecules: list[dict], ref_props: dict,
                   focus: str = "", user_context: str = "") -> RoundOutput:
        t0 = time.time()
        outputs = {}
        for agent in self.agents:
            outputs[agent.name] = agent.analyze(
                molecules, ref_props, focus=focus, user_context=user_context,
            )
        self._r1_outputs = outputs
        return RoundOutput(
            round_number=1,
            agent_outputs=dict(outputs),
            duration=round(time.time() - t0, 2),
        )

    def run_round2(self, user_guidance: str = "") -> RoundOutput:
        t0 = time.time()
        outputs = {}
        for agent in self.agents:
            other = {k: v for k, v in self._r1_outputs.items() if k != agent.name}
            outputs[agent.name] = agent.challenge(
                self._r1_outputs[agent.name], other,
                user_guidance=user_guidance,
            )
        self._r2_outputs = outputs
        return RoundOutput(
            round_number=2,
            agent_outputs=dict(outputs),
            duration=round(time.time() - t0, 2),
        )

    def run_round3(self) -> str:
        roles_text = "\n".join(
            f"- {name}：{AGENT_ROLES.get(name, '')}"
            for name in self._r1_outputs
        )

        r1_block = "\n\n".join(
            f"{name}：\n{text}" for name, text in self._r1_outputs.items()
        )
        r2_block = "\n\n".join(
            f"{name}：\n{text}" for name, text in self._r2_outputs.items()
        )

        n = len(self.agents)
        user_msg = f"""请综合以下 {n} 位分析师在两轮讨论中的观点，做出最终决策。

=== 第一轮独立分析 ===

{r1_block}

=== 第二轮交叉质疑 ===

{r2_block}

请做出最终判断。"""

        try:
            from agents.llm import chat
            from agents.sar_agents import _LANG_INSTRUCTION
            sys_prompt = format_prompt(
                CONVERGENCE_SYSTEM.replace("{agent_roles}", roles_text),
                self.project_config,
            )
            sys_msg = sys_prompt + _LANG_INSTRUCTION.get(self.lang, "")
            return chat(sys_msg, user_msg, temperature=0.5, max_tokens=800)
        except Exception as e:
            return f"[收敛分析不可用: {e}]"

    def _stream_parallel(self, agent_runners):
        """Run multiple agent generators in parallel threads, yielding events."""
        q: queue.Queue = queue.Queue()

        def _worker(agent, gen):
            q.put({"type": "agent_start", "agent": agent.name})
            full_text = ""
            try:
                for chunk in gen:
                    full_text += chunk
                    q.put({"type": "chunk", "agent": agent.name, "text": chunk})
            except Exception as e:
                full_text = f"[{agent.name} 不可用: {e}]"
                q.put({"type": "chunk", "agent": agent.name, "text": full_text})
            q.put({"type": "agent_done", "agent": agent.name,
                   "full_text": full_text})

        threads = []
        for agent, gen in agent_runners:
            t = threading.Thread(target=_worker, args=(agent, gen))
            t.start()
            threads.append(t)

        done_count = 0
        total = len(threads)
        while done_count < total:
            try:
                event = q.get(timeout=0.1)
                if event["type"] == "agent_done":
                    done_count += 1
                yield event
            except queue.Empty:
                if not any(t.is_alive() for t in threads):
                    break

    def stream_round1(self, molecules: list[dict], ref_props: dict,
                      focus: str = "", user_context: str = ""):
        t0 = time.time()
        runners = [
            (agent, agent.analyze_stream(molecules, ref_props,
                                         focus=focus, user_context=user_context))
            for agent in self.agents
        ]
        for event in self._stream_parallel(runners):
            if event["type"] == "agent_done":
                self._r1_outputs[event["agent"]] = event["full_text"]
            yield event
        yield {"type": "round_done", "round": 1,
               "duration": round(time.time() - t0, 2)}

    def stream_round2(self, user_guidance: str = ""):
        t0 = time.time()
        runners = []
        for agent in self.agents:
            other = {k: v for k, v in self._r1_outputs.items()
                     if k != agent.name}
            gen = agent.challenge_stream(
                self._r1_outputs[agent.name], other,
                user_guidance=user_guidance)
            runners.append((agent, gen))
        for event in self._stream_parallel(runners):
            if event["type"] == "agent_done":
                self._r2_outputs[event["agent"]] = event["full_text"]
            yield event
        yield {"type": "round_done", "round": 2,
               "duration": round(time.time() - t0, 2)}

    def _get_full_knowledge(self) -> str:
        if self._full_knowledge is None:
            self._full_knowledge = load_full_knowledge(self.project_id)
        return self._full_knowledge

    def _stream_parallel_react(self, agent_runners):
        q: queue.Queue = queue.Queue()

        def _worker(agent, gen):
            q.put({"type": "agent_start", "agent": agent.name})
            final_text = ""
            try:
                for item in gen:
                    if isinstance(item, dict):
                        if "__react_step__" in item:
                            q.put({"type": "react_step", "agent": agent.name,
                                   "step": item["__react_step__"],
                                   "name_zh": item["name_zh"],
                                   "name_en": item["name_en"]})
                        elif "__react_step_done__" in item:
                            q.put({"type": "react_step_done", "agent": agent.name,
                                   "step": item["__react_step_done__"],
                                   "text": item["text"]})
                        elif "__full_text__" in item:
                            final_text = item["__full_text__"]
                        continue
                    q.put({"type": "chunk", "agent": agent.name, "text": item})
            except Exception as e:
                final_text = f"[{agent.name} 不可用: {e}]"
                q.put({"type": "chunk", "agent": agent.name, "text": final_text})
            q.put({"type": "agent_done", "agent": agent.name,
                   "full_text": final_text})

        threads = []
        for agent, gen in agent_runners:
            t = threading.Thread(target=_worker, args=(agent, gen))
            t.start()
            threads.append(t)

        done_count = 0
        total = len(threads)
        while done_count < total:
            try:
                event = q.get(timeout=0.1)
                if event["type"] == "agent_done":
                    done_count += 1
                yield event
            except queue.Empty:
                if not any(t.is_alive() for t in threads):
                    break

    def stream_round1_react(self, molecules: list[dict], ref_props: dict,
                            focus: str = "", user_context: str = ""):
        t0 = time.time()
        fk = self._get_full_knowledge()
        runners = [
            (agent, agent.react_analyze_stream(
                molecules, ref_props, fk,
                focus=focus, user_context=user_context))
            for agent in self.agents
        ]
        for event in self._stream_parallel_react(runners):
            if event["type"] == "agent_done":
                self._r1_outputs[event["agent"]] = event["full_text"]
            yield event
        yield {"type": "round_done", "round": 1,
               "duration": round(time.time() - t0, 2)}

    def stream_round2_react(self, user_guidance: str = ""):
        t0 = time.time()
        fk = self._get_full_knowledge()
        runners = []
        for agent in self.agents:
            other = {k: v for k, v in self._r1_outputs.items()
                     if k != agent.name}
            gen = agent.react_challenge_stream(
                self._r1_outputs[agent.name], other, fk,
                user_guidance=user_guidance)
            runners.append((agent, gen))
        for event in self._stream_parallel_react(runners):
            if event["type"] == "agent_done":
                self._r2_outputs[event["agent"]] = event["full_text"]
            yield event
        yield {"type": "round_done", "round": 2,
               "duration": round(time.time() - t0, 2)}

    def stream_round3(self):
        roles_text = "\n".join(
            f"- {name}：{AGENT_ROLES.get(name, '')}"
            for name in self._r1_outputs
        )
        r1_block = "\n\n".join(
            f"{name}：\n{text}" for name, text in self._r1_outputs.items()
        )
        r2_block = "\n\n".join(
            f"{name}：\n{text}" for name, text in self._r2_outputs.items()
        )
        n = len(self.agents)
        user_msg = f"""请综合以下 {n} 位分析师在两轮讨论中的观点，做出最终决策。

=== 第一轮独立分析 ===

{r1_block}

=== 第二轮交叉质疑 ===

{r2_block}

请做出最终判断。"""

        from agents.sar_agents import _LANG_INSTRUCTION
        sys_prompt = format_prompt(
            CONVERGENCE_SYSTEM.replace("{agent_roles}", roles_text),
            self.project_config,
        )
        sys_msg = sys_prompt + _LANG_INSTRUCTION.get(self.lang, "")

        full_text = ""
        try:
            from agents.llm import chat_stream
            for chunk in chat_stream(sys_msg, user_msg,
                                     temperature=0.5, max_tokens=800):
                full_text += chunk
                yield {"type": "chunk", "text": chunk}
        except Exception as e:
            full_text = f"[收敛分析不可用: {e}]"
            yield {"type": "chunk", "text": full_text}
        self._r3_output = full_text
        yield {"type": "r3_done"}

    def run_all(self, molecules: list[dict], ref_props: dict):
        t_start = time.time()

        r1 = self.run_round1(molecules, ref_props)
        yield {"type": "round", "data": r1}

        r2 = self.run_round2()
        yield {"type": "round", "data": r2}

        convergence = self.run_round3()
        yield {"type": "convergence", "data": convergence}

        all_traces = []
        for agent in self.agents:
            all_traces.extend(agent.traces)
        yield {
            "type": "complete",
            "data": DeliberationResult(
                rounds=[r1, r2],
                convergence=convergence,
                all_traces=all_traces,
                total_duration=round(time.time() - t_start, 2),
            ),
        }
