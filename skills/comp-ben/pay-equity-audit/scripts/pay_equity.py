#!/usr/bin/env python3
"""pay_equity.py: análisis de brecha salarial sin ajustar, dentro de cada nivel, y (opcional)
por regresión lineal múltiple.

Uso:
    python pay_equity.py employees.csv --group gender [--min-cell 5]
        [--regression [--controls function,location]] [--json out.json]

Columnas requeridas: base_salary, level, y la columna --group.
Las brechas se reportan como (referencia - otro) / referencia, donde el grupo de
referencia es el que tiene la mediana global más alta (reportado explícitamente).

--regression agrega un análisis adicional (no reemplaza al de arriba): una regresión de
ln(base_salary) sobre nivel + controles + grupo, que estima la brecha de cada grupo
controlando varias variables SIMULTÁNEAMENTE en vez de una a la vez por nivel. Requiere más
observaciones que el análisis por nivel; si no alcanzan, reporta el motivo en vez de forzar
un resultado.

Parte de rhstack (https://github.com/luisgalvan/rhstack), creado por Luis Galvan. Licencia MIT.
"""
import argparse
import csv
import json
import math
import re
import statistics as st
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


def gap(ref, other):
    """(mediana(ref) - mediana(other)) / mediana(ref), en %. None si la mediana de referencia es
    0: dividir entre cero no es "brecha del -inf%", es un dato no computable que debe declararse
    como tal, nunca fallar con un traceback."""
    ref_med = st.median(ref)
    if ref_med == 0:
        return None
    return round((ref_med - st.median(other)) / ref_med * 100, 1)


# --- Regresión lineal múltiple ------------------------------------------------------------
# Motor de mínimos cuadrados puro-stdlib (sin numpy: CONTRIBUTING.md exige scripts sin
# dependencias). Se usa para el análisis "regression_adjusted_gap": en vez de comparar
# medianas nivel por nivel (una variable de control a la vez), estima la brecha del grupo
# controlando varias variables SIMULTÁNEAMENTE (nivel + función + ubicación, si existen), que
# es la metodología que ETHOS.md ya declara como estándar Capa 1 ("regresión controlada").

def _transpose(m):
    return [list(row) for row in zip(*m)]


def _matmul(a, b):
    bt = _transpose(b)
    return [[sum(x * y for x, y in zip(row, col)) for col in bt] for row in a]


def _matinv(m):
    """Inversión de matriz por Gauss-Jordan con pivoteo parcial. Lanza ValueError si la matriz
    es singular (colinealidad perfecta entre columnas, p. ej. un control que coincide 1:1 con
    otro, o una celda vacía por combinación de nivel × grupo)."""
    n = len(m)
    aug = [row[:] + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(m)]
    for col in range(n):
        pivot_row = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot_row][col]) < 1e-9:
            raise ValueError("matriz singular: colinealidad perfecta entre variables de control")
        aug[col], aug[pivot_row] = aug[pivot_row], aug[col]
        pivot = aug[col][col]
        aug[col] = [x / pivot for x in aug[col]]
        for r in range(n):
            if r != col:
                factor = aug[r][col]
                aug[r] = [aug[r][j] - factor * aug[col][j] for j in range(2 * n)]
    return [row[n:] for row in aug]


def ols_fit(x_matrix, y_vector):
    """Mínimos cuadrados ordinarios: beta = (X'X)^-1 X'y. x_matrix ya debe incluir la columna
    de 1s para el intercepto. Devuelve (beta, r_squared, adj_r_squared, standard_error_of_estimate)."""
    n, k = len(x_matrix), len(x_matrix[0])
    xt = _transpose(x_matrix)
    xtx_inv = _matinv(_matmul(xt, x_matrix))
    beta = [row[0] for row in _matmul(xtx_inv, _matmul(xt, [[v] for v in y_vector]))]
    y_hat = [sum(b * xij for b, xij in zip(beta, row)) for row in x_matrix]
    y_mean = sum(y_vector) / n
    ss_res = sum((y - yh) ** 2 for y, yh in zip(y_vector, y_hat))
    ss_tot = sum((y - y_mean) ** 2 for y in y_vector)
    r2 = 1 - ss_res / ss_tot if ss_tot else None
    df = n - k
    adj_r2 = 1 - (1 - r2) * (n - 1) / df if r2 is not None and df > 0 else None
    see = math.sqrt(ss_res / df) if df > 0 else None
    return beta, r2, adj_r2, see


def _dummy_columns(rows, col, reference):
    """Categorías distintas de `col` salvo `reference` (que queda implícita en el intercepto).
    Ordenado para que la salida sea determinística entre corridas."""
    values = sorted({(r.get(col) or "unspecified") for r in rows} - {reference})
    return values


def regression_adjusted_gap(rows, group_col, ref_group, min_obs_per_param=5, extra_controls=()):
    """Regresión de ln(base_salary) sobre nivel + controles disponibles (function/location) +
    dummies de grupo, con el grupo de referencia (mediana global más alta) como categoría base.
    El coeficiente de cada grupo, revertido de escala log, es la brecha % de ese grupo frente
    al de referencia CONTROLANDO simultáneamente por las demás variables, no solo por nivel a
    la vez, como hace el análisis within_level de arriba. Devuelve un dict con la brecha
    ajustada por grupo y las métricas de calidad del modelo, o {"error": "..."} si no hay datos
    suficientes o el modelo es singular; nunca hace fallback silencioso a un número inventado."""
    # base_salary debe ser > 0 (se usa ln(base_salary) más abajo): `is not None and > 0`
    # explícito, no un chequeo truthy: to_float(...) puede devolver 0.0 legítimamente (un
    # placeholder o un rol sin pago), que es falsy en Python pero un valor real, no "faltante".
    usable = [r for r in rows
              if (lambda v: v is not None and v > 0)(to_float(r.get("base_salary")))]

    # Las columnas dummy se construyen a partir de `usable`, no de `rows` sin filtrar: si se
    # construyeran antes del filtro, una categoría que solo aparece en una fila excluida (p. ej.
    # el único empleado de una función con salario 0) generaría una columna estructuralmente toda
    # en cero, y la matriz resultaría singular con un error genérico en vez de una causa clara.
    controls = ["level"] + [c for c in extra_controls if usable and c in usable[0]]
    level_dummies = {c: _dummy_columns(usable, c, reference=sorted({r.get(c) or "unspecified" for r in usable})[0])
                      for c in controls}
    group_dummies = _dummy_columns(usable, group_col, reference=ref_group)

    columns = []  # (kind, control_col, value) para reconstruir cada fila
    for c in controls:
        for v in level_dummies[c]:
            columns.append(("control", c, v))
    for v in group_dummies:
        columns.append(("group", group_col, v))

    n_params = len(columns) + 1  # + intercepto
    if len(usable) < n_params + min_obs_per_param:
        return {"error": f"Observaciones insuficientes para la regresión: se necesitan al menos "
                          f"{n_params + min_obs_per_param} filas para {n_params} parámetros "
                          f"(nivel × {'+ '.join(controls[1:]) or 'sin controles adicionales'} "
                          f"+ grupo), hay {len(usable)}. Usa el análisis por nivel de arriba."}

    x_matrix, y_vector = [], []
    for r in usable:
        row_x = [1.0]  # intercepto
        for kind, col, val in columns:
            actual = r.get(col) or "unspecified"
            row_x.append(1.0 if actual == val else 0.0)
        x_matrix.append(row_x)
        y_vector.append(math.log(to_float(r["base_salary"])))

    try:
        beta, r2, adj_r2, see = ols_fit(x_matrix, y_vector)
    except (ValueError, ZeroDivisionError) as e:
        return {"error": f"No se pudo estimar el modelo: {e}. Suele significar que una "
                          f"combinación de nivel/control/grupo no tiene ninguna fila (celda "
                          f"vacía); revisa el análisis por nivel de arriba en su lugar."}

    gaps_pct = {}
    for (kind, col, val), coef in zip(columns, beta[1:]):
        if kind == "group":
            # exp(coef)-1 revierte la transformación log exactamente (no coef*100, que es solo
            # una aproximación válida cerca de 0).
            gaps_pct[val] = round((math.exp(coef) - 1) * 100, 1)

    return {
        "controls_used": controls,
        "reference_group": ref_group,
        "n_obs": len(usable),
        "n_params": n_params,
        "r_squared": round(r2, 3) if r2 is not None else None,
        "adj_r_squared": round(adj_r2, 3) if adj_r2 is not None else None,
        "standard_error_of_estimate_log_scale": round(see, 4) if see is not None else None,
        "gaps_pct_holding_controls_constant": gaps_pct,
        "note": "Brecha % de cada grupo frente a la referencia, controlando simultáneamente "
                f"por {', '.join(controls)}, no es lo mismo que la brecha sin ajustar ni que "
                "la brecha por nivel individual; puede diferir de ambas.",
    }


def simpsons_paradox_flags(report, groups_gap):
    """Señala cuándo la brecha global (agregada) tiene signo contrario a la brecha típica
    dentro de los niveles: el patrón clásico de la Paradoja de Simpson; la
    brecha global la puede estar impulsando la representación por nivel, no el pago desigual
    dentro de cada nivel. No es un cálculo adicional, es una relectura de números que el script
    ya produjo."""
    flags = []
    for g, global_gap in groups_gap.items():
        if global_gap is None or abs(global_gap) < 1.0:
            continue
        within = [gaps[g] for gaps in report["within_level"].values() if g in gaps]
        within = [v for v in within if v is not None]
        if not within:
            continue
        typical = st.median(within)
        if abs(typical) < 1.0:
            continue
        if (global_gap > 0) != (typical > 0):
            flags.append({
                "group": g,
                "global_gap_pct": global_gap,
                "typical_within_level_gap_pct": round(typical, 1),
                "reading": "La brecha global y la brecha típica dentro de cada nivel apuntan en "
                           "direcciones opuestas; revisa representation_by_level: es probable "
                           "que la brecha global la explique en qué niveles está representado "
                           "cada grupo, no el pago dentro de un mismo nivel.",
            })
    return flags


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("employees")
    ap.add_argument("--group", default="gender")
    ap.add_argument("--min-cell", type=int, default=5)
    ap.add_argument("--regression", action="store_true",
                     help="agrega un análisis de regresión múltiple (ln(salario) ~ nivel + "
                          "controles + grupo), más riguroso que el análisis por nivel, "
                          "requiere más observaciones")
    ap.add_argument("--controls", default="function,location",
                     help="columnas adicionales a usar como control en --regression, si existen "
                          "en el CSV (separadas por coma)")
    ap.add_argument("--json")
    args = ap.parse_args()

    with open(args.employees, newline="", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if to_float(r.get("base_salary")) is not None]
    if not rows:
        sys.exit("No hay filas utilizables.")
    if args.group not in rows[0]:
        sys.exit(f"No se encontró la columna '{args.group}'. Disponibles: {', '.join(rows[0].keys())}")

    # medianas globales por grupo -> elegir referencia
    groups = {}
    for r in rows:
        groups.setdefault(r[args.group] or "unspecified", []).append(to_float(r["base_salary"]))
    medians = {g: st.median(v) for g, v in groups.items() if len(v) >= 2}
    if len(medians) < 2:
        sys.exit("Se necesitan al menos dos grupos con 2+ integrantes cada uno.")
    ref = max(medians, key=medians.get)

    report = {
        "group_column": args.group,
        "reference_group": ref,
        "group_sizes": {g: len(v) for g, v in groups.items()},
        "unadjusted_median_gap_pct": {},
        "within_level": {},
        "representation_by_level": {},
        "excluded_cells": [],
    }

    # Brecha global (sin ajustar). Aplica el mismo umbral --min-cell que within_level: un grupo
    # con menos de min_cell integrantes no produce un porcentaje "preciso" en el número más
    # visible del reporte, produce una nota en excluded_cells.
    for g, v in groups.items():
        if g == ref:
            continue
        if len(v) < args.min_cell or len(groups[ref]) < args.min_cell:
            report["excluded_cells"].append(
                {"level": "(global)", "group": g, "reason": f"tamaño de celda < {args.min_cell}"})
            continue
        report["unadjusted_median_gap_pct"][g] = gap(groups[ref], v)

    by_level = {}
    for r in rows:
        by_level.setdefault(r.get("level", "?"), {}).setdefault(
            r[args.group] or "unspecified", []).append(to_float(r["base_salary"]))

    for lvl, gmap in sorted(by_level.items()):
        total = sum(len(v) for v in gmap.values())
        report["representation_by_level"][lvl] = {
            g: round(len(v) / total * 100, 1) for g, v in gmap.items()
        }
        if ref not in gmap:
            continue
        lvl_gaps = {}
        for g, v in gmap.items():
            if g == ref:
                continue
            if len(v) < args.min_cell or len(gmap[ref]) < args.min_cell:
                report["excluded_cells"].append(
                    {"level": lvl, "group": g, "reason": f"tamaño de celda < {args.min_cell}"})
                continue
            lvl_gaps[g] = gap(gmap[ref], v)
        if lvl_gaps:
            report["within_level"][lvl] = lvl_gaps

    simpson = simpsons_paradox_flags(report, report["unadjusted_median_gap_pct"])
    if simpson:
        report["simpsons_paradox_flags"] = simpson

    if args.regression:
        controls = [c.strip() for c in args.controls.split(",") if c.strip()]
        report["regression_adjusted_gap"] = regression_adjusted_gap(
            rows, args.group, ref, extra_controls=controls)

    print(json.dumps(report, indent=2))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)


if __name__ == "__main__":
    main()
