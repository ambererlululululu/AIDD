from __future__ import annotations
import functools
from rdkit import Chem
from rdkit.Chem import AllChem, rdMolDescriptors, rdShapeHelpers

from chemistry.molecules import REFERENCE_SMILES


def _embed_3d(smiles: str) -> Chem.Mol | None:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    mol = Chem.AddHs(mol)
    params = AllChem.ETKDGv3()
    params.randomSeed = 42
    if AllChem.EmbedMolecule(mol, params) < 0:
        if AllChem.EmbedMolecule(mol, AllChem.ETKDG()) < 0:
            return None
    try:
        AllChem.MMFFOptimizeMolecule(mol, maxIters=500)
    except Exception:
        pass
    return mol


@functools.lru_cache(maxsize=1)
def _ref_conformer():
    return _embed_3d(REFERENCE_SMILES)


@functools.lru_cache(maxsize=256)
def _get_usrcat(smiles: str) -> tuple | None:
    mol = _embed_3d(smiles)
    if mol is None:
        return None
    try:
        return tuple(rdMolDescriptors.GetUSRCAT(mol))
    except Exception:
        return None


def compute_usrcat_similarity(smiles: str) -> float | None:
    ref = _ref_conformer()
    if ref is None:
        return None
    cand = _get_usrcat(smiles)
    if cand is None:
        return None
    ref_usrcat = tuple(rdMolDescriptors.GetUSRCAT(ref))
    return rdMolDescriptors.GetUSRScore(list(cand), list(ref_usrcat))


def compute_shape_similarity(smiles: str) -> float | None:
    ref = _ref_conformer()
    if ref is None:
        return None
    mol = _embed_3d(smiles)
    if mol is None:
        return None
    try:
        dist = rdShapeHelpers.ShapeTanimotoDist(mol, ref)
        return round(1.0 - dist, 4)
    except Exception:
        return None


def compute_3d_binding_proxy(smiles: str) -> dict | None:
    usrcat = compute_usrcat_similarity(smiles)
    shape = compute_shape_similarity(smiles)
    if usrcat is None and shape is None:
        return None
    u = usrcat if usrcat is not None else 0.0
    s = shape if shape is not None else 0.0
    score = 0.6 * u + 0.4 * s
    if usrcat is not None and shape is not None:
        confidence = "high"
    else:
        confidence = "low"
    return {
        "usrcat_similarity": round(u, 4),
        "shape_similarity": round(s, 4),
        "binding_proxy_score": round(score, 4),
        "confidence": confidence,
    }
