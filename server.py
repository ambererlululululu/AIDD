from __future__ import annotations
import json
import re
import uuid
import os
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel

from chemistry.visualizer import highlight_diff, render_radar_chart, render_sar_heatmap, render_multi_radar
from chemistry.evaluator import evaluate_candidate, generate_radar_data
from chemistry.sar import sar_to_heatmap_data
from chemistry.molecules import REFERENCE_SMILES

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

PROJECTS_DIR = Path("data/projects")

_data_cache: dict[str, dict] = {}
_config_cache: dict[str, dict] = {}
_sessions: dict[str, dict] = {}


def _load_project_config(project_id: str) -> dict | None:
    if project_id in _config_cache:
        return _config_cache[project_id]
    config_path = PROJECTS_DIR / project_id / "config.json"
    if not config_path.exists():
        return None
    with open(config_path) as f:
        config = json.load(f)
    _config_cache[project_id] = config
    return config


def _load_data(project_id: str = "c34-egfr") -> dict:
    if project_id in _data_cache:
        return _data_cache[project_id]

    project_path = PROJECTS_DIR / project_id / "sar_matrix.json"
    if project_path.exists():
        with open(project_path) as f:
            data = json.load(f)
    else:
        legacy_path = Path("data/sar_matrix.json")
        with open(legacy_path) as f:
            data = json.load(f)

    _data_cache[project_id] = data
    return data


def _get_ref_smiles(project_id: str = "c34-egfr") -> str:
    config = _load_project_config(project_id)
    if config and "reference" in config:
        return config["reference"]["smiles"]
    return REFERENCE_SMILES


# ── Page ──

@app.get("/", response_class=HTMLResponse)
async def index():
    return Path("static/index.html").read_text(encoding="utf-8")


# ── Projects ──

@app.get("/api/projects")
async def list_projects():
    projects = []
    if PROJECTS_DIR.exists():
        for d in sorted(PROJECTS_DIR.iterdir()):
            config_path = d / "config.json"
            if config_path.exists():
                config = _load_project_config(d.name)
                projects.append({
                    "id": config["id"],
                    "name": config["name"],
                    "description": config.get("description", ""),
                    "status": config.get("status", "active"),
                    "context": config.get("context", {}),
                })
    return {"projects": projects}


# ── Dashboard ──

@app.get("/api/dashboard")
async def dashboard():
    projects = []
    if PROJECTS_DIR.exists():
        for d in sorted(PROJECTS_DIR.iterdir()):
            config_path = d / "config.json"
            if not config_path.exists():
                continue
            config = _load_project_config(d.name)
            project_id = config["id"]

            molecule_count = 0
            sar_path = PROJECTS_DIR / project_id / "sar_matrix.json"
            if sar_path.exists():
                data = _load_data(project_id)
                molecule_count = len(data.get("all_molecules", []))

            last_analysis = None
            history_dir = PROJECTS_DIR / project_id / "history"
            if history_dir.exists():
                for f in sorted(history_dir.iterdir(), reverse=True):
                    if f.name.endswith(".json"):
                        with open(f) as fh:
                            h = json.load(fh)
                        last_analysis = h.get("timestamp")
                        break

            projects.append({
                "id": project_id,
                "name": config["name"],
                "description": config.get("description", ""),
                "status": config.get("status", "active"),
                "molecule_count": molecule_count,
                "last_analysis": last_analysis,
                "context": config.get("context", {}),
            })
    return {"projects": projects}


def _parse_knowledge_index(project_id: str) -> list[dict]:
    index_path = PROJECTS_DIR / project_id / "knowledge" / "index.md"
    if not index_path.exists():
        return []
    text = index_path.read_text(encoding="utf-8")
    papers = []
    current_type = "core"
    for line in text.split("\n"):
        if "Supporting Papers" in line:
            current_type = "supporting"
        if "Databases" in line:
            break
        m = re.match(r'\|\s*(P\d+|S\d+)\s*\|(.+?)\|(.+?)\|(.+?)\|(.+)', line)
        if not m:
            continue
        pid = m.group(1).strip()
        raw_title = m.group(2).strip().strip('"')
        title = raw_title[:120] if len(raw_title) > 120 else raw_title
        year_str = m.group(3).strip()
        journal = m.group(4).strip()
        try:
            year = int(year_str)
        except ValueError:
            year = 0
        papers.append({
            "id": pid, "title": title, "year": year,
            "journal": journal, "project": project_id,
            "type": current_type,
        })
    return papers


@app.get("/api/knowledge")
async def get_knowledge():
    all_papers = []
    if PROJECTS_DIR.exists():
        for d in sorted(PROJECTS_DIR.iterdir()):
            if (d / "knowledge" / "index.md").exists():
                all_papers.extend(_parse_knowledge_index(d.name))
    return {"papers": all_papers}


# ── Data endpoints ──

@app.get("/api/molecules")
async def get_molecules(project: str = Query("c34-egfr")):
    data = _load_data(project)
    ref_smiles = _get_ref_smiles(project)
    return {
        "molecules": data["all_molecules"],
        "ref_props": data["reference_props"],
        "ref_smiles": ref_smiles,
    }


@app.get("/api/molecule/{idx}")
async def get_molecule_detail(idx: int, project: str = Query("c34-egfr")):
    data = _load_data(project)
    mols = data["all_molecules"]
    if idx < 0 or idx >= len(mols):
        return JSONResponse({"error": "index out of range"}, 404)

    mol = mols[idx]
    ref_props = data["reference_props"]
    ref_smiles = _get_ref_smiles(project)

    svg = highlight_diff(ref_smiles, mol["smiles"], size=(450, 320))

    config = _load_project_config(project)
    ref_name = "C34 (Reference)"
    if config:
        ref_name = f"{config['reference']['name']} (Reference)"

    radar = generate_radar_data(
        mol["properties"], ref_props, mol.get("binding_3d"),
    )
    fig = render_radar_chart(
        radar["candidate"], radar["reference"],
        candidate_name=mol["name"][:20], ref_name=ref_name,
    )

    return {
        "molecule": mol,
        "svg": svg,
        "radar": json.loads(fig.to_json()),
        "brenk_alerts": mol.get("brenk_alerts", []),
        "pains_alerts": mol.get("pains_alerts", []),
    }


@app.get("/api/heatmap")
async def get_heatmap(prop: str = Query("score"), project: str = Query("c34-egfr")):
    data = _load_data(project)
    prop_map = {
        "score": "score", "binding": "binding_proxy_score",
        "mw": "mw", "logp": "logp", "qed": "qed",
        "sa": "sa_score", "tpsa": "tpsa", "logs": "logs",
        "delta_mw": "delta_mw", "delta_logp": "delta_logp",
    }
    prop_key = prop_map.get(prop, "score")
    label_map = {
        "score": "Score", "binding": "3D Shape", "mw": "MW",
        "logp": "cLogP", "qed": "QED", "sa": "SA Score", "tpsa": "TPSA",
        "logs": "LogS", "delta_mw": "ΔMW", "delta_logp": "ΔcLogP",
    }
    prop_label = label_map.get(prop, "Score")

    heatmap_list = sar_to_heatmap_data(data, prop_key)
    all_vals = [v for hm in heatmap_list for v in hm["values"]]
    global_range = (min(all_vals), max(all_vals)) if all_vals else None
    figures = []
    for hm in heatmap_list:
        fig = render_sar_heatmap(hm, property_label=prop_label, global_range=global_range)
        figures.append(json.loads(fig.to_json()))
    return {"figures": figures}


class EvalRequest(BaseModel):
    smiles: str
    project: str = "c34-egfr"

@app.post("/api/evaluate")
async def evaluate_smiles(req: EvalRequest):
    ref_smiles = _get_ref_smiles(req.project)
    ev = evaluate_candidate(req.smiles.strip(), ref_smiles)
    if not ev.get("valid", True):
        return ev

    svg = highlight_diff(ref_smiles, req.smiles.strip(), size=(450, 320))

    data = _load_data(req.project)
    ref_props = data["reference_props"]

    config = _load_project_config(req.project)
    ref_name = "C34 (Reference)"
    if config:
        ref_name = f"{config['reference']['name']} (Reference)"

    radar = generate_radar_data(
        ev["properties"], ref_props, ev.get("binding_3d"),
    )
    fig = render_radar_chart(
        radar["candidate"], radar["reference"],
        candidate_name="Custom", ref_name=ref_name,
    )

    ev["svg"] = svg
    ev["radar"] = json.loads(fig.to_json())
    return ev


# ── Comparison radar ──

@app.get("/api/comparison")
async def get_comparison(indices: str = Query(...), project: str = Query("c34-egfr")):
    data = _load_data(project)
    mols = data["all_molecules"]
    ref_props = data["reference_props"]
    ref_smiles = _get_ref_smiles(project)
    idx_list = [int(x) for x in indices.split(",") if x.strip().isdigit()]

    sel_mols = [mols[i] for i in idx_list if 0 <= i < len(mols)]
    results = []
    radar_mols = []
    for mol in sel_mols:
        svg = highlight_diff(ref_smiles, mol["smiles"])
        radar = generate_radar_data(mol["properties"], ref_props, mol.get("binding_3d"))
        radar_mols.append({"name": mol["name"][:15], "radar": radar["candidate"]})
        results.append({"molecule": mol, "svg": svg})

    fig = render_multi_radar(radar_mols)
    return {
        "molecules": results,
        "radar": json.loads(fig.to_json()),
    }


# ── Deliberation endpoints ──

class DelibStartRequest(BaseModel):
    focus: str = ""
    context: str = ""
    lang: str = "zh"
    project: str = "c34-egfr"
    strategy: str = "standard"

@app.post("/api/delib/start")
async def delib_start(req: DelibStartRequest):
    from agents.deliberation import Deliberation
    data = _load_data(req.project)
    config = _load_project_config(req.project)

    delib = Deliberation(
        lang=req.lang, project_config=config,
        strategy=req.strategy, project_id=req.project,
    )
    session_id = str(uuid.uuid4())[:8]
    _sessions[session_id] = {
        "delib": delib,
        "project": req.project,
        "focus": req.focus,
        "context": req.context,
        "lang": req.lang,
    }

    r1 = delib.run_round1(
        data["all_molecules"], data["reference_props"],
        focus=req.focus, user_context=req.context,
    )
    return {
        "session_id": session_id,
        "r1": {"agent_outputs": r1.agent_outputs, "duration": r1.duration},
    }


class DelibR2Request(BaseModel):
    session_id: str
    guidance: str = ""

@app.post("/api/delib/round2")
async def delib_round2(req: DelibR2Request):
    session = _sessions.get(req.session_id)
    if not session:
        return JSONResponse({"error": "session not found"}, 404)

    delib = session["delib"]
    r2 = delib.run_round2(user_guidance=req.guidance)
    return {
        "r2": {"agent_outputs": r2.agent_outputs, "duration": r2.duration},
    }


class DelibR3Request(BaseModel):
    session_id: str

@app.post("/api/delib/round3")
async def delib_round3(req: DelibR3Request):
    session = _sessions.get(req.session_id)
    if not session:
        return JSONResponse({"error": "session not found"}, 404)

    delib = session["delib"]
    convergence = delib.run_round3()
    traces = []
    for agent in delib.agents:
        traces.extend(agent.traces)

    _save_history(session, delib, convergence, traces)

    del _sessions[req.session_id]
    return {
        "convergence": convergence,
        "traces": traces,
    }


SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}


@app.post("/api/delib/stream/r1")
async def delib_stream_r1(req: DelibStartRequest):
    from agents.deliberation import Deliberation
    data = _load_data(req.project)
    config = _load_project_config(req.project)

    delib = Deliberation(
        lang=req.lang, project_config=config,
        strategy=req.strategy, project_id=req.project,
    )
    session_id = str(uuid.uuid4())[:8]
    _sessions[session_id] = {
        "delib": delib,
        "project": req.project,
        "focus": req.focus,
        "context": req.context,
        "lang": req.lang,
    }

    def generate():
        for event in delib.stream_round1_react(
                data["all_molecules"], data["reference_props"],
                focus=req.focus, user_context=req.context):
            if event["type"] == "round_done":
                event["session_id"] = session_id
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream",
                             headers=SSE_HEADERS)


@app.post("/api/delib/stream/r2")
async def delib_stream_r2(req: DelibR2Request):
    session = _sessions.get(req.session_id)
    if not session:
        return JSONResponse({"error": "session not found"}, 404)

    delib = session["delib"]

    def generate():
        for event in delib.stream_round2_react(user_guidance=req.guidance):
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream",
                             headers=SSE_HEADERS)


@app.post("/api/delib/stream/r3")
async def delib_stream_r3(req: DelibR3Request):
    session = _sessions.get(req.session_id)
    if not session:
        return JSONResponse({"error": "session not found"}, 404)

    delib = session["delib"]

    def generate():
        for event in delib.stream_round3():
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

        traces = []
        for agent in delib.agents:
            traces.extend(agent.traces)
        convergence = getattr(delib, '_r3_output', '')
        _save_history(session, delib, convergence, traces)
        del _sessions[req.session_id]

        yield f"data: {json.dumps({'type': 'all_done', 'traces': traces}, ensure_ascii=False)}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream",
                             headers=SSE_HEADERS)


def _save_history(session: dict, delib, convergence: str, traces: list):
    project_id = session["project"]
    history_dir = PROJECTS_DIR / project_id / "history"
    history_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    hist_id = str(uuid.uuid4())[:8]
    filename = f"{now.strftime('%Y-%m-%d')}_{hist_id}.json"

    history = {
        "id": hist_id,
        "timestamp": now.isoformat(timespec="seconds"),
        "project": project_id,
        "focus": session.get("focus", ""),
        "lang": session.get("lang", "zh"),
        "rounds": {
            "r1": delib._r1_outputs,
            "r2": delib._r2_outputs,
            "r3": convergence,
        },
        "traces": traces,
    }

    with open(history_dir / filename, "w") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


# ── History endpoints ──

@app.get("/api/history")
async def list_history(project: str = Query("c34-egfr")):
    history_dir = PROJECTS_DIR / project / "history"
    if not history_dir.exists():
        return {"history": []}

    items = []
    for f in sorted(history_dir.iterdir(), reverse=True):
        if not f.name.endswith(".json"):
            continue
        with open(f) as fh:
            h = json.load(fh)
        items.append({
            "id": h["id"],
            "timestamp": h["timestamp"],
            "focus": h.get("focus", ""),
            "lang": h.get("lang", "zh"),
        })
    return {"history": items}


@app.get("/api/history/{hist_id}")
async def get_history(hist_id: str, project: str = Query("c34-egfr")):
    history_dir = PROJECTS_DIR / project / "history"
    if not history_dir.exists():
        return JSONResponse({"error": "not found"}, 404)

    for f in history_dir.iterdir():
        if hist_id in f.name:
            with open(f) as fh:
                return json.load(fh)
    return JSONResponse({"error": "not found"}, 404)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
