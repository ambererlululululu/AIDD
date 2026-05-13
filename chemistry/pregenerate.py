"""Run once to pre-generate SAR matrix and chemical space data."""
from __future__ import annotations
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chemistry.sar import build_sar_matrix, compute_chemical_space


def main():
    parser = argparse.ArgumentParser(description="Pre-generate SAR matrix data")
    parser.add_argument("--project", default="c34-egfr",
                        help="Project ID (default: c34-egfr)")
    args = parser.parse_args()

    project_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data", "projects", args.project,
    )
    os.makedirs(project_dir, exist_ok=True)

    config_path = os.path.join(project_dir, "config.json")
    seed_smiles = None
    if os.path.exists(config_path):
        with open(config_path) as f:
            config = json.load(f)
        seed_smiles = config.get("reference", {}).get("smiles")
        print(f"Project: {config.get('name', args.project)}")
    else:
        print(f"No config.json found for {args.project}, using defaults")

    print("Building SAR matrix...")
    sar = build_sar_matrix(seed_smiles)
    print(f"  {sar['total_molecules']} molecules generated")

    out_path = os.path.join(project_dir, "sar_matrix.json")
    with open(out_path, "w") as f:
        json.dump(sar, f, ensure_ascii=False, indent=2)
    print(f"  Saved {out_path}")

    print("Computing chemical space...")
    space = compute_chemical_space(sar)
    print(f"  {len(space['coordinates'])} points projected")

    space_path = os.path.join(project_dir, "chemical_space.json")
    with open(space_path, "w") as f:
        json.dump(space, f, ensure_ascii=False, indent=2)
    print(f"  Saved {space_path}")

    # Also write to legacy location for backward compatibility
    legacy_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    legacy_sar = os.path.join(legacy_dir, "sar_matrix.json")
    legacy_space = os.path.join(legacy_dir, "chemical_space.json")
    if args.project == "c34-egfr":
        with open(legacy_sar, "w") as f:
            json.dump(sar, f, ensure_ascii=False, indent=2)
        with open(legacy_space, "w") as f:
            json.dump(space, f, ensure_ascii=False, indent=2)
        print("  Also updated legacy data/ files")

    print("Done.")


if __name__ == "__main__":
    main()
