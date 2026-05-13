# AI驱动药物发现平台竞争分析报告：聚焦先导化合物优化（Lead Optimization）

**时间范围：2024-2026 | 调研日期：2026年5月**

---

## 一、Latent Labs / Latent-Y（重点分析）

### 产品定位
Latent-Y 是一个**自主AI Agent**，能从文本 prompt 出发，**端到端自主执行抗体设计 campaign**——覆盖文献综述、靶点分析、表位（epitope）识别、候选分子设计、计算验证、实验可用序列筛选。

### 核心技术
- **Agentic Architecture**：运行在与人类专家相同的工作环境中，可访问生物信息学工具、分子数据库、科学文献
- **生成模型 Latent-X2**：frontier generative model，从靶点结构和表位规格生成 drug-like binder。支持多模态（VHH nanobody、scFv、macrocyclic peptide）
- **Self-extending capabilities**：agent 可从自然语言描述生成自定义计算方法

### 关键指标
- 9个靶点中6个成功（67% target-level success rate）
- 结合亲和力达到 single-digit nanomolar
- 比独立专家快 56 倍

### 关键澄清
**Latent-Y 聚焦 biologics（抗体/nanobody/peptide），而非小分子 lead optimization。**

### 融资
- 2025年 $50M seed（Radical Ventures、Sofinnova、Jeff Dean、Dario Amodei）
- 2026年3月正式发布

---

## 二、Recursion Pharmaceuticals（含 Exscientia 合并）

### 核心平台
- **LOWE**：LLM-Orchestrated Workflow Engine，自然语言界面驱动药物发现任务
- **Phenomic screening**：每周 220 万样本，60+ PB 数据
- **BioHive-2**：504 H100 GPU，2 exaflops
- 2024年11月完成与 Exscientia 合并（$688M all-stock）

### 最新进展
- REC-1245 获 IND 批准，首位患者入组 Phase I/II
- REC-994 和 REC-2282 因疗效不佳停止开发
- Bayer 为 LOWE 首个 beta 用户
- Cash runway 至 2028 年初

### 优势与劣势
| 优势 | 劣势 |
|---|---|
| 唯一真正 end-to-end | 核心临床项目失败 |
| 工业级自动化实验室 + 超算 | 整合风险高 |

---

## 三、Insilico Medicine / 英矽智能

### Chemistry42 核心技术
- 40+ 生成模型集成并行运行
- Multi-agent reinforcement learning 协议驱动
- 合成路线预测
- Chemistry42GPT 交互式辅助

### 最新进展
- 2024年：两篇 Nature Biotechnology
- 2025年12月港交所上市，IPO 22.8 亿港元
- 截至2026年4月：第30个 PCC 提名，12个 IND，3个 Phase II
- 与 Eli Lilly 合作 "Prompt-to-Drug" 框架

### 效率数据
- 平均 PCC 时间：12-18 个月（vs 传统 4.5 年）
- 每个项目合成 60-200 个分子，成本约 $2.6M

---

## 四、Schrödinger LiveDesign（Incumbent）

### 市场地位
- Top 20 药企中19家为客户
- 年合同 >= $500K 的客户 100% 留存率
- 2024年软件收入 $180.4M（+13.3%）
- Novartis $150M upfront + 最高 $2.3B milestones（2025.01）

### 核心技术
- FEP+（Free Energy Perturbation）量子力学精度
- 2024年推出 LiveDesign Biologics
- 2026年与 Eli Lilly 集成 Lilly TuneLab

---

## 五、PostEra

### 核心差异化
- Synthesis-aware molecular design（不只生成好分子，还确保能合成）
- Pfizer 合作扩大至 $610M（2025.01），新增 ADC 方向
- Preclinical milestones 比 Pfizer 预期快 40%
- 团队仅 43 人，累计合作总额超 $1B

---

## 六、Iambic Therapeutics

### 核心技术
- NeuralPLexer：超越 AlphaFold 的蛋白-配体结构预测
- Design-make-test cycle 每周一轮
- 2026年2月与 Takeda 合作，最高 $1.7B
- 总融资 $327M

---

## 七、Isomorphic Labs（Google DeepMind / Alphabet）

### 核心技术
- AlphaFold 3（2024.05）：蛋白-小分子交互预测精度提升 50%
- IsoDDE（2026.02）：精度是 AlphaFold 3 的 2 倍以上，完全私有
- 2026年5月 $2.1B Series B（AI drug discovery 史上最大私募融资之一）
- 17个活跃项目，预计 2026 年底进入人体临床

---

## 八、Terray Therapeutics

### 核心壁垒
- **14B** 个 target-molecule 测量（全球最大化学数据集，公开数据的 ~50 倍）
- TerraBind：比行业领先模型精度高 20%，速度快 26x，成本降 96%
- COATI foundation model（已开源）
- 合作伙伴：BMS、Calico、Gilead

---

## 九、中国竞争者

### 晶泰科技 XtalPi — AI-CRO 模式
- 2024年6月港交所上市，"中国 AI 制药第一股"
- 2024 营收 2.66 亿元（+52.8%）
- ID4Idea 平台：GLP-1 候选分子体外活性提升 3 倍
- 签署数十亿美元管线授权合作意向书

### 望石智慧 StoneWise
- Lingo3DMol（2024 Nature Machine Intelligence）：语言模型+几何深度学习
- StoneMIND Designer：国内首个商业化 AI 分子设计软件
- 与齐鲁制药战略合作、华为联合发布 AI 药研方案

### 深势科技 DP Technology
- Uni-Mol 系列（ICLR 2023, NeurIPS 2024），1.1B 参数
- 2025年 Series C $114M
- 定位 AI 科学计算"安卓系统"，1000+ 高校 + 150 企业客户

---

## 十、行业趋势总结

### 三种模型并存
1. **End-to-End 平台**（Recursion+Exscientia、Insilico、Isomorphic）
2. **Decision-support 工具**（Schrödinger LiveDesign、望石智慧）
3. **Specialized 平台**（PostEra synthesis-aware、Terray data-centric、Iambic physics-informed）

### 2025-2026 最新趋势
- AI Agent / Autonomous Systems 成为主流方向
- 数据壁垒成为核心竞争力（算法层正在被 commoditize）
- 临床验证成为分水岭（AI Phase I 成功率 80-90% vs 传统 52%，但 Phase II/III 极少）
- 融资超级集中化

### 仍未被填补的关键空白
1. 小分子 lead optimization 的"最后一公里"决策支持
2. 模型可解释性
3. 实验数据闭环（Terray 是例外）
4. 中小 biotech 和学术实验室的可及性
5. 跨疾病领域通用性
6. 监管框架
7. Multi-modal integration gap
