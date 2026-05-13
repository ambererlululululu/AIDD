from __future__ import annotations
import os, sys
from rdkit import Chem
from rdkit.Chem import Descriptors, QED


def _load_sa():
    try:
        from rdkit.Chem import RDConfig
        sa_path = os.path.join(RDConfig.RDContribDir, "SA_Score")
        if sa_path not in sys.path:
            sys.path.insert(0, sa_path)
        import sascorer
        return sascorer
    except Exception:
        return None


_sa = _load_sa()

COMPOUND_C34 = {
    "name": "C34",
    "smiles": "CCS(=O)(=O)N1CCC(c2nc(-c3ccc(F)cc3)c(-c3ccnc(Nc4ccc5c(ccn5CCN(C)C)c4)n3)s2)CC1",
    "target": "EGFR L858R/T790M/C797S",
    "generation": "4th-gen candidate",
    "mechanism": "Non-covalent reversible inhibitor",
    "indication": "NSCLC (osimertinib-resistant)",
    "source": "Zhu et al. 2023, J. Med. Chem. 66(21), 14633-14652",
    "ic50_nm": 5.1,
    "oral_bioavailability": 30.72,
}

REFERENCE_SMILES = COMPOUND_C34["smiles"]

REFERENCE_TKIS = [
    {
        "name": "Osimertinib (Tagrisso)",
        "smiles": "C=CC(=O)Nc1nc(Nc2ccc(N(C)CCN(C)C)cc2OC)ncc1-c1cn(C)c2ccccc12",
        "generation": "3rd-gen",
        "target": "EGFR T790M",
        "mechanism": "Irreversible covalent inhibitor (Cys797)",
        "indication": "NSCLC",
        "year": 2015,
    },
    {
        "name": "BLU-945",
        "smiles": "CC1C(CN1C2=C3C=NC(=CC3=C(C=C2)C(C)C)NC4=NC(=NC=C4)N5CCC(C(C5)F)OC)CS(=O)(=O)C",
        "generation": "4th-gen",
        "target": "EGFR L858R/T790M/C797S",
        "mechanism": "Reversible, WT-sparing",
        "indication": "NSCLC",
        "year": 2022,
    },
    {
        "name": "TQB3804",
        "smiles": "CC1=CC(=C(C=C1N2CCC(CC2)N3CCN(CC3)C)OC)NC4=NC=C(C(=N4)NC5=C(C6=NC=CN=C6C=C5)P(=O)(C)C)Br",
        "generation": "4th-gen",
        "target": "EGFR L858R/T790M/C797S",
        "mechanism": "Non-covalent reversible",
        "indication": "NSCLC",
        "year": 2019,
    },
    {
        "name": "Afatinib (Gilotrif)",
        "smiles": "CN(C)/C=C/C(=O)Nc1cc2c(Nc3ccc(F)c(Cl)c3)ncnc2cc1O[C@@H]1CCOC1",
        "generation": "2nd-gen",
        "target": "EGFR/HER2/HER4",
        "mechanism": "Irreversible pan-HER inhibitor",
        "indication": "NSCLC",
        "year": 2013,
    },
]

PHARMACOPHORE = {
    "pyrimidine_hinge": {
        "role": "Hinge binder — H-bonds with EGFR hinge region",
        "smarts": "c1ccnc(N)n1",
        "modifiable": False,
    },
    "thiazole_core": {
        "role": "Central linker connecting hinge binder to hydrophobic pocket",
        "smarts": "c1ncsc1",
        "modifiable": False,
    },
    "fluorophenyl": {
        "role": "Hydrophobic pocket filler — van der Waals with gatekeeper region",
        "smarts": "c1ccc(F)cc1",
        "modifiable": True,
    },
    "sulfonyl_cap": {
        "role": "Solubility and PK handle on piperidine nitrogen",
        "smarts": "CCS(=O)(=O)N",
        "modifiable": True,
    },
    "indole_tail": {
        "role": "Solvent-exposed tail — modulates PK and brain penetration",
        "smarts": "n1ccc2ccccc12",
        "modifiable": True,
    },
}


def get_reference_properties(smiles: str) -> dict | None:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    sa_score = _sa.calculateScore(mol) if _sa else 3.0
    return {
        "mw": round(Descriptors.MolWt(mol), 1),
        "logp": round(Descriptors.MolLogP(mol), 2),
        "tpsa": round(Descriptors.TPSA(mol), 1),
        "hbd": Descriptors.NumHDonors(mol),
        "hba": Descriptors.NumHAcceptors(mol),
        "rotatable_bonds": Descriptors.NumRotatableBonds(mol),
        "aromatic_rings": Descriptors.NumAromaticRings(mol),
        "qed": round(QED.qed(mol), 3),
        "sa_score": round(sa_score, 2),
        "num_rings": Descriptors.RingCount(mol),
        "fsp3": round(Descriptors.FractionCSP3(mol), 3),
        "heavy_atoms": mol.GetNumHeavyAtoms(),
    }
