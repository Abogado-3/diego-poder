#!/usr/bin/env python3
"""Buscar y agregar juzgados en el directorio CSV compartido (OneDrive del firm)."""

import argparse
import csv
import json
import re
import sys
import unicodedata

import diego_paths

HEADERS = ["email", "nombre", "departamento", "ciudad", "especialidad", "notas"]


def normalize(s: str) -> str:
    if not s:
        return ""
    s = s.lower()
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^\w\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def tokens(s: str) -> set:
    return set(t for t in normalize(s).split() if len(t) > 1)


def load_rows():
    csv_path = diego_paths.directorio_csv_path()
    if not csv_path.exists():
        return []
    with csv_path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_rows(rows):
    csv_path = diego_paths.directorio_csv_path()
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        for row in rows:
            writer.writerow({h: row.get(h, "") for h in HEADERS})


def _extraer_numero_juzgado(texto):
    m = re.search(r"juzgado\s+0*(\d+)", normalize(texto))
    return m.group(1) if m else None


def cmd_buscar(args):
    query_tokens = tokens(args.query)
    if not query_tokens:
        print(json.dumps({"matches": [], "error": "query vacía"}))
        return

    query_juz_num = _extraer_numero_juzgado(args.query)

    scored = []
    rejected_by_num = 0
    for row in load_rows():
        haystack = " ".join([row.get("nombre", ""), row.get("ciudad", ""),
                             row.get("departamento", ""), row.get("especialidad", "")])

        if query_juz_num and not args.fuzzy:
            row_juz_num = _extraer_numero_juzgado(row.get("nombre", ""))
            if row_juz_num != query_juz_num:
                rejected_by_num += 1
                continue

        row_tokens = tokens(haystack)
        hits = query_tokens & row_tokens
        if hits:
            score = len(hits) / len(query_tokens)
            scored.append((score, row))

    scored.sort(key=lambda x: -x[0])
    top = scored[: args.top]
    matches = [{"score": round(s, 3), **r} for s, r in top]
    out = {"matches": matches}
    if query_juz_num and not args.fuzzy:
        out["modo"] = "estricto"
        out["numero_juzgado_query"] = query_juz_num
        out["rechazados_por_numero_distinto"] = rejected_by_num
    print(json.dumps(out, ensure_ascii=False, indent=2))


def cmd_agregar(args):
    rows = load_rows()
    if any(r.get("email", "").lower() == args.email.lower() for r in rows):
        print(json.dumps({"status": "ya_existe", "email": args.email}, ensure_ascii=False))
        return

    nueva = {
        "email": args.email,
        "nombre": args.nombre,
        "departamento": args.departamento,
        "ciudad": args.ciudad,
        "especialidad": args.especialidad,
        "notas": args.notas or "",
    }
    rows.append(nueva)
    save_rows(rows)
    print(json.dumps({"status": "agregado", **nueva}, ensure_ascii=False))


def cmd_listar(args):
    rows = load_rows()
    print(json.dumps({"total": len(rows), "rows": rows}, ensure_ascii=False, indent=2))


def cmd_ruta(args):
    """Diagnóstico: muestra dónde está el CSV."""
    p = diego_paths.directorio_csv_path()
    print(json.dumps({"path": str(p), "existe": p.exists()}, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description="Directorio de juzgados")
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("buscar", help="Busca por nombre/ciudad/especialidad")
    b.add_argument("query")
    b.add_argument("--top", type=int, default=5)
    b.add_argument("--fuzzy", action="store_true",
                   help="Desactiva el filtro estricto por número de juzgado")
    b.set_defaults(func=cmd_buscar)

    a = sub.add_parser("agregar", help="Agrega una entrada nueva")
    a.add_argument("--email", required=True)
    a.add_argument("--nombre", required=True)
    a.add_argument("--departamento", required=True)
    a.add_argument("--ciudad", required=True)
    a.add_argument("--especialidad", required=True)
    a.add_argument("--notas", default="")
    a.set_defaults(func=cmd_agregar)

    l = sub.add_parser("listar", help="Lista todas las entradas")
    l.set_defaults(func=cmd_listar)

    r = sub.add_parser("ruta", help="Muestra dónde está el CSV (diagnóstico)")
    r.set_defaults(func=cmd_ruta)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
