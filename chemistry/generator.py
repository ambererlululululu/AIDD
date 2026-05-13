from __future__ import annotations
from rdkit import Chem
from rdkit.Chem import AllChem, DataStructs

from chemistry.molecules import REFERENCE_SMILES

ARYL_REPLACEMENTS = [
    ("chloro", "Cl"),
    ("bromo", "Br"),
    ("H (remove)", "[H]"),
    ("trifluoromethyl", "C(F)(F)F"),
    ("methoxy", "OC"),
    ("cyano", "C#N"),
]

SULFONYL_REPLACEMENTS = [
    ("methylsulfonyl", "[CH3:1]S(=[O:2])(=[O:3])[N:4]"),
    ("isopropylsulfonyl", "CC([CH3:1])S(=[O:2])(=[O:3])[N:4]"),
    ("cyclopropylsulfonyl", "C1CC1S(=[O:2])(=[O:3])[N:4]"),
    ("acetyl", "CC(=O)[N:4]"),
    ("N-H (remove cap)", "[NH:4]"),
]

TAIL_REPLACEMENTS = [
    ("morpholine-ethyl", "[n:1]CCN1CCOCC1"),
    ("piperazine-ethyl", "[n:1]CCN1CCNCC1"),
    ("pyrrolidine-ethyl", "[n:1]CCN1CCCC1"),
    ("simple-methyl", "[n:1]C"),
    ("diethylamine-ethyl", "[n:1]CCN(CC)CC"),
    ("H (free indole)", "[nH:1]"),
]

ARYL_RXN_TEMPLATE = "[c:1]([F])>>[c:1]({repl})"
SULFONYL_RXN_TEMPLATE = "[CH3:1][CH2]S(=[O:2])(=[O:3])[N:4]>>{product}"
TAIL_RXN_TEMPLATE = "[n:1]CCN(C)C>>{product}"


def validate_smiles(smiles: str) -> bool:
    if not smiles or len(smiles) < 5:
        return False
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return False
    try:
        Chem.SanitizeMol(mol)
    except Exception:
        return False
    if mol.GetNumHeavyAtoms() < 10:
        return False
    return True


def _run_reaction(mol, rxn_smarts: str) -> str | None:
    try:
        rxn = AllChem.ReactionFromSmarts(rxn_smarts)
        if rxn is None:
            return None
        prods = rxn.RunReactants((mol,))
        if not prods:
            return None
        smi = Chem.MolToSmiles(prods[0][0])
        if validate_smiles(smi):
            return smi
    except Exception:
        pass
    return None


def strategy_aryl_modification(seed_smiles: str) -> list[dict]:
    mol = Chem.MolFromSmiles(seed_smiles)
    if mol is None:
        return []

    pat = Chem.MolFromSmarts("[c]F")
    if pat is None or not mol.HasSubstructMatch(pat):
        return []

    results = []
    for name, repl in ARYL_REPLACEMENTS:
        rxn_sma = ARYL_RXN_TEMPLATE.format(repl=repl)
        smi = _run_reaction(mol, rxn_sma)
        if smi and smi != Chem.CanonSmiles(seed_smiles):
            results.append({
                "smiles": smi,
                "name": f"C34-aryl-{name}",
                "strategy": "R-group (aryl)",
                "region": "fluorophenyl para-substituent",
                "rationale": f"Replace para-F with {name} to modulate hydrophobic pocket interaction and metabolic stability",
            })
    return results


def strategy_sulfonyl_modification(seed_smiles: str) -> list[dict]:
    mol = Chem.MolFromSmiles(seed_smiles)
    if mol is None:
        return []

    pat = Chem.MolFromSmarts("CCS(=O)(=O)N")
    if pat is None or not mol.HasSubstructMatch(pat):
        return []

    results = []
    for name, product_template in SULFONYL_REPLACEMENTS:
        if name == "N-H (remove cap)":
            rxn_sma = "[CH3][CH2]S(=O)(=O)[N:4]>>[NH:4]"
        elif name == "acetyl":
            rxn_sma = "[CH3][CH2]S(=O)(=O)[N:4]>>CC(=O)[N:4]"
        else:
            rxn_sma = f"[CH3:1][CH2]S(=[O:2])(=[O:3])[N:4]>>{product_template}"
        smi = _run_reaction(mol, rxn_sma)
        if smi and smi != Chem.CanonSmiles(seed_smiles):
            results.append({
                "smiles": smi,
                "name": f"C34-sulfonyl-{name}",
                "strategy": "R-group (sulfonyl)",
                "region": "piperidine N-cap",
                "rationale": f"Replace ethylsulfonyl with {name} to tune polarity, clearance, and molecular weight",
            })
    return results


def strategy_tail_modification(seed_smiles: str) -> list[dict]:
    mol = Chem.MolFromSmiles(seed_smiles)
    if mol is None:
        return []

    pat = Chem.MolFromSmarts("[n]CCN(C)C")
    if pat is None or not mol.HasSubstructMatch(pat):
        return []

    results = []
    for name, product_template in TAIL_REPLACEMENTS:
        rxn_sma = f"[n:1]CCN(C)C>>{product_template}"
        smi = _run_reaction(mol, rxn_sma)
        if smi and smi != Chem.CanonSmiles(seed_smiles):
            results.append({
                "smiles": smi,
                "name": f"C34-tail-{name}",
                "strategy": "R-group (tail)",
                "region": "indole N-aminoethyl tail",
                "rationale": f"Replace dimethylaminoethyl with {name} to modulate PK, brain penetration, and clearance",
            })
    return results


def strategy_combination(seed_smiles: str) -> list[dict]:
    results = []
    aryl_mols = strategy_aryl_modification(seed_smiles)
    for a in aryl_mols[:3]:
        sulfonyl_mols = strategy_sulfonyl_modification(a["smiles"])
        for s in sulfonyl_mols[:2]:
            s["name"] = f"C34-combo-{a['name'].split('-')[-1]}+{s['name'].split('-')[-1]}"
            s["strategy"] = "Combination"
            s["region"] = "aryl + sulfonyl"
            s["rationale"] = f"Combined: aryl {a['name'].split('-')[-1]} + sulfonyl {s['name'].split('-')[-1]}"
            results.append(s)
    return results


ALL_STRATEGIES = {
    "aryl": strategy_aryl_modification,
    "sulfonyl": strategy_sulfonyl_modification,
    "tail": strategy_tail_modification,
    "combination": strategy_combination,
}

ROUND_STRATEGY_ROTATION = {
    1: ["aryl", "sulfonyl"],
    2: ["tail", "aryl"],
    3: ["combination", "sulfonyl"],
    4: ["tail", "aryl"],
    5: ["combination", "tail"],
}


def generate_candidates(seed_smiles: str, round_number: int,
                        n_candidates: int = 8,
                        preferred_strategies: list[str] | None = None,
                        avoid_strategies: list[str] | None = None,
                        exclude_smiles: set = None) -> list[dict]:
    if exclude_smiles is None:
        exclude_smiles = set()

    if preferred_strategies:
        strategy_names = [s for s in preferred_strategies if s in ALL_STRATEGIES]
    else:
        strategy_names = ROUND_STRATEGY_ROTATION.get(
            round_number, list(ALL_STRATEGIES.keys())[:2]
        )

    if avoid_strategies:
        strategy_names = [s for s in strategy_names if s not in avoid_strategies]

    if not strategy_names:
        strategy_names = ["aryl", "sulfonyl"]

    all_candidates = []
    for sname in strategy_names:
        fn = ALL_STRATEGIES[sname]
        mols = fn(seed_smiles)
        all_candidates.extend(mols)

    seed_canon = Chem.CanonSmiles(seed_smiles)
    seen_smiles = set()
    unique = []
    for c in all_candidates:
        canon = Chem.CanonSmiles(c["smiles"]) if validate_smiles(c["smiles"]) else None
        if canon and canon not in seen_smiles and canon != seed_canon and canon not in exclude_smiles:
            seen_smiles.add(canon)
            c["smiles"] = canon
            unique.append(c)

    if len(unique) > n_candidates:
        unique = _diverse_select(unique, n_candidates)

    return unique


def _diverse_select(candidates: list[dict], n: int) -> list[dict]:
    if len(candidates) <= n:
        return candidates

    fps = []
    for c in candidates:
        mol = Chem.MolFromSmiles(c["smiles"])
        fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)
        fps.append(fp)

    selected = [0]
    remaining = list(range(1, len(candidates)))

    while len(selected) < n and remaining:
        best_idx = None
        best_min_dist = -1
        for idx in remaining:
            min_sim = min(DataStructs.TanimotoSimilarity(fps[idx], fps[s]) for s in selected)
            dist = 1 - min_sim
            if dist > best_min_dist:
                best_min_dist = dist
                best_idx = idx
        if best_idx is not None:
            selected.append(best_idx)
            remaining.remove(best_idx)

    return [candidates[i] for i in selected]
