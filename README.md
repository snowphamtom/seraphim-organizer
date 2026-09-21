# Seraphim Organizer

Local Solvent×Seraphim hybrid dump organizer. Parses CSV/TSV/JSON/JSONL/TXT/MD,
maps each item → resource vector + Howard affinity pairs, then runs
`HeadroomAdmissionController` with Seraphim residual witness.

**Law:** `S_H = S_solv · R_H` (fail-closed; φ observes only).

## Run

```bash
cd /workspace/state/seraphim-organizer
python3 server.py
```

Open **http://127.0.0.1:8777/**

## API

`POST /api/organize`

- multipart `file` (any supported dump), or
- JSON `{ "text": "..." }` / `{ "rows": [...] }` / `{ "items": [...] }`

Returns `{ n, counts: {admit, refuse}, verdicts: [...], seal, ... }`.

## Demo

```bash
curl -s -F file=@sample_dump.csv http://127.0.0.1:8777/api/organize | python3 -m json.tool | head
```

Engines copied from `drive2026/sortboard/engines/`.
