#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Construit `viewer/diplomatic_pages.json`, le jeu de données de l'éditeur de
transcription diplomatique (`viewer/diplomatic_editor.html`).

Sources (dépôt Bench_HTR, voisin de 533yes) :
  - gold éditorial actuel : Bench_HTR/gold_sol_terra_luna.csv
  - sorties par modèle    : Bench_HTR/results/<run>/gpt56-{sol,terra,luna}.jsonl

Règle de préchargement (cf. README_DIPLOMATIC.md) : on ne précharge qu'un texte
« exploitable », c.-à-d. non vide et non dégénéré (boucles de marqueurs
`[illisible]`). Ordre de préférence sol > terra > luna. Si aucun candidat n'est
exploitable, la page est préchargée **vide** : le gold éditorial existant reste
accessible dans le sélecteur, mais n'est jamais chargé par défaut, pour ne pas
contaminer la saisie diplomatique par une mise au propre éditoriale.

Usage :
    python viewer/build_diplomatic_data.py [--run <nom_du_run>]
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BENCH = REPO.parent / "Bench_HTR"
DEFAULT_RUN = "sol_terra_luna_20260726_1020"
MODELS = ["sol", "terra", "luna"]

# Un texte est jugé dégénéré si la ligne la plus fréquente occupe au moins cette
# part des lignes non vides (les boucles `[illisible]` de luna/terra sont à 1.0),
# ou si le texte est plus court que MIN_CHARS.
DEGENERATE_RATIO = 0.55
MIN_CHARS = 120


def usability(text: str) -> tuple[bool, str]:
    """Retourne (exploitable, motif)."""
    text = (text or "").strip()
    if not text:
        return False, "vide"
    if len(text) < MIN_CHARS:
        return False, f"trop court ({len(text)} car.)"
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if lines:
        top, n = Counter(lines).most_common(1)[0]
        ratio = n / len(lines)
        if ratio >= DEGENERATE_RATIO:
            return False, f"dégénéré ({ratio:.0%} de lignes « {top[:20]} »)"
    return True, "exploitable"


def image_url(path: str) -> str:
    """URL servie par server.py pour un chemin d'image absolu."""
    p = Path(path)
    try:
        rel = p.resolve().relative_to(REPO)
        return "/" + str(rel).replace("\\", "/")
    except ValueError:
        pass
    try:
        rel = p.resolve().relative_to(BENCH)
        return "/bench/" + str(rel).replace("\\", "/")
    except ValueError:
        return "/" + str(p).replace("\\", "/").lstrip("/")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default=DEFAULT_RUN)
    ap.add_argument("--out", default=str(REPO / "viewer" / "diplomatic_pages.json"))
    args = ap.parse_args()

    gold_csv = BENCH / "gold_sol_terra_luna.csv"
    run_dir = BENCH / "results" / args.run
    if not gold_csv.exists():
        print(f"gold introuvable : {gold_csv}", file=sys.stderr)
        return 1
    if not run_dir.is_dir():
        print(f"run introuvable : {run_dir}", file=sys.stderr)
        return 1

    with gold_csv.open(encoding="utf-8", newline="") as fh:
        gold_rows = list(csv.DictReader(fh))

    outputs: dict[str, dict[str, str]] = {}
    for model in MODELS:
        jsonl = run_dir / f"gpt56-{model}.jsonl"
        if not jsonl.exists():
            continue
        with jsonl.open(encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                rec = json.loads(line)
                outputs.setdefault(rec["item_name"], {})[model] = rec.get("transcription") or ""

    pages = []
    for row in gold_rows:
        item = row["item_name"]
        cands = {}
        preload_source = None
        for model in MODELS:
            text = outputs.get(item, {}).get(model, "")
            ok, why = usability(text)
            cands[model] = {"text": text, "usable": ok, "reason": why, "chars": len(text)}
            if ok and preload_source is None:
                preload_source = model
        img = row["image_path"]
        pages.append({
            "item_name": item,
            "family": row["family"],
            "image_path": img,
            "image_url": image_url(img),
            "image_exists": os.path.exists(img),
            "candidates": cands,
            "gold_editorial": row["gold_text"],
            "preload_source": preload_source or "vide",
        })

    data = {
        "run": args.run,
        "generated_by": "viewer/build_diplomatic_data.py",
        "rule": (
            "Précharge le premier modèle exploitable dans l'ordre sol > terra > luna "
            "(non vide, >= %d car., pas de boucle de lignes identiques >= %d%%). "
            "Sinon : vide. Le gold éditorial n'est jamais préchargé." % (MIN_CHARS, int(DEGENERATE_RATIO * 100))
        ),
        "csv_columns": ["item_name", "gold_text", "family", "image_path"],
        "pages": pages,
    }
    out = Path(args.out)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"{len(pages)} pages -> {out}")
    for p in pages:
        flags = " ".join(
            f"{m}:{'ok' if p['candidates'][m]['usable'] else '-'}" for m in MODELS if m in p["candidates"]
        )
        print(f"  {p['item_name'][:50]:52} preload={p['preload_source']:6} {flags}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
