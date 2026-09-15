#!/usr/bin/env python3
"""market_model.py: ajusta modelos de mercado a datos de encuesta salarial y compara pago de
empleados contra el modelo, siguiendo los cinco métodos estándar de análisis de encuestas de
compensación: Modelo Lineal, Exponencial, Maturity Curve (aproximado con un polinomio cúbico,
ver limitación abajo), Power Model, y los dos Job Pricing Market Models (Group of Jobs y Power).

Subcomandos:

  fit      : ajusta un modelo (linear|exponential|power|cubic) a puntos de encuesta (x, y) y
             reporta coeficientes + calidad del ajuste (R², correlación, error estándar de
             estimación). Guarda el modelo en --out para usarlo con `compare`.

             python market_model.py fit survey_points.csv --x points --y survey_median \
                 --model linear --out model.json

  compare  : dado un modelo ya ajustado (de `fit`) y un dataset de empleados con la misma
             columna x, predice el pago de mercado para cada empleado y calcula
             market_ratio = pago_empleado / pago_de_mercado_predicho (el equivalente continuo
             del compa-ratio de `comp-bands`, pero contra una curva en vez de una banda
             discreta).

             python market_model.py compare employees.csv --model model.json --x years_experience

  job-pricing : Job Pricing Market Model: Group of Jobs. No ajusta ninguna
             curva: compara el pago de cada empleado directamente contra la mediana de encuesta
             de SU propio skill/nivel (join por --key), igual criterio de emparejamiento por
             geografía que usa comp_analysis.py si la encuesta trae geo.

             python market_model.py job-pricing employees.csv --survey survey_medians.csv --key level

Limitaciones que hay que declarar en el informe, no ocultar:
- El "modelo cúbico" es una aproximación polinómica a una maturity curve; un enfoque alternativo,
  splines por tramos, NO está implementado aquí (splines con stdlib puro no es trivial y se
  prestaría a errores sutiles); si el ajuste cúbico se ve mal en los extremos del rango de
  experiencia, dilo explícitamente en vez de forzar el cúbico.
- Nunca fabriques datos de encuesta: los puntos (x, y) de `fit` y las medianas de `job-pricing`
  deben venir de una encuesta real (Radford/Mercer/Pave/Ravio/lo que el usuario aporte), citada
  por nombre y fecha en el informe.
- "Identificar outliers" es una inspección VISUAL, no automática. Este script señala residuales
  grandes como candidatos a revisar, nunca los descarta por sí mismo ni concluye que un dato es
  incorrecto solo por estar lejos del modelo.

Parte de rhstack (https://github.com/luisgalvan/rhstack), creado por Luis Galvan. Licencia MIT.
"""
import argparse
import csv
import json
import math
import re
import statistics as st
import sys


# --- Motor de mínimos cuadrados puro-stdlib (duplicado deliberadamente de pay_equity.py: cada
# skill debe quedar autocontenida porque `setup` enlaza cada carpeta de skills/ por separado). ---


def parse_x(value):
    """Convierte el valor de la columna x a número. Acepta números directos ('4', '4.5') y
    niveles estilo rhstack ('L4', 'l4') → 4.0, para que `fit`/`compare` funcionen con la misma
    columna `level` que usan comp-bands y pay-equity-audit."""
    if value is None:
        raise ValueError("valor ausente")
    s = str(value).strip()
    if not s:
        raise ValueError("valor vacío")
    m = re.fullmatch(r"[Ll](\d+(?:\.\d+)?)", s)
    if m:
        return float(m.group(1))
    return float(s.replace(",", ""))


def _transpose(m):
    return [list(row) for row in zip(*m)]


def _matmul(a, b):
    bt = _transpose(b)
    return [[sum(x * y for x, y in zip(row, col)) for col in bt] for row in a]


def _matinv(m):
    n = len(m)
    aug = [row[:] + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(m)]
    for col in range(n):
        pivot_row = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot_row][col]) < 1e-9:
            raise ValueError("matriz singular: revisa si hay puntos x duplicados o insuficientes")
        aug[col], aug[pivot_row] = aug[pivot_row], aug[col]
        pivot = aug[col][col]
        aug[col] = [x / pivot for x in aug[col]]
        for r in range(n):
            if r != col:
                factor = aug[r][col]
                aug[r] = [aug[r][j] - factor * aug[col][j] for j in range(2 * n)]
    return [row[n:] for row in aug]


def ols_fit(x_matrix, y_vector):
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
    return beta, y_hat, r2, adj_r2, see


def _correlation(a, b):
    n = len(a)
    if n < 2:
        return None
    ma, mb = sum(a) / n, sum(b) / n
    num = sum((ai - ma) * (bi - mb) for ai, bi in zip(a, b))
    da = math.sqrt(sum((ai - ma) ** 2 for ai in a))
    db = math.sqrt(sum((bi - mb) ** 2 for bi in b))
    if da == 0 or db == 0:
        return None
    return round(num / (da * db), 4)


# --- Los cuatro modelos --------------------------------------------------------------------

def fit_linear(xs, ys):
    """y = b0 + b1*x: modelo lineal."""
    x_matrix = [[1.0, x] for x in xs]
    beta, y_hat, r2, adj_r2, see = ols_fit(x_matrix, ys)
    return {
        "model": "linear",
        "equation": f"y = {beta[0]:.4f} + {beta[1]:.6f} * x",
        "intercept": round(beta[0], 4), "slope": round(beta[1], 6),
    }, y_hat, r2, adj_r2, see, _correlation(ys, y_hat)


def fit_exponential(xs, ys):
    """ln(y) = b0 + b1*x  =>  y = exp(b0) * exp(b1*x): modelo exponencial. Requiere y > 0."""
    if any(y <= 0 for y in ys):
        raise ValueError("el modelo exponencial requiere que todos los valores de y sean > 0")
    ln_ys = [math.log(y) for y in ys]
    x_matrix = [[1.0, x] for x in xs]
    beta, ln_y_hat, r2_log, adj_r2_log, see_log = ols_fit(x_matrix, ln_ys)
    y_hat = [math.exp(v) for v in ln_y_hat]
    return {
        "model": "exponential",
        "equation": f"y = exp({beta[0]:.4f}) * exp({beta[1]:.6f} * x)",
        "b0_log_scale": round(beta[0], 4), "b1_log_scale": round(beta[1], 6),
    }, y_hat, r2_log, adj_r2_log, see_log, _correlation(ln_ys, ln_y_hat), True


def fit_power(xs, ys):
    """ln(y) = b0 + b1*ln(x)  =>  y = exp(b0) * x^b1: modelo power. Requiere x > 0, y > 0."""
    if any(x <= 0 for x in xs) or any(y <= 0 for y in ys):
        raise ValueError("el modelo power requiere que todos los valores de x e y sean > 0")
    ln_xs, ln_ys = [math.log(x) for x in xs], [math.log(y) for y in ys]
    x_matrix = [[1.0, lx] for lx in ln_xs]
    beta, ln_y_hat, r2_log, adj_r2_log, see_log = ols_fit(x_matrix, ln_ys)
    y_hat = [math.exp(v) for v in ln_y_hat]
    return {
        "model": "power",
        "equation": f"y = exp({beta[0]:.4f}) * x^{beta[1]:.6f}",
        "b0_log_scale": round(beta[0], 4), "b1_log_scale": round(beta[1], 6),
    }, y_hat, r2_log, adj_r2_log, see_log, _correlation(ln_ys, ln_y_hat), True


def fit_cubic(xs, ys):
    """y = b0 + b1*x + b2*x^2 + b3*x^3: aproximación polinómica a una maturity curve (el
    enfoque alternativo, splines por tramos, no está implementado aquí; ver limitaciones en
    el docstring del módulo)."""
    x_matrix = [[1.0, x, x ** 2, x ** 3] for x in xs]
    beta, y_hat, r2, adj_r2, see = ols_fit(x_matrix, ys)
    return {
        "model": "cubic",
        "equation": f"y = {beta[0]:.4f} + {beta[1]:.6f}*x + {beta[2]:.8f}*x^2 + {beta[3]:.10f}*x^3",
        "coefficients": [round(b, 8) for b in beta],
        "limitation": "Aproximación polinómica a una maturity curve; revisa visualmente el "
                      "ajuste en los extremos del rango de x: un cúbico puede oscilar mal "
                      "fuera del rango de datos observado. Un modelo de splines por tramos "
                      "sería más robusto en los extremos, pero no está implementado aquí.",
    }, y_hat, r2, adj_r2, see, _correlation(ys, y_hat)


def predict(model, x):
    m = model["model"]
    if m == "linear":
        return model["intercept"] + model["slope"] * x
    if m == "exponential":
        return math.exp(model["b0_log_scale"] + model["b1_log_scale"] * x)
    if m == "power":
        if x <= 0:
            return None
        return math.exp(model["b0_log_scale"]) * (x ** model["b1_log_scale"])
    if m == "cubic":
        b0, b1, b2, b3 = model["coefficients"]
        return b0 + b1 * x + b2 * x ** 2 + b3 * x ** 3
    raise ValueError(f"modelo desconocido: {m}")


FITTERS = {"linear": fit_linear, "exponential": fit_exponential, "power": fit_power, "cubic": fit_cubic}


def cmd_fit(args):
    with open(args.survey, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    xs, ys, skipped = [], [], 0
    for r in rows:
        try:
            xs.append(parse_x(r[args.x]))
            ys.append(float(str(r[args.y]).replace(",", "")))
        except (KeyError, ValueError, TypeError):
            skipped += 1
            continue
    if skipped:
        print(f"Aviso: se descartaron {skipped} de {len(rows)} filas sin valores utilizables "
              f"en las columnas '{args.x}'/'{args.y}'. Si la columna x no es numérica "
              f"(p. ej. nombres de puesto), usa una columna numérica como years_experience, "
              f"o niveles L1..Ln que este script sí convierte a números.", file=sys.stderr)
    if len(xs) < 5:
        sys.exit(f"Se necesitan al menos 5 puntos de encuesta utilizables; hay {len(xs)}. "
                  f"Un modelo de mercado ajustado a menos de 5 puntos no es defendible.")

    fitter = FITTERS.get(args.model)
    if fitter is None:
        sys.exit(f"Modelo desconocido '{args.model}'. Usa: {', '.join(FITTERS)}.")

    try:
        result = fitter(xs, ys)
    except ValueError as e:
        sys.exit(f"No se pudo ajustar el modelo '{args.model}': {e}")

    model_info, y_hat, r2, adj_r2, see, correl = result[0], result[1], result[2], result[3], result[4], result[5]
    fit_in_log_scale = len(result) > 6 and result[6]

    # calidad del ajuste en escala original (además de la escala log si aplica): es lo que
    # importa para revisar a simple vista qué tan cerca está y_hat de y real.
    orig_r2 = _correlation(ys, y_hat)
    orig_r2 = round(orig_r2 ** 2, 4) if orig_r2 is not None else None

    residuals = [{"x": x, "y_actual": y, "y_predicted": round(yh, 2),
                  "residual": round(y - yh, 2)} for x, y, yh in zip(xs, ys, y_hat)]
    large_resid = sorted(residuals, key=lambda r: abs(r["residual"]), reverse=True)[:5]

    report = {
        **model_info,
        "n_points": len(xs),
        "r_squared": round(r2, 4) if r2 is not None else None,
        "adj_r_squared": round(adj_r2, 4) if adj_r2 is not None else None,
        "standard_error_of_estimate": round(see, 2) if see is not None else None,
        "correlation": correl,
        "fit_computed_in_log_scale": fit_in_log_scale,
        "r_squared_original_scale": orig_r2,
        "candidates_to_review_visually": large_resid,
        "note": "R²/correlación/error estándar se calculan sobre la escala en la que se ajustó "
                "el modelo (log para exponential/power). r_squared_original_scale compara el "
                "valor predicho ya revertido contra el valor real, que es lo que importa para "
                "juzgar el ajuste a simple vista. Nunca descartes un punto de "
                "candidates_to_review_visually solo por estar lejos del modelo; investígalo "
                "primero; siempre hay una razón detrás de un dato atípico.",
    }
    print(json.dumps(report, indent=2))
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(model_info, f, indent=2)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)


def cmd_compare(args):
    with open(args.model, encoding="utf-8") as f:
        model = json.load(f)
    with open(args.employees, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    out_rows, skipped = [], 0
    for r in rows:
        try:
            x = parse_x(r[args.x])
            pay = float(str(r.get("base_salary", "")).replace(",", ""))
        except (KeyError, ValueError, TypeError):
            skipped += 1
            continue
        market_pay = predict(model, x)
        if market_pay is None or market_pay <= 0:
            skipped += 1
            continue
        ratio = round(pay / market_pay, 3)
        out_rows.append({"employee_id": r.get("employee_id"), args.x: x, "base_salary": pay,
                          "predicted_market_pay": round(market_pay, 2), "market_ratio": ratio})

    if not out_rows:
        sys.exit("Ningún empleado tiene datos utilizables para comparar contra el modelo.")

    ratios = [r["market_ratio"] for r in out_rows]
    report = {
        "model_used": model["model"], "n_employees": len(out_rows), "n_skipped": skipped,
        "market_ratio_summary": {
            "min": min(ratios), "median": st.median(ratios),
            "max": max(ratios),
        },
        "below_market": [r for r in out_rows if r["market_ratio"] < 0.90],
        "above_market": [r for r in out_rows if r["market_ratio"] > 1.10],
        "detail": out_rows,
    }
    print(json.dumps(report, indent=2))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)


def cmd_job_pricing(args):
    """Job Pricing Market Model: Group of Jobs, sin curva, comparación directa contra la
    mediana de encuesta de la propia celda (--key, típicamente level o skill_level)."""
    with open(args.survey, newline="", encoding="utf-8") as f:
        survey_rows = list(csv.DictReader(f))
    survey_by_key = {}
    for r in survey_rows:
        try:
            survey_by_key[r[args.key]] = float(r[args.median_col])
        except (KeyError, ValueError, TypeError):
            continue

    with open(args.employees, newline="", encoding="utf-8") as f:
        emp_rows = list(csv.DictReader(f))

    out_rows, unmatched = [], []
    for r in emp_rows:
        key = r.get(args.key)
        survey_median = survey_by_key.get(key)
        try:
            pay = float(str(r.get("base_salary", "")).replace(",", ""))
        except (ValueError, TypeError):
            pay = None
        if survey_median is None or pay is None:
            unmatched.append({"employee_id": r.get("employee_id"), args.key: key})
            continue
        out_rows.append({"employee_id": r.get("employee_id"), args.key: key,
                          "base_salary": pay, "survey_median": survey_median,
                          "market_ratio": round(pay / survey_median, 3) if survey_median else None})

    if not out_rows:
        sys.exit(f"Ningún empleado emparejó con la encuesta por '{args.key}'. Revisa que los "
                  f"valores de '{args.key}' coincidan exactamente entre ambos archivos.")

    ratios = [r["market_ratio"] for r in out_rows if r["market_ratio"] is not None]
    report = {
        "method": "job_pricing_group_of_jobs",
        "key_column": args.key,
        "n_employees_matched": len(out_rows),
        "n_unmatched": len(unmatched),
        "market_ratio_summary": {
            "min": min(ratios), "median": st.median(ratios), "max": max(ratios),
        } if ratios else None,
        "below_market": [r for r in out_rows if r["market_ratio"] and r["market_ratio"] < 0.90],
        "above_market": [r for r in out_rows if r["market_ratio"] and r["market_ratio"] > 1.10],
        "unmatched": unmatched,
        "detail": out_rows,
    }
    print(json.dumps(report, indent=2))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)

    p_fit = sub.add_parser("fit", help="ajusta un modelo de mercado a puntos de encuesta")
    p_fit.add_argument("survey")
    p_fit.add_argument("--x", required=True, help="columna x (p. ej. puntos de evaluación de "
                        "puesto, años de experiencia, o ingresos de la empresa)")
    p_fit.add_argument("--y", required=True, help="columna y (mediana de encuesta ya llevada a "
                        "una fecha común: envejece cada encuesta a la misma fecha antes de "
                        "combinarlas)")
    p_fit.add_argument("--model", required=True, choices=list(FITTERS))
    p_fit.add_argument("--out", help="guardar el modelo ajustado aquí, para usar con `compare`")
    p_fit.add_argument("--json", help="también escribir el reporte completo aquí")
    p_fit.set_defaults(func=cmd_fit)

    p_cmp = sub.add_parser("compare", help="compara pago de empleados contra un modelo ajustado")
    p_cmp.add_argument("employees")
    p_cmp.add_argument("--model", required=True, help="archivo de modelo producido por `fit --out`")
    p_cmp.add_argument("--x", required=True, help="misma columna x usada al ajustar el modelo")
    p_cmp.add_argument("--json")
    p_cmp.set_defaults(func=cmd_compare)

    p_jp = sub.add_parser("job-pricing", help="Job Pricing Market Model: Group of Jobs (sin curva)")
    p_jp.add_argument("employees")
    p_jp.add_argument("--survey", required=True, help="CSV con --key y --median-col por celda")
    p_jp.add_argument("--key", default="level", help="columna de emparejamiento (level, skill_level, ...)")
    p_jp.add_argument("--median-col", default="survey_median")
    p_jp.add_argument("--json")
    p_jp.set_defaults(func=cmd_job_pricing)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
