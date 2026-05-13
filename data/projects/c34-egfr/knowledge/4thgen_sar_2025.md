# 4th-Gen EGFR-TKI Comprehensive SAR Review (Layer 1 Summary)

**Full title**: Fourth-generation EGFR-TKI to overcome C797S mutation: past, present, and future
**Journal**: J. Enzyme Inhib. Med. Chem. 2025
**PMC**: PMC12172088
**Scope**: 77 compounds across 12+ scaffold classes

## Critical Binding Interactions (All Scaffolds)

### MET793 (Hinge Region) — Most Important
- Bidentate H-bonds: compounds using pyrimidinone, pyrrolidine scaffolds
- Single H-bonds: aminopyrimidine motifs
- **Universal requirement across all active 4th-gen compounds**

### MET790 (Gatekeeper) — Selectivity Driver
- Hydrophobic interactions: Br (van der Waals), 5-methyl, isopropoxy/isobutoxy
- Larger hydrophobic groups → better T790M selectivity over WT
- Key for discriminating mutant from WT EGFR

### SER797 (C797S Residue) — Potency Differentiator
- Direct H-bonds: methanesulfonamide oxygen, pyrazinylmethylamino, piperidine-4-methanol
- Compounds with S797 interactions show highest potency against triple mutant
- **Distinguishes best C797S-active compounds from merely T790M-active ones**

### LYS745 — Versatile Anchor
- H-bonds: isoindolinone carbonyl, phosphine oxide, quinoxaline N
- Water-mediated: pyrimidinone carbonyl
- Covalent: sulfonyl electrophiles (alternative to C797)

### Back Hydrophobic Pocket (K745, E762, L788, M766, M790)
- Consistently occupied by 2-chlorophenyl, 4-fluorophenyl, aryl groups
- Required for potent binding

## Top Compounds by Potency

| Compound | IC₅₀ (Triple Mutant) | Scaffold | WT Selectivity |
|----------|----------------------|----------|----------------|
| BI-4020 (73) | 0.20 nM | Aminobenzimidazole macrocycle | High |
| CH7233163 (74) | <1 nM | HTS hit, non-covalent | High |
| JND3229 (51) | 5.8 nM | Pyrimidinopyridone | Low (limitation) |
| C34 (Zhu) | 5.1 nM | Thiazole-pyrimidine | Needs data |
| Compound 19 | 13.7 nM | Osimertinib-derived reversible | 131x |
| BPI-361175 | 15 nM (Del19), 34 nM (L858R) | Undisclosed | Phase 2 |
| Compound 56 | 18 nM | 9H-purine sulfonyl | Good |
| Brigatinib | 55.5 nM | DMPO-pyrimidine | 10x |

## Scaffold Classes and Design Strategies

### 1. Quinazoline-derived (from gefitinib/erlotinib)
- Gefitinib/erlotinib modifications with new functional groups
- Hydroxylamine groups for brain penetration (compound 2: CNS-active)

### 2. Osimertinib-derived (acrylamide removed)
- Remove Michael acceptor → reversible binding
- Add hydroxyalkyl chains for DFG motif interaction (Asp855)
- Methanesulfonamide → H-bond with S797 (compound 22)
- Cyclization strategy (compound 18): TGI=70.75%, superior to TQB3804

### 3. Brigatinib-derived (DMPO-containing)
- DMPO moiety occupies triphosphate space → 70x potency increase
- Compound 26: >50x selectivity, dose-dependent in vivo
- Compound 34: F=81.7% oral bioavailability, 94x WT selectivity

### 4. Allosteric (EAI series)
- EAI001 → EAI045 → JBJ series
- 2-aminothiazole core between MET790/LYS745
- Monotherapy insufficient (EGFR dimerization blocks access)
- Combination with cetuximab or osimertinib required

### 5. Macrocyclic
- "Start Selective and Rigidify" principle (BI-4020)
- Lock active conformation → dramatic potency improvement
- BI-4020: 0.20 nM, TGI=121%

### 6. Hybrid (osimertinib + brigatinib)
- Combine structural features from both scaffolds
- Mixed results — some compounds excellent in enzyme but poor cell permeability

## Key SAR Principles for C34 Optimization

1. **Hinge H-bond (MET793)** — C34's pyrimidine provides this. Must maintain.
2. **Hydrophobic MET790 interaction** — C34's fluorophenyl fills this. Para-F is optimal.
3. **S797 H-bond** — Current C34 may lack direct S797 interaction. Adding methanesulfonamide or hydroxyl groups could improve potency.
4. **Back pocket occupation** — C34's fluorophenyl occupies this. Keep.
5. **Reducing MW** — Macrocyclization or conformational constraint could help. But C34 at 634 Da is already near limit.
6. **WT selectivity** — Exploit MET790 hydrophobic contacts (C34's fluorophenyl already does this).
7. **Oral bioavailability** — C34 at 30.72%. Brigatinib derivative 34 achieves 81.7%. Study piperidine modifications.
8. **Brain penetration** — Not reported for C34. Increasingly important for NSCLC with CNS mets.

## Clinical Landscape Summary (as of 2025)

| Status | Compounds |
|--------|-----------|
| **Discontinued** | BLU-945, BBT-176 |
| **Phase I/II active** | TQB-3804, BDTX-1535, H002, JIN-A02, BPI-361175, BAY2927088 |
| **Phase I no data** | TQB-3804, ES-072 |
| **Most promising** | BDTX-1535 (55% ORR, brain-penetrant, broadest coverage) |
| **Most potent preclinical** | BI-4020 (0.20 nM), CH7233163 (<1 nM) |
| **Preclinical only** | BI-4020, JND3229, THE-349, LS-106, and ~60 others |
