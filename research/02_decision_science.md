# 决策科学与药物发现的交叉：Lead Optimization 领域（2023-2026）

**调研日期：2026年5月**

---

## 1. 药物化学中的决策一致性

### 1.1 Choung et al. 2023 — Novartis / Microsoft Research, Nature Communications

**论文：** "Extracting medicinal chemistry intuition via preference machine learning"

**具体发现：**
- **35名** Novartis 化学家，收集超过 **5,000 条**标注（pairwise comparison）
- **Inter-rater agreement：** Fleiss' kappa = **0.4**（第一轮）和 **0.32**（第二轮），属于"中等一致性"
- **Intra-rater agreement：** Cohen's kappa = **0.6**，个体一致率 78.9%-100%
- **ML 结果：** MolSkill 在 5,000 对标注后 AUROC ~0.75，且未到达 plateau
- **核心发现：** MolSkill 与现有 in silico metrics（QED 等）的 Pearson 相关系数不超过 **0.4**——化学家的直觉知识**正交于**现有计算指标
- **区分能力：** MolSkill F-statistic = **546.88**，远超 QED 的 **22.83**

**Source:** https://www.nature.com/articles/s41467-023-42242-1

### 1.2 Llompart et al. 2025 — Sanofi / Max Planck, J. Med. Chem.

**论文：** "Harnessing Medicinal Chemical Intuition from Collective Intelligence"

**具体发现：**
- **92 名** Sanofi 研究者，匿名参与，自评 med chem 经验 1-5 分
- 实验设计：Late-stage lead optimization 的 ADMET 属性判断
- **三大核心结论：**
  1. **Collective > Individual：** 混合专家和非专家的群体聚合后准确度显著提升
  2. **Collective > AI（除 hERG 外）：** logP、logD、permeability、solubility 四个 endpoint 上集体智慧优于 AI
  3. **互补性：** 人类集体+AI 的 hybrid prediction 效果最优

**Source:** https://doi.org/10.1021/acs.jmedchem.4c03066
**GitHub:** https://github.com/Sanofi-Public/IDD-Collective-Intelligence

### 1.3 其他相关研究
- **Truebel & Seidler 2022, Nat Rev Drug Disc：** 117名药企高管排名 top cognitive biases
- **Weber et al. 2024, Clin Trans Sci：** 认知偏差影响从研发到临床到监管全链条
- **Leeson & Springthorpe 2007, Nat Rev Drug Disc：** Lipinski Ro5 如何塑造并限制决策空间

---

## 2. 多参数优化（MPO）现状

### 2.1 主要方法
- **Pfizer CNS MPO：** 6个理化性质，0-6分。局限：logP和logD double counting；完全无法区分立体异构体（AUROC=0.50）
- **AbbVie AB-MPS：** cLogD + aromatic rings + rotatable bonds。局限：与 PAMPA 相关性弱（r=-0.28）
- **CNS-TEMPO：** 8个理化性质，显著优于前两者

### 2.2 系统性批评
- Retrospective bias：基于已上市药物校准，对传统靶点过拟合
- 软件依赖：不同计算器对同一化合物打分不同
- 新模态失效：PROTACs、macrocycles 超出 Ro5 框架
- AI 模型超越 MPO：Bayesian model 92.5% vs CNS MPO v1 75%

### 2.3 2024-2025 前沿
- **Mechanistic MPO（2024）：** 基于生理学机制，AUCROC > 0.95
- **Racz et al. 2025, Nat Rev Drug Disc：** Novartis+AZ 联合分析优化趋势系统性变化
- **Holistic Drug Design：** 根据项目阶段灵活组合 MPO 方法

---

## 3. AI 辅助决策实例

### 3.1 行业共识："Augmented Intelligence" > "Artificial Intelligence"
- "Not a replacement... but complementary tools that augment human expertise"
- FDA 2025 草案：AI 是 support 而非 replace 监管决策

### 3.2 已部署系统
- **AstraZeneca ChatInvent（2026）：** 从单 agent 发展为 multi-agent 架构，集成机构数据库和 HPC
- **AstraZeneca PIP：** Cloud-native 建模平台，生成式 AI + 强化学习
- **Insilico Chemistry42：** de novo 设计 + 优化 + GPT 交互

---

## 4. 多智能体 AI 系统在科学领域

### 4.1 理论基础
- **Du et al. 2023 (ICML 2024)：** 奠基性工作——多 LLM 辩论提升推理和事实准确性
- **关键发现：** 初始轻度分歧（"productive initial chaos"）增加辩论后改进概率

### 4.2 科学领域已验证实例

**Coated-LLM (iScience 2025)：**
- Alzheimer's disease 联合用药假设生成
- Researcher + Reviewers + Moderator 三类 agent
- 准确率 **0.82**（外部验证），显著优于传统方法（0.52）
- **实验验证了全新联合疗法**（m266 + Gypenoside XVII）
- **最接近"多智能体审议做科学决策"的已验证案例**

**The Virtual Biotech (bioRxiv 2026, Stanford)：**
- 11 agent + Virtual CSO，分析 55,984 个临床试验
- 靶向 cell-type-specific genes 的药物进入 Phase II 概率高 **40%**，到市场概率高 **48%**

**Google AI Co-Scientist (arXiv 2025)：**
- 基于 Gemini 2.0，"generate, debate, and evolve"
- Scientist-in-the-loop 设计
- AML 药物重定位、liver fibrosis 新靶点均经实验确认

**ChemCrow (Nature Machine Intelligence 2024)：**
- 18 个化学工具 + GPT-4 agent
- 自主规划并执行合成

### 4.3 Sanofi 研究如何支持 Multi-Agent 方法

Llompart 的发现映射到 Wisdom of Crowds 四条件：
1. **Diversity** → 不同 system prompt 和工具集
2. **Independence** → 独立生成分析后再聚合
3. **Decentralization** → 各自持有不同知识和工具
4. **Aggregation** → 结构化聚合机制

**核心论点：** 通过 multi-agent 模拟"结构化分歧→聚合"，理论上可在更低成本下获得类似的决策质量提升。

---

## 5. Lead Optimization 的真正瓶颈

### 瓶颈层次分析

**#1 合成速度（Make 环节）：** 物理性瓶颈，每个化合物 $5K-50K，2-6 周

**#2 决策质量（Design 环节）：** 因为合成产能有限，**选择合成哪些化合物**的决策质量决定整个项目效率。每一个错误选择消耗 2-6 周和数万美元

**#3 数据碎片化：** DMTA 循环中数据缺乏一致性和可重复性

**#4 多目标冲突：** Drug target binding 仅是 15-20 个需要同时优化的参数之一

**关键结论：** 真正的瓶颈是**合成产能约束下的决策质量**。这不是"数据不够"或"算法不准"——Choung 证明人类知识正交于现有算法，Llompart 证明集体智慧优于单一判断——这是一个**决策结构问题**。

---

## 面试可引用论文

| 论文 | 核心论点 | 面试用法 |
|------|---------|---------|
| Choung 2023, Nat Commun | kappa 仅 0.32-0.4；直觉正交于现有指标 | 证明决策不一致是真实问题 |
| Llompart 2025, J Med Chem | 集体 > 个人 > AI（除hERG）；互补 | 证明"结构化聚合"的价值 |
| Truebel & Seidler 2022 | 117名高管排名 cognitive biases | 行业层面承认的问题 |
| Coated-LLM 2025, iScience | Multi-agent debate 准确率 0.82 | 最接近的已验证案例 |
| Virtual Biotech 2026 | 11 agent 分析 55,984 临床试验 | 工程可行性 |
| Google AI Co-Scientist 2025 | Generate-debate-evolve | 产业级实现 |
| ChatInvent 2026 | AZ 的 agentic 分子设计 | 大药企已部署 |
