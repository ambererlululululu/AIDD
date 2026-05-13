# 药物化学家 Lead Optimization 日常工作流深度调研报告

**调研日期：2026年5月**

---

## 一、工具生态（按实际使用频率排列）

### Excel + ChemDraw：至今仍是"默认操作系统"
- Excel 不"理解"化学结构，科学家发明各种 workaround（截图粘贴、SMILES 字符串）
- 按结构搜索"几乎不可能"
- 无版本控制、无审计追踪
- 数据孤岛问题：从一个系统导出到 spreadsheet 再导入另一个
- 多家公司报告"因 spreadsheet 管理小错误导致不必要的开支"——包括向监管机构提交错误数据
- Mount Sinai 2024年的 Drug Discovery Guide 仍是 Excel 模板格式

### Spotfire：SAR 可视化行业标准
- 交互式数据探索、SAR 图表、模块化化学图表
- 让 bench chemist 能直接使用高级 SAR 分析工具

### Schrödinger LiveDesign：渗透率最高的协作平台
- Top 20 药企中 **19家** 使用
- ACV>=50万美元客户 **100% 续约率**（2024）
- 2024年软件收入 $180.4M
- 实际场景："团队经常在开会时打开 LiveDesign，实时编辑、展示想法、决定最佳设计方案"

### Dotmatics Vortex：化学感知数据分析
- 2025年 Siemens 以 **$5.1B** 收购
- "团队花费大量时间在各模块间协调数据"

### 其他工具
- **Benchling**：分子生物学强，化学工具弱
- **CDD Vault**：中小型 biotech 的 SaaS 选择
- **ACD/Labs Percepta**：物化性质预测，超过 80% Top 品牌药企使用
- **开源生态**：RDKit + Jupyter + Python，近年增长显著

### 市场数据
- Drug Discovery Informatics 2025年约 $3B，预计2031年 $5.3B
- **67% 中型 biotech 在采用平台后 18个月内就超出了平台能力**

---

## 二、DMTA 决策周期

### Design（设计）
- 跨学科团队：药化学家、计算化学家、DMPK、生物学家、安全性评估
- 审查当前 SAR 数据，提出下一轮合成方案
- 使用 MPO 框架同时平衡 15-20 个参数
- 计算化学家分析 SAR 数据并"以清晰简洁的方式"分享结果

### Make（合成）— 最大瓶颈
- DMTA 迭代可能占药物发现项目总支出的 **30%**（AstraZeneca 数据）
- 单次循环需要**数周到数月**
- 合成偏差：科学家倾向于合成**容易获得**而非**真正有意义**的化合物
- 当前最常用合成反应中**没有一个是过去20年内发现的**

### Test（测试）
- Screening cascade 层级测试
- 体外活性 → ADME → 理化性质 → 毒性筛选

### Analyze（分析）
- 数据汇总、SAR 更新、指导下一轮

### 关键矛盾
- **设计通量远大于合成通量**："合成和测试通量明显低于团队提出新方案的速度"
- MPO 数据质量困境：IC50 等实测值可能有 **2倍实验变异**，预测值可能有**一个数量级不确定性**

---

## 三、从业者自述痛点

### Reddit 社区系统性分析（ACS Med Chem Lett 2025）
1. **AI "黑箱"问题**：无法理解推荐理由，"因为 AI 说的"不是可接受的答案
2. **AI 分子不可合成**：约 **30%** AI 生成分子需 7步以上合成或含不稳定结构
3. **合成仍是 rate-limiting step**：最常用反应没有一个是过去20年发现的
4. **新模态 "intellectually promising but logistically frustrating"**

### Derek Lowe（Novartis 总监，27年行业经验）
- "短期悲观主义者，长期乐观主义者"
- "我们行业想解决的问题，与 AI 能解决的问题，几乎成反比"
- "有机合成化学文献是一团糟"——训练数据有系统性偏差
- "不是机器取代化学家，而是**使用机器的化学家取代不使用的**"
- 2025年1月 Chemistry World 专栏："Claims of an AI revolution are missing the biggest problem"

### 数据孤岛
- "许多项目在数据管理策略上存在断裂的数据孤岛"
- "虽然产生了大量数据，但为数据科学家标准化数据是许多实验室中相对较新的问题"

---

## 四、AI 工具实际采用

### 真正在用的工具
- **FEP+**（Schrödinger）：行业采用最广的物理+计算工具，可替代约 60% 物理合成
- **Chemistry42**（Insilico）：20+药企使用，30+内部管线，rentosertib Phase IIa 达主要终点
- **REINVENT 4**（AZ）：2024年发表，已部署到管线
- **Makya**（Iktos）：用已知反应和真实起始物料逐步构建分子，直接解决可合成性
- **MolSkill**（Novartis）：化学家直觉的 ML 代理，已在多个项目实际使用，已开源

### 量化数据
- 超过 **70项 IND** 涉及 AI/ML 方法
- 2024年 **15个+ AI 分子**进入临床
- **76%** biotech 团队用 AI 做文献综述，71% 结构预测，66% 报告撰写
- AI 驱动药物发现融资 2024年超 **$3B**（+43%）

### 最大障碍
Iktos CEO："大多数采用挑战**与算法无关**，而与**组织整合**有关。你必须说服药化学家、给他们想用的工具、投资培训。"

---

## 五、决策一致性：20年研究链

| 研究 | 年份 | 参与者 | 核心发现 |
|------|------|--------|----------|
| **Lajiness** (Pharmacia) | 2004 | ~11组 | 自我一致性 **50%**，同行一致性 **28%** |
| **Kutchukian** (PLOS ONE) | 2012 | 多名 | 仅用 **1-2个参数**决策，不自知偏差 |
| **Choung** (Novartis) | 2023 | 35人 | Inter-rater kappa **0.32-0.4**；ML学到正交于现有指标的维度 |
| **Llompart** (Sanofi) | 2025 | 92人 | **集体>个人>AI**（除hERG）；CI+AI混合最优 |

**20年一致结论**：决策不一致不是能力问题，而是任务认知复杂性超出人类个体处理能力。解决方案是"系统化增强和聚合人类专业知识"。

---

## 六、行业数字化率

### Deloitte R&D Lab of the Future（2025.04）
- 仅 **11%** 药企实现 "predictive lab"
- 22% 认为 2-3年可达到
- **近60%** R&D 高管预期投资带来 IND 增加和发现加速

### Deloitte Measuring Return from Innovation（2024-2025）
- 药物发现到上市平均成本 2025年 **$2.67B**
- 去除 GLP-1 后 IRR 仅 **2.9%**
- **AI 尚未缩短 100个月的 bench-to-filing 周期**

### McKinsey
- GenAI 每年可为制药创造 **$60-110B** 价值
- **工作流重设计**对 EBIT 影响最大

### BCG
- 不到 **50%** 员工有权使用 GenAI 工具
- AI 候选药物临床成功率号称 90% vs 传统 65%（需谨慎解读）

---

## 七、国内从业者特点

### 市场
- 2019年0.7亿元 → 2023年4.1亿元（CAGR 57.4%）
- 预计2028年 58.6亿元

### 工具生态差异
- LiveDesign/Spotfire 在外资药企和大 CRO 使用
- 国产平台（晶泰 ID4Idea、英矽 Pharma.AI）在国内 biotech 更常见
- **Excel 依赖同样严重**

### 人才结构
- AI 制药人才更多来自计算机/AI 背景而非传统药化
- 可能导致"会AI不懂化学" vs "懂化学不会AI"的沟通鸿沟

### 从业者痛点（知乎/公众号）
- 数据可及性不足、模型可解释性差、临床翻译困难
- "知其然不知其所以然"——缺乏底层原理的方法开发逻辑

---

## Sources
- [Llompart 2025, J. Med. Chem.](https://pubs.acs.org/doi/abs/10.1021/acs.jmedchem.4c03066)
- [Choung 2023, Nature Communications](https://www.nature.com/articles/s41467-023-42242-1)
- [Kutchukian 2012, PLOS ONE](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0048476)
- [Derek Lowe, Bio-IT World 2025](https://www.bio-itworld.com/news/2025/04/15/derek-lowe-on-ai-in-drug-discovery-between-hype-and-hope)
- [ACS Med Chem Lett 2025 - Reddit分析](https://pubs.acs.org/doi/10.1021/acsmedchemlett.5c00483)
- [Deloitte 2025 Lab of the Future](https://www.deloitte.com/us/en/insights/industry/health-care/future-proofing-pharma-rnd-labs.html)
- [Deloitte 2025 Measuring Return](https://www.deloitte.com/us/en/Industries/life-sciences-health-care/articles/measuring-return-from-pharmaceutical-innovation.html)
- [ACD/Labs Excel问题](https://www.acdlabs.com/blog/your-data-deserves-better-than-excel-7-ways-spreadsheets-hold-back-pharmaceutical-innovation/)
- [AZ DMTA 2024, Drug Discovery Today](https://www.sciencedirect.com/science/article/pii/S1359644624000709)
- [J. Med. Chem. 2024 - Real-World AI/ML](https://pubs.acs.org/doi/10.1021/acs.jmedchem.4c03044)
