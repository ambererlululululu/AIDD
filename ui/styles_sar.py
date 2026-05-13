SAR_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

:root {
    --bg: #EDEDED;
    --bg-card: #F5F5F5;
    --bg-white: #FFFFFF;
    --accent: #76FB91;
    --accent-dim: rgba(118, 251, 145, 0.15);
    --accent-border: rgba(118, 251, 145, 0.35);
    --accent-dark: #1A1A1A;
    --text: #000000;
    --text-secondary: #666666;
    --text-muted: #999999;
    --border: #E0E0E0;
    --agent-sa: #76FB91;
    --agent-mpo: #76D4FB;
    --agent-risk: #FBD076;
    --success: #22C55E;
    --warning: #F59E0B;
    --danger: #EF4444;
    --radius: 16px;
    --radius-sm: 10px;
    --shadow: 0 2px 12px rgba(0,0,0,0.06);
}

/* ── Global ── */
.stApp {
    background-color: var(--bg) !important;
    font-family: 'Outfit', sans-serif !important;
}
.stApp [data-testid="stHeader"] {
    background-color: var(--bg) !important;
}
.stApp h1, .stApp h2, .stApp h3, .stApp p, .stApp span, .stApp div {
    font-family: 'Outfit', sans-serif !important;
}
section[data-testid="stSidebar"] {
    background-color: var(--bg-white) !important;
    border-right: 1px solid var(--border);
}

/* ── Header ── */
.sar-header {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 16px 0 24px;
}
.sar-header h1 {
    font-size: 28px;
    font-weight: 700;
    color: var(--text);
    margin: 0;
}
.sar-header .subtitle {
    font-size: 14px;
    color: var(--text-secondary);
    font-weight: 400;
}

/* ── Stat Cards ── */
.stat-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 32px;
}
.stat-card {
    background: var(--bg-white);
    border-radius: var(--radius);
    padding: 20px 24px;
    box-shadow: var(--shadow);
    border: 1px solid var(--border);
}
.stat-card .stat-label {
    font-size: 13px;
    font-weight: 500;
    color: var(--text-secondary);
    margin-bottom: 6px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.stat-card .stat-value {
    font-size: 32px;
    font-weight: 700;
    color: var(--text);
    line-height: 1;
}
.stat-card .stat-sub {
    font-size: 12px;
    color: var(--text-muted);
    margin-top: 4px;
}
.stat-card.accent {
    background: linear-gradient(135deg, var(--accent-dim), var(--bg-white));
    border-color: var(--accent-border);
}

/* ── Round Section ── */
.round-section {
    margin-bottom: 36px;
}
.round-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 2px solid var(--border);
}
.round-badge {
    background: var(--accent-dark);
    color: var(--bg-white);
    font-size: 12px;
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 20px;
    letter-spacing: 0.5px;
}
.round-title {
    font-size: 18px;
    font-weight: 600;
    color: var(--text);
}
.round-duration {
    font-size: 12px;
    color: var(--text-muted);
    margin-left: auto;
}

/* ── Agent Cards ── */
.agent-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    align-items: start;
}
.agent-grid > * {
    min-height: 100%;
}
.agent-card {
    background: var(--bg-white);
    border-radius: var(--radius);
    padding: 0;
    box-shadow: var(--shadow);
    border: 1px solid var(--border);
    overflow: hidden;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.agent-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}
.agent-card-header {
    padding: 16px 20px;
    display: flex;
    align-items: center;
    gap: 10px;
    border-bottom: 1px solid var(--border);
}
.agent-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    flex-shrink: 0;
}
.agent-dot.sa { background: var(--agent-sa); }
.agent-dot.mpo { background: var(--agent-mpo); }
.agent-dot.risk { background: var(--agent-risk); }
.agent-name {
    font-size: 14px;
    font-weight: 600;
    color: var(--text);
}
.agent-card-body {
    padding: 20px;
}
.agent-card-body p {
    font-size: 13.5px;
    line-height: 1.7;
    color: var(--text);
    margin: 0 0 4px;
}
.agent-heading {
    font-size: 13.5px;
    font-weight: 600;
    color: var(--text);
    margin: 12px 0 4px;
    line-height: 1.5;
}
.agent-heading:first-child {
    margin-top: 0;
}
.agent-bullet {
    font-size: 13px;
    color: var(--text);
    line-height: 1.6;
    padding-left: 6px;
    margin: 2px 0;
}
.agent-chain {
    font-size: 12.5px;
    color: var(--text-secondary);
    line-height: 1.6;
    padding: 6px 10px;
    background: var(--bg-card);
    border-radius: 6px;
    margin: 4px 0;
    font-family: monospace;
}

/* ── Glassmorphism Accent Card ── */
.glass-card {
    background: rgba(118, 251, 145, 0.12);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid var(--accent-border);
    border-radius: var(--radius);
    padding: 24px;
    margin-bottom: 24px;
}
.glass-card h3 {
    font-size: 16px;
    font-weight: 600;
    color: var(--text);
    margin: 0 0 12px;
}

/* ── Convergence Section ── */
.convergence-card {
    background: var(--bg-white);
    border-radius: var(--radius);
    padding: 28px;
    box-shadow: var(--shadow);
    border: 1px solid var(--border);
    border-left: 4px solid var(--accent);
}
.convergence-card h3 {
    font-size: 18px;
    font-weight: 600;
    color: var(--text);
    margin: 0 0 16px;
}
.convergence-card .convergence-body {
    font-size: 14px;
    line-height: 1.8;
    color: var(--text);
}
.convergence-card .convergence-body p {
    margin: 0 0 8px;
}

/* ── Execution Trace ── */
.trace-container {
    background: var(--bg-card);
    border-radius: var(--radius);
    padding: 20px;
    margin-top: 24px;
    border: 1px solid var(--border);
}
.trace-item {
    display: grid;
    grid-template-columns: 80px 120px 1fr 60px;
    gap: 12px;
    padding: 10px 0;
    border-bottom: 1px solid var(--border);
    font-size: 12px;
    color: var(--text-secondary);
    align-items: center;
}
.trace-item:last-child { border-bottom: none; }
.trace-round {
    font-weight: 600;
    color: var(--text);
}
.trace-agent {
    font-weight: 500;
}
.trace-preview {
    color: var(--text-muted);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.trace-time {
    text-align: right;
    font-variant-numeric: tabular-nums;
}

/* ── Trace Detail (expandable) ── */
.trace-detail {
    display: flex;
    gap: 12px;
}
.trace-color-bar {
    width: 4px;
    border-radius: 2px;
    flex-shrink: 0;
}
.trace-color-bar.sa { background: var(--agent-sa); }
.trace-color-bar.mpo { background: var(--agent-mpo); }
.trace-color-bar.risk { background: var(--agent-risk); }
.trace-content {
    flex: 1;
    font-size: 13px;
    line-height: 1.7;
    color: var(--text);
}
.trace-content p {
    margin: 0 0 4px;
}

/* ── Verdict Tags ── */
.tag {
    display: inline-block;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 4px;
    letter-spacing: 0.3px;
}
.tag-pass { background: #DCFCE7; color: #166534; }
.tag-conditional { background: #FEF3C7; color: #92400E; }
.tag-fail { background: #FEE2E2; color: #991B1B; }

/* ── Molecule Table ── */
.mol-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}
.mol-table th {
    text-align: left;
    padding: 10px 12px;
    font-weight: 600;
    color: var(--text-secondary);
    border-bottom: 2px solid var(--border);
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.mol-table td {
    padding: 10px 12px;
    border-bottom: 1px solid var(--border);
    color: var(--text);
}
.mol-table tr:hover td {
    background: var(--accent-dim);
}
.mol-table .score-cell {
    font-weight: 600;
    font-variant-numeric: tabular-nums;
}

/* ── Progress ── */
.progress-bar {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 16px 24px;
    background: var(--bg-white);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    border: 1px solid var(--border);
    margin-bottom: 24px;
}
.progress-step {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    color: var(--text-muted);
}
.progress-step.active {
    color: var(--text);
    font-weight: 600;
}
.progress-step.done {
    color: var(--success);
}
.progress-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--border);
}
.progress-dot.active {
    background: var(--accent);
    box-shadow: 0 0 8px rgba(118, 251, 145, 0.5);
}
.progress-dot.done { background: var(--success); }
.progress-line {
    flex: 1;
    height: 2px;
    background: var(--border);
    max-width: 40px;
}
.progress-line.done { background: var(--success); }

/* ── Custom SMILES Input ── */
.smiles-input {
    background: var(--bg-white);
    border-radius: var(--radius);
    padding: 20px;
    border: 1px dashed var(--border);
    margin-top: 16px;
}

/* ── Hide Streamlit defaults ── */
#MainMenu { display: none !important; }
footer { display: none !important; }
header { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stHeader"] { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
[data-testid="stSidebarCollapsedControl"] { display: none !important; }

/* ── Streamlit Overrides ── */
.stButton > button {
    background: var(--accent-dark) !important;
    color: var(--bg-white) !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 10px 28px !important;
    transition: all 0.15s ease !important;
}
.stButton > button:hover {
    background: #333 !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
}
.stSelectbox > div > div {
    border-radius: var(--radius-sm) !important;
    border-color: var(--border) !important;
    font-family: 'Outfit', sans-serif !important;
}
.stExpander {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    background: var(--bg-white) !important;
}
div[data-testid="stExpander"] details {
    border: none !important;
}
.stTextArea textarea {
    border-radius: var(--radius-sm) !important;
    border-color: var(--border) !important;
    font-family: 'Outfit', monospace !important;
    font-size: 13px !important;
}
.stMultiSelect > div > div {
    border-radius: var(--radius-sm) !important;
    border-color: var(--border) !important;
    font-family: 'Outfit', sans-serif !important;
}
.stTextInput > div > div > input {
    border-radius: var(--radius-sm) !important;
    border-color: var(--border) !important;
    font-family: 'Outfit', monospace !important;
    font-size: 13px !important;
}

/* ── Section Headers ── */
.sar-section {
    margin: 32px 0 20px;
}
.sar-section-title {
    font-size: 18px;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 6px;
}
.sar-section-desc {
    font-size: 13px;
    color: var(--text-secondary);
    margin-bottom: 16px;
}

/* ── Molecule Detail ── */
.mol-detail-card {
    background: var(--bg-white);
    border-radius: var(--radius);
    padding: 24px;
    box-shadow: var(--shadow);
    border: 1px solid var(--border);
    margin: 16px 0;
}
.mol-detail-card svg {
    max-width: 100%;
    height: auto;
}

/* ── Property Grid ── */
.sar-prop-grid {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 12px;
    margin: 16px 0;
}
.sar-prop-item {
    text-align: center;
    background: var(--bg-card);
    border-radius: var(--radius-sm);
    padding: 10px 8px;
}
.sar-prop-label {
    font-size: 11px;
    font-weight: 500;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.sar-prop-value {
    font-size: 20px;
    font-weight: 600;
    color: var(--text);
    margin-top: 2px;
}
.sar-prop-value.good { color: var(--success); }
.sar-prop-value.warn { color: var(--warning); }
.sar-prop-value.bad { color: var(--danger); }

/* ── Score Breakdown Bars ── */
.sar-breakdown {
    margin: 12px 0;
}
.sar-bd-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 3px 0;
}
.sar-bd-label {
    width: 56px;
    font-size: 11px;
    color: var(--text-muted);
    text-align: right;
    flex-shrink: 0;
}
.sar-bd-track {
    flex: 1;
    background: var(--bg-card);
    border-radius: 3px;
    height: 10px;
    overflow: hidden;
}
.sar-bd-fill {
    height: 100%;
    border-radius: 3px;
}
.sar-bd-val {
    width: 44px;
    font-size: 12px;
    font-weight: 600;
    color: var(--text-secondary);
    text-align: right;
    font-variant-numeric: tabular-nums;
    flex-shrink: 0;
}
.sar-bd-total {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 6px 0 0;
    padding-top: 6px;
    border-top: 1px solid var(--border);
}
.sar-bd-total .sar-bd-label {
    font-weight: 600;
    color: var(--text);
}
.sar-bd-total .sar-bd-val {
    font-size: 14px;
    font-weight: 700;
    color: var(--text);
}

/* ── Comparison Cards ── */
.compare-col {
    background: var(--bg-white);
    border-radius: var(--radius);
    padding: 16px;
    box-shadow: var(--shadow);
    border: 1px solid var(--border);
    text-align: center;
}
.compare-col .mol-name {
    font-size: 14px;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 2px;
}
.compare-col .mol-position {
    font-size: 11px;
    color: var(--text-muted);
    margin-bottom: 8px;
}
.compare-col .mol-score {
    font-size: 28px;
    font-weight: 700;
    line-height: 1;
    margin: 6px 0;
}
</style>
"""
