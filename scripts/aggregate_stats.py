import csv
from collections import defaultdict

def main():
    by_rating = defaultdict(list)
    by_bucket = defaultdict(list)
    by_cell = defaultdict(list)
    zero_increases = []

    with open("examples/merit-increases.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            pct = float(r["%"])
            curr = float(r["current"])
            prop = float(r["proposed"])
            inc_amt = prop - curr
            cell = r["cell"]
            rating, bucket = cell.split(" / ")
            
            by_rating[rating].append((pct, inc_amt))
            by_bucket[bucket].append((pct, inc_amt))
            by_cell[cell].append((pct, inc_amt))
            
            if inc_amt == 0.0:
                zero_increases.append(r["employee_id"])

    print("=== STATISTICS BY RATING ===")
    for rating, val in sorted(by_rating.items()):
        pcts = [v[0] for v in val]
        amts = [v[1] for v in val]
        avg_pct = sum(pcts) / len(pcts)
        total_amt = sum(amts)
        print(f"{rating}: count={len(val)}, avg_pct={avg_pct:.2f}%, total_increase_cost={total_amt:.2f}")

    print("\n=== STATISTICS BY BUCKET ===")
    for bucket, val in sorted(by_bucket.items()):
        pcts = [v[0] for v in val]
        amts = [v[1] for v in val]
        avg_pct = sum(pcts) / len(pcts)
        total_amt = sum(amts)
        print(f"{bucket}: count={len(val)}, avg_pct={avg_pct:.2f}%, total_increase_cost={total_amt:.2f}")

    print("\n=== STATISTICS BY CELL ===")
    for cell, val in sorted(by_cell.items()):
        pcts = [v[0] for v in val]
        amts = [v[1] for v in val]
        avg_pct = sum(pcts) / len(pcts)
        total_amt = sum(amts)
        print(f"{cell}: count={len(val)}, avg_pct={avg_pct:.2f}%, total_increase_cost={total_amt:.2f}")

    print(f"\nZero increase count: {len(zero_increases)}")
    print(f"Zero increase employees: {', '.join(zero_increases)}")

if __name__ == "__main__":
    main()
