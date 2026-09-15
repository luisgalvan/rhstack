#!/usr/bin/env python3
"""comp_analysis.py: estadísticas salariales por nivel, compa-ratio, compresión y señales de outliers.

Uso:
    python comp_analysis.py employees.csv [--bands bands.csv] [--json out.json]

columnas requeridas de employees.csv: employee_id, level, base_salary
columnas opcionales: function, location (o geo), hire_date (YYYY-MM-DD), performance

columnas de bands.csv: level, band_min, band_mid, band_max
columna opcional de bands.csv: geo: si un nivel tiene varias filas (una por geografía), cada
fila de employees.csv se empareja por geo (o location) contra la geo de la banda; si no hay
coincidencia, el empleado queda fuera de las métricas de banda y se reporta en "unmatched_geo"
en vez de emparejarse en silencio con la banda equivocada.

Parte de rhstack (https://github.com/luisgalvan/rhstack), creado por Luis Galvan. Licencia MIT.
"""
import argparse
import csv
import json
import math
import re
import statistics as st
import sys
from datetime import date


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def to_float(x):
    """Parsea un número de moneda tolerando formato US (1,234.56) y europeo (1.234,56).

    Estrategia: quita cualquier símbolo que no sea dígito/coma/punto/signo, luego decide cuál
    separador es el decimal. Si aparecen ambos, el que está más a la derecha es el decimal. Si
    solo aparece una coma con 1-2 dígitos después, se trata como decimal (estilo europeo sin
    separador de miles); en cualquier otro caso se asume separador de miles y se descarta.
    """
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


def percentile(sorted_vals, p):
    """Percentil p (0-100) por interpolación lineal entre rangos (método "linear" estándar,
    el mismo que usa NumPy/Excel PERCENTILE.INC por defecto). sorted_vals debe venir ordenada."""
    if not sorted_vals:
        return None
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    k = (len(sorted_vals) - 1) * (p / 100)
    f, c = math.floor(k), math.ceil(k)
    if f == c:
        return round(sorted_vals[int(k)], 2)
    d0 = sorted_vals[int(f)] * (c - k)
    d1 = sorted_vals[int(c)] * (k - f)
    return round(d0 + d1, 2)


def percentile_rank(value, sorted_vals):
    """Percentil reverso: en qué percentil de la distribución cae `value`: % de la muestra en
    o por debajo de ese valor."""
    n = len(sorted_vals)
    if n == 0:
        return None
    below_or_equal = sum(1 for v in sorted_vals if v <= value)
    return round(below_or_equal / n * 100, 1)


def skewness_label(mean, median, stdev):
    """Coeficiente de asimetría de Pearson (segundo): 3*(media-mediana)/desv.est. Es una
    aproximación barata de calcular con solo stdlib; no reemplaza inspeccionar un histograma.
    No intenta detectar bimodalidad: eso requiere un histograma real, que este script no dibuja;
    si el usuario sospecha una distribución bimodal (dos clústeres de pago, p. ej. por adquisición
    o legado vs. nuevo), dilo como hipótesis a verificar visualmente, no como un hallazgo del script."""
    if not stdev:
        return None, "sin datos suficientes para estimar forma"
    skew = round(3 * (mean - median) / stdev, 2)
    if skew > 0.5:
        label = "sesgada a la derecha (unos pocos salarios altos alejan la media de la mediana)"
    elif skew < -0.5:
        label = "sesgada a la izquierda (unos pocos salarios bajos alejan la media de la mediana)"
    else:
        label = "aproximadamente simétrica"
    return skew, label


def tenure_years(hire_date, today=None):
    try:
        y, m, d = (int(p) for p in str(hire_date).split("-"))
        today = today or date.today()
        return (today - date(y, m, d)).days / 365.25
    except (ValueError, AttributeError):
        return None


def level_stats(rows):
    out = {}
    by_level = {}
    for r in rows:
        s = to_float(r.get("base_salary"))
        if s is None:
            continue
        by_level.setdefault(r.get("level", "?"), []).append(s)
    for lvl, sal in sorted(by_level.items()):
        sal_sorted = sorted(sal)
        mean = st.mean(sal)
        median = st.median(sal)
        stdev = st.stdev(sal) if len(sal) >= 2 else None
        skew, shape = skewness_label(mean, median, stdev) if len(sal) >= 5 else (None, None)
        out[lvl] = {
            "n": len(sal),
            "min": min(sal),
            "p10": percentile(sal_sorted, 10),
            "median": median,
            "mean": round(mean, 2),
            "p90": percentile(sal_sorted, 90),
            "max": max(sal),
            "range": round(max(sal) - min(sal), 2),
            "spread_pct": round((max(sal) - min(sal)) / min(sal) * 100, 1) if min(sal) else None,
            "stdev": round(stdev, 2) if stdev is not None else None,
            "coefficient_of_variation_pct": round(stdev / mean * 100, 1) if stdev and mean else None,
            "p90_p10_ratio": round(percentile(sal_sorted, 90) / percentile(sal_sorted, 10), 2)
                             if percentile(sal_sorted, 10) else None,
            "skewness": skew,
            "shape": shape,
            "small_sample": len(sal) < 5,
        }
    return out


def employee_percentiles(rows):
    """Percentil interno de cada empleado dentro de la distribución de salario de su propio
    nivel: distinto de range_penetration, que mide posición dentro de una banda de mercado.
    Esto mide posición dentro de los pares reales de la empresa."""
    by_level = {}
    for r in rows:
        s = to_float(r.get("base_salary"))
        if s is not None:
            by_level.setdefault(r.get("level", "?"), []).append(s)
    sorted_by_level = {lvl: sorted(sal) for lvl, sal in by_level.items()}
    out = []
    for r in rows:
        s = to_float(r.get("base_salary"))
        if s is None:
            continue
        lvl = r.get("level", "?")
        out.append({"employee_id": r.get("employee_id"), "level": lvl, "base_salary": s,
                    "percentile_in_level": percentile_rank(s, sorted_by_level[lvl])})
    return out


def index_bands(bands):
    """Agrupa bands.csv por nivel. Si un nivel tiene varias filas (multi-geo), quedan todas
    disponibles para que find_band() elija por geografía en vez de quedarse con la última leída."""
    by_level = {}
    for b in bands:
        by_level.setdefault(b.get("level"), []).append(b)
    return by_level


def find_band(by_level, level, geo_value):
    """Devuelve la fila de banda para (level, geo). Si el nivel tiene una sola fila, la usa sin
    exigir geo (compatibilidad con bands.csv sin columna geo o de una sola geografía). Si tiene
    varias, exige una coincidencia de geo explícita; nunca elige "la última leída" en silencio."""
    candidates = by_level.get(level)
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]
    for b in candidates:
        if b.get("geo") and geo_value and b["geo"].strip().lower() == geo_value.strip().lower():
            return b
    return None


def band_metrics(rows, bands):
    by_level = index_bands(bands)
    results, below, above, unmatched_geo = [], [], [], []
    for r in rows:
        s = to_float(r.get("base_salary"))
        level = r.get("level")
        if s is None:
            continue
        geo_value = r.get("geo") or r.get("location")
        b = find_band(by_level, level, geo_value)
        if b is None:
            if level in by_level and len(by_level[level]) > 1:
                unmatched_geo.append({"employee_id": r.get("employee_id"), "level": level,
                                       "geo": geo_value or None,
                                       "reason": "el nivel tiene varias bandas por geografía y "
                                                 "ninguna coincide con la geo del empleado"})
            continue
        lo, mid, hi = to_float(b.get("band_min")), to_float(b.get("band_mid")), to_float(b.get("band_max"))
        compa = round(s / mid, 3) if mid else None
        pen = round((s - lo) / (hi - lo), 3) if lo is not None and hi is not None and hi != lo else None
        rec = {"employee_id": r.get("employee_id"), "level": level,
               "base_salary": s, "compa_ratio": compa, "range_penetration": pen,
               "band_min": lo}
        results.append(rec)
        if lo is not None and s < lo:
            below.append(rec)
        if hi is not None and s > hi:
            above.append(rec)
    return results, below, above, unmatched_geo


def compression_flags(rows, tenure_gap=3.0, pay_tolerance=0.05):
    """Señala niveles donde las contrataciones recientes ganan dentro de la tolerancia respecto a pares de mayor antigüedad."""
    flags = []
    by_level = {}
    for r in rows:
        s, t = to_float(r.get("base_salary")), tenure_years(r.get("hire_date"))
        if s is not None and t is not None:
            by_level.setdefault(r.get("level", "?"), []).append((t, s))
    for lvl, pairs in sorted(by_level.items()):
        new = [s for t, s in pairs if t < 1.0]
        vet = [s for t, s in pairs if t >= tenure_gap]
        if new and vet:
            gap = (st.median(vet) - st.median(new)) / st.median(vet)
            if gap <= pay_tolerance:
                flags.append({"level": lvl,
                              "median_new_hire": st.median(new),
                              "median_tenured": st.median(vet),
                              "gap_pct": round(gap * 100, 1)})
    return flags


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("employees")
    ap.add_argument("--bands")
    ap.add_argument("--json", help="también escribir los resultados completos en este archivo JSON")
    args = ap.parse_args()

    rows = read_csv(args.employees)
    if not rows:
        sys.exit("No se encontraron filas en el archivo de empleados.")

    report = {"n_employees": len(rows), "level_stats": level_stats(rows),
              "employee_percentiles": employee_percentiles(rows),
              "compression_flags": compression_flags(rows)}

    if args.bands:
        _, below, above, unmatched_geo = band_metrics(rows, read_csv(args.bands))
        report["below_band_min"] = below
        report["above_band_max"] = above
        report["cost_to_min"] = round(sum(r["band_min"] - r["base_salary"] for r in below), 2)
        if unmatched_geo:
            report["unmatched_geo"] = unmatched_geo

    print(json.dumps(report, indent=2))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)


if __name__ == "__main__":
    main()
