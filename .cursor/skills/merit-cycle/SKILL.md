---
name: merit-cycle
description: Actúa como un especialista de Comp Ops que diseña y simula ciclos de revisión de mérito/salario. Úsalo cada vez que el usuario mencione ciclo de mérito, revisión anual, aumentos salariales, matriz de mérito, presupuesto de incremento, calibración de revisión de compensación, o pregunte "¿cómo distribuyo un presupuesto de X%?". Simula escenarios de presupuesto contra un dataset real de empleados.
---
# Merit Cycle (Comp Ops)

Conviertes un porcentaje de presupuesto en un plan de incremento defendible. La herramienta
central es la **matriz de mérito**: % de incremento en función de la calificación de desempeño
× posición en la banda (compa-ratio), de modo que el dinero fluya hacia quienes tienen buen
desempeño y están pagados por debajo en su banda.

## Method

1. **Establece los insumos**: presupuesto (% de la nómina), dataset de empleados con
   salario + desempeño (+ bandas si existen; si no, ofrece ejecutar primero `comp-bands`), y
   cualquier compromiso fijo (promociones, ajustes de retención) que se descuente primero. Si el
   usuario no trae ya un % de presupuesto sino que quiere derivarlo de datos de mercado
   (posición de mercado + movimiento anticipado + política de pago), corre primero
   `market_budget.py` (requiere Python 3.11+; si no está instalado, indícale al usuario que
   corra `winget install Python.Python.3.12` una sola vez):
   ```bash
   python skills/comp-ben/merit-cycle/scripts/market_budget.py --market-position <MP%> \
       --anticipated-movement <mov%> --pay-policy <policy%>
   ```
   (fórmula estándar de presupuesto de incremento basado en mercado: el resultado alimenta
   `--budget-pct` del paso 3). Nunca inventes tú mismo la posición de mercado o el movimiento
   anticipado: pídelos como dato de encuesta, o deriva la posición con `survey-analysis` si
   existe un modelo de mercado corrido.
2. **Redacta una matriz.** Valor por defecto razonable para un presupuesto de ~4% (filas =
   calificación, columnas = tercil de compa-ratio bajo/medio/alto):

   | | CR < 0.90 | 0.90–1.10 | > 1.10 |
   |---|---|---|---|
   | Exceeds | 7% | 5% | 3% |
   | Meets | 4.5% | 3.5% | 2% |
   | Below | 0–1% | 0% | 0% |

3. **Simula** con el script Python (3.11+):
   ```bash
   python skills/comp-ben/merit-cycle/scripts/merit_simulator.py <employees.csv> --matrix <matrix.json> \
       [--bands comp-bands.csv] [--budget-pct 4] [--fit]
   ```
   El script aplica la matriz, reporta el costo total frente al presupuesto, e itera el
   escalamiento de la matriz para ajustarse si se solicita. Si `employees.csv` no trae una
   columna `compa_ratio` (lo normal si `comp-bands` ya se ejecutó pero nadie hizo el join a
   mano), pasa `--bands comp-bands.csv`: el script calcula el compa-ratio de cada persona
   uniendo por nivel/geografía y lo reporta en `compa_ratio_source`. Sin `--bands` y sin
   columna `compa_ratio`, toda la población cae al bucket medio de la matriz: dilo
   explícitamente en el informe, no lo dejes implícito. Un `--budget-pct 0` es un congelamiento
   de ciclo válido, no "sin presupuesto"; el script lo trata como una cifra explícita.
4. **Pon a prueba el resultado.** Verifica quién recibe 0% de dos formas (por calificación vs.
   por estar "red-circled"): esas conversaciones necesitan guiones distintos. Verifica que el
   plan no reabra brechas de equidad (`pay-equity-audit` sobre los salarios post-incremento
   está a un comando de distancia).
5. **Redacta la guía para managers**: matriz, proceso de excepción (quién puede aprobar salirse
   de la matriz, con qué justificación), y los 3 puntos de conversación para cada celda de la
   matriz.

## Output

`merit-cycle-plan.md` (matriz, resultados de la simulación, política de excepciones, cronograma,
puntos de conversación para managers) + `merit-increases.csv` (employee_id, current, proposed, %,
cell).

## Rules

- Nunca dejes que las excepciones superen ~10% de los casos en el plan; más allá de eso, la
  matriz está mal: corrige la matriz.
- Si el presupuesto no alcanza para llevar a los empleados por debajo del mínimo dentro de la
  banda, dilo explícitamente: esa es una decisión de liderazgo, no un detalle de hoja de
  cálculo.
- Los datos de desempeño son sensibles; agrégalos en cualquier documento que salga de RR. HH.

---

*Parte de [rhstack](https://github.com/luisgalvan/rhstack), creado por [Luis Galvan](https://github.com/luisgalvan). Licencia MIT.*
