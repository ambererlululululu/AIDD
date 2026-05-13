/* ── State ── */
let allMolecules = [];
let refProps = {};
let refSmiles = '';
let selectedMolIdx = -1;
let delibSessionId = null;
let currentFilter = 'All';
let compareSet = new Set();
let analysisStrategy = 'standard';
let lang = 'en';
let currentProject = 'c34-egfr';
let allProjects = [];
let currentView = 'home';

/* ── i18n ── */
const LANG = {
    en: {
        title: 'SAR Deliberation',
        subtitle: 'AI-Driven Drug Discovery',
        molecules: 'Library',
        passed: 'Passed',
        avgScore: 'Mean Score',
        best: 'Top Candidate',
        conditional: 'conditional',
        outOf100: '/ 100',
        positions: 'mod. positions',
        candidatesLabel: 'Candidates Evaluated',
        passedLabel: 'Passed All Filters',
        conditionalLabel: 'conditional pass',
        avgScoreLabel: 'Mean Composite Score',
        bestLabel: 'Top Candidate',
        candidate: 'Candidate',
        sarMatrix: 'SAR Matrix',
        compare: 'Compare',
        analysis: 'Analysis',
        customMol: 'Custom Molecule',
        smilesHint: 'Paste a SMILES string to score any molecule against the reference compound.',
        evaluate: 'Evaluate',
        startAnalysis: 'Start Analysis',
        compareSelected: 'Compare Selected',
        compareHint: 'Select 2–4 molecules to compare properties and radar profiles',
        focusPlaceholder: 'Analysis focus (optional)',
        reviewTitle: 'Review & Steer',
        reviewDesc: 'Review the independent analyses above. You can optionally steer the cross-challenge round.',
        guidanceHint: 'Guidance is optional — leave blank to let agents debate freely',
        continueR2: 'Continue to Round 2 →',
        r1: 'Independent Analysis',
        r2: 'Cross-Challenge',
        r3: 'Convergence',
        consensus: 'Multi-Agent Consensus',
        complete: 'Analysis Complete',
        traces: 'Execution Traces',
        running: 'Running Round 1...',
        copyHint: 'Click to copy',
        flowDesc1: '3 agents analyze all molecules from different perspectives',
        flowDesc2: 'Agents challenge each other\'s findings with your guidance',
        flowDesc3: 'Agents reach consensus on rankings and recommendations',
        strategy: 'Strategy',
        focused: 'Focused',
        standard: 'Standard',
        comprehensive: 'Comprehensive',
        historyTitle: 'Deliberation History',
        historyEmpty: 'No deliberation history yet',
        historyFocus: 'Focus',
        domainKnowledge: 'Domain Knowledge',
        contextHint: 'Paste paper excerpts, SAR rules, or design constraints to give agents deeper context.',
        contextPlaceholder: 'e.g. Zhu et al. found that fluorine at para position is optimal for EGFR binding...',
        reasoning: 'Reasoning',
        nRefs: 'references',
        projectLabel: 'Project',
        reactPlan: 'Plan',
        reactInvestigate: 'Investigate',
        reactConclude: 'Conclude',
        reactIdentify: 'Identify',
        reactVerify: 'Verify',
        reactChallenge: 'Challenge',
        step: 'Step',
        home: 'Home',
        myProjects: 'My Projects',
        knowledgeBase: 'Knowledge Base',
        platformOverview: 'How It Works',
        lastAnalysis: 'Last analysis',
        noActivity: 'No analysis history yet',
        activeStatus: 'Active',
        corePapers: 'Core',
        supportingPapers: 'Supporting',
        platformDesc1: 'Upload your SAR matrix with molecular properties',
        platformDesc2: 'Multiple AI agents analyze from different perspectives',
        platformDesc3: 'Agents debate and converge on consensus recommendations',
        comingSoon: 'Coming Soon',
        comingSoonDesc: 'This project is under development. SAR matrix data will be available in a future release.',
        moleculeCount: 'molecules',
        sidebarMolecules: 'Molecules',
        signIn: 'Sign in',
    },
    zh: {
        title: 'SAR 评议',
        subtitle: 'AI 驱动药物发现',
        molecules: '分子库',
        passed: '通过',
        avgScore: '均分',
        best: '最优候选',
        conditional: '有条件',
        outOf100: '/ 100',
        positions: '个修饰位点',
        candidatesLabel: '已评估候选分子',
        passedLabel: '通过全部筛选',
        conditionalLabel: '有条件通过',
        avgScoreLabel: '综合评分均值',
        bestLabel: '最优候选分子',
        candidate: '候选分子',
        sarMatrix: 'SAR 矩阵',
        compare: '对比',
        analysis: '分析',
        customMol: '自定义分子',
        smilesHint: '输入 SMILES 字符串，评估任意分子与参考化合物的匹配度。',
        evaluate: '评估',
        startAnalysis: '开始分析',
        compareSelected: '对比选中',
        compareHint: '选择 2–4 个分子，对比属性与雷达图',
        focusPlaceholder: '分析重点（可选）',
        reviewTitle: '审阅与引导',
        reviewDesc: '查看以上独立分析，可引导下一轮交叉质疑方向。',
        guidanceHint: '留空则由智能体自由讨论',
        continueR2: '进入第二轮 →',
        r1: '独立分析',
        r2: '交叉质疑',
        r3: '共识收敛',
        consensus: '多智能体共识',
        complete: '分析完成',
        traces: '执行轨迹',
        running: '正在运行第一轮…',
        copyHint: '点击复制',
        flowDesc1: '多个智能体从不同视角独立分析全部候选分子',
        flowDesc2: '智能体互相质疑，可由用户引导方向',
        flowDesc3: '智能体达成排名与推荐共识',
        strategy: '策略',
        focused: '快速',
        standard: '标准',
        comprehensive: '深度',
        historyTitle: '评议历史',
        historyEmpty: '暂无评议记录',
        historyFocus: '分析重点',
        domainKnowledge: '领域知识',
        contextHint: '粘贴论文摘要、已知 SAR 规律或设计约束，让智能体获得更深的背景信息。',
        contextPlaceholder: '例如：Zhu et al. 发现氟苯基对位取代对 EGFR 结合最优...',
        reasoning: '推理过程',
        nRefs: '条参考',
        projectLabel: '项目',
        reactPlan: '规划',
        reactInvestigate: '调查',
        reactConclude: '结论',
        reactIdentify: '识别分歧',
        reactVerify: '验证证据',
        reactChallenge: '质疑',
        step: '步骤',
        home: '首页',
        myProjects: '我的项目',
        knowledgeBase: '知识库',
        platformOverview: '工作流程',
        lastAnalysis: '最近分析',
        noActivity: '暂无分析记录',
        activeStatus: '进行中',
        corePapers: '核心',
        supportingPapers: '辅助',
        platformDesc1: '上传 SAR 矩阵与分子属性数据',
        platformDesc2: '多个 AI 智能体从不同视角分析',
        platformDesc3: '智能体辩论并达成共识推荐',
        comingSoon: '即将推出',
        comingSoonDesc: '该项目正在开发中，SAR 矩阵数据将在后续版本中提供。',
        moleculeCount: '个分子',
        sidebarMolecules: '分子列表',
        signIn: '登录',
    },
};
function t(key) { return LANG[lang][key] || key; }

function toggleLang() {
    lang = lang === 'en' ? 'zh' : 'en';
    document.querySelectorAll('[data-i18n]').forEach(el => {
        el.textContent = t(el.dataset.i18n);
    });
    document.querySelector('.lang-toggle').textContent = lang === 'en' ? '中文' : 'EN';
    document.getElementById('analysis-focus').placeholder = t('focusPlaceholder');
    if (currentView === 'home') {
        document.querySelector('.sar-header h1').textContent = t('title');
        document.querySelector('.sar-header .subtitle').textContent = t('subtitle');
        renderDashboard();
    } else if (currentView === 'knowledge') {
        document.querySelector('.sar-header h1').textContent = t('title');
        document.querySelector('.sar-header .subtitle').textContent = t('subtitle');
        renderKnowledgePage();
    } else {
        const proj = allProjects.find(p => p.id === currentProject);
        if (proj) {
            document.querySelector('.sar-header h1').textContent = proj.name;
            const desc = typeof proj.description === 'object'
                ? (proj.description[lang] || proj.description['en']) : (proj.description || '');
            document.querySelector('.sar-header .subtitle').textContent = desc;
        }
        renderProjectContext();
        renderOverview();
        renderFilterTabs();
        renderMoleculeList();
        renderCompareCheckboxes();
        renderStrategyCards();
        loadHistory();
    }
}

let projectContext = {
    en: 'Optimizing C34 (Zhu et al. 2023), a non-covalent EGFR C797S inhibitor (IC₅₀ 5.1 nM), across 3 modification sites. Candidates generated via RDKit SMARTS transforms; scored by physicochemical properties, structural alerts, and 3D shape complementarity.',
    zh: '优化先导化合物 C34（Zhu et al. 2023），非共价 EGFR C797S 抑制剂（IC₅₀ 5.1 nM），在 3 个位点进行结构修饰。候选分子由 RDKit SMARTS 变换生成，基于理化性质、结构警报和 3D 形状互补性评分。',
};

function renderProjectContext() {
    document.getElementById('project-context').textContent = projectContext[lang] || projectContext['en'] || '';
}

const AGENT_META = {
    '结构-活性分析': { dot: 'sa', icon: '🔬', en: 'Structure-Activity' },
    '多参数优化':   { dot: 'mpo', icon: '⚖️', en: 'Multi-Parameter Optimization' },
    '风险评估':     { dot: 'risk', icon: '🛡️', en: 'Risk & Feasibility' },
    'ADMET预测':    { dot: 'admet', icon: '💊', en: 'ADMET Prediction' },
    '合成可行性':   { dot: 'synth', icon: '🧪', en: 'Synth. Feasibility' },
};

const PLOTLY_CONFIG = { displayModeBar: false, responsive: true };

const STRATEGY_CARDS = {
    focused: {
        agents: 2,
        perspectives: [
            { icon: '🔬', en: 'Structure-Activity', zh: '构效关系' },
            { icon: '⚖️', en: 'Multi-Parameter', zh: '多参数优化' },
        ],
    },
    standard: {
        agents: 3,
        perspectives: [
            { icon: '🔬', en: 'Structure-Activity', zh: '构效关系' },
            { icon: '⚖️', en: 'Multi-Parameter', zh: '多参数优化' },
            { icon: '🛡️', en: 'Risk Assessment', zh: '风险评估' },
        ],
    },
    comprehensive: {
        agents: 5,
        perspectives: [
            { icon: '🔬', en: 'Structure-Activity', zh: '构效关系' },
            { icon: '⚖️', en: 'Multi-Parameter', zh: '多参数优化' },
            { icon: '🛡️', en: 'Risk Assessment', zh: '风险评估' },
            { icon: '💊', en: 'ADMET Prediction', zh: 'ADMET 预测' },
            { icon: '🧪', en: 'Synth. Feasibility', zh: '合成可行性' },
        ],
    },
};

function renderStrategyCards() {
    const strategies = ['focused', 'standard', 'comprehensive'];
    const sectionTitle = lang === 'zh' ? '选择分析模式' : 'Select Analysis Mode';
    const modeLabel = lang === 'zh' ? '模式' : 'MODE';
    const cards = strategies.map(key => {
        const card = STRATEGY_CARDS[key];
        const active = analysisStrategy === key ? ' active' : '';
        const agentLabel = lang === 'zh'
            ? `${card.agents} 个智能体`
            : `${card.agents} agent${card.agents > 1 ? 's' : ''}`;
        const list = card.perspectives.map(p =>
            `<div class="strategy-perspective">${p.icon} ${p[lang]}</div>`
        ).join('');
        return `
            <div class="strategy-card${active}" onclick="setStrategy('${key}')">
                <span class="strategy-mode-badge">${modeLabel}</span>
                <div class="strategy-card-title">${t(key)}</div>
                <div class="strategy-card-agents">${agentLabel}</div>
                <div class="strategy-card-list">${list}</div>
            </div>`;
    }).join('');
    document.getElementById('strategy-cards').innerHTML =
        `<div class="strategy-section-title">${sectionTitle}</div>
         <div class="strategy-cards-grid">${cards}</div>`;
}

function setStrategy(strategy) {
    analysisStrategy = strategy;
    renderStrategyCards();
    const n = STRATEGY_CARDS[strategy].agents;
    const el = document.querySelector('[data-i18n="flowDesc1"]');
    if (el) {
        el.textContent = lang === 'zh'
            ? `${n} 个智能体从不同视角独立分析所有分子`
            : `${n} agents analyze all molecules from different perspectives`;
    }
}

/* ── API ── */
const API = {
    async get(url) {
        const res = await fetch(url);
        return res.json();
    },
    async post(url, body) {
        const res = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        return res.json();
    },
};

/* ── Init ── */
document.addEventListener('DOMContentLoaded', async () => {
    const projRes = await API.get('/api/projects');
    allProjects = projRes.projects || [];
    renderProjectSelect();
    document.querySelector('.sar-header h1').textContent = t('title');
    document.querySelector('.sar-header .subtitle').textContent = t('subtitle');
    switchView('home');
});

function renderProjectSelect() {
    const sel = document.getElementById('project-select');
    sel.innerHTML = allProjects.map(p =>
        `<option value="${p.id}" ${p.id === currentProject ? 'selected' : ''}>${p.name}</option>`
    ).join('');
}

/* ── View Switching ── */
async function switchView(view, projectId) {
    currentView = view;
    document.querySelectorAll('.view-pane').forEach(p =>
        p.classList.toggle('active', p.id === `view-${view}`)
    );

    const showSidebar = (view === 'project');
    document.getElementById('sidebar').classList.toggle('hidden', !showSidebar);
    document.querySelector('.app-layout').classList.toggle('no-sidebar', !showSidebar);
    document.getElementById('molecule-list').classList.toggle('hidden', view !== 'project');

    document.getElementById('project-select').classList.toggle('hidden', view !== 'project');
    document.getElementById('project-label').classList.toggle('hidden', view !== 'project');

    document.getElementById('nav-home').classList.toggle('active', view === 'home');
    const knNav = document.getElementById('nav-knowledge');
    if (knNav) knNav.classList.toggle('active', view === 'knowledge');

    if (view === 'home') {
        document.querySelector('.sar-header h1').textContent = t('title');
        document.querySelector('.sar-header .subtitle').textContent = t('subtitle');
        document.getElementById('project-context').textContent = '';
        renderDashboard();
    } else if (view === 'knowledge') {
        document.querySelector('.sar-header h1').textContent = t('title');
        document.querySelector('.sar-header .subtitle').textContent = t('subtitle');
        document.getElementById('project-context').textContent = '';
        renderKnowledgePage();
    } else if (view === 'project') {
        if (projectId) {
            currentProject = projectId;
            document.getElementById('project-select').value = projectId;
        }
        const proj = allProjects.find(p => p.id === currentProject);
        if (proj) {
            if (proj.context) projectContext = proj.context;
            document.querySelector('.sar-header h1').textContent = proj.name;
            const desc = typeof proj.description === 'object'
                ? (proj.description[lang] || proj.description['en']) : (proj.description || '');
            document.querySelector('.sar-header .subtitle').textContent = desc;
        }
        await loadProjectData();
    }
}

async function renderDashboard() {
    const container = document.getElementById('dashboard-content');
    container.innerHTML = '<div class="loading"><div class="spinner"></div><span class="loading-text">Loading...</span></div>';

    const [dashData, knowledgeData] = await Promise.all([
        API.get('/api/dashboard'),
        API.get('/api/knowledge'),
    ]);

    const totalPapers = knowledgeData.papers?.length || 0;
    const corePapers = knowledgeData.papers?.filter(p => p.type === 'core').length || 0;
    const activeProjects = dashData.projects.filter(p => p.status === 'active');
    const totalMols = activeProjects.reduce((s, p) => s + (p.molecule_count || 0), 0);

    const heroLabel = lang === 'zh' ? '✦ AI 驱动药物发现' : '✦ AI-DRIVEN DRUG DISCOVERY';
    const heroMain = lang === 'zh'
        ? '多智能体<span class="hero-accent">协作评议</span>，让每一步结构优化都有据可依。'
        : 'Multi-agent <span class="hero-accent">deliberation</span> for evidence-based lead optimization.';
    const heroSub = lang === 'zh'
        ? '独立分析、交叉质疑、共识收敛——三轮 AI 评议将 SAR 数据转化为可行的结构优化建议。'
        : 'Independent analysis, cross-challenge, and convergence — three rounds of AI deliberation transform SAR data into actionable recommendations.';

    container.innerHTML = `
        <div class="dashboard-hero">
            <div class="hero-label">${heroLabel}</div>
            <h2 class="hero-headline">${heroMain}</h2>
            <p class="hero-sub">${heroSub}</p>
        </div>

        <div class="dashboard-section">
            <h2 class="dashboard-section-title">${t('myProjects')}</h2>
            ${renderProjectCards(dashData.projects)}
        </div>

        <div class="dashboard-stats">
            ${renderStatCard('workflow', lang === 'zh' ? '分析流程' : 'Workflow',
                lang === 'zh' ? '独立分析 → 交叉质疑 → 共识收敛' : 'Independent → Cross-challenge → Consensus',
                lang === 'zh' ? '三轮评议' : '3-Round Deliberation')}
            ${renderStatCard('agents', lang === 'zh' ? '分析框架' : 'Agent Framework',
                lang === 'zh' ? 'Exploitation · Exploration · Risk' : 'Exploitation · Exploration · Risk',
                lang === 'zh' ? '3 个独立视角' : '3 Perspectives')}
            ${renderStatCard('knowledge', t('knowledgeBase'),
                lang === 'zh' ? `${corePapers} 篇核心 + ${totalPapers - corePapers} 篇辅助文献` : `${corePapers} core + ${totalPapers - corePapers} supporting papers`,
                lang === 'zh' ? 'ReAct 按需检索' : 'ReAct Retrieval',
                "switchView('knowledge')")}
            ${renderStatCard('molecules', lang === 'zh' ? '候选分子' : 'Candidates',
                lang === 'zh' ? `RDKit 确定性评分 · ${totalMols} 个候选` : `RDKit deterministic scoring · ${totalMols} candidates`,
                lang === 'zh' ? '无 LLM 计算层' : 'LLM-Free Scoring')}
        </div>
    `;
}

function renderStatCard(icon, title, desc, badge, onclick) {
    const icons = {
        workflow: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="5" cy="6" r="2.5"/><circle cx="19" cy="6" r="2.5"/><circle cx="12" cy="18" r="2.5"/><path d="M7.5 7l3 7.5M16.5 7l-3 7.5"/></svg>',
        agents: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="7" r="3"/><circle cx="4.5" cy="9" r="2"/><circle cx="19.5" cy="9" r="2"/><path d="M8 14.5c0-2.2 1.8-4 4-4s4 1.8 4 4v2H8v-2z"/><path d="M4.5 12.5c-1.4.7-2.5 2-2.5 3.5v1h4"/><path d="M19.5 12.5c1.4.7 2.5 2 2.5 3.5v1h-4"/></svg>',
        knowledge: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/><path d="M8 7h8M8 11h5"/></svg>',
        molecules: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 3h6v5.172a2 2 0 01-.586 1.414l-1.828 1.828a2 2 0 00-.586 1.414V22"/><path d="M7.5 3l-.354.354M16.5 3l.354.354"/><circle cx="12" cy="16" r="1.5"/><path d="M6 22h12"/><path d="M8 12l-2.5 3M16 12l2.5 3"/></svg>',
    };
    return `
        <div class="dash-stat-card${onclick ? ' clickable' : ''}"${onclick ? ` onclick="${onclick}"` : ''}>
            <div class="dash-stat-icon">${icons[icon]}</div>
            <div class="dash-stat-body">
                <div class="dash-stat-title">${title}${onclick ? ' <span class="dash-stat-arrow">&rsaquo;</span>' : ''}</div>
                <div class="dash-stat-desc">${desc}</div>
            </div>
            <div class="dash-stat-badge">${badge}</div>
        </div>`;
}

function renderProjectCards(projects) {
    return `<div class="project-cards">${projects.map(p => {
        const desc = typeof p.description === 'object'
            ? (p.description[lang] || p.description['en'])
            : (p.description || '');
        const ctx = p.context
            ? (typeof p.context === 'object' ? (p.context[lang] || p.context['en']) : p.context)
            : '';
        const isComingSoon = p.status === 'coming_soon';
        const statusCls = isComingSoon ? 'st-coming-soon' : 'st-active';
        const statusLabel = isComingSoon ? t('comingSoon') : t('activeStatus');
        const lastStr = p.last_analysis
            ? `${t('lastAnalysis')}: ${new Date(p.last_analysis).toLocaleDateString()}`
            : t('noActivity');
        const onclick = isComingSoon
            ? `showToast('${lang === 'zh' ? '该项目正在开发中' : 'This project is under development'}')`
            : `switchView('project','${p.id}')`;
        return `
            <div class="project-card ${isComingSoon ? 'disabled' : ''}"
                 onclick="${onclick}">
                <div class="project-card-header">
                    <div class="project-card-name">${p.name}</div>
                    <span class="project-status ${statusCls}">${statusLabel}</span>
                </div>
                <div class="project-card-desc">${desc}</div>
                ${ctx ? `<div class="project-card-context">${ctx}</div>` : ''}
                <div class="project-card-meta">
                    ${p.molecule_count ? `<span>${p.molecule_count} ${t('moleculeCount')}</span>` : ''}
                    <span>${lastStr}</span>
                </div>
                ${!isComingSoon ? `<div class="project-card-cta">${lang === 'zh' ? '进入项目' : 'Open Project'} <span class="cta-arrow">&rarr;</span></div>` : ''}
            </div>`;
    }).join('')}</div>`;
}

async function renderKnowledgePage() {
    const container = document.getElementById('knowledge-content');
    container.innerHTML = '<div class="loading"><div class="spinner"></div><span class="loading-text">Loading...</span></div>';

    const [knData, projData] = await Promise.all([
        API.get('/api/knowledge'),
        API.get('/api/projects'),
    ]);

    const papers = knData.papers || [];
    const projectMap = {};
    for (const p of projData.projects) { projectMap[p.id] = p; }

    const grouped = {};
    for (const p of papers) {
        if (!grouped[p.project]) grouped[p.project] = [];
        grouped[p.project].push(p);
    }

    const renderItems = (items) => items.map(p => `
        <div class="knowledge-item">
            <span class="knowledge-id">${p.id}</span>
            <span class="knowledge-title">${p.title}</span>
            <span class="knowledge-meta">${p.journal}, ${p.year}</span>
        </div>`).join('');

    let groupsHtml = '';
    for (const [projId, items] of Object.entries(grouped)) {
        const proj = projectMap[projId];
        const projName = proj ? proj.name : projId;
        const core = items.filter(p => p.type === 'core');
        const supporting = items.filter(p => p.type === 'supporting');
        groupsHtml += `
            <div class="knowledge-project-group">
                <div class="knowledge-project-name">${projName}</div>
                ${core.length ? `<div class="knowledge-group-label"><span class="knowledge-type-dot core"></span> ${t('corePapers')} · ${core.length}</div><div class="knowledge-list">${renderItems(core)}</div>` : ''}
                ${supporting.length ? `<div class="knowledge-group-label"><span class="knowledge-type-dot supporting"></span> ${t('supportingPapers')} · ${supporting.length}</div><div class="knowledge-list">${renderItems(supporting)}</div>` : ''}
            </div>`;
    }

    container.innerHTML = `
        <div class="knowledge-page">
            <div class="knowledge-page-header">
                <button class="knowledge-back-btn" onclick="switchView('home')" title="Back">&#8592;</button>
                <h2>${t('knowledgeBase')}</h2>
                <span class="knowledge-page-count">${papers.length} ${lang === 'zh' ? '篇文献' : 'papers'}</span>
            </div>
            ${groupsHtml}
        </div>`;
}

async function switchProject(projectId) {
    currentProject = projectId;
    const proj = allProjects.find(p => p.id === projectId);

    if (proj && proj.status === 'coming_soon') {
        switchView('project');
        showComingSoon(proj);
        return;
    }

    switchView('project', projectId);
}

function showComingSoon(proj) {
    const desc = typeof proj.description === 'object' ? (proj.description[lang] || proj.description['en']) : proj.description;
    projectContext = proj.context || { en: desc, zh: desc };
    document.querySelector('.sar-header h1').textContent = proj.name;
    document.querySelector('.sar-header .subtitle').textContent = desc;
    renderProjectContext();

    document.getElementById('overview-cards').innerHTML = '';
    document.getElementById('mol-list-body').innerHTML = '';
    document.getElementById('mol-count').textContent = '0';
    document.getElementById('molecule-detail').innerHTML = `
        <div class="placeholder">
            <div>
                <div style="font-size:18px;font-weight:600;margin-bottom:8px;">${t('comingSoon')}</div>
                <div style="font-size:13px;color:var(--text-muted);max-width:360px;">${t('comingSoonDesc')}</div>
                <div style="font-size:12px;color:var(--text-muted);margin-top:12px;">${desc}</div>
            </div>
        </div>`;
    document.getElementById('heatmap-charts').innerHTML = '';
    document.getElementById('compare-results').innerHTML = '';
}

async function loadProjectData() {
    switchTab('detail');
    document.getElementById('molecule-detail').innerHTML =
        '<div class="placeholder"><div class="spinner"></div></div>';
    const data = await API.get(`/api/molecules?project=${currentProject}`);
    allMolecules = data.molecules;
    refProps = data.ref_props;
    refSmiles = data.ref_smiles;

    const proj = allProjects.find(p => p.id === currentProject);
    if (proj) {
        if (proj.context) projectContext = proj.context;
        document.querySelector('.sar-header h1').textContent = proj.name;
        const desc = typeof proj.description === 'object'
            ? (proj.description[lang] || proj.description['en']) : (proj.description || '');
        document.querySelector('.sar-header .subtitle').textContent = desc;
    }
    renderProjectContext();
    renderOverview();
    renderFilterTabs();
    renderMoleculeList();
    renderHeatmapControls();
    renderCompareCheckboxes();
    renderStrategyCards();
    renderSmilesPresets();
    loadHeatmap('score');
    loadHistory();

    const bestIdx = allMolecules.reduce((bi, m, i, arr) => m.score > arr[bi].score ? i : bi, 0);
    selectMolecule(bestIdx);
}

/* ── Overview Cards ── */
function renderOverview() {
    const n = allMolecules.length;
    const passed = allMolecules.filter(m => m.verdict === 'PASS').length;
    const conditional = allMolecules.filter(m => m.verdict === 'CONDITIONAL').length;
    const bestI = allMolecules.reduce((bi, m, i, arr) => m.score > arr[bi].score ? i : bi, 0);
    const best = allMolecules[bestI];
    const avg = (allMolecules.reduce((s, m) => s + m.score, 0) / n).toFixed(1);
    const positions = new Set(allMolecules.map(m => m.position)).size;

    document.getElementById('overview-cards').innerHTML = `
        <div class="stat-card">
            <div class="stat-label">${t('candidatesLabel')}</div>
            <div class="stat-value">${n}</div>
            <div class="stat-sub">${positions} ${t('positions')}</div>
        </div>
        <div class="stat-card accent">
            <div class="stat-label">${t('passedLabel')}</div>
            <div class="stat-value">${passed}</div>
            <div class="stat-sub">${conditional} ${t('conditionalLabel')}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">${t('avgScoreLabel')}</div>
            <div class="stat-value">${avg}</div>
            <div class="stat-sub">${t('outOf100')}</div>
        </div>
        <div class="stat-card" style="cursor:pointer" onclick="selectMolecule(${bestI})">
            <div class="stat-label">${t('bestLabel')}</div>
            <div class="stat-value">${best.score}</div>
            <div class="stat-sub">${best.name.slice(0, 20)}</div>
        </div>
    `;
}

/* ── Filter Tabs ── */
function renderFilterTabs() {
    const positions = ['All', ...new Set(allMolecules.map(m => m.position))];
    document.getElementById('mol-filter-tabs').innerHTML = positions.map(p => {
        const count = p === 'All' ? allMolecules.length : allMolecules.filter(m => m.position === p).length;
        return `<button class="filter-tab ${p === currentFilter ? 'active' : ''}"
                        onclick="filterMolecules('${p}')">${p} <span style="opacity:0.6">${count}</span></button>`;
    }).join('');
}

function filterMolecules(position) {
    currentFilter = position;
    renderFilterTabs();
    renderMoleculeList();
    let filtered = allMolecules.map((m, i) => ({ ...m, idx: i }));
    if (currentFilter !== 'All') {
        filtered = filtered.filter(m => m.position === currentFilter);
    }
    if (filtered.length > 0 && !filtered.some(m => m.idx === selectedMolIdx)) {
        const best = filtered.reduce((a, b) => a.score > b.score ? a : b);
        selectMolecule(best.idx);
    }
}

/* ── Molecule List ── */
function renderMoleculeList() {
    let filtered = allMolecules.map((m, i) => ({ ...m, idx: i }));
    if (currentFilter !== 'All') {
        filtered = filtered.filter(m => m.position === currentFilter);
    }
    const sorted = filtered.sort((a, b) => b.score - a.score);

    document.getElementById('mol-count').textContent = `${sorted.length}`;
    document.getElementById('mol-list-body').innerHTML = sorted.map(m => {
        const vcls = m.verdict === 'PASS' ? 'tag-pass' : m.verdict === 'CONDITIONAL' ? 'tag-conditional' : 'tag-fail';
        const isActive = m.idx === selectedMolIdx ? ' active' : '';
        return `
            <div class="mol-list-item${isActive}" data-idx="${m.idx}" onclick="selectMolecule(${m.idx})">
                <div class="mol-list-info">
                    <div class="mol-list-name">${m.name}</div>
                    <div class="mol-list-position">${m.position}</div>
                </div>
                <div class="mol-list-right">
                    <span class="mol-list-score">${m.score}</span>
                    <span class="tag ${vcls}">${m.verdict}</span>
                </div>
            </div>`;
    }).join('');
}

/* ── Select Molecule ── */
async function selectMolecule(idx) {
    selectedMolIdx = idx;

    document.querySelectorAll('.mol-list-item').forEach(el => {
        el.classList.toggle('active', parseInt(el.dataset.idx) === idx);
    });

    const activeTab = document.querySelector('.tab-btn.active')?.dataset.tab;
    if (activeTab === 'heatmap') {
        highlightHeatmapMolecule(allMolecules[idx].position, allMolecules[idx].name);
    }

    const detail = document.getElementById('molecule-detail');
    detail.innerHTML = '<div class="placeholder"><div class="spinner"></div></div>';

    const data = await API.get(`/api/molecule/${idx}?project=${currentProject}`);
    renderMoleculeDetail(data);
}

function highlightHeatmapMolecule(position, moleculeName) {
    const shortName = moleculeName ? moleculeName.replace(/^C34-/, '') : null;

    document.querySelectorAll('#heatmap-charts > div').forEach(div => {
        if (!div.data || !div.data[0]) return;

        if (div._origAnnotations) {
            Plotly.relayout(div, { shapes: [], annotations: div._origAnnotations });
            delete div._origAnnotations;
        }

        if (div.dataset.position !== position) return;
        div.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        if (!shortName) return;

        const xCats = div.data[0].x || [];
        const barIdx = xCats.findIndex(x => {
            if (x === shortName) return true;
            const xClean = x.replace(/…$/, '');
            const sClean = shortName.replace(/…$/, '');
            return sClean.startsWith(xClean) || xClean.startsWith(sClean);
        });
        if (barIdx < 0) return;

        const origAnnotations = (div.layout?.annotations || []).map(a => ({ ...a, font: { ...a.font } }));
        div._origAnnotations = origAnnotations;

        const dimmedAnnotations = origAnnotations.map((a, i) => {
            if (i === barIdx) return { ...a, font: { ...a.font, size: 15 }, text: `<b>${a.text}</b>` };
            return { ...a, font: { ...a.font, size: a.font.size, color: 'rgba(150,150,150,0.6)' } };
        });

        const shapes = [
            { type: 'rect', xref: 'x', yref: 'y',
              x0: barIdx - 0.5, x1: barIdx + 0.5, y0: -0.5, y1: 0.5,
              line: { color: 'rgba(118,251,145,0.7)', width: 1.5 },
              fillcolor: 'rgba(0,0,0,0)' },
        ];
        for (let i = 0; i < xCats.length; i++) {
            if (i === barIdx) continue;
            shapes.push({
                type: 'rect', xref: 'x', yref: 'y',
                x0: i - 0.5, x1: i + 0.5, y0: -0.5, y1: 0.5,
                line: { width: 0 },
                fillcolor: 'rgba(255,255,255,0.55)',
            });
        }

        Plotly.relayout(div, { shapes, annotations: dimmedAnnotations });
    });
}

/* ── Molecule Detail ── */
function renderMoleculeDetail(data) {
    const mol = data.molecule;
    const p = mol.properties;
    const bd = mol.breakdown || {};
    const vcls = mol.verdict === 'PASS' ? 'tag-pass' : mol.verdict === 'CONDITIONAL' ? 'tag-conditional' : 'tag-fail';

    const propItems = [
        { label: 'MW', value: p.mw.toFixed(1), cls: propCls(p.mw, 500, 550) },
        { label: 'cLogP', value: p.logp.toFixed(2), cls: propCls(p.logp, 5.0, 5.5) },
        { label: 'TPSA', value: p.tpsa.toFixed(1), cls: '' },
        { label: 'QED', value: p.qed.toFixed(3), cls: propClsInv(p.qed, 0.3, 0.2) },
        { label: 'SA', value: p.sa_score.toFixed(2), cls: propCls(p.sa_score, 5.0, 7.0) },
        { label: 'LogS', value: (p.logs || 0).toFixed(2), cls: propClsInv(p.logs || 0, -4, -6) },
    ];

    const gateItems = GATES.map(g => {
        const val = bd[g.key] || 0;
        return { ...g, val, status: gateStatus(val, g) };
    });
    const failedGates = gateItems.filter(g => g.status.cls !== 'gate-pass');
    const brenkAlerts = data.brenk_alerts || [];
    const brenkChips = brenkAlerts.map(a =>
        `<span class="risk-chip gate-warn">Brenk: ${a} ⚠</span>`
    ).join('');
    const gateChips = failedGates.map(g =>
        `<span class="risk-chip ${g.status.cls}">${g.label} ${g.val.toFixed(0)}/${g.max} ${g.status.icon}</span>`
    ).join('');
    const riskChipsHtml = (failedGates.length === 0 && brenkAlerts.length === 0)
        ? '<span class="risk-chip gate-pass">All Gates ✓</span>'
        : gateChips + brenkChips;

    const totalScore = bd.total || 0;
    const scoreColor = totalScore >= 75 ? 'score-good' : totalScore >= 60 ? 'score-ok' : 'score-low';

    const detail = document.getElementById('molecule-detail');
    detail.innerHTML = `
        <div class="detail-header">
            <div class="detail-header-left">
                <div class="detail-name">${mol.name}</div>
                <div class="detail-meta">${mol.position} · Similarity: ${(mol.similarity || 0).toFixed(3)}</div>
                <div class="detail-smiles" onclick="copyToClipboard(this)" title="Click to copy">${mol.smiles || ''}</div>
            </div>
            <div class="detail-header-right">
                <div class="detail-score">${mol.score}</div>
                <span class="tag ${vcls}">${mol.verdict}</span>
            </div>
        </div>
        <div class="risk-chips">${riskChipsHtml}</div>
        <div class="detail-body">
            <div class="detail-svg">${data.svg}</div>
            <div class="detail-radar" id="detail-radar"></div>
        </div>
        <div class="prop-grid">
            ${propItems.map(item => `
                <div class="prop-item">
                    <div class="prop-label">${item.label}</div>
                    <div class="prop-value ${item.cls}">${item.value}</div>
                </div>`).join('')}
        </div>
        <div class="gate-table">
            ${gateItems.map(g => {
                const passPos = (g.pass / g.max * 100).toFixed(0);
                const valPos = Math.min(g.val / g.max * 100, 100).toFixed(0);
                const needleColor = g.status.cls === 'gate-pass' ? 'var(--success)' : g.status.cls === 'gate-warn' ? 'var(--warning)' : 'var(--danger)';
                return `
                <div class="gate-range-row">
                    <span class="gate-dot ${g.status.cls}"></span>
                    <span class="gate-range-name">${g.label}</span>
                    <span class="gate-range-val">${g.val.toFixed(0)}<small> / ${g.max}</small></span>
                    <div class="gate-range-bar">
                        <div class="gate-bar-track">
                            <div class="gate-bar-fail-zone" style="width:${passPos}%"></div>
                            <div class="gate-bar-pass-zone" style="width:${100 - passPos}%"></div>
                        </div>
                        <div class="gate-needle" style="left:${valPos}%;background:${needleColor}"></div>
                        <span class="gate-threshold" style="left:${passPos}%">${g.pass}</span>
                    </div>
                </div>`;
            }).join('')}
            <div class="gate-total-row">
                <div class="gate-total-label">Total</div>
                <div class="gate-total-score ${scoreColor}">${(bd.total || 0).toFixed(0)}<small> / ${bd.total_max || 100}</small></div>
                <div class="gate-total-bar">
                    <div class="gate-total-fill" style="width:${((bd.total || 0) / (bd.total_max || 100) * 100).toFixed(0)}%"></div>
                </div>
            </div>
        </div>
    `;

    const radarData = data.radar;
    Plotly.newPlot('detail-radar', radarData.data, radarData.layout, PLOTLY_CONFIG);
}

function propCls(val, lo, hi) {
    return val <= lo ? 'good' : val <= hi ? 'warn' : 'bad';
}
function propClsInv(val, lo, hi) {
    return val >= lo ? 'good' : val >= hi ? 'warn' : 'bad';
}

const GATES = [
    { key: 'binding_3d', label: '3D Shape Match', max: 25, pass: 20, warn: 12 },
    { key: 'lipinski', label: 'Lipinski', max: 20, pass: 18, warn: 12 },
    { key: 'qed', label: 'QED', max: 15, pass: 12, warn: 7 },
    { key: 'sa', label: 'Synth. Access.', max: 10, pass: 8, warn: 5 },
    { key: 'veber', label: 'Veber', max: 10, pass: 10, warn: null },
    { key: 'pains', label: 'PAINS', max: 10, pass: 10, warn: null },
    { key: 'similarity', label: 'Similarity', max: 10, pass: 8, warn: 5 },
];

function gateStatus(val, gate) {
    if (val >= gate.pass) return { cls: 'gate-pass', icon: '✓' };
    if (gate.warn !== null && val >= gate.warn) return { cls: 'gate-warn', icon: '⚠' };
    return { cls: 'gate-fail', icon: '✗' };
}

/* ── Heatmap ── */
const HEATMAP_PROPS = [
    { key: 'score', label: 'Score' },
    { key: 'binding', label: '3D Shape' },
    { key: 'mw', label: 'MW' },
    { key: 'logp', label: 'cLogP' },
    { key: 'qed', label: 'QED' },
    { key: 'sa', label: 'SA Score' },
    { key: 'logs', label: 'LogS' },
    { key: 'delta_mw', label: 'ΔMW' },
    { key: 'delta_logp', label: 'ΔLogP' },
];

function renderHeatmapControls() {
    document.getElementById('heatmap-controls').innerHTML = HEATMAP_PROPS.map(p =>
        `<button class="heatmap-btn ${p.key === 'score' ? 'active' : ''}"
                 data-prop="${p.key}" onclick="loadHeatmap('${p.key}')">${p.label}</button>`
    ).join('');
}

async function loadHeatmap(prop) {
    document.querySelectorAll('.heatmap-btn').forEach(b => {
        b.classList.toggle('active', b.dataset.prop === prop);
    });

    const container = document.getElementById('heatmap-charts');
    container.innerHTML = '<div class="loading"><div class="spinner"></div><span class="loading-text">Loading heatmap...</span></div>';

    try {
        const data = await API.get(`/api/heatmap?prop=${prop}&project=${currentProject}`);
        container.innerHTML = '';
        const divs = [];
        for (const fig of data.figures) {
            const div = document.createElement('div');
            div.style.marginBottom = '16px';
            container.appendChild(div);
            divs.push({ div, fig });
        }
        await new Promise(r => requestAnimationFrame(r));
        const cw = container.clientWidth;
        for (const { div, fig } of divs) {
            const titleText = fig.layout?.title?.text || fig.layout?.title || '';
            div.dataset.position = titleText.split(/\s*[—–\-]\s*/)[0].trim();
            const layout = { ...fig.layout };
            delete layout.template;
            layout.width = cw > 0 ? cw : undefined;
            layout.margin = { l: 70, r: 50, t: 30, b: 70 };
            layout.xaxis = { ...layout.xaxis, type: 'category' };
            layout.yaxis = { ...layout.yaxis, type: 'category' };
            if (fig.data[0]?.colorbar) {
                fig.data[0].colorbar = { ...fig.data[0].colorbar, x: 1.0, xpad: 4, thickness: 10 };
            }
            await Plotly.newPlot(div, fig.data, layout, { displayModeBar: false, responsive: true });
        }
    } catch (err) {
        container.innerHTML = `<div style="color:var(--danger);padding:16px;">Heatmap error: ${err.message}</div>`;
    }
}

/* ── Comparison ── */
function renderCompareCheckboxes() {
    const sorted = allMolecules.map((m, i) => ({ ...m, idx: i }))
        .sort((a, b) => b.score - a.score);

    document.getElementById('compare-checkboxes').innerHTML = sorted.map(m => {
        const sel = compareSet.has(m.idx) ? ' selected' : '';
        return `<button class="compare-chip${sel}" onclick="toggleCompare(${m.idx})"><span class="chip-name">${m.name.slice(0, 18)}</span><span class="chip-score">${m.score}</span></button>`;
    }).join('');
}

function toggleCompare(idx) {
    if (compareSet.has(idx)) {
        compareSet.delete(idx);
    } else if (compareSet.size < 4) {
        compareSet.add(idx);
    }
    renderCompareCheckboxes();
}

async function runComparison() {
    if (compareSet.size < 2 || compareSet.size > 4) {
        alert('Select 2-4 molecules to compare.');
        return;
    }
    const indices = Array.from(compareSet).join(',');
    const container = document.getElementById('compare-results');
    container.innerHTML = '<div class="loading"><div class="spinner"></div><span class="loading-text">Comparing...</span></div>';

    const data = await API.get(`/api/comparison?indices=${indices}&project=${currentProject}`);

    const cols = data.molecules.length;
    let cardsHtml = `<div class="compare-grid" style="grid-template-columns:repeat(${cols},1fr);">`;
    data.molecules.forEach(item => {
        const mol = item.molecule;
        const sColor = mol.verdict === 'PASS' ? '#22C55E' : mol.verdict === 'CONDITIONAL' ? '#F59E0B' : '#EF4444';
        cardsHtml += `
            <div class="compare-card">
                <div class="mol-name">${mol.name.slice(0, 18)}</div>
                <div class="mol-position">${mol.position}</div>
                <div class="mol-score" style="color:${sColor}">${mol.score}</div>
                ${item.svg}
            </div>`;
    });
    cardsHtml += '</div>';

    const propKeys = ['mw', 'logp', 'tpsa', 'qed', 'sa_score', 'hbd', 'hba'];
    const propLabels = ['MW', 'cLogP', 'TPSA', 'QED', 'SA Score', 'HBD', 'HBA'];
    const refVals = {};
    propKeys.forEach(k => { refVals[k] = typeof refProps[k] === 'number' ? refProps[k] : 0; });

    let tableHtml = '<table class="compare-table"><thead><tr><th>Property</th>';
    tableHtml += '<th class="ref-cell">C34 (Ref)</th>';
    data.molecules.forEach(item => { tableHtml += `<th>${item.molecule.name.slice(0, 15)}</th>`; });
    tableHtml += '</tr></thead><tbody>';
    propKeys.forEach((k, i) => {
        const rv = refVals[k];
        tableHtml += `<tr><td>${propLabels[i]}</td>`;
        tableHtml += `<td class="ref-cell">${rv.toFixed(2)}</td>`;
        data.molecules.forEach(item => {
            const v = item.molecule.properties[k];
            const num = typeof v === 'number' ? v : 0;
            const d = num - rv;
            const dStr = d === 0 ? '' : ` <span class="delta-inline">${d > 0 ? '+' : ''}${d.toFixed(2)}</span>`;
            tableHtml += `<td>${num.toFixed(2)}${dStr}</td>`;
        });
        tableHtml += '</tr>';
    });
    tableHtml += '</tbody></table>';

    container.innerHTML = cardsHtml + tableHtml + '<div id="compare-radar" class="mt-16"></div>';
    Plotly.newPlot('compare-radar', data.radar.data, data.radar.layout, PLOTLY_CONFIG);
}

/* ── Custom SMILES ── */
const SMILES_PRESETS = [
    { label: 'Osimertinib', smiles: 'C=CC(=O)Nc1nc(Nc2ccc(N(C)CCN(C)C)cc2OC)ncc1-c1cn(C)c2ccccc12' },
    { label: 'Gefitinib', smiles: 'COc1cc2ncnc(Nc3ccc(F)c(Cl)c3)c2cc1OCCCN1CCOCC1' },
    { label: 'Afatinib', smiles: 'CN(C)C/C=C/C(=O)Nc1cc2c(Nc3ccc(F)c(Cl)c3)ncnc2cc1OC1CCOC1' },
];

function renderSmilesPresets() {
    document.getElementById('smiles-presets').innerHTML = SMILES_PRESETS.map(p =>
        `<button class="smiles-preset" onclick="fillSmiles('${p.smiles}')">${p.label}</button>`
    ).join('');
}

function fillSmiles(smiles) {
    document.getElementById('smiles-input').value = smiles;
}

async function evaluateSmiles() {
    const smiles = document.getElementById('smiles-input').value.trim();
    if (!smiles) return;

    const container = document.getElementById('smiles-result');
    container.innerHTML = '<div class="loading"><div class="spinner"></div><span class="loading-text">Evaluating...</span></div>';

    const ev = await API.post('/api/evaluate', { smiles, project: currentProject });

    if (ev.valid === false) {
        container.innerHTML = `<div style="color:var(--danger);padding:16px;">${ev.error || 'Invalid SMILES'}</div>`;
        return;
    }

    const p = ev.properties;
    const vcls = ev.verdict === 'PASS' ? 'tag-pass' : ev.verdict === 'CONDITIONAL' ? 'tag-conditional' : 'tag-fail';
    const evalProps = [
        { label: 'MW', value: p.mw.toFixed(1), cls: propCls(p.mw, 500, 550) },
        { label: 'cLogP', value: p.logp.toFixed(2), cls: propCls(p.logp, 5.0, 5.5) },
        { label: 'TPSA', value: p.tpsa.toFixed(1), cls: '' },
        { label: 'QED', value: p.qed.toFixed(3), cls: propClsInv(p.qed, 0.3, 0.2) },
        { label: 'SA', value: p.sa_score.toFixed(2), cls: propCls(p.sa_score, 5.0, 7.0) },
        { label: 'LogS', value: (p.logs || 0).toFixed(2), cls: propClsInv(p.logs || 0, -4, -6) },
    ];
    container.innerHTML = `
        <div class="detail-card" style="margin-top:12px;">
            <div class="detail-header">
                <div class="detail-header-left">
                    <div class="detail-name">Custom Molecule</div>
                    <div class="detail-meta">Similarity: ${(ev.similarity || 0).toFixed(3)}</div>
                </div>
                <div class="detail-header-right">
                    <div class="detail-score">${ev.score}</div>
                    <span class="tag ${vcls}">${ev.verdict}</span>
                </div>
            </div>
            <div class="detail-body">
                <div class="detail-svg">${ev.svg}</div>
                <div class="detail-radar" id="smiles-eval-radar"></div>
            </div>
            <div class="prop-grid">
                ${evalProps.map(item => `
                    <div class="prop-item">
                        <div class="prop-label">${item.label}</div>
                        <div class="prop-value ${item.cls}">${item.value}</div>
                    </div>`).join('')}
            </div>
        </div>
    `;
    Plotly.newPlot('smiles-eval-radar', ev.radar.data, ev.radar.layout, PLOTLY_CONFIG);
}

/* ── Collapsible ── */
function toggleCollapsible(id) {
    const el = document.getElementById(id);
    if (el.classList.contains('collapsible')) {
        el.classList.toggle('open');
    } else {
        const isHidden = el.style.display === 'none';
        el.style.display = isHidden ? 'block' : 'none';
    }
}

/* ── Streaming helpers ── */
const STRATEGY_AGENT_NAMES = {
    focused: ['结构-活性分析', '多参数优化'],
    standard: ['结构-活性分析', '多参数优化', '风险评估'],
    comprehensive: ['结构-活性分析', '多参数优化', '风险评估', 'ADMET预测', '合成可行性'],
};

function agentDotKey(agentName) {
    return (AGENT_META[agentName] || {}).dot || 'sa';
}

function renderEmptyRound(num, agentNames, title) {
    const n = agentNames.length;
    const gridCls = n <= 2 ? 'agent-grid-2' : n >= 5 ? 'agent-grid-5' : 'agent-grid';
    let cards = `<div class="${gridCls}">`;
    agentNames.forEach(name => {
        const meta = AGENT_META[name] || { dot: 'sa', icon: '🔬', en: name };
        const displayName = lang === 'en' ? (meta.en || name) : name;
        const cardId = `agent-r${num}-${meta.dot}`;
        cards += `
            <div class="agent-card streaming" id="card-${cardId}">
                <div class="agent-card-header">
                    <div class="agent-dot ${meta.dot}"></div>
                    <div class="agent-name">${meta.icon} ${displayName}</div>
                    <div class="agent-status" id="status-${cardId}"></div>
                </div>
                <div class="agent-card-body" id="body-${cardId}">
                    <div class="agent-waiting">${lang === 'zh' ? '等待中…' : 'Waiting…'}</div>
                </div>
            </div>`;
    });
    cards += '</div>';
    return `
        <div class="round-section">
            <div class="round-header">
                <span class="round-badge">${num === 3 ? '<span style="background:var(--accent);color:var(--text);">' : ''}Round ${num}${num === 3 ? '</span>' : ''}</span>
                <span class="round-title">${title}</span>
                <span class="round-duration" id="round${num}-duration"></span>
            </div>
        </div>
        ${cards}`;
}

function onAgentStart(roundNum, agentName) {
    const dot = agentDotKey(agentName);
    const cardId = `agent-r${roundNum}-${dot}`;
    const card = document.getElementById(`card-${cardId}`);
    const body = document.getElementById(`body-${cardId}`);
    const status = document.getElementById(`status-${cardId}`);
    if (card) card.classList.add('generating');
    if (status) status.innerHTML = '<div class="agent-generating-dot"></div>';
    if (body) body.innerHTML = '';
}

function onReactStep(roundNum, agentName, step, nameZh, nameEn) {
    const dot = agentDotKey(agentName);
    const cardId = `agent-r${roundNum}-${dot}`;
    const body = document.getElementById(`body-${cardId}`);
    if (!body) return;
    const stepName = lang === 'zh' ? nameZh : nameEn;
    const stepId = `${cardId}-step${step}`;
    const stepHtml = `
        <div class="react-step active" id="${stepId}">
            <div class="react-step-header" onclick="this.parentElement.classList.toggle('collapsed')">
                <span class="react-step-num">${step}</span>
                <span class="react-step-name">${stepName}</span>
                <span class="react-step-chevron">▾</span>
            </div>
            <div class="react-step-body">
                <div class="agent-stream-text streaming-cursor"></div>
            </div>
        </div>`;
    body.insertAdjacentHTML('beforeend', stepHtml);
}

function onChunk(roundNum, agentName, text) {
    const dot = agentDotKey(agentName);
    const cardId = `agent-r${roundNum}-${dot}`;
    const body = document.getElementById(`body-${cardId}`);
    if (!body) return;
    const steps = body.querySelectorAll('.react-step');
    const lastStep = steps.length > 0 ? steps[steps.length - 1] : null;
    if (lastStep) {
        const streamEl = lastStep.querySelector('.agent-stream-text');
        if (streamEl) {
            streamEl.textContent += text;
            lastStep.querySelector('.react-step-body').scrollTop = lastStep.querySelector('.react-step-body').scrollHeight;
        }
    }
}

function onReactStepDone(roundNum, agentName, step, text) {
    const dot = agentDotKey(agentName);
    const cardId = `agent-r${roundNum}-${dot}`;
    const stepEl = document.getElementById(`${cardId}-step${step}`);
    if (!stepEl) return;
    stepEl.classList.remove('active');
    stepEl.classList.add('done');
    const stepBody = stepEl.querySelector('.react-step-body');
    if (stepBody) stepBody.innerHTML = mdToHtml(text);
    if (step < 3) {
        stepEl.classList.add('collapsed');
    }
}

function onAgentDone(roundNum, agentName, fullText) {
    const dot = agentDotKey(agentName);
    const cardId = `agent-r${roundNum}-${dot}`;
    const card = document.getElementById(`card-${cardId}`);
    const status = document.getElementById(`status-${cardId}`);
    if (card) { card.classList.remove('generating', 'streaming'); card.classList.add('done'); }
    if (status) status.innerHTML = '<span class="agent-done-check">✓</span>';
}

async function consumeSSE(url, body, onEvent) {
    const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    });
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop();
        for (const line of lines) {
            if (!line.startsWith('data: ')) continue;
            try { onEvent(JSON.parse(line.slice(6))); }
            catch (e) { console.error('SSE parse error:', e); }
        }
    }
}

/* ── Deliberation ── */
async function startDeliberation() {
    const focus = document.getElementById('analysis-focus').value.trim();
    const contextEl = document.getElementById('user-context');
    const context = contextEl ? contextEl.value.trim() : '';
    const btn = document.getElementById('start-btn');
    btn.disabled = true;
    btn.textContent = t('running');

    const emptyEl = document.getElementById('analysis-empty');
    if (emptyEl) emptyEl.style.display = 'none';

    const agentNames = STRATEGY_AGENT_NAMES[analysisStrategy];
    document.getElementById('round1-area').innerHTML = renderEmptyRound(1, agentNames, t('r1'));
    document.getElementById('review-gate').classList.add('hidden');
    document.getElementById('round2-area').innerHTML = '';
    document.getElementById('round3-area').innerHTML = '';
    document.getElementById('delib-summary').innerHTML = '';

    try {
        await consumeSSE('/api/delib/stream/r1',
            { focus, context, lang, project: currentProject, strategy: analysisStrategy },
            (event) => {
                switch (event.type) {
                    case 'agent_start':
                        onAgentStart(1, event.agent);
                        break;
                    case 'react_step':
                        onReactStep(1, event.agent, event.step, event.name_zh, event.name_en);
                        break;
                    case 'chunk':
                        onChunk(1, event.agent, event.text);
                        break;
                    case 'react_step_done':
                        onReactStepDone(1, event.agent, event.step, event.text);
                        break;
                    case 'agent_done':
                        onAgentDone(1, event.agent, event.full_text || '');
                        break;
                    case 'round_done':
                        delibSessionId = event.session_id;
                        const durEl = document.getElementById('round1-duration');
                        if (durEl) durEl.textContent = `${event.duration}s`;
                        showReviewGate();
                        break;
                }
            });
    } catch (err) {
        document.getElementById('round1-area').innerHTML =
            `<div style="color:var(--danger);padding:16px;">Error: ${err.message}</div>`;
    }

    btn.disabled = false;
    btn.textContent = t('startAnalysis');
}

function showReviewGate() {
    const gate = document.getElementById('review-gate');
    gate.classList.remove('hidden');
    gate.innerHTML = `
        <div class="review-gate">
            <h3>${t('reviewTitle')}</h3>
            <p>${t('reviewDesc')}</p>
            <textarea class="guidance-input" id="guidance-input"
                      placeholder="e.g. Focus on Tail position synthesis feasibility; challenge the MPO ranking"></textarea>
            <div style="font-size:12px;color:var(--text-muted);margin-bottom:12px;">${t('guidanceHint')}</div>
            <button class="btn btn-primary btn-full" onclick="continueRound2()">${t('continueR2')}</button>
        </div>`;
}

async function continueRound2() {
    const guidance = document.getElementById('guidance-input').value.trim();
    const gate = document.getElementById('review-gate');
    gate.innerHTML = '<div class="review-gate" style="border-left-color:var(--accent)"><p style="margin:0;color:var(--text-muted);font-size:13px;">Guidance submitted</p></div>';

    const agentNames = STRATEGY_AGENT_NAMES[analysisStrategy];
    document.getElementById('round2-area').innerHTML = renderEmptyRound(2, agentNames, t('r2'));

    await consumeSSE('/api/delib/stream/r2',
        { session_id: delibSessionId, guidance },
        (event) => {
            switch (event.type) {
                case 'agent_start':
                    onAgentStart(2, event.agent);
                    break;
                case 'react_step':
                    onReactStep(2, event.agent, event.step, event.name_zh, event.name_en);
                    break;
                case 'chunk':
                    onChunk(2, event.agent, event.text);
                    break;
                case 'react_step_done':
                    onReactStepDone(2, event.agent, event.step, event.text);
                    break;
                case 'agent_done':
                    onAgentDone(2, event.agent, event.full_text || '');
                    break;
                case 'round_done':
                    const durEl = document.getElementById('round2-duration');
                    if (durEl) durEl.textContent = `${event.duration}s`;
                    break;
            }
        });

    await runRound3();
}

async function runRound3() {
    document.getElementById('round3-area').innerHTML = `
        <div class="round-section">
            <div class="round-header">
                <span class="round-badge" style="background:var(--accent);color:var(--text);">Round 3</span>
                <span class="round-title">${t('r3')}</span>
            </div>
        </div>
        <div class="convergence-card generating">
            <h3>${t('consensus')}</h3>
            <div class="convergence-body">
                <div class="agent-stream-text streaming-cursor" id="r3-stream"></div>
            </div>
        </div>`;

    let fullText = '';
    let traces = [];

    await consumeSSE('/api/delib/stream/r3',
        { session_id: delibSessionId },
        (event) => {
            switch (event.type) {
                case 'chunk':
                    fullText += event.text;
                    const el = document.getElementById('r3-stream');
                    if (el) { el.textContent += event.text; el.parentElement.scrollTop = el.parentElement.scrollHeight; }
                    break;
                case 'r3_done':
                    document.querySelector('.convergence-card')?.classList.remove('generating');
                    document.getElementById('round3-area').innerHTML = `
                        <div class="round-section">
                            <div class="round-header">
                                <span class="round-badge" style="background:var(--accent);color:var(--text);">Round 3</span>
                                <span class="round-title">${t('r3')}</span>
                            </div>
                        </div>
                        <div class="convergence-card">
                            <h3>${t('consensus')}</h3>
                            <div class="convergence-body">${formatConvergence(fullText)}</div>
                        </div>`;
                    break;
                case 'all_done':
                    traces = event.traces || [];
                    break;
            }
        });

    document.getElementById('delib-summary').innerHTML = `
        <div class="glass-card">
            <h3>${t('complete')}</h3>
            <p style="font-size:14px;color:var(--text-secondary);margin:0;">
                ${STRATEGY_CARDS[analysisStrategy].agents} Agents × 3 Rounds · ${traces.length} LLM calls
            </p>
        </div>
        ${renderTraces(traces)}
    `;
    delibSessionId = null;
    loadHistory();
}

/* ── History ── */
async function loadHistory() {
    const container = document.getElementById('history-list');
    if (!container) return;
    try {
        const data = await API.get(`/api/history?project=${currentProject}`);
        const items = data.history || [];
        if (items.length === 0) {
            container.innerHTML = `<div style="font-size:12px;color:var(--text-muted);padding:8px 0;">${t('historyEmpty')}</div>`;
            return;
        }
        container.innerHTML = items.map(h => {
            const date = new Date(h.timestamp);
            const dateStr = date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            const focusStr = h.focus ? ` · ${h.focus}` : '';
            return `
                <div class="history-item" onclick="loadHistoryDetail('${h.id}')">
                    <div class="history-date">${dateStr}</div>
                    <div class="history-focus">${focusStr}</div>
                </div>`;
        }).join('');
    } catch (e) {
        container.innerHTML = '';
    }
}

async function loadHistoryDetail(histId) {
    try {
        const h = await API.get(`/api/history/${histId}?project=${currentProject}`);
        const r1Data = { agent_outputs: h.rounds.r1, duration: 0 };
        const r2Data = { agent_outputs: h.rounds.r2, duration: 0 };

        document.getElementById('analysis-empty').style.display = 'none';
        document.getElementById('round1-area').innerHTML = renderRound(1, r1Data, t('r1'));
        document.getElementById('review-gate').classList.add('hidden');
        document.getElementById('round2-area').innerHTML = renderRound(2, r2Data, t('r2'));
        document.getElementById('round3-area').innerHTML = `
            <div class="round-section">
                <div class="round-header">
                    <span class="round-badge" style="background:var(--accent);color:var(--text);">Round 3</span>
                    <span class="round-title">${t('r3')}</span>
                </div>
            </div>
            <div class="convergence-card">
                <h3>${t('consensus')}</h3>
                <div class="convergence-body">${formatConvergence(h.rounds.r3)}</div>
            </div>`;
        document.getElementById('delib-summary').innerHTML = '';

        switchTab('analysis');
    } catch (e) {
        console.error('Failed to load history:', e);
    }
}

/* ── CoT Parsing (backward compat for history) ── */
function parseAgentOutput(text) {
    const markerPairs = [
        ['【推理过程】', '【分析结论】'],
        ['【Reasoning Process】', '【Analysis Conclusion】'],
    ];
    for (const [cotMarker, conclusionMarker] of markerPairs) {
        const cotIdx = text.indexOf(cotMarker);
        const concIdx = text.indexOf(conclusionMarker);
        if (cotIdx >= 0 && concIdx > cotIdx) {
            return {
                thinking: text.slice(cotIdx + cotMarker.length, concIdx).trim(),
                conclusion: text.slice(concIdx + conclusionMarker.length).trim(),
            };
        }
    }
    return { thinking: '', conclusion: text };
}

function renderCotBlock(thinking) {
    if (!thinking) return '';
    const lines = thinking.split('\n').filter(l => l.trim());
    const refCount = lines.filter(l => l.includes('[') && l.includes(']')).length || lines.length;
    const body = lines.map(l => {
        l = l.trim().replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        return `<div class="agent-cot-line">${l}</div>`;
    }).join('');
    return `
        <div class="agent-cot collapsed" onclick="this.classList.toggle('collapsed')">
            <div class="agent-cot-header">
                <span class="agent-cot-icon">▸</span>
                <span>${t('reasoning')}</span>
                <span class="agent-cot-count">${refCount} ${t('nRefs')}</span>
            </div>
            <div class="agent-cot-body">${body}</div>
        </div>`;
}

/* ── Render Helpers ── */
function showLoading(text) {
    return `<div class="loading"><div class="spinner"></div><span class="loading-text">${text}</span></div>`;
}

function renderRound(num, roundData, title) {
    const dur = roundData.duration ? `${roundData.duration}s` : '';
    const agentNames = Object.keys(roundData.agent_outputs);
    const n = agentNames.length;
    const gridCls = n <= 2 ? 'agent-grid-2' : n >= 5 ? 'agent-grid-5' : 'agent-grid';

    let cards = `<div class="${gridCls}">`;
    agentNames.forEach(name => {
        const meta = AGENT_META[name] || { dot: 'sa', icon: '🔬', en: name };
        const content = roundData.agent_outputs[name] || '';
        const displayName = lang === 'en' ? (meta.en || name) : name;
        const parsed = parseAgentOutput(content);
        const cotHtml = renderCotBlock(parsed.thinking);
        cards += `
            <div class="agent-card">
                <div class="agent-card-header">
                    <div class="agent-dot ${meta.dot}"></div>
                    <div class="agent-name">${meta.icon} ${displayName}</div>
                </div>
                <div class="agent-card-body">${cotHtml}${mdToHtml(parsed.conclusion)}</div>
            </div>`;
    });
    cards += '</div>';

    return `
        <div class="round-section">
            <div class="round-header">
                <span class="round-badge">Round ${num}</span>
                <span class="round-title">${title}</span>
                <span class="round-duration">${dur}</span>
            </div>
        </div>
        ${cards}`;
}

function mdToHtml(text) {
    if (!text) return '';
    return text.split('\n').filter(l => l.trim()).map(line => {
        line = line.trim();
        line = line.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        if (line.startsWith('•')) return `<div class="agent-bullet">${line}</div>`;
        if (line.match(/^(<strong>|[1-3]\.)/)) return `<div class="agent-heading">${line}</div>`;
        if (line.startsWith('易') || line.startsWith('难')) return `<div style="font-size:12px;color:var(--text-secondary);padding:6px 10px;background:var(--bg-card);border-radius:6px;margin:4px 0;font-family:monospace;">${line}</div>`;
        return `<p>${line}</p>`;
    }).join('');
}

function formatConvergence(text) {
    if (!text) return '';
    const sections = text.split('【');
    return sections.map(section => {
        if (!section.trim()) return '';
        section = '【' + section;
        const titleEnd = section.indexOf('】');
        if (titleEnd > 0) {
            const title = section.slice(1, titleEnd);
            const body = section.slice(titleEnd + 1).trim();
            const lines = body.split('\n').filter(l => l.trim()).map(l => {
                l = l.trim().replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
                return `<p>${l}</p>`;
            }).join('');
            return `<h4>【${title}】</h4>${lines}`;
        }
        return `<p>${section.trim()}</p>`;
    }).join('');
}

function renderTraces(traces) {
    if (!traces || !traces.length) return '';

    const items = traces.map((tr, i) => {
        const dotCls = (AGENT_META[tr.agent] || {}).dot || 'sa';
        return `
            <div class="trace-item" id="trace-${i}">
                <div class="trace-header" onclick="document.getElementById('trace-${i}').classList.toggle('open')">
                    <span class="trace-round-tag">Round ${tr.round}</span>
                    <span class="trace-agent-tag">${tr.agent}</span>
                    <span class="trace-duration">${tr.duration || 0}s</span>
                </div>
                <div class="trace-body">
                    <div class="trace-color-bar ${dotCls}"></div>
                    <div class="trace-content">${mdToHtml(tr.output)}</div>
                </div>
            </div>`;
    }).join('');

    return `
        <div class="collapsible" id="traces-collapsible">
            <div class="collapsible-header" onclick="toggleCollapsible('traces-collapsible')">
                <span>${t('traces')} (${traces.length} calls)</span>
                <span class="chevron">&#9662;</span>
            </div>
            <div class="collapsible-body">
                <div class="trace-container">${items}</div>
            </div>
        </div>`;
}

/* ── Tab Switching ── */
function switchTab(tab) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.toggle('active', b.dataset.tab === tab));
    document.querySelectorAll('.tab-pane').forEach(p => p.classList.toggle('active', p.id === `tab-${tab}`));
}

/* ── Molecule Panel Toggle ── */
function toggleMolPanel() {
    document.querySelector('.app-layout').classList.toggle('sidebar-collapsed');
}

/* ── Copy to Clipboard ── */
function copyToClipboard(el) {
    const text = el.textContent.trim();
    navigator.clipboard.writeText(text);
    const orig = el.textContent;
    el.textContent = 'Copied!';
    setTimeout(() => { el.textContent = orig; }, 1200);
}

/* ── Keyboard Navigation ── */
document.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    if (e.key !== 'ArrowUp' && e.key !== 'ArrowDown') return;
    e.preventDefault();

    const items = Array.from(document.querySelectorAll('.mol-list-item'));
    if (!items.length) return;

    const activeIdx = items.findIndex(el => el.classList.contains('active'));
    let nextIdx;
    if (e.key === 'ArrowDown') {
        nextIdx = activeIdx < items.length - 1 ? activeIdx + 1 : 0;
    } else {
        nextIdx = activeIdx > 0 ? activeIdx - 1 : items.length - 1;
    }
    const molIdx = parseInt(items[nextIdx].dataset.idx);
    selectMolecule(molIdx);
    items[nextIdx].scrollIntoView({ block: 'nearest' });
});

/* ── Toast ── */
function showToast(msg) {
    let toast = document.getElementById('app-toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'app-toast';
        toast.className = 'app-toast';
        document.body.appendChild(toast);
    }
    toast.textContent = msg;
    toast.classList.add('show');
    clearTimeout(toast._timer);
    toast._timer = setTimeout(() => toast.classList.remove('show'), 2500);
}
