from __future__ import annotations
import json
import streamlit as st
from ui.styles_sar import SAR_CSS
from ui.sar_components import (
    render_header, render_overview_cards, render_progress,
    render_round, render_convergence, render_molecule_table,
    render_traces,
    render_molecule_detail, render_sar_heatmap_section,
    render_smiles_input, render_comparison_panel,
)
from chemistry.molecules import REFERENCE_SMILES


st.set_page_config(
    page_title="SAR Deliberation",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown(SAR_CSS, unsafe_allow_html=True)


@st.cache_data
def load_preset_molecules():
    with open("data/sar_matrix.json") as f:
        data = json.load(f)
    return data["all_molecules"], data["reference_props"], data


# ── Main ──
render_header()

molecules, ref_props, sar_data = load_preset_molecules()
ref_smiles = REFERENCE_SMILES

if not molecules:
    st.warning("No valid molecules found.")
    st.stop()

render_overview_cards(molecules, ref_props)

# ── SAR Heatmap ──
with st.expander("SAR Heatmap", expanded=False):
    render_sar_heatmap_section(sar_data)

# ── Molecule Table + Detail ──
if "show_table" not in st.session_state:
    st.session_state.show_table = False

col_toggle, _ = st.columns([1, 3])
with col_toggle:
    if st.button(
        "Hide Molecules" if st.session_state.show_table else "View All Molecules",
    ):
        st.session_state.show_table = not st.session_state.show_table
        st.rerun()

if st.session_state.show_table:
    render_molecule_table(molecules)

    mol_names = [m["name"] for m in molecules]
    selected_name = st.selectbox("Select molecule for detail view", mol_names, key="mol_detail_select")
    if selected_name:
        mol = next(m for m in molecules if m["name"] == selected_name)
        render_molecule_detail(mol, ref_props, ref_smiles)

# ── Comparison Panel ──
with st.expander("Molecule Comparison", expanded=False):
    render_comparison_panel(molecules, ref_smiles, ref_props)

# ── Custom SMILES ──
with st.expander("Custom Molecule Evaluation", expanded=False):
    render_smiles_input(ref_smiles, ref_props)

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ── Deliberation State Machine ──
if "delib_stage" not in st.session_state:
    st.session_state.delib_stage = "idle"

# ── Analysis Focus Input ──
analysis_focus = st.text_input(
    "Analysis focus (optional)",
    placeholder="e.g. Prioritize synthetic feasibility for Tail modifications",
    key="analysis_focus",
)

# ── Start Button ──
if st.session_state.delib_stage == "idle":
    if st.button("Start Multi-Agent Analysis", type="primary", use_container_width=True):
        from agents.deliberation import Deliberation
        delib = Deliberation()
        st.session_state.delib = delib

        with st.status("Round 1: Independent Analysis...", expanded=True) as s1:
            st.write("3 Agents analyzing molecules from different perspectives...")
            r1 = delib.run_round1(molecules, ref_props, focus=analysis_focus)
            s1.update(label=f"Round 1 Complete ({r1.duration}s)", state="complete")

        st.session_state.r1_output = r1
        st.session_state.delib_stage = "r1_done"
        st.rerun()

# ── R1 Done: Show results + gate ──
if st.session_state.delib_stage == "r1_done":
    r1 = st.session_state.r1_output
    render_round(1, r1.agent_outputs, r1.duration)

    st.markdown(
        '<div class="convergence-card" style="border-left-color:var(--agent-mpo);">'
        '<h3 style="font-size:16px;margin:0 0 12px;">Review & Steer</h3>'
        '<p style="font-size:13px;color:var(--text-secondary);margin:0 0 16px;">'
        'Review the independent analyses above. Optionally add guidance to steer the cross-challenge round.'
        '</p></div>',
        unsafe_allow_html=True,
    )

    user_guidance = st.text_area(
        "Guidance for Round 2 (optional)",
        placeholder="e.g. Focus on Tail position synthesis feasibility; challenge the MPO ranking of C34-sulfonyl-methylsulfonyl",
        key="r2_guidance",
        height=80,
    )

    if st.button("Continue to Round 2", type="primary", use_container_width=True):
        delib = st.session_state.delib

        with st.status("Round 2: Cross-Challenge...", expanded=True) as s2:
            st.write("Each Agent reviewing and challenging the others...")
            r2 = delib.run_round2(user_guidance=user_guidance)
            s2.update(label=f"Round 2 Complete ({r2.duration}s)", state="complete")

        st.session_state.r2_output = r2
        st.session_state.delib_stage = "r2_done"
        st.rerun()

# ── R2 Done: Auto-proceed to R3 ──
if st.session_state.delib_stage in ("r2_done", "complete"):
    r1 = st.session_state.r1_output
    r2 = st.session_state.r2_output
    render_round(1, r1.agent_outputs, r1.duration)
    render_round(2, r2.agent_outputs, r2.duration)

    if st.session_state.delib_stage == "r2_done":
        delib = st.session_state.delib
        with st.status("Round 3: Convergence...", expanded=True) as s3:
            st.write("Synthesizing all perspectives into final recommendations...")
            convergence = delib.run_round3()
            s3.update(label="Round 3 Complete", state="complete")

        st.session_state.convergence = convergence
        st.session_state.all_traces = (
            delib.sa_agent.traces
            + delib.mpo_agent.traces
            + delib.risk_agent.traces
        )
        st.session_state.delib_stage = "complete"
        st.rerun()

    # ── Complete: Show everything ──
    if st.session_state.delib_stage == "complete":
        render_convergence(st.session_state.convergence)

        all_traces = st.session_state.all_traces
        st.markdown(
            f"<div class='glass-card'>"
            f"<h3>Analysis Complete</h3>"
            f"<p style='font-size:14px;color:var(--text-secondary);margin:0;'>"
            f"3 Agents × 3 Rounds · {len(all_traces)} LLM calls"
            f"</p></div>",
            unsafe_allow_html=True,
        )
        with st.expander("Execution Traces", expanded=False):
            render_traces(all_traces)

        if st.button("New Analysis", key="reset_delib"):
            for k in ("delib_stage", "delib", "r1_output", "r2_output",
                       "convergence", "all_traces"):
                st.session_state.pop(k, None)
            st.rerun()
