from __future__ import annotations
import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem, DataStructs
from chemistry.generator import (
    strategy_aryl_modification, strategy_sulfonyl_modification,
    strategy_tail_modification,
    ARYL_REPLACEMENTS, SULFONYL_REPLACEMENTS, TAIL_REPLACEMENTS,
)
from chemistry.evaluator import evaluate_candidate, compute_properties
from chemistry.scoring3d import compute_3d_binding_proxy
from chemistry.molecules import COMPOUND_C34, REFERENCE_TKIS, REFERENCE_SMILES


POSITIONS = {
    "Aryl": {
        "key": "aryl",
        "generator": strategy_aryl_modification,
        "r_groups": [name for name, _ in ARYL_REPLACEMENTS],
        "original": "para-F",
    },
    "Sulfonyl": {
        "key": "sulfonyl",
        "generator": strategy_sulfonyl_modification,
        "r_groups": [name for name, _ in SULFONYL_REPLACEMENTS],
        "original": "EtSO₂",
    },
    "Tail": {
        "key": "tail",
        "generator": strategy_tail_modification,
        "r_groups": [name for name, _ in TAIL_REPLACEMENTS],
        "original": "NMe₂-ethyl",
    },
}


def build_sar_matrix(seed_smiles: str | None = None) -> dict:
    seed = seed_smiles or REFERENCE_SMILES
    ref_props = compute_properties(seed)

    positions_data = {}
    all_molecules = []

    for pos_name, pos_info in POSITIONS.items():
        gen_fn = pos_info["generator"]
        candidates = gen_fn(seed)
        entries = []
        for c in candidates:
            ev = evaluate_candidate(c["smiles"], seed)
            delta = {}
            if ev.get("properties") and ref_props:
                for k in ["mw", "logp", "tpsa", "qed", "sa_score", "fsp3"]:
                    if k in ev["properties"] and k in ref_props:
                        delta[k] = round(ev["properties"][k] - ref_props[k], 3)
            b3d = ev.get("binding_3d")
            brenk = ev.get("brenk", {})
            pains = ev.get("pains", {})
            entry = {
                "position": pos_name,
                "r_group": c.get("name", ""),
                "smiles": c["smiles"],
                "name": c.get("name", ""),
                "properties": ev.get("properties"),
                "score": ev.get("score", 0),
                "verdict": ev.get("verdict", "FAIL"),
                "breakdown": ev.get("breakdown", {}),
                "binding_3d": b3d,
                "delta": delta,
                "similarity": ev.get("similarity", 0),
                "brenk_alerts": brenk.get("alerts", []),
                "pains_alerts": pains.get("alerts", []),
            }
            entries.append(entry)
            all_molecules.append(entry)
        positions_data[pos_name] = entries

    return {
        "positions": positions_data,
        "reference_props": ref_props,
        "total_molecules": len(all_molecules),
        "all_molecules": all_molecules,
    }


def sar_to_heatmap_data(sar_result: dict, property_key: str) -> list[dict]:
    heatmaps = []
    for pos_name, entries in sar_result["positions"].items():
        labels = []
        values = []
        for e in entries:
            labels.append(e["r_group"])
            if property_key == "score":
                values.append(e["score"])
            elif property_key == "binding_proxy_score":
                b3d = e.get("binding_3d") or {}
                values.append(b3d.get("binding_proxy_score", 0) * 100)
            elif property_key.startswith("delta_"):
                dk = property_key.replace("delta_", "")
                values.append(e.get("delta", {}).get(dk, 0))
            else:
                props = e.get("properties") or {}
                values.append(props.get(property_key, 0))
        paired = sorted(zip(values, labels), reverse=True)
        values_sorted = [v for v, _ in paired]
        labels_sorted = [l for _, l in paired]
        heatmaps.append({
            "position": pos_name,
            "labels": labels_sorted,
            "values": values_sorted,
            "original": POSITIONS[pos_name]["original"],
        })
    return heatmaps


def compute_chemical_space(sar_result: dict) -> dict:
    molecules = []

    molecules.append({
        "smiles": REFERENCE_SMILES,
        "name": "C34 (参考)",
        "group": "参考化合物",
        "score": None,
    })
    for tki in REFERENCE_TKIS:
        molecules.append({
            "smiles": tki["smiles"],
            "name": tki["name"].split("(")[0].strip(),
            "group": "参考化合物",
            "score": None,
        })

    for entry in sar_result.get("all_molecules", []):
        molecules.append({
            "smiles": entry["smiles"],
            "name": entry["name"],
            "group": entry["position"],
            "score": entry["score"],
        })

    fps = []
    valid_mols = []
    for m in molecules:
        mol = Chem.MolFromSmiles(m["smiles"])
        if mol is None:
            continue
        fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)
        arr = np.zeros(2048, dtype=np.float32)
        DataStructs.ConvertToNumpyArray(fp, arr)
        fps.append(arr)
        valid_mols.append(m)

    if len(fps) < 3:
        return {"coordinates": [], "explained_variance": []}

    X = np.array(fps)
    X_centered = X - X.mean(axis=0)
    U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
    coords = X_centered @ Vt[:2].T

    total_var = (S ** 2).sum()
    explained = [(S[i] ** 2 / total_var) for i in range(min(2, len(S)))]

    coordinates = []
    for i, m in enumerate(valid_mols):
        coordinates.append({
            "x": round(float(coords[i, 0]), 6),
            "y": round(float(coords[i, 1]), 6),
            "name": m["name"],
            "smiles": m["smiles"],
            "group": m["group"],
            "score": m["score"],
        })

    return {
        "coordinates": coordinates,
        "explained_variance": [round(float(v), 4) for v in explained],
    }
