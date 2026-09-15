import csv

def main():
    # Read comp-bands
    bands = {}
    with open("comp-bands.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            bands[row["level"]] = float(row["band_mid"])

    # Read sample employees and add compa_ratio
    updated_rows = []
    with open("examples/sample_employees.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames + ["compa_ratio"]
        for row in reader:
            level = row["level"]
            salary = float(row["base_salary"])
            if level in bands:
                row["compa_ratio"] = round(salary / bands[level], 3)
            else:
                row["compa_ratio"] = ""
            updated_rows.append(row)

    # Write updated rows to a new file
    with open("examples/sample_employees_with_cr.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)
    print("Successfully added compa_ratio to examples/sample_employees_with_cr.csv")

if __name__ == "__main__":
    main()
