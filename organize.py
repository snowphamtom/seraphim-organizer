#!/usr/bin/env python3
"""Parse dumps and run Solvent×Seraphim hybrid gate (Headroom + Seraphim residual)."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple, Union

from engines.headroom_engine import HeadroomAdmissionController, ResourceVector
from engines.seraphim_residual import SeraphimResidual

CORE_TOKENS = [
    "magpie", "gr-21", "gr21", "dr4g0n", "dragon", "ch4r0n", "charon",
    "headroom", "seraphim", "howard", "tripleecho", "farseer", "chimera",
    "residual", "solvency", "claimed", "interior", "vesica", "lynchpin",
    "lean", "feec", "ppa", "uspto", "monsters", "gqc", "walle",
    "ceilinggate", "hopf", "axi", "pulse", "formal", "patent",
]

KIND_COST = {
    "folder": (0.5, 0.2, 0.1, 0.1),
    "doc": (2.0, 1.5, 0.8, 0.5),
    "sheet": (2.5, 2.0, 1.0, 0.6),
    "slides": (3.0, 2.0, 1.2, 0.8),
    "pdf": (3.5, 2.5, 1.5, 1.0),
    "docx": (3.0, 2.0, 1.2, 0.8),
    "xlsx": (2.5, 2.0, 1.0, 0.6),
    "image": (1.5, 3.0, 1.0, 0.8),
    "video": (4.0, 5.0, 2.0, 1.5),
    "code": (2.0, 1.0, 0.6, 0.4),
    "text": (1.0, 0.8, 0.4, 0.3),
    "json": (1.0, 0.8, 0.4, 0.3),
    "csv": (1.2, 1.0, 0.5, 0.3),
    "html": (1.5, 1.0, 0.5, 0.4),
    "archive": (4.0, 4.0, 1.5, 1.2),
    "drawing": (1.5, 1.5, 0.6, 0.5),
    "form": (1.0, 0.8, 0.4, 0.3),
    "gapp": (1.5, 1.0, 0.5, 0.4),
    "audio": (2.0, 2.0, 1.0, 0.6),
    "other": (2.0, 2.0, 1.0, 0.7),
}

PHRASE_BIAS = {
    "patent": -0.2,
    "core-ip": -0.4,
    "headroom": -0.5,
    "formal": -0.3,
    "gov": 0.1,
    "commerce": 0.3,
    "archive": 0.6,
    "brief": -0.1,
    "ledger": -0.2,
    "noise": 1.2,
    "plain": 0.2,
}


def affinity_tokens(title: str) -> List[str]:
    t = title.lower()
    return [tok for tok in CORE_TOKENS if tok in t]


def guess_kind(text: str) -> str:
    low = text.lower()
    for ext, kind in (
        (".pdf", "pdf"), (".docx", "docx"), (".xlsx", "xlsx"),
        (".csv", "csv"), (".json", "json"), (".py", "code"),
        (".ts", "code"), (".js", "code"), (".html", "html"),
        (".png", "image"), (".jpg", "image"), (".gif", "image"),
        (".mp4", "video"), (".zip", "archive"), (".md", "text"),
    ):
        if ext in low:
            return kind
    if any(w in low for w in ("sheet", "spreadsheet", "ledger")):
        return "sheet"
    if any(w in low for w in ("slide", "deck", "pitch")):
        return "slides"
    if any(w in low for w in ("folder", "dir", "vault")):
        return "folder"
    if any(w in low for w in ("patent", "ppa", "formal", "brief")):
        return "doc"
    return "other"


def guess_phrase(text: str) -> str:
    low = text.lower()
    for key in PHRASE_BIAS:
        if key in low or key.replace("-", " ") in low:
            return key
    return "plain"


def text_to_R_and_pairs(item: Dict[str, str]):
    title = item.get("text") or ""
    kind = item.get("kind") or guess_kind(title)
    phrase = item.get("phrase") or guess_phrase(title)
    base = KIND_COST.get(kind, KIND_COST["other"])
    bias = PHRASE_BIAS.get(phrase, 0.2)
    toks = affinity_tokens(title)
    aff = min(1.0, len(toks) / 3.0)
    scale = max(0.25, 1.0 + bias - 0.55 * aff)
    scale *= 1.0 + min(1.5, len(title) / 80.0) * 0.15
    R = ResourceVector(*(c * scale for c in base))

    h = int(hashlib.sha256((item.get("id") or title).encode()).hexdigest()[:8], 16)
    pairs: List[Tuple[float, float]] = []
    if not toks:
        d = 0.4 + (h % 100) / 200.0
        dk = 0.05 + (h % 50) / 500.0
        pairs += [(d, dk), (d * 0.7, dk * 1.4)]
    else:
        for i, tok in enumerate(toks[:6]):
            th = int(hashlib.sha256(tok.encode()).hexdigest()[:6], 16)
            d = 0.05 + (th % 40) / 400.0
            dk = 0.05 + ((h ^ th) % 40) / 400.0
            if aff > 0.3:
                dk = d / max(0.5, 0.85 + 0.1 * i)
            pairs.append((d, dk))
    return R, pairs, toks, aff, kind, phrase


def echo_lanes(item_id: str, aff: float):
    h = int(hashlib.sha256((item_id or "").encode()).hexdigest()[:12], 16)
    a = (h & 0xFFF) / 4096.0 * math.tau
    phase = 0.35 * (1.0 - aff)
    mag = 0.5 + 0.5 * aff
    z1 = complex(math.cos(a), math.sin(a)) * mag
    z2 = complex(math.cos(a + phase), math.sin(a + phase)) * mag
    z3 = complex(math.cos(a + 2 * phase), math.sin(a + 2 * phase)) * mag
    return (z1, z2, z3)


def _cell(row: Dict[str, Any], *keys: str) -> str:
    for k in keys:
        if k in row and row[k] is not None:
            return str(row[k]).strip()
    # case-insensitive
    low = {str(a).lower(): a for a in row}
    for k in keys:
        if k.lower() in low:
            v = row[low[k.lower()]]
            if v is not None:
                return str(v).strip()
    return ""


def rows_from_mapping_list(rows: Sequence[Any]) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    for i, row in enumerate(rows):
        if isinstance(row, str):
            text = row.strip()
            if not text:
                continue
            out.append({"id": f"row-{i+1}", "text": text})
            continue
        if not isinstance(row, dict):
            text = str(row).strip()
            if text:
                out.append({"id": f"row-{i+1}", "text": text})
            continue
        text = _cell(row, "text", "t", "title", "name", "label", "item", "content", "line")
        if not text:
            # first stringy value
            for v in row.values():
                if isinstance(v, str) and v.strip():
                    text = v.strip()
                    break
        if not text:
            continue
        iid = _cell(row, "id", "ID", "key") or f"row-{i+1}"
        item = {"id": iid, "text": text}
        kind = _cell(row, "kind", "k", "type")
        phrase = _cell(row, "phrase", "p")
        if kind:
            item["kind"] = kind
        if phrase:
            item["phrase"] = phrase
        out.append(item)
    return out


def parse_csv_bytes(raw: bytes, delim: str = ",") -> List[Dict[str, str]]:
    text = raw.decode("utf-8-sig", errors="replace")
    sample = text[:4096]
    # detect header
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=delim + "\t,;")
        delim = dialect.delimiter
    except csv.Error:
        pass
    reader = csv.DictReader(io.StringIO(text), delimiter=delim)
    if reader.fieldnames and any(
        f and f.lower() in ("text", "t", "title", "name", "label", "item", "content", "line")
        for f in reader.fieldnames
    ):
        return rows_from_mapping_list(list(reader))
    # no useful header — re-read as plain rows
    lines = []
    for i, row in enumerate(csv.reader(io.StringIO(text), delimiter=delim)):
        if not row:
            continue
        cells = [c.strip() for c in row if c and c.strip()]
        if not cells:
            continue
        # skip header-ish first row
        if i == 0 and cells[0].lower() in ("text", "title", "name", "t", "id"):
            continue
        iid = cells[0] if len(cells) > 1 else f"row-{i+1}"
        text_val = cells[1] if len(cells) > 1 else cells[0]
        if len(cells) == 1:
            iid = f"row-{i+1}"
            text_val = cells[0]
        lines.append({"id": str(iid), "text": text_val})
    return lines


def parse_json_bytes(raw: bytes) -> List[Dict[str, str]]:
    data = json.loads(raw.decode("utf-8-sig", errors="replace"))
    if isinstance(data, list):
        return rows_from_mapping_list(data)
    if isinstance(data, dict):
        for key in ("items", "rows", "data", "lines", "entries", "verdicts"):
            if key in data and isinstance(data[key], list):
                return rows_from_mapping_list(data[key])
        if "text" in data or "t" in data:
            return rows_from_mapping_list([data])
    raise ValueError("JSON must be a list or object with items/rows")


def parse_jsonl_bytes(raw: bytes) -> List[Dict[str, str]]:
    rows = []
    for i, line in enumerate(raw.decode("utf-8-sig", errors="replace").splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            rows.append({"id": f"row-{i+1}", "text": line})
            continue
        if isinstance(obj, str):
            rows.append({"id": f"row-{i+1}", "text": obj})
        elif isinstance(obj, dict):
            rows.extend(rows_from_mapping_list([obj]))
        else:
            rows.append({"id": f"row-{i+1}", "text": str(obj)})
    return rows


def parse_text_bytes(raw: bytes) -> List[Dict[str, str]]:
    out = []
    for i, line in enumerate(raw.decode("utf-8-sig", errors="replace").splitlines()):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        out.append({"id": f"line-{i+1}", "text": line})
    return out


def parse_dump(
    raw: Union[bytes, str],
    filename: str = "",
    content_type: str = "",
) -> List[Dict[str, str]]:
    if isinstance(raw, str):
        raw = raw.encode("utf-8")
    name = (filename or "").lower()
    ct = (content_type or "").lower()

    if name.endswith(".csv") or "csv" in ct:
        return parse_csv_bytes(raw, ",")
    if name.endswith(".tsv") or "tab-separated" in ct:
        return parse_csv_bytes(raw, "\t")
    if name.endswith(".jsonl") or name.endswith(".ndjson"):
        return parse_jsonl_bytes(raw)
    if name.endswith(".json") or "json" in ct:
        # try json first, fall back to jsonl
        try:
            return parse_json_bytes(raw)
        except (json.JSONDecodeError, ValueError):
            return parse_jsonl_bytes(raw)
    if name.endswith((".txt", ".md", ".markdown")) or "text/plain" in ct:
        return parse_text_bytes(raw)

    # sniff
    text = raw.decode("utf-8-sig", errors="replace").lstrip()
    if text.startswith("[") or text.startswith("{"):
        try:
            return parse_json_bytes(raw)
        except (json.JSONDecodeError, ValueError):
            return parse_jsonl_bytes(raw)
    if "\t" in text.split("\n", 1)[0] and text.count("\t") >= 1:
        return parse_csv_bytes(raw, "\t")
    if "," in text.split("\n", 1)[0]:
        try:
            return parse_csv_bytes(raw, ",")
        except Exception:
            pass
    return parse_text_bytes(raw)


def parse_payload(payload: Dict[str, Any]) -> List[Dict[str, str]]:
    if "rows" in payload and isinstance(payload["rows"], list):
        return rows_from_mapping_list(payload["rows"])
    if "items" in payload and isinstance(payload["items"], list):
        return rows_from_mapping_list(payload["items"])
    if "text" in payload and isinstance(payload["text"], str):
        return parse_text_bytes(payload["text"].encode("utf-8"))
    raise ValueError("JSON body needs text|rows|items")


def run_gate(items: Sequence[Dict[str, str]]) -> Dict[str, Any]:
    ctrl = HeadroomAdmissionController(
        supported=ResourceVector(120.0, 120.0, 100.0, 100.0),
        epsilon_H=0.15,
    )
    seraph = SeraphimResidual(dim=4, T_s=0.05, K_r=8.0)

    ui_rows = []
    for i, item in enumerate(items):
        if i > 0 and i % 40 == 0:
            rel = ResourceVector(
                ctrl.active.compute * 0.35,
                ctrl.active.memory * 0.35,
                ctrl.active.power * 0.40,
                ctrl.active.thermal * 0.45,
            )
            ctrl.update_telemetry(release=rel)

        R, pairs, toks, aff, kind, phrase = text_to_R_and_pairs(item)
        ctrl.update_telemetry()
        echo = echo_lanes(item.get("id") or "", aff)
        title = item.get("text") or ""
        v = ctrl.evaluate(
            R, pairs=pairs, echo=echo, meta={"id": item.get("id"), "t": title[:80]}
        )

        innov = [
            v.r_H * 0.01,
            (1 - v.S_solv) * 0.02,
            (1 - v.R_H) * 0.02,
            (1 - aff) * 0.01,
        ]
        V = seraph.step(innovate=innov)

        ui_rows.append({
            "t": title,
            "id": item.get("id") or "",
            "c": "",
            "k": kind,
            "p": phrase,
            "decision": "admit" if v.admit else "refuse",
            "S_solv": bool(v.S_solv),
            "R_H": bool(v.R_H),
            "S_H": bool(v.S_H),
            "cause": v.reason or "",
            "phi": round(v.phi_H, 4),
            "seraphim_V": round(V, 8),
            "audit": (v.digest or "")[:16],
            "R": v.claimed or {},
            "aff": round(aff, 3),
            "toks": toks,
            "r_H": round(v.r_H, 6),
            "interior": v.interior,
        })

    return {
        "n": len(ui_rows),
        "stamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "seal": "S_H = S_solv · R_H",
        "ppa": ctrl.ppa_ref,
        "epsilon_H": ctrl.epsilon_H,
        "ledger_tip": ctrl.ledger.tip()[:24],
        "seraphim": seraph.snapshot(),
        "counts": {"admit": ctrl.admits, "refuse": ctrl.refuses},
        "verdicts": ui_rows,
    }


def organize_bytes(raw: bytes, filename: str = "", content_type: str = "") -> Dict[str, Any]:
    items = parse_dump(raw, filename=filename, content_type=content_type)
    return run_gate(items)


def organize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    items = parse_payload(payload)
    return run_gate(items)


if __name__ == "__main__":
    import sys
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "sample_dump.csv")
    result = organize_bytes(path.read_bytes(), filename=path.name)
    print(json.dumps({
        "n": result["n"],
        "counts": result["counts"],
        "seal": result["seal"],
    }, indent=2))
