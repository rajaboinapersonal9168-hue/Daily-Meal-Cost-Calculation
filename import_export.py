import csv
from pathlib import Path
from .logic import create_record
from .storage import FIELDS

def import_csv(path, existing_records):
    accepted, errors, imported = list(existing_records), [], 0
    with Path(path).open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        required = {"date", "item", "category", "quantity", "unit_price"}
        if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
            raise ValueError("CSV must include date,item,category,quantity,unit_price; notes is optional.")
        for line_no, row in enumerate(reader, start=2):
            try:
                accepted.append(create_record(accepted, row.get("date"), row.get("item"), row.get("category"),
                                              row.get("quantity"), row.get("unit_price"), row.get("notes", "")))
                imported += 1
            except (ValueError, TypeError) as exc:
                errors.append(f"Row {line_no}: {exc}")
    return accepted, imported, errors

def export_csv(records, path):
    with Path(path).open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(records)

def export_text(text, path):
    Path(path).write_text(text, encoding="utf-8")
