"""Read the supplied CSV and print verified totals. No writes, packages, or network."""
import csv
import sys
from decimal import Decimal
from pathlib import Path
from collections import defaultdict

def analyze(path):
    with path.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        required = {"Date", "Location", "Product", "Category", "Units", "UnitPrice", "Discount", "NetSales"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("Missing required CSV columns")
        rows = list(reader)
    if not rows:
        raise ValueError("No data rows")
    units_total = 0
    sales_total = Decimal("0")
    products = defaultdict(lambda: Decimal("0"))
    for number, row in enumerate(rows, 2):
        units = int(row["Units"])
        price, discount, sales = (Decimal(row[k]) for k in ("UnitPrice", "Discount", "NetSales"))
        if units <= 0 or not all(x.is_finite() and x >= 0 for x in (price, discount, sales)):
            raise ValueError(f"Invalid numeric value on CSV line {number}")
        if units * price - discount != sales:
            raise ValueError(f"NetSales equation mismatch on CSV line {number}")
        if not all(row[k].strip() for k in ("Date", "Location", "Product", "Category")):
            raise ValueError(f"Missing label on CSV line {number}")
        units_total += units
        sales_total += sales
        products[row["Product"]] += sales
    print(f"Data rows: {len(rows)}")
    print(f"Total units: {units_total}")
    print(f"Total net sales: ${sales_total:.2f}")
    print("Net sales by product:")
    for product, value in sorted(products.items(), key=lambda item: (-item[1], item[0])):
        print(f"  {product}: ${value:.2f}")
    highest = max(products.values())
    print("Highest net-sales product(s): " + ", ".join(sorted(k for k, v in products.items() if v == highest)))
    print("All row equations validated.")

if __name__ == "__main__":
    analyze(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("SmartBean_SalesSample.csv"))
