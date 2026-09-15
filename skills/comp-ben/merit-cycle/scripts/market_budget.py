#!/usr/bin/env python3
"""market_budget.py: deriva un presupuesto de incremento salarial basado en mercado, con la
fórmula estándar de compensación, en vez de que el usuario invente el % a mano.

Dos pasos:

1. Presupuesto INICIAL ("catch-up/fall-back") a partir de la posición de mercado (MP%, cuánto
   se está pagando por encima/debajo del mercado hoy):

       SIB% = (-MP%) / (100% + MP%)

   No es simplemente "-MP%": si estás 4% por debajo del mercado, necesitas un incremento de
   4.17%, no de 4.0%, porque el 4% de diferencia se calculó sobre una base más chica (la tuya),
   no sobre la base de mercado a la que quieres llegar.

2. Presupuesto FINAL = catch-up (el SIB% de arriba) + movimiento de mercado anticipado (%,
   dato externo, encuesta o proveedor de datos de mercado) + política de pago (%, decisión
   deliberada de pagar por encima/debajo de mercado; 0% = pagar exactamente al mercado). Los
   tres términos se SUMAN: la posición de mercado ya quedó absorbida en el catch-up, no se
   vuelve a sumar aparte (error común: sumar los cuatro números en vez de los tres).

Uso:
    python market_budget.py --market-position -4.0 --anticipated-movement 3.0 \
        --pay-policy 0.0 [--json out.json]

    # Si ya tienes el catch-up calculado por otro medio, sáltate la derivación:
    python market_budget.py --catch-up 4.2 --anticipated-movement 3.0 --pay-policy 0.0

Ninguno de estos números lo inventa el script: market-position y anticipated-movement deben
venir de una encuesta de mercado real (o de una corrida de market_model.py de la skill
survey-analysis); pay-policy es una decisión de la empresa que debe quedar documentada. Si
falta un dato, pásalo como 0.0 explícitamente y dilo en el informe; nunca lo asumas en silencio.

Parte de rhstack (https://github.com/luisgalvan/rhstack), creado por Luis Galvan. Licencia MIT.
"""
import argparse
import json


def catch_up_from_market_position(market_position_pct):
    """SIB% = (-MP%) / (100% + MP%): presupuesto inicial de incremento requerido para alcanzar
    el mercado, a partir de la posición de mercado actual. MP=0 siempre da SIB=0."""
    denominator = 100.0 + market_position_pct
    if denominator == 0:
        return None
    return round(-market_position_pct / denominator * 100, 2)


def recommend(catch_up_pct, anticipated_movement_pct, pay_policy_pct, market_position_pct=None):
    total = catch_up_pct + anticipated_movement_pct + pay_policy_pct
    out = {
        "catch_up_fall_back_pct": round(catch_up_pct, 2),
        "anticipated_market_movement_pct": anticipated_movement_pct,
        "pay_policy_pct": pay_policy_pct,
        "market_based_salary_increase_budget_recommendation_pct": round(total, 2),
    }
    if market_position_pct is not None:
        out["market_position_pct"] = market_position_pct
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mp_group = ap.add_mutually_exclusive_group(required=True)
    mp_group.add_argument("--market-position", type=float,
                           help="%% de distancia entre la nómina actual y la mediana de mercado "
                                "hoy (negativo = por debajo de mercado); el script deriva el "
                                "catch-up con la fórmula estándar de presupuesto de incremento "
                                "basado en mercado")
    mp_group.add_argument("--catch-up", type=float,
                           help="catch-up/fall-back ya calculado (%%), si no quieres que el "
                                "script lo derive de --market-position")
    ap.add_argument("--anticipated-movement", type=float, required=True,
                     help="%% esperado de movimiento del mercado en el próximo período")
    ap.add_argument("--pay-policy", type=float, default=0.0,
                     help="%% de política deliberada de pagar por encima/debajo de mercado (0 = a mercado)")
    ap.add_argument("--json")
    args = ap.parse_args()

    if args.catch_up is not None:
        catch_up, market_position = args.catch_up, None
    else:
        catch_up = catch_up_from_market_position(args.market_position)
        market_position = args.market_position
        if catch_up is None:
            raise SystemExit("market-position = -100% no tiene un catch-up definido "
                              "(división entre cero); revisa el dato de entrada.")

    report = recommend(catch_up, args.anticipated_movement, args.pay_policy, market_position)
    print(json.dumps(report, indent=2))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
    print("\nEsta cifra alimenta --budget-pct de merit_simulator.py. No es una recomendación "
          "de mercado por sí misma: market-position y anticipated-movement deben venir de datos "
          "de encuesta reales, y pay-policy de una decisión de política documentada, nunca de "
          "un supuesto del script.")


if __name__ == "__main__":
    main()
