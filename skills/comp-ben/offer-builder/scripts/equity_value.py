#!/usr/bin/env python3
"""equity_value.py: proyecta el cronograma de vesting de una concesión de equity y su valor
presente, usando interés compuesto estándar (valor futuro/valor presente).

El SKILL.md de offer-builder es explícito: "el valor en papel del equity de una empresa privada
es un escenario, no una promesa". Este script hace ese escenario explícito y auditable en vez de
dejar que alguien diga "esto vale aproximadamente X" sin mostrar el supuesto de crecimiento
detrás. Cambia --annual-growth-pct y el resultado cambia con él, a la vista de todos.

Uso:
    python equity_value.py --shares 4000 --price-per-share 10.00 --vesting-years 4 \
        --cliff-months 12 [--annual-growth-pct 0] [--discount-rate-pct 0] [--json out.json]

- --annual-growth-pct: supuesto de crecimiento anual del valor por acción (0 = sin supuesto de
  crecimiento, el escenario más conservador y el que deberías usar por defecto salvo que el
  usuario pida explícitamente modelar un escenario optimista).
- --discount-rate-pct: si se quiere el valor PRESENTE del total en vez de solo el valor
  proyectado a futuro de cada tramo.

Vesting: cliff de --cliff-months, luego el resto en tramos mensuales iguales hasta completar
--vesting-years (el esquema más común en startups; si la empresa usa otro esquema, dilo y
ajusta --schedule).

Parte de rhstack (https://github.com/luisgalvan/rhstack), creado por Luis Galvan. Licencia MIT.
"""
import argparse
import json


def future_value(present_value, annual_rate_pct, years):
    """VF = VP * (1 + r)^t: interés compuesto."""
    return present_value * (1 + annual_rate_pct / 100) ** years


def present_value(future_value_, annual_rate_pct, years):
    """VP = VF / (1 + r)^t."""
    return future_value_ / (1 + annual_rate_pct / 100) ** years


def vesting_schedule(total_shares, cliff_months, vesting_years):
    """Cliff + tramos mensuales iguales. Devuelve lista de (mes, shares_vested_ese_mes)."""
    total_months = int(round(vesting_years * 12))
    if cliff_months >= total_months:
        return [(cliff_months, total_shares)]
    cliff_shares = round(total_shares * cliff_months / total_months)
    remaining_months = total_months - cliff_months
    remaining_shares = total_shares - cliff_shares
    per_month = remaining_shares / remaining_months
    schedule = [(cliff_months, cliff_shares)]
    accumulated = cliff_shares
    for m in range(cliff_months + 1, total_months + 1):
        this_month = round(per_month) if m < total_months else remaining_shares - (accumulated - cliff_shares)
        accumulated += this_month
        schedule.append((m, this_month))
    return schedule


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--shares", type=float, required=True)
    ap.add_argument("--price-per-share", type=float, required=True,
                     help="valor actual por acción: dato del usuario (última ronda/409A), "
                          "nunca inventado por el script")
    ap.add_argument("--vesting-years", type=float, default=4.0)
    ap.add_argument("--cliff-months", type=int, default=12)
    ap.add_argument("--annual-growth-pct", type=float, default=0.0,
                     help="supuesto de crecimiento anual del precio por acción; 0 = escenario "
                          "conservador por defecto")
    ap.add_argument("--discount-rate-pct", type=float, default=0.0,
                     help="si se quiere el valor presente del total en vez del valor nominal proyectado")
    ap.add_argument("--json")
    args = ap.parse_args()

    schedule = vesting_schedule(args.shares, args.cliff_months, args.vesting_years)
    total_current_value = args.shares * args.price_per_share

    tranches = []
    total_projected = 0.0
    total_present = 0.0
    for month, shares in schedule:
        years = month / 12
        price_at_vest = future_value(args.price_per_share, args.annual_growth_pct, years)
        value_at_vest = shares * price_at_vest
        value_today = present_value(value_at_vest, args.discount_rate_pct, years) if args.discount_rate_pct else value_at_vest
        total_projected += value_at_vest
        total_present += value_today
        tranches.append({
            "month": month, "shares_vesting": shares,
            "assumed_price_per_share_at_vest": round(price_at_vest, 4),
            "value_at_vest": round(value_at_vest, 2),
            "value_in_today_dollars": round(value_today, 2),
        })

    report = {
        "total_shares": args.shares,
        "current_price_per_share": args.price_per_share,
        "total_current_value_no_growth_assumption": round(total_current_value, 2),
        "assumptions": {
            "annual_growth_pct": args.annual_growth_pct,
            "discount_rate_pct": args.discount_rate_pct,
            "cliff_months": args.cliff_months,
            "vesting_years": args.vesting_years,
        },
        "total_projected_value_at_vest_dates": round(total_projected, 2),
        "total_value_in_today_dollars": round(total_present, 2),
        "schedule": tranches,
        "note": "Estos números son un escenario bajo los supuestos de arriba, no una promesa. "
                "Si annual_growth_pct > 0, cada centavo por encima del valor actual depende de "
                "ese supuesto; dilo explícitamente al candidato/empleado, nunca lo presentes "
                "como un valor garantizado.",
    }
    print(json.dumps(report, indent=2))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)


if __name__ == "__main__":
    main()
