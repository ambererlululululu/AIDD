CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --bg: #FFFFFF;
        --bg-secondary: #F8FAFC;
        --bg-tertiary: #F1F5F9;
        --border: #E2E8F0;
        --border-light: #F1F5F9;

        --text-primary: #0F172A;
        --text-secondary: #475569;
        --text-muted: #94A3B8;

        --brand: #2563EB;
        --brand-hover: #1D4ED8;
        --brand-light: #EFF6FF;
        --accent: #0891B2;

        --success: #059669;
        --success-bg: #F0FDF4;
        --warning: #D97706;
        --warning-bg: #FFFBEB;
        --danger: #DC2626;
        --danger-bg: #FEF2F2;
    }

    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* --- 页面头部 --- */
    .page-header {
        padding: 1.5rem 0 1rem;
        border-bottom: 1px solid var(--border);
        margin-bottom: 1.5rem;
    }
    .page-header h1 {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0 0 0.25rem;
    }
    .page-header p {
        font-size: 0.875rem;
        color: var(--text-secondary);
        margin: 0;
        line-height: 1.5;
    }

    /* --- 流程指示器 --- */
    .pipeline {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0;
        padding: 1rem 0;
    }
    .pipeline-step {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    .pipeline-step-a {
        background: var(--brand-light);
        color: var(--brand);
        border: 1px solid #BFDBFE;
    }
    .pipeline-step-b {
        background: #F0FDFA;
        color: var(--accent);
        border: 1px solid #99F6E4;
    }
    .pipeline-arrow {
        color: var(--text-muted);
        padding: 0 0.5rem;
        font-size: 0.75rem;
    }

    /* --- 状态标签 --- */
    .tag-pass {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        background: var(--success-bg);
        color: var(--success);
    }
    .tag-conditional {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        background: var(--warning-bg);
        color: var(--warning);
    }
    .tag-fail {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        background: var(--danger-bg);
        color: var(--danger);
    }

    /* --- 对话消息 --- */
    .msg {
        padding: 0.75rem 1rem;
        border-radius: 6px;
        margin-bottom: 0.5rem;
        font-size: 0.85rem;
        line-height: 1.5;
        border-left: 3px solid;
    }
    .msg-designer {
        background: var(--brand-light);
        border-left-color: var(--brand);
    }
    .msg-critic {
        background: #F0FDFA;
        border-left-color: var(--accent);
    }
    .msg-role {
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 0.25rem;
    }
    .msg-role-a { color: var(--brand); }
    .msg-role-b { color: var(--accent); }

    /* --- 属性网格 --- */
    .props {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0.5rem;
        margin: 0.5rem 0;
    }
    .prop {
        text-align: center;
        padding: 0.375rem 0;
        background: var(--bg-secondary);
        border-radius: 4px;
    }
    .prop-label {
        font-size: 0.625rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .prop-val {
        font-size: 0.8rem;
        font-weight: 600;
        font-variant-numeric: tabular-nums;
    }
    .c-ok { color: var(--text-primary); }
    .c-warn { color: var(--warning); }
    .c-fail { color: var(--danger); }
    .c-good { color: var(--success); }

    /* --- 分子卡片 --- */
    .mol-card {
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        background: var(--bg);
    }
    .mol-name {
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0;
    }
    .mol-strategy {
        font-size: 0.7rem;
        color: var(--text-muted);
        margin-top: 2px;
    }

    /* --- 统计卡 --- */
    .stat-card {
        text-align: center;
        padding: 1rem 0.5rem;
        background: var(--bg-secondary);
        border-radius: 8px;
        border: 1px solid var(--border);
    }
    .stat-num {
        font-size: 1.75rem;
        font-weight: 700;
        font-variant-numeric: tabular-nums;
        line-height: 1;
    }
    .stat-label {
        font-size: 0.7rem;
        color: var(--text-muted);
        margin-top: 0.25rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    /* --- 侧边栏 --- */
    .sidebar-footer {
        font-size: 0.7rem;
        color: var(--text-muted);
        line-height: 1.6;
    }

    /* --- AI 透明展示 --- */
    .ai-stats {
        display: flex;
        gap: 12px;
        padding: 8px 12px;
        background: #F5F3FF;
        border-radius: 6px;
        border: 1px solid #DDD6FE;
        font-size: 0.78rem;
        margin: 8px 0;
        flex-wrap: wrap;
    }
    .ai-stats .stat { color: #7C3AED; font-weight: 600; }

    /* --- 杂项 --- */
    div[data-testid="stExpander"] {
        border: 1px solid var(--border);
        border-radius: 8px;
    }
</style>
"""
