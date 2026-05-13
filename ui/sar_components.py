from __future__ import annotations
import streamlit as st


AGENT_META = {
    "结构-活性分析": {"dot_cls": "sa", "icon": "🔬", "en": "Structure-Activity"},
    "多参数优化": {"dot_cls": "mpo", "icon": "⚖️", "en": "Multi-Parameter Optimization"},
    "风险评估": {"dot_cls": "risk", "icon": "🛡️", "en": "Risk & Feasibility"},
}


def render_header():
    st.markdown("""
    <div class="sar-header">
        <div>
            <h1>SAR Deliberation</h1>
            <div class="subtitle">Multi-Agent Structure-Activity Relationship Analysis</div>
            <div style="font-size:13px;color:#999;margin-top:8px;max-width:720px;line-height:1.6;">
                场景：EGFR C797S 三重突变耐药（L858R/T790M/C797S），目前无批准的第四代抑制剂。
                基于 Zhu et al. 2023 发现的先导化合物 C34（IC₅₀=5.1nM），
                用多智能体结构化审议辅助下一轮合成决策。
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_overview_cards(molecules: list[dict], ref_props: dict):
    n = len(molecules)
    passed = sum(1 for m in molecules if m["verdict"] == "PASS")
    conditional = sum(1 for m in molecules if m["verdict"] == "CONDITIONAL")
    best = max(molecules, key=lambda x: x["score"]) if molecules else None
    avg_score = round(sum(m["score"] for m in molecules) / max(n, 1), 1)
    positions = len({m["position"] for m in molecules})

    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-card">
            <div class="stat-label">Molecules</div>
            <div class="stat-value">{n}</div>
            <div class="stat-sub">{positions} modification positions</div>
        </div>
        <div class="stat-card accent">
            <div class="stat-label">Passed</div>
            <div class="stat-value">{passed}</div>
            <div class="stat-sub">{conditional} conditional</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Avg Score</div>
            <div class="stat-value">{avg_score}</div>
            <div class="stat-sub">out of 100</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Best</div>
            <div class="stat-value">{best['score'] if best else 0}</div>
            <div class="stat-sub">{best['name'][:20] if best else '—'}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_progress(current_step: int):
    steps = [
        ("Round 1", "独立分析"),
        ("Round 2", "交叉质疑"),
        ("Round 3", "收敛决策"),
    ]
    items = []
    for i, (name, desc) in enumerate(steps):
        if i < current_step:
            dot_cls = "done"
            step_cls = "done"
        elif i == current_step:
            dot_cls = "active"
            step_cls = "active"
        else:
            dot_cls = ""
            step_cls = ""
        items.append(
            f'<div class="progress-step {step_cls}">'
            f'<div class="progress-dot {dot_cls}"></div>'
            f'{name} <span style="font-weight:400;color:var(--text-muted)">{desc}</span></div>'
        )
        if i < len(steps) - 1:
            line_cls = "done" if i < current_step else ""
            items.append(f'<div class="progress-line {line_cls}"></div>')

    st.markdown(
        f'<div class="progress-bar">{"".join(items)}</div>',
        unsafe_allow_html=True,
    )


def _md_to_html(text: str) -> str:
    import re
    lines = text.replace("\n\n", "\n").split("\n")
    parts = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
        if line.startswith("•"):
            parts.append(f'<div class="agent-bullet">{line}</div>')
        elif line.startswith(("<strong>", "1.", "2.", "3.")):
            parts.append(f'<div class="agent-heading">{line}</div>')
        elif line.startswith("易") or line.startswith("难"):
            parts.append(f'<div class="agent-chain">{line}</div>')
        else:
            parts.append(f'<p>{line}</p>')
    return "".join(parts)


def render_agent_card(agent_name: str, content: str):
    meta = AGENT_META.get(agent_name, {"dot_cls": "sa", "icon": "🔬", "en": agent_name})
    body_html = _md_to_html(content)

    st.markdown(f"""
    <div class="agent-card">
        <div class="agent-card-header">
            <div class="agent-dot {meta['dot_cls']}"></div>
            <div class="agent-name">{meta['icon']} {agent_name}</div>
        </div>
        <div class="agent-card-body">
            {body_html}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_round(round_number: int, agent_outputs: dict[str, str], duration: float = 0):
    titles = {
        1: ("Round 1", "独立分析"),
        2: ("Round 2", "交叉质疑"),
    }
    name, desc = titles.get(round_number, (f"Round {round_number}", ""))
    dur_text = f"{duration}s" if duration else ""

    st.markdown(f"""
    <div class="round-section">
        <div class="round-header">
            <span class="round-badge">{name}</span>
            <span class="round-title">{desc}</span>
            <span class="round-duration">{dur_text}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(3)
    agent_order = ["结构-活性分析", "多参数优化", "风险评估"]
    for i, agent_name in enumerate(agent_order):
        content = agent_outputs.get(agent_name, "")
        with cols[i]:
            render_agent_card(agent_name, content)


def render_convergence(convergence_text: str):
    import re
    sections = convergence_text.split("【")
    body_parts = []
    for section in sections:
        if not section.strip():
            continue
        section = "【" + section
        title_end = section.find("】")
        if title_end > 0:
            title = section[1:title_end]
            body = section[title_end + 1:].strip()
            body_lines = body.replace("\n\n", "\n").split("\n")
            html_lines = []
            for line in body_lines:
                line = line.strip()
                if not line:
                    continue
                line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
                html_lines.append(f"<p>{line}</p>")
            body_parts.append(f"<h4 style='margin:16px 0 8px;font-size:15px;font-weight:600;'>【{title}】</h4>{''.join(html_lines)}")
        else:
            body_parts.append(f"<p>{section.strip()}</p>")

    st.markdown(f"""
    <div class="round-section">
        <div class="round-header">
            <span class="round-badge" style="background:var(--accent);color:var(--text);">Round 3</span>
            <span class="round-title">收敛决策</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="convergence-card">
        <h3>Multi-Agent Consensus</h3>
        <div class="convergence-body">
            {"".join(body_parts)}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_molecule_table(molecules: list[dict]):
    import pandas as pd
    sorted_mols = sorted(molecules, key=lambda x: x["score"], reverse=True)
    rows = []
    for m in sorted_mols:
        p = m.get("properties", {})
        rows.append({
            "Name": m["name"],
            "Position": m["position"],
            "Score": m["score"],
            "Verdict": m["verdict"],
            "MW": round(p.get("mw", 0), 1),
            "LogP": round(p.get("logp", 0), 2),
            "QED": round(p.get("qed", 0), 3),
            "SA": round(p.get("sa_score", 0), 2),
        })
    df = pd.DataFrame(rows)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Score": st.column_config.NumberColumn(format="%.1f"),
            "Verdict": st.column_config.TextColumn(),
        },
    )


def render_traces(traces: list[dict]):
    if not traces:
        return

    agent_dot_cls = {
        "结构-活性分析": "sa",
        "多参数优化": "mpo",
        "风险评估": "risk",
    }

    st.markdown(f"""
    <div class="trace-container">
        <div style="font-size:13px;font-weight:600;color:var(--text);margin-bottom:12px;">
            Execution Traces ({len(traces)} calls)
        </div>
    </div>
    """, unsafe_allow_html=True)

    for i, t in enumerate(traces):
        agent = t.get("agent", "")
        dot_cls = agent_dot_cls.get(agent, "sa")
        output = t.get("output", "")
        duration = t.get("duration", 0)
        header = f"Round {t['round']} · {agent} · {duration}s"

        with st.expander(header, expanded=False):
            st.markdown(
                f'<div class="trace-detail">'
                f'<div class="trace-color-bar {dot_cls}"></div>'
                f'<div class="trace-content">{_md_to_html(output)}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )


# ── Helpers ──────────────────────────────────────────────

_PLOTLY_CONFIG = {"displayModeBar": False}


def _prop_cls(value, lo, hi) -> str:
    if lo < hi:
        return "good" if value <= lo else "warn" if value <= hi else "bad"
    return "good" if value >= lo else "warn" if value >= hi else "bad"


def _sar_prop_grid_html(props: dict) -> str:
    items = [
        ("MW", f"{props.get('mw', 0):.1f}", _prop_cls(props.get("mw", 0), 500, 550)),
        ("cLogP", f"{props.get('logp', 0):.2f}", _prop_cls(props.get("logp", 0), 5.0, 5.5)),
        ("TPSA", f"{props.get('tpsa', 0):.1f}", ""),
        ("QED", f"{props.get('qed', 0):.3f}", _prop_cls(props.get("qed", 0), 0.3, 0.2)),
        ("SA", f"{props.get('sa_score', 10):.2f}", _prop_cls(props.get("sa_score", 10), 5.0, 7.0)),
        ("Fsp3", f"{props.get('fsp3', 0):.3f}", ""),
    ]
    cells = "".join(
        f'<div class="sar-prop-item">'
        f'<div class="sar-prop-label">{lbl}</div>'
        f'<div class="sar-prop-value {cls}">{val}</div>'
        f'</div>'
        for lbl, val, cls in items
    )
    return f'<div class="sar-prop-grid">{cells}</div>'


def _sar_score_breakdown_html(bd: dict) -> str:
    items = [
        ("3D Bind", bd.get("binding_3d", 0), bd.get("binding_3d_max", 25)),
        ("Lipinski", bd.get("lipinski", 0), bd.get("lipinski_max", 20)),
        ("QED", bd.get("qed", 0), bd.get("qed_max", 15)),
        ("SA", bd.get("sa", 0), bd.get("sa_max", 10)),
        ("Veber", bd.get("veber", 0), bd.get("veber_max", 10)),
        ("PAINS", bd.get("pains", 0), bd.get("pains_max", 10)),
        ("Similarity", bd.get("similarity", 0), bd.get("similarity_max", 10)),
    ]
    rows = ""
    for label, val, mx in items:
        pct = val / mx * 100 if mx else 0
        color = "#22C55E" if pct >= 80 else "#F59E0B" if pct >= 40 else "#EF4444"
        rows += (
            f'<div class="sar-bd-row">'
            f'<span class="sar-bd-label">{label}</span>'
            f'<div class="sar-bd-track">'
            f'<div class="sar-bd-fill" style="width:{pct:.0f}%;background:{color};"></div></div>'
            f'<span class="sar-bd-val">{val:.0f}/{mx}</span>'
            f'</div>'
        )
    total = bd.get("total", 0)
    total_max = bd.get("total_max", 100)
    rows += (
        f'<div class="sar-bd-total">'
        f'<span class="sar-bd-label">Total</span>'
        f'<div style="flex:1"></div>'
        f'<span class="sar-bd-val">{total:.0f}/{total_max}</span>'
        f'</div>'
    )
    return f'<div class="sar-breakdown">{rows}</div>'


# ── Feature 1: Molecule Detail ──────────────────────────

def render_molecule_detail(molecule: dict, ref_props: dict, ref_smiles: str):
    from chemistry.visualizer import highlight_diff, render_radar_chart
    from chemistry.evaluator import generate_radar_data

    name = molecule.get("name", "Unknown")
    score = molecule.get("score", 0)
    verdict = molecule.get("verdict", "FAIL")
    position = molecule.get("position", "")
    similarity = molecule.get("similarity", 0)
    v_cls = "tag-pass" if verdict == "PASS" else "tag-conditional" if verdict == "CONDITIONAL" else "tag-fail"

    st.markdown(
        f'<div class="mol-detail-card">'
        f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">'
        f'<div>'
        f'<div style="font-size:18px;font-weight:600;color:#1A1A1A;">{name}</div>'
        f'<div style="font-size:12px;color:#999;margin-top:2px;">{position} · Similarity: {similarity:.3f}</div>'
        f'</div>'
        f'<div style="display:flex;align-items:center;gap:10px;">'
        f'<span style="font-size:32px;font-weight:700;color:#1A1A1A;font-variant-numeric:tabular-nums;">{score}</span>'
        f'<span class="tag {v_cls}">{verdict}</span>'
        f'</div></div></div>',
        unsafe_allow_html=True,
    )

    col_struct, col_radar = st.columns(2)

    with col_struct:
        svg = highlight_diff(ref_smiles, molecule["smiles"], size=(450, 320))
        st.markdown(svg, unsafe_allow_html=True)

    with col_radar:
        radar = generate_radar_data(
            molecule["properties"], ref_props, molecule.get("binding_3d"),
        )
        fig = render_radar_chart(
            radar["candidate"], radar["reference"],
            candidate_name=name[:20], ref_name="C34 (Reference)",
        )
        st.plotly_chart(fig, use_container_width=True, config=_PLOTLY_CONFIG)

    props_html = _sar_prop_grid_html(molecule["properties"])
    bd_html = _sar_score_breakdown_html(molecule.get("breakdown", {}))
    st.markdown(props_html, unsafe_allow_html=True)
    st.markdown(bd_html, unsafe_allow_html=True)


# ── Feature 2: SAR Heatmap ──────────────────────────────

def render_sar_heatmap_section(sar_data: dict):
    from chemistry.sar import sar_to_heatmap_data
    from chemistry.visualizer import render_sar_heatmap

    prop_options = {
        "Score": "score",
        "3D Binding": "binding_proxy_score",
        "MW": "mw",
        "cLogP": "logp",
        "QED": "qed",
        "SA Score": "sa_score",
        "TPSA": "tpsa",
    }
    selected_label = st.selectbox(
        "Property", list(prop_options.keys()), key="heatmap_prop",
    )
    prop_key = prop_options[selected_label]

    heatmap_list = sar_to_heatmap_data(sar_data, prop_key)
    for hm in heatmap_list:
        fig = render_sar_heatmap(hm, property_label=selected_label)
        st.plotly_chart(fig, use_container_width=True, config=_PLOTLY_CONFIG)


# ── Feature 3: Custom SMILES Input ──────────────────────

def render_smiles_input(ref_smiles: str, ref_props: dict):
    smiles_input = st.text_input(
        "SMILES", placeholder="e.g. CC(=O)Oc1ccccc1C(=O)O", key="custom_smiles",
    )

    if st.button("Evaluate", key="eval_smiles") and smiles_input:
        from chemistry.evaluator import evaluate_candidate
        with st.spinner("Evaluating..."):
            ev = evaluate_candidate(smiles_input.strip(), ref_smiles)

        if not ev.get("valid", True):
            st.error(f"Invalid SMILES: {ev.get('error', 'could not parse')}")
            return

        mol_dict = {
            "name": "Custom",
            "position": "custom",
            "smiles": smiles_input.strip(),
            "properties": ev["properties"],
            "score": ev["score"],
            "verdict": ev["verdict"],
            "breakdown": ev.get("breakdown", {}),
            "binding_3d": ev.get("binding_3d"),
            "similarity": ev.get("similarity", 0),
        }
        render_molecule_detail(mol_dict, ref_props, ref_smiles)


# ── Feature 4: Comparison Panel ─────────────────────────

def render_comparison_panel(molecules: list[dict], ref_smiles: str, ref_props: dict):
    from chemistry.visualizer import highlight_diff, render_multi_radar
    from chemistry.evaluator import generate_radar_data

    mol_names = [f"{m['name']} ({m['position']}) — {m['score']}" for m in molecules]
    selected = st.multiselect(
        "Select molecules", mol_names, max_selections=3, key="compare_mols",
    )

    if len(selected) < 2:
        return

    sel_mols = [molecules[mol_names.index(s)] for s in selected]

    cols = st.columns(len(sel_mols))
    for i, mol in enumerate(sel_mols):
        with cols[i]:
            score = mol["score"]
            v = mol["verdict"]
            s_color = "#22C55E" if v == "PASS" else "#F59E0B" if v == "CONDITIONAL" else "#EF4444"
            svg = highlight_diff(ref_smiles, mol["smiles"])
            st.markdown(
                f'<div class="compare-col">'
                f'<div class="mol-name">{mol["name"][:18]}</div>'
                f'<div class="mol-position">{mol["position"]}</div>'
                f'<div class="mol-score" style="color:{s_color}">{score}</div>'
                f'{svg}'
                f'</div>',
                unsafe_allow_html=True,
            )

    import pandas as pd
    prop_keys = ["mw", "logp", "tpsa", "qed", "sa_score", "hbd", "hba"]
    prop_labels = ["MW", "cLogP", "TPSA", "QED", "SA Score", "HBD", "HBA"]
    data = {}
    for mol in sel_mols:
        p = mol["properties"]
        data[mol["name"][:15]] = [round(p.get(k, 0), 2) for k in prop_keys]
    df = pd.DataFrame(data, index=prop_labels)
    st.dataframe(df, use_container_width=True)

    radar_mols = []
    for mol in sel_mols:
        radar = generate_radar_data(mol["properties"], ref_props, mol.get("binding_3d"))
        radar_mols.append({"name": mol["name"][:15], "radar": radar["candidate"]})
    fig = render_multi_radar(radar_mols)
    st.plotly_chart(fig, use_container_width=True, config=_PLOTLY_CONFIG)
