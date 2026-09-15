#!/usr/bin/env python3
"""merit_simulator.py: aplica una matriz de mérito a un archivo de empleados y calcula su costo.

Uso:
    python merit_simulator.py employees.csv --matrix matrix.json [--bands comp-bands.csv]
                               [--budget-pct 4] [--fit] [--out increases.csv]

columnas requeridas de employees.csv: employee_id, base_salary, performance
opcional: compa_ratio: si una fila no trae compa_ratio (o viene vacía) y se pasa --bands, se
calcula uniendo por nivel (y por geo/location si ese nivel tiene varias bandas) contra
comp-bands.csv, igual criterio de emparejamiento que usa comp_analysis.py. Si tampoco hay
--bands, esa fila se trata como bucket 'mid' (comportamiento anterior, ahora explícito en el
resumen vía "compa_ratio_source").

formato de matrix.json (% de incremento por rating y bucket de compa-ratio):
{
  "buckets": [0.90, 1.10],
  "matrix": {
    "Exceeds": [7, 5, 3],
    "Meets":   [4.5, 3.5, 2],
    "Below":   [1, 0, 0]
  }
}
"buckets" [a, b] significa que las columnas son CR<a, a<=CR<=b, CR>b.
--fit escala toda la matriz para que el costo total coincida con --budget-pct.

Parte de rhstack (https://github.com/luisgalvan/rhstack), creado por Luis Galvan. Licencia MIT.
"""
import argparse
import csv
import json
import re
import sys


def to_float(x):
    """Parsea un número de moneda tolerando formato US (1,234.56) y europeo (1.234,56)."""
    if x is None:
        return None
    s = re.sub(r"[^0-9,.\-]", "", str(x)).strip()
    if s in ("", "-"):
        return None
    has_comma, has_dot = "," in s, "." in s
    if has_comma and has_dot:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif has_comma:
        last_group = s.split(",")[-1]
        if s.count(",") == 1 and len(last_group) in (1, 2):
            s = s.replace(",", ".")
        else:
            s = s.replace(",", "")
    try:
        return float(s)
    except ValueError:
        return None


def index_bands(bands):
    by_level = {}
    for b in bands:
        by_level.setdefault(b.get("level"), []).append(b)
    return by_level


def find_band(by_level, level, geo_value):
    candidates = by_level.get(level)
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]
    for b in candidates:
        if b.get("geo") and geo_value and b["geo"].strip().lower() == geo_value.strip().lower():
            return b
    return None


def bucket_index(cr, buckets):
    if cr is None:
        return 1
    if cr < buckets[0]:
        return 0
    if cr > buckets[1]:
        return 2
    return 1


def resolve_compa_ratio(r, by_level_bands, no_band_match):
    """Devuelve (compa_ratio, source) para una fila de empleado.

    source es uno de: "input" (venía en employees.csv), "bands" (calculada uniendo con
    comp-bands.csv), "no_band_match" (había --bands pero ningún band_mid coincidió con el nivel/
    geo del empleado), "default_mid" (no había compa_ratio ni --bands)."""
    given = to_float(r.get("compa_ratio"))
    if given is not None:
        return given, "input"
    if by_level_bands is None:
        return None, "default_mid"
    b = find_band(by_level_bands, r.get("level"), r.get("geo") or r.get("location"))
    mid = to_float(b.get("band_mid")) if b else None
    s = to_float(r.get("base_salary"))
    if mid and s is not None:
        return round(s / mid, 3), "bands"
    no_band_match.add(r.get("employee_id") or "(sin id)")
    return None, "no_band_match"


def run(rows, cfg, scale=1.0, by_level_bands=None):
    total_payroll, total_cost, lines, unmatched, no_band_match = 0.0, 0.0, [], set(), set()
    for r in rows:
        s = to_float(r.get("base_salary"))
        if s is None:
            continue
        total_payroll += s
        rating = (r.get("performance") or "").strip()
        row = cfg["matrix"].get(rating)
        compa, compa_source = resolve_compa_ratio(r, by_level_bands, no_band_match)
        if row is None:
            unmatched.add(rating or "(empty)")
            pct = 0.0
        else:
            pct = row[bucket_index(compa, cfg["buckets"])] * scale
        inc = round(s * pct / 100, 2)
        total_cost += inc
        lines.append({"employee_id": r.get("employee_id"), "base_salary": s,
                      "performance": rating, "compa_ratio": compa,
                      "compa_ratio_source": compa_source,
                      "increase_pct": round(pct, 2), "increase_amount": inc,
                      "new_salary": round(s + inc, 2)})
    return total_payroll, total_cost, lines, unmatched, no_band_match


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("employees")
    ap.add_argument("--matrix", required=True)
    ap.add_argument("--bands", help="comp-bands.csv: calcula compa_ratio para filas que no lo traigan")
    ap.add_argument("--budget-pct", type=float)
    ap.add_argument("--fit", action="store_true", help="escalar la matriz para alcanzar el presupuesto")
    ap.add_argument("--out", help="escribir CSV de incrementos por empleado")
    args = ap.parse_args()

    with open(args.employees, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    with open(args.matrix, encoding="utf-8") as f:
        cfg = json.load(f)

    by_level_bands = None
    if args.bands:
        with open(args.bands, newline="", encoding="utf-8") as f:
            by_level_bands = index_bands(list(csv.DictReader(f)))

    payroll, cost, lines, unmatched, no_band_match = run(rows, cfg, by_level_bands=by_level_bands)
    scale = 1.0
    # args.budget_pct is not None (no "and args.budget_pct"): 0 es un presupuesto explícito
    # válido (congelamiento de ciclo) y es falsy en Python: un chequeo truthy lo saltaría en
    # silencio y aplicaría la matriz sin escalar, ignorando el 0% pedido.
    if args.fit and args.budget_pct is not None and cost > 0:
        scale = (args.budget_pct / 100 * payroll) / cost
        payroll, cost, lines, unmatched, no_band_match = run(rows, cfg, scale, by_level_bands)

    summary = {
        "n_employees": len(lines),
        "total_payroll": round(payroll, 2),
        "total_increase_cost": round(cost, 2),
        "effective_pct_of_payroll": round(cost / payroll * 100, 2) if payroll else None,
        "budget_pct": args.budget_pct,
        "matrix_scale_applied": round(scale, 3),
        "zero_increase_count": sum(1 for l in lines if l["increase_amount"] == 0),
        "unmatched_ratings": sorted(unmatched),
        "no_band_match_count": len(no_band_match),
    }
    print(json.dumps(summary, indent=2))
    if no_band_match:
        print(f"ADVERTENCIA: {len(no_band_match)} empleado(s) sin banda coincidente para "
              f"calcular compa_ratio (bucket 'mid' por defecto): {sorted(no_band_match)}",
              file=sys.stderr)
    if unmatched:
        print(f"ADVERTENCIA: ratings que no están en la matriz recibieron 0%: {sorted(unmatched)}", file=sys.stderr)

    if args.out:
        with open(args.out, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=lines[0].keys())
            w.writeheader()
            w.writerows(lines)


if __name__ == "__main__":
    main()
