from __future__ import annotations
import io
import streamlit as st
import pandas as pd
from chemistry.visualizer import (
    mol_to_svg, highlight_diff, render_radar_chart,
    render_score_trajectory, render_multi_radar,
    render_sar_heatmap, render_chemical_space,
)
from chemistry.evaluator import (
    evaluate_candidate, generate_radar_data, compute_properties,
)
from chemistry.molecules import OSIMERTINIB, REFERENCE_TKIS, PHARMACOPHORE, get_reference_properties


def _tag(verdict: str) -> str:
    cls = {"PASS": "tag-pass", "CONDITIONAL": "tag-conditional", "FAIL": "tag-fail"}
    label = {"PASS": "通过", "CONDITIONAL": "有条件", "FAIL": "未通过"}
    return f'<span class="{cls.get(verdict, "tag-fail")}">{label.get(verdict, verdict)}</span>'


def _prop_cls(value, lo, hi):
    if lo <= value <= hi:
        return "c-ok"
    return "c-warn" if abs(value - hi) < (hi - lo) * 0.2 or abs(value - lo) < (hi - lo) * 0.2 else "c-fail"


def render_reference_molecule():
    st.markdown("#### 参考药物")
    st.markdown(f"**{OSIMERTINIB['name']}**")
    st.caption(f"{OSIMERTINIB['target']} · {OSIMERTINIB['indication']}")

    svg = mol_to_svg(OSIMERTINIB["smiles"], size=(260, 180))
    st.markdown(svg, unsafe_allow_html=True)

    props = get_reference_properties(OSIMERTINIB["smiles"])
    if props:
        st.markdown(f"""<div class="props">
            <div class="prop"><div class="prop-label">MW</div><div class="prop-val c-ok">{props['mw']} Da</div></div>
            <div class="prop"><div class="prop-label">cLogP</div><div class="prop-val c-ok">{props['logp']}</div></div>
            <div class="prop"><div class="prop-label">QED</div><div class="prop-val c-ok">{props['qed']}</div></div>
            <div class="prop"><div class="prop-label">TPSA</div><div class="prop-val c-ok">{props['tpsa']} A²</div></div>
        </div>""", unsafe_allow_html=True)


def render_agent_message(speaker: str, role: str, message: str, detail: str = ""):
    if speaker == "Designer":
        cls, role_cls = "msg-designer", "msg-role-a"
        label = "Agent A · 分子设计师"
    else:
        cls, role_cls = "msg-critic", "msg-role-b"
        label = "Agent B · ADMET 评审官"

    detail_html = f'<div style="color:var(--text-muted);font-size:0.78rem;margin-top:4px;">{detail}</div>' if detail else ""
    st.markdown(f"""<div class="msg {cls}">
        <div class="msg-role {role_cls}">{label}</div>
        <div style="color:var(--text-primary);">{message}</div>
        {detail_html}
    </div>""", unsafe_allow_html=True)


def _prop_grid_html(props: dict) -> str:
    mw = props.get("mw", 0)
    logp = props.get("logp", 0)
    qed = props.get("qed", 0)
    sa = props.get("sa_score", 10)

    mw_c = "c-good" if mw <= 500 else "c-warn" if mw <= 550 else "c-fail"
    logp_c = "c-good" if logp <= 5.0 else "c-warn" if logp <= 5.5 else "c-fail"
    qed_c = "c-good" if qed >= 0.3 else "c-warn" if qed >= 0.2 else "c-fail"
    sa_c = "c-good" if sa <= 5.0 else "c-warn" if sa <= 7.0 else "c-fail"

    return f"""<div class="props">
        <div class="prop"><div class="prop-label">MW</div><div class="prop-val {mw_c}">{mw} Da</div></div>
        <div class="prop"><div class="prop-label">cLogP</div><div class="prop-val {logp_c}">{logp}</div></div>
        <div class="prop"><div class="prop-label">QED</div><div class="prop-val {qed_c}">{qed}</div></div>
        <div class="prop"><div class="prop-label">SA</div><div class="prop-val {sa_c}">{sa}/10</div></div>
    </div>"""


def _score_breakdown_html(bd: dict) -> str:
    items = [
        ("3D结合", bd.get("binding_3d", 0), bd.get("binding_3d_max", 25)),
        ("Lipinski", bd.get("lipinski", 0), bd.get("lipinski_max", 20)),
        ("QED", bd.get("qed", 0), bd.get("qed_max", 15)),
        ("SA", bd.get("sa", 0), bd.get("sa_max", 10)),
        ("Veber", bd.get("veber", 0), bd.get("veber_max", 10)),
        ("PAINS", bd.get("pains", 0), bd.get("pains_max", 10)),
        ("相似度", bd.get("similarity", 0), bd.get("similarity_max", 10)),
    ]
    rows = ""
    for label, val, mx in items:
        pct = val / mx * 100 if mx else 0
        color = "var(--success)" if pct >= 80 else "var(--warning)" if pct >= 40 else "var(--danger)"
        rows += (
            f'<div style="display:flex;align-items:center;gap:8px;margin:3px 0;">'
            f'<span style="width:52px;font-size:0.7rem;color:var(--text-muted);text-align:right;">{label}</span>'
            f'<div style="flex:1;background:var(--bg-tertiary);border-radius:3px;height:14px;overflow:hidden;">'
            f'<div style="width:{pct:.0f}%;height:100%;background:{color};border-radius:3px;"></div></div>'
            f'<span style="width:40px;font-size:0.72rem;font-weight:600;color:var(--text-secondary);">{val:.0f}/{mx}</span>'
            f'</div>'
        )
    total = bd.get("total", 0)
    total_max = bd.get("total_max", 100)
    rows += (
        f'<div style="display:flex;align-items:center;gap:8px;margin:6px 0 0;padding-top:4px;border-top:1px solid var(--border-light);">'
        f'<span style="width:52px;font-size:0.72rem;font-weight:600;color:var(--text-primary);text-align:right;">总分</span>'
        f'<div style="flex:1;"></div>'
        f'<span style="width:40px;font-size:0.8rem;font-weight:700;color:var(--text-primary);">{total:.0f}/{total_max}</span>'
        f'</div>'
    )
    return f'<div style="margin:4px 0;">{rows}</div>'


def render_molecule_card(ev: dict, ref_smiles: str):
    verdict = ev.get("verdict", "FAIL")
    score = ev.get("score", 0)
    name = ev.get("name", "")
    smiles = ev.get("smiles", "")
    props = ev.get("properties", {})
    reasons = ev.get("reasons", [])
    suggestions = ev.get("suggestions", [])
    strategy = ev.get("strategy", "")
    breakdown = ev.get("breakdown", {})

    score_c = "c-good" if score >= 65 else "c-warn" if score >= 45 else "c-fail"

    st.markdown(f"""<div class="mol-card">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
                <p class="mol-name">{name}</p>
                <p class="mol-strategy">{strategy}</p>
            </div>
            <div style="text-align:right;">
                {_tag(verdict)}
                <span class="prop-val {score_c}" style="margin-left:8px;">{score:.0f}</span>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    svg = highlight_diff(ref_smiles, smiles, size=(300, 190))
    st.markdown(svg, unsafe_allow_html=True)

    if props:
        st.markdown(_prop_grid_html(props), unsafe_allow_html=True)

    if breakdown:
        with st.expander("评分分解", expanded=False):
            st.markdown(_score_breakdown_html(breakdown), unsafe_allow_html=True)

    if reasons and reasons[0] != "All criteria satisfied":
        with st.expander("问题与建议", expanded=False):
            for r in reasons:
                st.markdown(f"- {r}")
            for s in suggestions:
                st.markdown(f"- *{s}*")


def render_round_results(round_result):
    rn = round_result.round_number
    critic = round_result.critic_output
    s = critic["stats"]

    label = f"第 {rn} 轮  |  通过 {s['n_passed']}  ·  有条件 {s['n_conditional']}  ·  未通过 {s['n_failed']}  |  均分 {s['avg_score']}"

    with st.expander(label, expanded=(rn == 1)):
        for msg in round_result.conversation:
            render_agent_message(msg["speaker"], msg["role"], msg["message"], msg.get("detail", ""))

        st.markdown("---")
        evaluations = critic["evaluations"]
        ref_smi = OSIMERTINIB["smiles"]

        for i in range(0, len(evaluations), 2):
            cols = st.columns(2)
            for j, col in enumerate(cols):
                if i + j < len(evaluations):
                    with col:
                        render_molecule_card(evaluations[i + j], ref_smi)


def render_summary(summary):
    st.markdown("## 结果总览")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="stat-card"><div class="stat-num" style="color:var(--brand);">{summary.total_generated}</div><div class="stat-label">已生成</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card"><div class="stat-num" style="color:var(--success);">{summary.total_passed}</div><div class="stat-label">通过</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-card"><div class="stat-num" style="color:var(--warning);">{summary.total_conditional}</div><div class="stat-label">有条件</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="stat-card"><div class="stat-num" style="color:var(--danger);">{summary.total_failed}</div><div class="stat-label">未通过</div></div>', unsafe_allow_html=True)

    if summary.round_stats:
        st.markdown("### 迭代趋势")
        fig = render_score_trajectory(summary.round_stats)
        st.pyplot(fig)

    if summary.best_candidates:
        st.markdown("### 最优候选分子")
        rows = []
        for c in summary.best_candidates:
            p = c.get("properties", {})
            rows.append({
                "名称": c.get("name", ""),
                "评分": c.get("score", 0),
                "结论": c.get("verdict", ""),
                "MW (Da)": p.get("mw", ""),
                "cLogP": p.get("logp", ""),
                "QED": p.get("qed", ""),
                "SA": p.get("sa_score", ""),
                "TPSA (A²)": p.get("tpsa", ""),
                "相似度": c.get("similarity", ""),
            })
        df = pd.DataFrame(rows)
        col_config = {
            "评分": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%d"),
            "MW (Da)": st.column_config.NumberColumn(format="%.1f"),
            "cLogP": st.column_config.NumberColumn(format="%.2f"),
            "QED": st.column_config.NumberColumn(format="%.3f"),
            "SA": st.column_config.NumberColumn(format="%.2f"),
            "TPSA (A²)": st.column_config.NumberColumn(format="%.1f"),
            "相似度": st.column_config.NumberColumn(format="%.3f"),
        }
        st.dataframe(df, use_container_width=True, hide_index=True, column_config=col_config)

        best = summary.best_candidates[0]
        if best.get("radar"):
            st.markdown("### 最优候选 vs 奥希替尼")
            col_r, col_m = st.columns([1, 1])
            with col_r:
                fig = render_radar_chart(
                    best["radar"]["candidate"],
                    best["radar"]["reference"],
                    candidate_name=best.get("name", "候选"),
                    ref_name="奥希替尼",
                )
                st.pyplot(fig)
            with col_m:
                svg = highlight_diff(OSIMERTINIB["smiles"], best["smiles"], size=(340, 260))
                st.markdown(svg, unsafe_allow_html=True)
                st.markdown(f"**{best.get('name', '')}** — 评分 {best['score']}")


# ──────────────────────────────────────────────
# Tab 2: 单分子评估
# ──────────────────────────────────────────────

_PROP_META = [
    ("mw",              "分子量",         "Da",  200, 500),
    ("logp",            "cLogP",          "",    -1,  5.0),
    ("tpsa",            "TPSA",           "Å²",  20, 140),
    ("hbd",             "氢键供体",       "",     0,   5),
    ("hba",             "氢键受体",       "",     0,  10),
    ("rotatable_bonds", "可旋转键",       "",     0,  10),
    ("aromatic_rings",  "芳香环",         "",     0,   4),
    ("num_rings",       "环数",           "",     0,   5),
    ("heavy_atoms",     "重原子数",       "",    10,  40),
    ("fsp3",            "Fsp3",           "",   0.0, 1.0),
    ("qed",             "QED",            "",   0.0, 1.0),
    ("sa_score",        "SA Score",       "/10", 1.0,10.0),
]


def _rule_row(label: str, passed: bool, detail: str = "") -> str:
    icon = "✓" if passed else "✗"
    color = "var(--success)" if passed else "var(--danger)"
    det = f'<span style="color:var(--text-muted);font-size:0.72rem;margin-left:6px;">{detail}</span>' if detail else ""
    return (
        f'<div style="display:flex;align-items:center;gap:6px;padding:4px 0;'
        f'border-bottom:1px solid var(--border-light);">'
        f'<span style="color:{color};font-weight:700;font-size:0.85rem;width:18px;">{icon}</span>'
        f'<span style="font-size:0.8rem;color:var(--text-primary);">{label}</span>'
        f'{det}</div>'
    )


def render_full_evaluation(ev: dict):
    if not ev.get("valid", False):
        st.error("无效的 SMILES，无法解析分子结构")
        return

    props = ev["properties"]
    smiles = ev["smiles"]

    col_mol, col_props = st.columns([1, 1])

    with col_mol:
        st.markdown("#### 分子结构")
        svg = mol_to_svg(smiles, size=(360, 260))
        st.markdown(svg, unsafe_allow_html=True)
        st.code(smiles, language=None)

        st.markdown("#### 药效团匹配")
        _render_pharmacophore_matches(smiles)

    with col_props:
        st.markdown("#### 分子属性")
        rows_html = ""
        for key, label, unit, lo, hi in _PROP_META:
            val = props.get(key, "—")
            if isinstance(val, float):
                display = f"{val:.2f}" if val < 10 else f"{val:.1f}"
            else:
                display = str(val)
            if isinstance(val, (int, float)):
                sa_invert = key == "sa_score"
                if sa_invert:
                    in_range = val <= 5.0
                    warn = val <= 7.0
                else:
                    in_range = lo <= val <= hi
                    rng = hi - lo if hi != lo else 1
                    warn = abs(val - hi) < rng * 0.25 or abs(val - lo) < rng * 0.25
                color_cls = "c-good" if in_range else ("c-warn" if warn else "c-fail")
            else:
                color_cls = "c-ok"
            unit_str = f' <span style="font-size:0.65rem;color:var(--text-muted);">{unit}</span>' if unit else ""
            rows_html += (
                f'<div style="display:flex;justify-content:space-between;padding:5px 8px;'
                f'border-bottom:1px solid var(--border-light);">'
                f'<span style="font-size:0.8rem;color:var(--text-secondary);">{label}</span>'
                f'<span class="prop-val {color_cls}" style="font-size:0.82rem;">{display}{unit_str}</span>'
                f'</div>'
            )
        st.markdown(f'<div style="background:var(--bg-secondary);border-radius:6px;overflow:hidden;border:1px solid var(--border);">{rows_html}</div>', unsafe_allow_html=True)

    st.markdown("---")

    col_rules, col_score = st.columns([1, 1])

    with col_rules:
        st.markdown("#### 规则检查")
        lipinski = ev.get("lipinski", {})
        veber = ev.get("veber", {})
        pains = ev.get("pains", {})
        brenk = ev.get("brenk", {})
        struct = ev.get("structural_alerts", {})

        lip_detail = f"{lipinski.get('n_violations', 0)} 项违规" if not lipinski.get("passed") else ""
        rules_html = _rule_row("Lipinski Ro5", lipinski.get("passed", False), lip_detail)
        if lipinski.get("violations"):
            for v in lipinski["violations"]:
                rules_html += f'<div style="padding:2px 0 2px 24px;font-size:0.72rem;color:var(--danger);">{v}</div>'

        rules_html += _rule_row("Veber", veber.get("passed", False))
        if veber.get("violations"):
            for v in veber["violations"]:
                rules_html += f'<div style="padding:2px 0 2px 24px;font-size:0.72rem;color:var(--danger);">{v}</div>'

        pains_ok = not pains.get("has_alerts", False)
        rules_html += _rule_row("PAINS", pains_ok, "" if pains_ok else f"{len(pains.get('alerts', []))} 项警告")
        if pains.get("alerts"):
            for a in pains["alerts"][:3]:
                rules_html += f'<div style="padding:2px 0 2px 24px;font-size:0.72rem;color:var(--warning);">{a}</div>'

        brenk_ok = not brenk.get("has_alerts", False)
        rules_html += _rule_row("BRENK", brenk_ok, "" if brenk_ok else f"{len(brenk.get('alerts', []))} 项警告")
        if brenk.get("alerts"):
            for a in brenk["alerts"][:3]:
                rules_html += f'<div style="padding:2px 0 2px 24px;font-size:0.72rem;color:var(--warning);">{a}</div>'

        struct_ok = not struct.get("has_alerts", False)
        rules_html += _rule_row("结构警报", struct_ok)
        if struct.get("alerts"):
            for a in struct["alerts"]:
                rules_html += f'<div style="padding:2px 0 2px 24px;font-size:0.72rem;color:var(--warning);">{a}</div>'

        st.markdown(rules_html, unsafe_allow_html=True)

    with col_score:
        st.markdown("#### 评分分解")
        bd = ev.get("breakdown", {})
        if bd:
            st.markdown(_score_breakdown_html(bd), unsafe_allow_html=True)

        verdict = ev.get("verdict", "FAIL")
        score = ev.get("score", 0)
        score_c = "c-good" if score >= 65 else "c-warn" if score >= 45 else "c-fail"
        st.markdown(
            f'<div style="text-align:center;margin-top:1rem;padding:1rem;background:var(--bg-secondary);border-radius:8px;border:1px solid var(--border);">'
            f'<div style="font-size:0.75rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.05em;">综合评定</div>'
            f'<div class="prop-val {score_c}" style="font-size:2rem;margin:4px 0;">{score:.0f}</div>'
            f'{_tag(verdict)}</div>',
            unsafe_allow_html=True,
        )

    b3d = ev.get("binding_3d")
    sim = ev.get("similarity", 0)
    if sim is not None or b3d:
        st.markdown("---")
        col_radar, col_diff = st.columns([1, 1])
        with col_radar:
            st.markdown(f"#### 与奥希替尼对比  (Tanimoto = {sim:.3f})")
            if b3d:
                st.markdown(
                    f'<div class="ai-stats">'
                    f'<span>USRCAT: <b>{b3d["usrcat_similarity"]:.3f}</b></span>'
                    f'<span>3D形状: <b>{b3d["shape_similarity"]:.3f}</b></span>'
                    f'<span>结合代理: <b class="stat">{b3d["binding_proxy_score"]:.3f}</b></span>'
                    f'</div>', unsafe_allow_html=True,
                )
            radar = ev.get("radar")
            if radar:
                fig = render_radar_chart(radar["candidate"], radar["reference"], ref_name="奥希替尼")
                st.pyplot(fig)
        with col_diff:
            st.markdown("#### 结构差异")
            diff_svg = highlight_diff(OSIMERTINIB["smiles"], smiles, size=(360, 260))
            st.markdown(diff_svg, unsafe_allow_html=True)


def _render_pharmacophore_matches(smiles: str):
    from rdkit import Chem
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return

    rows = ""
    for key, info in PHARMACOPHORE.items():
        pat = Chem.MolFromSmarts(info["smarts"])
        matched = mol.HasSubstructMatch(pat) if pat else False
        icon = "✓" if matched else "—"
        color = "var(--success)" if matched else "var(--text-muted)"
        mod_label = {True: "可修饰", False: "不可修饰", "conservative": "保守修饰"}.get(info["modifiable"], "—")
        rows += (
            f'<div style="display:flex;align-items:center;gap:6px;padding:4px 0;'
            f'border-bottom:1px solid var(--border-light);font-size:0.78rem;">'
            f'<span style="color:{color};font-weight:700;width:18px;">{icon}</span>'
            f'<span style="color:var(--text-primary);flex:1;">{info["role"].split("—")[0].strip()}</span>'
            f'<span style="color:var(--text-muted);font-size:0.68rem;">{mod_label}</span>'
            f'</div>'
        )
    st.markdown(rows, unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Tab 3: 分子对比
# ──────────────────────────────────────────────

def render_comparison_table():
    rows = []
    for tki in REFERENCE_TKIS:
        p = get_reference_properties(tki["smiles"])
        if p is None:
            continue
        rows.append({
            "药物": tki["name"],
            "代际": tki.get("generation", ""),
            "靶点": tki.get("target", ""),
            "机制": tki.get("mechanism", ""),
            "年份": tki.get("year", ""),
            "MW (Da)": p["mw"],
            "cLogP": p["logp"],
            "TPSA (Å²)": p["tpsa"],
            "HBD": p["hbd"],
            "HBA": p["hba"],
            "旋转键": p["rotatable_bonds"],
            "QED": p["qed"],
            "Fsp3": p["fsp3"],
            "SA": p.get("sa_score", "—"),
        })
    if not rows:
        st.info("无法加载参考药物数据")
        return

    df = pd.DataFrame(rows)
    col_config = {
        "MW (Da)": st.column_config.NumberColumn(format="%.1f"),
        "cLogP": st.column_config.NumberColumn(format="%.2f"),
        "TPSA (Å²)": st.column_config.NumberColumn(format="%.1f"),
        "QED": st.column_config.NumberColumn(format="%.3f"),
        "Fsp3": st.column_config.NumberColumn(format="%.3f"),
    }
    st.dataframe(df, use_container_width=True, hide_index=True, column_config=col_config)


def render_tki_gallery():
    for i in range(0, len(REFERENCE_TKIS), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            idx = i + j
            if idx >= len(REFERENCE_TKIS):
                break
            tki = REFERENCE_TKIS[idx]
            with col:
                st.markdown(f"""<div class="mol-card">
                    <p class="mol-name">{tki['name']}</p>
                    <p class="mol-strategy">{tki.get('generation','')} · {tki.get('target','')} · {tki.get('year','')}</p>
                </div>""", unsafe_allow_html=True)
                svg = mol_to_svg(tki["smiles"], size=(300, 190))
                st.markdown(svg, unsafe_allow_html=True)
                st.caption(tki.get("mechanism", ""))


def render_tki_multi_radar():
    ref_props_base = get_reference_properties(OSIMERTINIB["smiles"])
    if ref_props_base is None:
        return

    molecules_for_radar = []
    for tki in REFERENCE_TKIS:
        p = get_reference_properties(tki["smiles"])
        if p is None:
            continue
        radar_data = generate_radar_data(p, ref_props_base)
        molecules_for_radar.append({"name": tki["name"].split("(")[0].strip(), "radar": radar_data["candidate"]})

    if molecules_for_radar:
        fig = render_multi_radar(molecules_for_radar)
        st.pyplot(fig)


def render_feedback_detail(feedback: dict):
    if not feedback:
        return
    html = '<div style="font-size:0.8rem;">'
    if feedback.get("successful_strategies"):
        html += '<div style="margin-bottom:6px;"><span style="color:var(--success);font-weight:600;">成功策略:</span> '
        html += ", ".join(feedback["successful_strategies"]) + "</div>"
    if feedback.get("avoid_strategies"):
        html += '<div style="margin-bottom:6px;"><span style="color:var(--danger);font-weight:600;">应避免:</span> '
        html += ", ".join(feedback["avoid_strategies"]) + "</div>"
    if feedback.get("prioritize"):
        html += '<div style="margin-bottom:6px;"><span style="color:var(--brand);font-weight:600;">优化方向:</span><ul style="margin:2px 0;padding-left:1.2em;">'
        for p in feedback["prioritize"]:
            html += f"<li>{p}</li>"
        html += "</ul></div>"
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def build_export_dataframe(summary) -> pd.DataFrame:
    rows = []
    for c in summary.all_passed:
        p = c.get("properties", {})
        b3d = c.get("binding_3d") or {}
        rows.append({
            "名称": c.get("name", ""),
            "SMILES": c.get("smiles", ""),
            "评分": c.get("score", 0),
            "结论": c.get("verdict", ""),
            "策略": c.get("strategy", ""),
            "MW": p.get("mw", ""),
            "cLogP": p.get("logp", ""),
            "TPSA": p.get("tpsa", ""),
            "HBD": p.get("hbd", ""),
            "HBA": p.get("hba", ""),
            "旋转键": p.get("rotatable_bonds", ""),
            "QED": p.get("qed", ""),
            "SA": p.get("sa_score", ""),
            "Fsp3": p.get("fsp3", ""),
            "Tanimoto": c.get("similarity", ""),
            "3D结合": b3d.get("binding_proxy_score", ""),
        })
    return pd.DataFrame(rows)


# ──────────────────────────────────────────────
# AI 透明展示
# ──────────────────────────────────────────────

def render_ai_contribution(designer_output: dict):
    ai_contrib = designer_output.get("ai_contribution", "")
    sar_reasoning = designer_output.get("sar_reasoning", "")
    llm_invalid = designer_output.get("llm_invalid", [])

    if not ai_contrib and not sar_reasoning:
        return

    html = '<div class="ai-stats">'
    if ai_contrib:
        html += f'<span class="stat">{ai_contrib}</span>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

    if sar_reasoning:
        st.markdown(
            f'<div style="font-size:0.78rem;color:var(--text-secondary);padding:6px 10px;'
            f'background:#F5F3FF;border-radius:4px;border-left:3px solid #7C3AED;margin:6px 0;">'
            f'<b style="color:#7C3AED;">AI SAR 分析:</b> {sar_reasoning}</div>',
            unsafe_allow_html=True,
        )

    if llm_invalid:
        with st.expander(f"AI 无效 SMILES（{len(llm_invalid)} 个）", expanded=False):
            for inv in llm_invalid:
                st.code(inv.get("smiles", ""), language=None)


# ──────────────────────────────────────────────
# SAR 探索
# ──────────────────────────────────────────────

def render_sar_explorer(sar_data: dict):
    from chemistry.sar import sar_to_heatmap_data, POSITIONS

    property_options = {
        "综合评分": "score",
        "3D 结合力": "binding_proxy_score",
        "分子量 (MW)": "mw",
        "cLogP": "logp",
        "QED": "qed",
        "SA Score": "sa_score",
        "TPSA": "tpsa",
    }
    selected_label = st.selectbox("选择展示属性", list(property_options.keys()))
    prop_key = property_options[selected_label]

    heatmaps = sar_to_heatmap_data(sar_data, prop_key)

    for hm in heatmaps:
        fig = render_sar_heatmap(hm, property_label=selected_label)
        st.pyplot(fig)

    st.markdown("---")
    st.markdown("##### 分子详情")

    all_mols = sar_data.get("all_molecules", [])
    if not all_mols:
        return

    mol_names = [f"{m['position']} — {m['r_group']} ({m['score']:.0f}分)" for m in all_mols]
    selected_idx = st.selectbox("选择分子", range(len(mol_names)), format_func=lambda i: mol_names[i])
    selected = all_mols[selected_idx]

    col_svg, col_detail = st.columns([1, 1])
    with col_svg:
        diff_svg = highlight_diff(OSIMERTINIB["smiles"], selected["smiles"], size=(320, 220))
        st.markdown(diff_svg, unsafe_allow_html=True)
        st.code(selected["smiles"], language=None)

    with col_detail:
        verdict = selected.get("verdict", "FAIL")
        score = selected.get("score", 0)
        score_c = "c-good" if score >= 65 else "c-warn" if score >= 45 else "c-fail"
        st.markdown(
            f'{_tag(verdict)} <span class="prop-val {score_c}" style="margin-left:8px;">{score:.0f}</span>',
            unsafe_allow_html=True,
        )

        bd = selected.get("breakdown", {})
        if bd:
            st.markdown(_score_breakdown_html(bd), unsafe_allow_html=True)

        delta = selected.get("delta", {})
        if delta:
            delta_html = '<div style="margin-top:8px;font-size:0.78rem;"><b>vs 奥希替尼 变化:</b><br>'
            delta_labels = {"mw": "MW", "logp": "LogP", "tpsa": "TPSA", "qed": "QED", "sa_score": "SA", "fsp3": "Fsp3"}
            for k, label in delta_labels.items():
                if k in delta:
                    v = delta[k]
                    sign = "+" if v > 0 else ""
                    color = "var(--text-secondary)"
                    delta_html += f'<span style="margin-right:10px;color:{color};">{label}: {sign}{v:.2f}</span>'
            delta_html += "</div>"
            st.markdown(delta_html, unsafe_allow_html=True)


def render_chemical_space_tab(space_data: dict):
    fig = render_chemical_space(space_data)
    st.pyplot(fig)
    st.caption("圆点为候选分子（按评分着色），方块为参考药物。距离越近表示结构越相似。")
