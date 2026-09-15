import csv

def get_bucket_label(cr):
    if cr == "":
        return "Mid"
    cr = float(cr)
    if cr < 0.90:
        return "Low"
    elif cr > 1.10:
        return "High"
    return "Mid"

def main():
    rows = []
    with open("examples/merit_increases.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            cr = r["compa_ratio"]
            bucket = get_bucket_label(cr)
            cell = f"{r['performance']} / {bucket}"
            
            rows.append({
                "employee_id": r["employee_id"],
                "current": float(r["base_salary"]),
                "proposed": float(r["new_salary"]),
                "%": float(r["increase_pct"]),
                "cell": cell
            })
            
    with open("examples/merit-increases.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["employee_id", "current", "proposed", "%", "cell"])
        writer.writeheader()
        writer.writerows(rows)
    print("Successfully wrote examples/merit-increases.csv")

if __name__ == "__main__":
    main()
