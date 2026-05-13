# C34 EGFR C797S — Domain Knowledge

## Target Biology

EGFR C797S is the most common tertiary resistance mutation in NSCLC patients after osimertinib treatment, occurring in 10-26% of second-line and ~7% of first-line osimertinib-resistant cases (Su et al. 2024, Transl. Cancer Res.). The triple mutant L858R/T790M/C797S eliminates the Cys797 residue that all covalent EGFR inhibitors rely on for irreversible binding. Fourth-generation inhibitors must use non-covalent reversible binding mechanisms.

No approved 4th-gen EGFR TKI exists as of 2025. BDTX-1535 (55% ORR, brain-penetrant) is the most promising clinical candidate. BLU-945 and BBT-176 have both been discontinued. TQB-3804 is in Phase I/II in China with no released data (NCT04128085).

## C34 Scaffold and Binding Mode (Zhu et al. 2023, J. Med. Chem.)

C34 is a thiazole-pyrimidine derivative discovered via structure-based virtual screening from lead S8. IC50 = 5.1 nM against EGFR L858R/T790M/C797S; cell IC50 = 50 nM (H1975-TM). Oral bioavailability = 30.72%.

**Structure**: C₃₂H₃₆FN₇O₂S₂, MW = 633.81
**SMILES**: CCS(=O)(=O)N1CCC(CC1)C2=NC(=C(C3=CC=NC(NC4=CC=C5N(CCN(C)C)C=CC5=C4)=N3)S2)C6=CC=C(C=C6)F

Pharmacophore elements:
- **Pyrimidine** (hinge binder): H-bonds with MET793 in hinge region. Fixed — do not modify.
- **Thiazole** (central linker): Connects hinge to hydrophobic pocket. Fixed — do not modify.
- **4-Fluorophenyl** (Aryl position): Fills back hydrophobic pocket (K745/E762/L788/M766/M790), van der Waals with gatekeeper MET790. Modifiable.
- **Ethylsulfonyl-piperidine** (Sulfonyl position): Solubility/PK handle. Modifiable.
- **Indole-dimethylaminoethyl** (Tail): Solvent-exposed, PK/brain penetration. Modifiable.

## SAR Findings (Zhu et al. 2023)

### Aryl Position (para-F phenyl)
- para-F optimal: electron withdrawal enhances binding via thiazole to hinge
- para-Cl/Br: slightly reduced potency (steric clash with MET790 pocket)
- para-CH₃: tolerated but LogP increase without benefit
- para-OMe/NH₂: electron-donating → reduced activity
- para-CF₃: maintains potency but MW/LogP penalty

### Sulfonyl Position (EtSO₂-piperidine)
- Sulfonyl critical for solubility (reduces LogP vs alkyl)
- Et optimal: Me too small (less metabolic shielding), Pr diminishing returns + MW
- Cyclic sultam: improved metabolic stability but harder to synthesize
- Carboxamide replacement: significantly reduced solubility

### Tail Position (indole + NMe₂-ethyl)
- NMe₂-ethyl basicity (pKa ~8-9) essential for solubility
- Removing basic amine: dramatically reduced oral bioavailability
- Morpholine replacement: tolerated, may improve metabolic stability
- Propyl linker: reduced potency vs ethyl
- Indole N-methylation: tolerated without potency loss

## Key SAR Principles from Literature (77 compounds across 12+ scaffold classes)

Based on comprehensive review of 4th-gen EGFR-TKI SAR (PMC12172088, 2025):

1. **MET793 hinge H-bond** — universal requirement, C34's pyrimidine provides this
2. **MET790 hydrophobic interaction** — drives selectivity over WT EGFR. Larger hydrophobic groups (isopropoxy, Br, methyl) improve selectivity. C34's para-F phenyl serves this role.
3. **SER797 direct H-bond** — distinguishes the most potent C797S compounds. C34 may lack this. Adding methanesulfonamide or hydroxyl groups is a validated strategy (compound 22, IC50 improvement with S797 H-bond).
4. **Back hydrophobic pocket** (K745/E762/L788/M766/M790) — must be occupied. C34's fluorophenyl does this.
5. **Macrocyclization** can dramatically improve potency: BI-4020 achieves 0.20 nM via conformational constraint.
6. **DMPO group** (brigatinib-derived) occupies triphosphate space → 70x potency increase.

## Design Constraints

1. MW = 634 — near upper limit. Prefer MW-neutral modifications.
2. Measured LogP ~6.2 — above Ro5. Reducing LogP is high priority for oral PK.
3. Must maintain non-covalent mechanism (no electrophilic warheads targeting C797S).
4. F = 30.72% — acceptable but improvable. Brigatinib derivative 34 achieves 81.7% via piperidine optimization.
5. WT EGFR selectivity critical. Best-in-class achieves 131x (compound 19) to >500x (D51, same group).
6. Brain penetration not reported for C34 but increasingly important (NSCLC CNS mets).

## Competitor Landscape (Updated 2025)

| Compound | Scaffold | Status | Key Data |
|----------|----------|--------|----------|
| Osimertinib | Pyrimidine (covalent C797) | Approved (3rd-gen) | Ineffective vs C797S |
| BDTX-1535 | Irreversible (non-C797) | Phase I/II | 55% ORR, brain-penetrant, broadest coverage |
| BLU-945 | 2,7-naphthyridine | **Discontinued** | Cannot cover 19del/C797S without T790M |
| BBT-176 | Reversible ATP-comp | **Terminated** | 1/18 PR, successor BBT-207 in development |
| TQB-3804 | Non-covalent | Phase I/II (China) | IC50 0.218 (triple), 36x WT selectivity |
| BI-4020 | Aminobenzimidazole macrocycle | Preclinical | IC50 0.20 nM, TGI 121% |
| CH7233163 | HTS hit | Preclinical | IC50 <1 nM |
| BPI-361175 | Undisclosed | Phase II | IC50 15 nM (Del19), 34 nM (L858R) |
| D51 (Dong) | Same group as C34 | Preclinical | IC50 14 nM, >500x WT selectivity |

## Detailed Summaries

See `knowledge/` directory for per-paper Layer 1 summaries:
- [index.md](knowledge/index.md) — Full literature index
- [zhu_2023_c34.md](knowledge/zhu_2023_c34.md) — C34 source paper
- [eno_2022_blu945.md](knowledge/eno_2022_blu945.md) — BLU-945 discovery
- [su_2024_review.md](knowledge/su_2024_review.md) — 4th-gen landscape review
- [4thgen_sar_2025.md](knowledge/4thgen_sar_2025.md) — Comprehensive SAR (77 compounds)
