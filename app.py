from __future__ import annotations
import json
import os
import streamlit as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.styles import CUSTOM_CSS
from ui.components import (
    render_reference_molecule, render_round_results, render_summary,
    render_full_evaluation, render_comparison_table, render_tki_gallery,
    render_tki_multi_radar, render_feedback_detail, build_export_dataframe,
    render_ai_contribution, render_sar_explorer, render_chemical_space_tab,
)
from agents.loop import AdversarialLoop
from chemistry.molecules import OSIMERTINIB, REFERENCE_TKIS
from chemistry.evaluator import evaluate_candidate, generate_radar_data, compute_properties

st.set_page_config(
    page_title="AIDD — EGFR T790M 分子设计平台",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ── 侧边栏 ──
with st.sidebar:
    render_reference_molecule()
    st.markdown("---")
    st.markdown('<div class="sidebar-footer">RDKit 本地计算 · DeepSeek LLM 决策 · 无需 GPU</div>', unsafe_allow_html=True)

# ── 页面头 ──
st.markdown("""<div class="page-header">
    <h1>EGFR T790M 分子设计平台</h1>
    <p>对抗式分子设计 · 构效关系探索 · ADMET 评估 · 参考药物对比</p>
</div>""", unsafe_allow_html=True)

# ── 四标签页 ──
tab1, tab2, tab3, tab4 = st.tabs(["对抗式设计", "SAR 探索", "单分子评估", "分子对比"])


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Tab 1: 对抗式设计
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab1:
    st.markdown("""<div class="pipeline">
        <div class="pipeline-step pipeline-step-a">LLM 策略决策</div>
        <div class="pipeline-arrow">→</div>
        <div class="pipeline-step pipeline-step-a">分子设计师</div>
        <div class="pipeline-arrow">→</div>
        <div class="pipeline-step pipeline-step-b">ADMET + 3D 评审</div>
        <div class="pipeline-arrow">→</div>
        <div class="pipeline-step pipeline-step-a">迭代优化</div>
        <div class="pipeline-arrow" style="font-size:0.9rem;">↻</div>
    </div>""", unsafe_allow_html=True)

    col_cfg1, col_cfg2 = st.columns(2)
    with col_cfg1:
        n_rounds = st.slider("迭代轮数", 2, 5, 3)
    with col_cfg2:
        n_candidates = st.slider("每轮候选数", 4, 12, 8)

    st.markdown("---")

    if st.button("开始设计", type="primary", use_container_width=True, key="btn_design"):
        loop = AdversarialLoop(
            n_rounds=n_rounds,
            n_candidates=n_candidates,
            seed_smiles=OSIMERTINIB["smiles"],
        )
        progress = st.progress(0, text="初始化...")

        for result in loop.run_all():
            progress.progress(
                result.round_number / n_rounds,
                text=f"第 {result.round_number} / {n_rounds} 轮",
            )

            render_ai_contribution(result.designer_output)
            render_round_results(result)

            fb = result.critic_output.get("feedback")
            if fb:
                with st.expander(f"第 {result.round_number} 轮 — 反馈详情", expanded=False):
                    render_feedback_detail(fb)

        progress.progress(1.0, text="设计完成")
        st.markdown("---")

        summary = loop.get_summary()
        render_summary(summary)

        export_df = build_export_dataframe(summary)
        if not export_df.empty:
            csv = export_df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "下载候选分子 CSV",
                csv,
                file_name="aidd_candidates.csv",
                mime="text/csv",
                use_container_width=True,
            )
    else:
        st.markdown(
            '<div style="text-align:center;color:var(--text-muted);padding:2.5rem 1rem;">'
            '调整参数后，点击上方按钮开始对抗式设计。<br>'
            '<span style="font-size:0.75rem;">LLM 将参与策略决策并尝试生成 SMILES，评分包含 3D 靶点结合力。</span></div>',
            unsafe_allow_html=True,
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Tab 2: SAR 探索
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab2:
    st.markdown("#### 构效关系矩阵")
    st.markdown(
        "基于奥希替尼的 4 个可修饰位点（吲哚 N、甲氧基、尾基、弹头），"
        "穷举单点修饰并评估每个 R 基团对各项属性的影响。"
    )

    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    sar_path = os.path.join(data_dir, "sar_matrix.json")
    space_path = os.path.join(data_dir, "chemical_space.json")

    if os.path.exists(sar_path) and os.path.exists(space_path):
        with open(sar_path, "r") as f:
            sar_data = json.load(f)
        with open(space_path, "r") as f:
            space_data = json.load(f)

        st.markdown(
            f'<div class="ai-stats">'
            f'<span>修饰位点: <b class="stat">4</b></span>'
            f'<span>候选分子: <b class="stat">{sar_data["total_molecules"]}</b></span>'
            f'<span>含 3D 结合力评分</span>'
            f'</div>', unsafe_allow_html=True,
        )

        render_sar_explorer(sar_data)

        st.markdown("---")
        st.markdown("#### 化学空间分布")
        st.markdown("所有 SAR 候选分子与参考 TKI 药物在化学空间中的分布（Morgan 指纹 → PCA 降维）。")
        render_chemical_space_tab(space_data)
    else:
        st.warning(
            "SAR 预生成数据未找到。请先运行: `python chemistry/pregenerate.py`"
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Tab 3: 单分子评估
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab3:
    st.markdown("粘贴任意 SMILES，系统将自动完成完整 ADMET 评估（含 3D 靶点结合力代理评分）并与奥希替尼对比。")

    default_smi = OSIMERTINIB["smiles"]
    smiles_input = st.text_input(
        "SMILES",
        value="",
        placeholder=f"例: {default_smi}",
        key="smi_input",
    )

    if st.button("评估", type="primary", use_container_width=True, key="btn_eval"):
        smi = smiles_input.strip()
        if not smi:
            st.warning("请输入 SMILES")
        else:
            with st.spinner("计算中（含 3D 构象评分）..."):
                ev = evaluate_candidate(smi, OSIMERTINIB["smiles"])
                ref_props = compute_properties(OSIMERTINIB["smiles"])
                if ev.get("valid") and ev.get("properties") and ref_props:
                    b3d = ev.get("binding_3d")
                    ev["radar"] = generate_radar_data(ev["properties"], ref_props, binding_3d=b3d)
                render_full_evaluation(ev)
    else:
        st.markdown(
            '<div style="text-align:center;color:var(--text-muted);padding:2.5rem 1rem;">'
            '输入 SMILES 后点击评估按钮。</div>',
            unsafe_allow_html=True,
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Tab 4: 分子对比
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab4:
    st.markdown("#### EGFR TKI 代际总览")
    st.markdown(
        "从第一代可逆抑制剂到第三代共价不可逆抑制剂，"
        "展示靶向治疗的演进路线与分子属性差异。"
    )

    st.markdown("##### 参考药物")
    render_tki_gallery()

    st.markdown("---")
    st.markdown("##### 属性对比")
    render_comparison_table()

    st.markdown("---")
    st.markdown("##### 多维雷达图对比")
    render_tki_multi_radar()
