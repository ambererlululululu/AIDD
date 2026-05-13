from __future__ import annotations
import io
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import rcParams
import plotly.graph_objects as go
from rdkit import Chem
from rdkit.Chem import Draw, rdDepictor, rdFMCS
from rdkit.Chem.Draw import rdMolDraw2D

rcParams["font.sans-serif"] = ["Outfit", "Helvetica Neue", "Arial", "PingFang HK", "sans-serif"]
rcParams["axes.unicode_minus"] = False

MOL_BG = (0.961, 0.961, 0.961, 1.0)
MOL_BG_HEX = "#F5F5F5"

_FG = "#1A1A1A"
_FG2 = "#666666"
_GRID = "#E0E0E0"
_ACCENT = "#76FB91"
_BG_WHITE = "#FFFFFF"


def _configure_drawer(drawer):
    opts = drawer.drawOptions()
    opts.addStereoAnnotation = True
    opts.bondLineWidth = 2.2
    opts.setBackgroundColour((1.0, 1.0, 1.0, 1.0))
    opts.additionalAtomLabelPadding = 0.12
    return opts


def mol_to_svg(smiles: str, size=(350, 250), highlight_smarts=None) -> str:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return '<div style="color:#ff6b6b;padding:2rem;text-align:center;">Invalid molecule</div>'

    rdDepictor.Compute2DCoords(mol)
    drawer = rdMolDraw2D.MolDraw2DSVG(size[0], size[1])
    _configure_drawer(drawer)

    highlight_atoms = []
    if highlight_smarts:
        pat = Chem.MolFromSmarts(highlight_smarts)
        if pat:
            for match in mol.GetSubstructMatches(pat):
                highlight_atoms.extend(match)

    if highlight_atoms:
        colors = {a: (0.3, 0.6, 1.0, 0.35) for a in highlight_atoms}
        drawer.DrawMolecule(mol, highlightAtoms=highlight_atoms,
                            highlightAtomColors=colors)
    else:
        drawer.DrawMolecule(mol)

    drawer.FinishDrawing()
    svg = drawer.GetDrawingText()
    return _wrap_svg(svg)


def highlight_diff(parent_smiles: str, child_smiles: str, size=(350, 250)) -> str:
    parent = Chem.MolFromSmiles(parent_smiles)
    child = Chem.MolFromSmiles(child_smiles)
    if parent is None or child is None:
        return mol_to_svg(child_smiles or parent_smiles or "", size)

    mcs = rdFMCS.FindMCS([parent, child], timeout=2,
                          bondCompare=rdFMCS.BondCompare.CompareAny,
                          atomCompare=rdFMCS.AtomCompare.CompareElements)
    if not mcs.smartsString:
        return mol_to_svg(child_smiles, size)

    mcs_mol = Chem.MolFromSmarts(mcs.smartsString)
    if mcs_mol is None:
        return mol_to_svg(child_smiles, size)

    match = child.GetSubstructMatch(mcs_mol)
    matched_atoms = set(match)
    diff_atoms = [i for i in range(child.GetNumAtoms()) if i not in matched_atoms]

    rdDepictor.Compute2DCoords(child)
    drawer = rdMolDraw2D.MolDraw2DSVG(size[0], size[1])
    _configure_drawer(drawer)

    if diff_atoms:
        colors = {a: (0.96, 0.62, 0.04, 0.35) for a in diff_atoms}
        drawer.DrawMolecule(child, highlightAtoms=diff_atoms,
                            highlightAtomColors=colors)
    else:
        drawer.DrawMolecule(child)

    drawer.FinishDrawing()
    svg = drawer.GetDrawingText()
    return _wrap_svg(svg)


def _wrap_svg(svg: str) -> str:
    return (
        f'<div style="text-align:center;padding:4px;">'
        f'{svg}</div>'
    )


def render_radar_chart(candidate_data: dict, ref_data: dict,
                       candidate_name: str = "Candidate",
                       ref_name: str = "C34 (Reference)") -> go.Figure:
    labels = list(candidate_data.keys())
    cand_vals = list(candidate_data.values())
    ref_vals = list(ref_data.values())

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=ref_vals + [ref_vals[0]],
        theta=labels + [labels[0]],
        name=ref_name,
        line=dict(color="#BDBDBD", width=1.5, dash="dot"),
        fillcolor="rgba(189,189,189,0.04)",
        fill="toself",
        marker=dict(size=4),
    ))
    fig.add_trace(go.Scatterpolar(
        r=cand_vals + [cand_vals[0]],
        theta=labels + [labels[0]],
        name=candidate_name,
        line=dict(color="#2E7D52", width=2.5),
        fillcolor="rgba(118,251,145,0.15)",
        fill="toself",
        marker=dict(size=5, color="#2E7D52"),
    ))
    fig.update_layout(
        polar=dict(
            bgcolor=_BG_WHITE,
            radialaxis=dict(
                visible=True, range=[0, 1], showticklabels=False,
                gridcolor=_GRID, gridwidth=0.8,
            ),
            angularaxis=dict(
                gridcolor=_GRID, linecolor=_GRID, gridwidth=0.8,
                tickfont=dict(size=12, color=_FG),
            ),
        ),
        paper_bgcolor=_BG_WHITE,
        font=dict(family="Outfit, Helvetica Neue, Arial, sans-serif", color=_FG),
        legend=dict(
            x=0.98, y=1.05, xanchor="right",
            font=dict(size=11),
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor=_GRID, borderwidth=1,
        ),
        margin=dict(l=60, r=60, t=50, b=50),
        height=380,
    )
    return fig


def render_score_trajectory(round_scores: list[dict]) -> plt.Figure:
    rounds = [r["round"] for r in round_scores]
    avg_scores = [r["avg_score"] for r in round_scores]
    pass_rates = [r["pass_rate"] * 100 for r in round_scores]

    fig, ax1 = plt.subplots(figsize=(6, 3))
    fig.patch.set_facecolor("#FFFFFF")
    ax1.set_facecolor("#F8FAFC")

    ax1.plot(rounds, avg_scores, "o-", color="#1A1A1A", linewidth=2, markersize=7, label="Avg Score")
    ax1.set_xlabel("Round", color=_FG, fontsize=10)
    ax1.set_ylabel("Avg Score", color="#1A1A1A", fontsize=10)
    ax1.tick_params(axis="y", labelcolor="#2563EB", labelsize=9)
    ax1.tick_params(axis="x", colors="#334155", labelsize=9)
    ax1.set_ylim(0, 100)
    ax1.set_xticks(rounds)

    ax2 = ax1.twinx()
    ax2.plot(rounds, pass_rates, "s--", color="#059669", linewidth=2, markersize=7, label="Pass Rate %")
    ax2.set_ylabel("Pass Rate %", color="#059669", fontsize=10)
    ax2.tick_params(axis="y", labelcolor="#059669", labelsize=9)
    ax2.set_ylim(0, 100)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="lower right",
               fontsize=9, facecolor="#FFFFFF", edgecolor="#E2E8F0", labelcolor="#334155")

    for spine in list(ax1.spines.values()) + list(ax2.spines.values()):
        spine.set_color("#E2E8F0")

    plt.tight_layout()
    return fig


MULTI_COLORS = ["#1A1A1A", "#22C55E", "#3B82F6", "#F59E0B", "#EF4444"]


def render_multi_radar(molecules: list[dict]) -> go.Figure:
    if not molecules:
        return go.Figure()

    labels = list(molecules[0]["radar"].keys())
    fig = go.Figure()
    for i, mol in enumerate(molecules):
        vals = list(mol["radar"].values())
        color = MULTI_COLORS[i % len(MULTI_COLORS)]
        fig.add_trace(go.Scatterpolar(
            r=vals + [vals[0]],
            theta=labels + [labels[0]],
            name=mol["name"],
            line=dict(color=color, width=2.2),
            fillcolor=color.replace(")", ",0.06)").replace("rgb", "rgba") if "rgb" in color else f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.06)",
            fill="toself",
            marker=dict(size=5, color=color),
        ))
    fig.update_layout(
        polar=dict(
            bgcolor=_BG_WHITE,
            radialaxis=dict(
                visible=True, range=[0, 1], showticklabels=False,
                gridcolor=_GRID, gridwidth=0.8,
            ),
            angularaxis=dict(
                gridcolor=_GRID, linecolor=_GRID, gridwidth=0.8,
                tickfont=dict(size=12, color=_FG),
            ),
        ),
        paper_bgcolor=_BG_WHITE,
        font=dict(family="Outfit, Helvetica Neue, Arial, sans-serif", color=_FG),
        legend=dict(
            x=0.98, y=1.05, xanchor="right",
            font=dict(size=11),
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor=_GRID, borderwidth=1,
        ),
        margin=dict(l=60, r=60, t=50, b=50),
        height=420,
    )
    return fig


def render_sar_heatmap(heatmap_data: dict, property_label: str = "Score",
                       cmap_name: str = "RdYlGn",
                       global_range: tuple | None = None) -> go.Figure:
    labels = heatmap_data["labels"]
    values = heatmap_data["values"]
    pos_name = heatmap_data["position"]
    original = heatmap_data.get("original", "")

    short_labels = [_shorten_label(l) for l in labels]

    text = [[f"{v:.0f}" if abs(v) >= 10 else f"{v:.1f}" for v in values]]
    hover = [[f"<b>{labels[i]}</b><br>{property_label}: {text[0][i]}"
              for i in range(len(labels))]]

    zmin, zmax = (global_range if global_range else (None, None))
    vmin = zmin if zmin is not None else min(values)
    vmax = zmax if zmax is not None else max(values)

    fig = go.Figure(data=go.Heatmap(
        z=[values],
        x=short_labels,
        y=[pos_name],
        customdata=hover,
        hovertemplate="%{customdata}<extra></extra>",
        colorscale="RdYlGn",
        showscale=True,
        zmin=zmin,
        zmax=zmax,
        colorbar=dict(
            thickness=10, len=0.9,
            tickfont=dict(size=9, color=_FG2),
            outlinecolor=_GRID, outlinewidth=1,
            nticks=3,
        ),
    ))

    annotations = []
    span = vmax - vmin if vmax != vmin else 1
    for i, v in enumerate(values):
        ratio = (v - vmin) / span
        color = "#FFFFFF" if ratio < 0.25 or ratio > 0.8 else _FG
        annotations.append(dict(
            x=short_labels[i], y=pos_name,
            text=text[0][i],
            font=dict(size=13, color=color),
            showarrow=False,
        ))

    fig.update_layout(
        title=dict(text=f"{pos_name} — {property_label}", font=dict(size=13, color=_FG)),
        paper_bgcolor=_BG_WHITE,
        plot_bgcolor=_BG_WHITE,
        font=dict(family="Outfit, Helvetica Neue, Arial, sans-serif", color=_FG),
        xaxis=dict(type="category", tickfont=dict(size=9), tickangle=-35),
        yaxis=dict(type="category", tickfont=dict(size=10)),
        margin=dict(l=80, r=40, t=30, b=70),
        height=150,
        dragmode=False,
        annotations=annotations,
    )
    return fig


def _shorten_label(label: str, max_len: int = 18) -> str:
    prefixes = ["C34-", "Tail-"]
    for p in prefixes:
        if label.startswith(p):
            label = label[len(p):]
            break
    if len(label) > max_len:
        label = label[:max_len - 1] + "…"
    return label


GROUP_COLORS = {
    "Reference TKIs": "#DC2626",
    "Indole N": "#1A1A1A",
    "Methoxy": "#059669",
    "Tail": "#D97706",
    "Warhead": "#7C3AED",
}


def render_chemical_space(space_data: dict) -> plt.Figure:
    coords = space_data["coordinates"]
    explained = space_data.get("explained_variance", [0, 0])

    fig, ax = plt.subplots(figsize=(7, 5.5))
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#F8FAFC")

    groups = {}
    for c in coords:
        g = c["group"]
        if g not in groups:
            groups[g] = {"x": [], "y": [], "names": [], "scores": []}
        groups[g]["x"].append(c["x"])
        groups[g]["y"].append(c["y"])
        groups[g]["names"].append(c["name"])
        groups[g]["scores"].append(c["score"])

    for group_name, pts in groups.items():
        color = GROUP_COLORS.get(group_name, "#94A3B8")
        if group_name == "Reference TKIs":
            ax.scatter(pts["x"], pts["y"], c=color, s=100, marker="s",
                       edgecolors="#FFFFFF", linewidths=1.5, zorder=5, label=group_name)
            for i, name in enumerate(pts["names"]):
                ax.annotate(name, (pts["x"][i], pts["y"][i]),
                            textcoords="offset points", xytext=(6, 6),
                            fontsize=7, color=color, fontweight="bold")
        else:
            scores = pts["scores"]
            sc = ax.scatter(pts["x"], pts["y"], c=scores, cmap="RdYlGn",
                            s=50, edgecolors=color, linewidths=1.0,
                            vmin=30, vmax=90, alpha=0.85, zorder=3, label=group_name)

    ax.set_xlabel(f"PC1 ({explained[0]*100:.1f}%)" if explained else "PC1",
                  fontsize=10, color="#334155")
    ax.set_ylabel(f"PC2 ({explained[1]*100:.1f}%)" if len(explained) > 1 else "PC2",
                  fontsize=10, color="#334155")
    ax.tick_params(colors="#94A3B8", labelsize=8)
    for spine in ax.spines.values():
        spine.set_color("#E2E8F0")
    ax.grid(color="#E2E8F0", alpha=0.5, linestyle="--")

    ax.legend(fontsize=8, facecolor="#FFFFFF", edgecolor="#E2E8F0",
              labelcolor="#334155", loc="best")

    ax.set_title("Chemical Space (PCA)", fontsize=11, color=_FG, fontweight=600, pad=10)
    plt.tight_layout()
    return fig
