from __future__ import annotations
from rdkit import Chem
from rdkit.Chem import Descriptors, QED, FilterCatalog, DataStructs
from rdkit.Chem.FilterCatalog import FilterCatalogParams
from rdkit.Chem import AllChem
import os

from chemistry.scoring3d import compute_3d_binding_proxy


def _load_sa_scorer():
    try:
        from rdkit.Chem import RDConfig
        import sys
        sa_path = os.path.join(RDConfig.RDContribDir, "SA_Score")
        if sa_path not in sys.path:
            sys.path.insert(0, sa_path)
        import sascorer
        return sascorer
    except Exception:
        return None


_sa_scorer = _load_sa_scorer()

_pains_params = FilterCatalogParams()
_pains_params.AddCatalog(FilterCatalogParams.FilterCatalogs.PAINS)
_pains_catalog = FilterCatalog.FilterCatalog(_pains_params)

_brenk_params = FilterCatalogParams()
_brenk_params.AddCatalog(FilterCatalogParams.FilterCatalogs.BRENK)
_brenk_catalog = FilterCatalog.FilterCatalog(_brenk_params)

STRUCTURAL_ALERT_SMARTS = {
    "nitro": "[N+](=O)[O-]",
    "acyl_halide": "C(=O)[F,Cl,Br,I]",
    "epoxide": "C1OC1",
    "peroxide": "OO",
    "aldehyde": "[CH]=O",
    "sulfonyl_halide": "S(=O)(=O)[F,Cl,Br,I]",
    "phosphoramide": "NP(=O)",
}


def compute_properties(smiles: str) -> dict | None:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None

    sa_score = _sa_scorer.calculateScore(mol) if _sa_scorer else 3.0

    logp = Descriptors.MolLogP(mol)
    mw = Descriptors.MolWt(mol)
    rb = Descriptors.NumRotatableBonds(mol)
    ha = mol.GetNumHeavyAtoms()
    ar_atoms = sum(1 for a in mol.GetAtoms() if a.GetIsAromatic())
    ap = ar_atoms / ha if ha > 0 else 0
    logs = 0.16 - 0.63 * logp - 0.0062 * mw + 0.066 * rb - 0.74 * ap

    return {
        "mw": round(mw, 1),
        "logp": round(logp, 2),
        "tpsa": round(Descriptors.TPSA(mol), 1),
        "hbd": Descriptors.NumHDonors(mol),
        "hba": Descriptors.NumHAcceptors(mol),
        "rotatable_bonds": rb,
        "aromatic_rings": Descriptors.NumAromaticRings(mol),
        "qed": round(QED.qed(mol), 3),
        "sa_score": round(sa_score, 2),
        "num_rings": Descriptors.RingCount(mol),
        "fsp3": round(Descriptors.FractionCSP3(mol), 3),
        "heavy_atoms": ha,
        "logs": round(logs, 2),
    }


def check_lipinski(props: dict) -> dict:
    violations = []
    if props["mw"] > 500:
        violations.append(f"MW={props['mw']} > 500")
    if props["logp"] > 5.0:
        violations.append(f"LogP={props['logp']} > 5.0")
    if props["hbd"] > 5:
        violations.append(f"HBD={props['hbd']} > 5")
    if props["hba"] > 10:
        violations.append(f"HBA={props['hba']} > 10")
    return {
        "passed": len(violations) <= 1,
        "violations": violations,
        "n_violations": len(violations),
    }


def check_veber(props: dict) -> dict:
    violations = []
    if props["rotatable_bonds"] > 10:
        violations.append(f"RotBonds={props['rotatable_bonds']} > 10")
    if props["tpsa"] > 140:
        violations.append(f"TPSA={props['tpsa']} > 140")
    return {"passed": len(violations) == 0, "violations": violations}


def check_pains(smiles: str) -> dict:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {"has_alerts": True, "alerts": ["Invalid SMILES"]}
    entries = _pains_catalog.GetMatches(mol)
    alerts = [e.GetDescription() for e in entries]
    return {"has_alerts": len(alerts) > 0, "alerts": alerts}


def check_brenk(smiles: str) -> dict:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {"has_alerts": True, "alerts": ["Invalid SMILES"]}

    entries = _brenk_catalog.GetMatches(mol)
    alerts = [e.GetDescription() for e in entries]
    return {"has_alerts": len(alerts) > 0, "alerts": alerts}


def check_structural_alerts(smiles: str) -> dict:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {"has_alerts": True, "alerts": ["Invalid SMILES"]}

    alerts = []
    for name, smarts in STRUCTURAL_ALERT_SMARTS.items():
        pat = Chem.MolFromSmarts(smarts)
        if pat and mol.HasSubstructMatch(pat):
            alerts.append(name)
    return {"has_alerts": len(alerts) > 0, "alerts": alerts}


def compute_similarity(smiles1: str, smiles2: str) -> float | None:
    mol1 = Chem.MolFromSmiles(smiles1)
    mol2 = Chem.MolFromSmiles(smiles2)
    if mol1 is None or mol2 is None:
        return None
    fp1 = AllChem.GetMorganFingerprintAsBitVect(mol1, 2, nBits=2048)
    fp2 = AllChem.GetMorganFingerprintAsBitVect(mol2, 2, nBits=2048)
    return round(DataStructs.TanimotoSimilarity(fp1, fp2), 3)


def score_breakdown(props: dict, lipinski: dict, veber: dict,
                    pains: dict, brenk: dict, similarity: float,
                    binding_3d: dict | None = None) -> dict:
    lip = 20.0 if lipinski["passed"] else max(0, 20 - 8 * lipinski["n_violations"])
    veb = 10.0 if veber["passed"] else 0.0
    pai = 10.0 if not pains["has_alerts"] else 0.0
    qed = 15.0 * min(props["qed"] / 0.5, 1.0)
    sa_raw = max(0, 1 - (props["sa_score"] - 1) / 9)
    sa = 10.0 * sa_raw
    sim = 10.0 if 0.3 <= similarity <= 0.85 else 5.0 if 0.2 <= similarity <= 0.95 else 0.0

    bind_score = 0.0
    if binding_3d and binding_3d.get("binding_proxy_score") is not None:
        bind_score = 25.0 * min(binding_3d["binding_proxy_score"] / 0.6, 1.0)

    total = lip + veb + pai + qed + sa + sim + bind_score
    return {
        "lipinski": round(lip, 1), "lipinski_max": 20,
        "veber": round(veb, 1), "veber_max": 10,
        "pains": round(pai, 1), "pains_max": 10,
        "qed": round(qed, 1), "qed_max": 15,
        "sa": round(sa, 1), "sa_max": 10,
        "similarity": round(sim, 1), "similarity_max": 10,
        "binding_3d": round(bind_score, 1), "binding_3d_max": 25,
        "total": round(total, 1), "total_max": 100,
    }


def compute_score(props: dict, lipinski: dict, veber: dict,
                  pains: dict, brenk: dict, similarity: float,
                  binding_3d: dict | None = None) -> float:
    bd = score_breakdown(props, lipinski, veber, pains, brenk, similarity, binding_3d)
    return bd["total"]


def evaluate_candidate(smiles: str, reference_smiles: str) -> dict:
    props = compute_properties(smiles)
    if props is None:
        return {
            "smiles": smiles,
            "valid": False,
            "verdict": "FAIL",
            "reasons": ["Invalid SMILES — cannot parse molecule"],
            "suggestions": [],
            "score": 0,
        }

    lipinski = check_lipinski(props)
    veber = check_veber(props)
    pains = check_pains(smiles)
    brenk = check_brenk(smiles)
    struct_alerts = check_structural_alerts(smiles)
    similarity = compute_similarity(smiles, reference_smiles)
    if similarity is None:
        similarity = 0.0

    binding_3d = compute_3d_binding_proxy(smiles)

    score = compute_score(props, lipinski, veber, pains, brenk, similarity, binding_3d)
    breakdown = score_breakdown(props, lipinski, veber, pains, brenk, similarity, binding_3d)

    reasons = []
    suggestions = []

    if not lipinski["passed"]:
        reasons.append(f"Lipinski violations: {', '.join(lipinski['violations'])}")
        if props["mw"] > 500:
            suggestions.append(f"Reduce MW by ~{int(props['mw'] - 480)} Da — try smaller substituents or remove a ring")
        if props["logp"] > 5.0:
            suggestions.append("Reduce lipophilicity — add polar group or replace alkyl with heteroatom")
    if not veber["passed"]:
        reasons.append(f"Veber violations: {', '.join(veber['violations'])}")
    if pains["has_alerts"]:
        reasons.append(f"PAINS alerts: {', '.join(pains['alerts'][:2])}")
        suggestions.append("Remove or modify the flagged substructure")
    if brenk["has_alerts"]:
        reasons.append(f"BRENK alerts: {', '.join(brenk['alerts'][:2])}")
    if struct_alerts["has_alerts"]:
        reasons.append(f"Structural alerts: {', '.join(struct_alerts['alerts'])}")
    if props["sa_score"] > 7.0:
        reasons.append(f"SA Score={props['sa_score']} — very difficult to synthesize")
        suggestions.append("Simplify ring systems or reduce stereocenters")
    elif props["sa_score"] > 5.0:
        reasons.append(f"SA Score={props['sa_score']} — moderately difficult synthesis")
    if props["qed"] < 0.2:
        reasons.append(f"QED={props['qed']} — poor drug-likeness")
        suggestions.append("Improve balance of MW, LogP, and polar surface area")
    if similarity > 0.95:
        reasons.append(f"Tanimoto={similarity} — too similar to reference (patent risk)")
        suggestions.append("Make larger structural changes for novelty")
    elif similarity < 0.2:
        reasons.append(f"Tanimoto={similarity} — very different from reference (activity risk)")
        suggestions.append("Retain core pharmacophore features")

    if not reasons:
        reasons.append("All criteria satisfied")

    if score >= 65:
        verdict = "PASS"
    elif score >= 45:
        verdict = "CONDITIONAL"
    else:
        verdict = "FAIL"

    return {
        "smiles": smiles,
        "valid": True,
        "properties": props,
        "lipinski": lipinski,
        "veber": veber,
        "pains": pains,
        "brenk": brenk,
        "structural_alerts": struct_alerts,
        "similarity": similarity,
        "binding_3d": binding_3d,
        "score": score,
        "breakdown": breakdown,
        "verdict": verdict,
        "reasons": reasons,
        "suggestions": suggestions,
    }


def generate_radar_data(props: dict, ref_props: dict,
                        binding_3d: dict | None = None) -> dict:
    def normalize(val, low, high):
        return max(0, min(1, (val - low) / (high - low))) if high != low else 0.5

    axes = {
        "MW": 1 - normalize(props["mw"], 200, 600),
        "LogP": 1 - normalize(props["logp"], -1, 7),
        "TPSA": normalize(props["tpsa"], 0, 200),
        "QED": props["qed"],
        "SA": 1 - normalize(props["sa_score"], 1, 10),
        "Solubility": normalize(props.get("logs", -4), -8, 0),
        "3D Shape": binding_3d["binding_proxy_score"] if binding_3d else 0.0,
    }
    ref_axes = {
        "MW": 1 - normalize(ref_props["mw"], 200, 600),
        "LogP": 1 - normalize(ref_props["logp"], -1, 7),
        "TPSA": normalize(ref_props["tpsa"], 0, 200),
        "QED": ref_props["qed"],
        "SA": 1 - normalize(ref_props["sa_score"], 1, 10),
        "Solubility": normalize(ref_props.get("logs", -4), -8, 0),
        "3D Shape": 1.0,
    }
    return {"candidate": axes, "reference": ref_axes}
