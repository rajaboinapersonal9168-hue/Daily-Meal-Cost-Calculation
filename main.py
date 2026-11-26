"""Menu-driven terminal application explicitly required by the SRS."""
from datetime import date, datetime
from pathlib import Path
from meal_calculator.storage import MealStorage, StorageError
from meal_calculator.logic import create_record, search_records, calculate_summary, build_markdown_report
from meal_calculator.validation import CATEGORIES
from meal_calculator.import_export import import_csv, export_csv, export_text

BASE = Path(__file__).resolve().parent
storage = MealStorage(BASE / "data")

def ask_text(prompt):
    while True:
        value = input(prompt).strip()
        if value: return value
        print("Input cannot be blank. Try again.")

def ask_date():
    while True:
        value = input(f"Meal date YYYY-MM-DD [Enter for {date.today().isoformat()}]: ").strip()
        if not value: return date.today().isoformat()
        try: return date.fromisoformat(value).isoformat()
        except ValueError: print("Enter a valid date in YYYY-MM-DD format.")

def ask_number(prompt, allow_zero=False):
    while True:
        try:
            value = float(input(prompt).strip())
            if value < 0 or (value == 0 and not allow_zero): raise ValueError
            return value
        except ValueError: print("Enter a valid " + ("non-negative" if allow_zero else "positive") + " number.")

def show_records(rows):
    if not rows:
        print("No matching records found."); return
    print("-" * 105)
    print(f"{'ID':<5}{'DATE':<13}{'ITEM':<23}{'CATEGORY':<14}{'QTY':>8}{'UNIT ₹':>12}{'TOTAL ₹':>13}")
    print("-" * 105)
    for r in rows:
        print(f"{r['id']:<5}{r['date']:<13}{r['item'][:21]:<23}{r['category']:<14}{r['quantity']:>8.2f}{r['unit_price']:>12.2f}{r['total_cost']:>13.2f}")
    print("-" * 105)

def add_record(rows):
    try:
        print("\\nADD MEAL RECORD")
        day, item = ask_date(), ask_text("Food item: ")
        print("Categories:", ", ".join(CATEGORIES))
        category = ask_text("Category: ").title()
        qty = ask_number("Quantity: ")
        price = ask_number("Unit price (₹): ", allow_zero=True)
        notes = input("Notes (optional): ").strip()
        record = create_record(rows, day, item, category, qty, price, notes)
        rows.append(record); storage.save(rows)
        print(f"Saved. Calculated cost = ₹{record['total_cost']:.2f}")
    except ValueError as exc: print("Validation error:", exc)

def summary_screen(rows):
    s = calculate_summary(rows)
    print("\\nEXECUTIVE SUMMARY")
    for label, key in [("Total entries","entry_count"),("Recorded days","recorded_days")]:
        print(f"{label}: {s[key]}")
    for label, key in [("Total spending","total_spending"),("Average per recorded day","average_per_day"),
                       ("Average per entry","average_per_entry"),("Today's spending","today_spending")]:
        print(f"{label}: ₹{s[key]:.2f}")
    print("\\nCategory totals:")
    for k,v in s["category_totals"].items(): print(f"  {k}: ₹{v:.2f}")
    print("\\nDaily totals:")
    for k,v in s["daily_totals"].items(): print(f"  {k}: ₹{v:.2f}")
    if rows:
        limit = ask_number("Daily threshold in ₹ (0 to skip): ", allow_zero=True)
        if limit:
            over = [(d,v) for d,v in s["daily_totals"].items() if v > limit]
            if over:
                print("WARNING - threshold exceeded:")
                for d,v in over: print(f"  {d}: ₹{v:.2f}")
            else: print("No recorded day exceeded the threshold.")

def search_screen(rows):
    keyword = input("Keyword in item/notes (optional): ").strip()
    category = input("Category or All (default All): ").strip().title() or "All"
    if category != "All" and category not in CATEGORIES:
        print("Invalid category; category filter ignored."); category = "All"
    start = input("Start date YYYY-MM-DD (optional): ").strip() or None
    end = input("End date YYYY-MM-DD (optional): ").strip() or None
    try:
        if start: date.fromisoformat(start)
        if end: date.fromisoformat(end)
        if start and end and start > end: raise ValueError("Start date is after end date.")
        show_records(search_records(rows, keyword, category, start, end))
    except ValueError as exc: print("Date filter error:", exc)

def export_reports(rows):
    if not rows: print("No records to export."); return
    report_dir = BASE / "reports"; report_dir.mkdir(exist_ok=True)
    report = build_markdown_report(rows, calculate_summary(rows), datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    export_csv(rows, report_dir / "meal_report.csv")
    export_text(report, report_dir / "meal_summary.md")
    export_text(report, report_dir / "meal_summary.txt")
    print("Saved CSV, Markdown and TXT reports in reports/.")

def bulk_import(rows):
    path = input("CSV file path: ").strip().strip('"')
    try:
        updated, count, errors = import_csv(path, rows)
        storage.save(updated); rows[:] = updated
        print(f"Imported {count} valid row(s).")
        for error in errors: print("Rejected:", error)
    except (OSError, ValueError) as exc: print("Import failed:", exc)

def main():
    print("="*58 + "\\n DAILY MEAL COST CALCULATOR | DataSpark Project #64\\n" + "="*58)
    try: rows = storage.load()
    except StorageError as exc: print("Storage warning:", exc); rows = []
    actions = {
        "1": ("Add meal record", lambda: add_record(rows)),
        "2": ("View all records", lambda: show_records(rows)),
        "3": ("Search and filter records", lambda: search_screen(rows)),
        "4": ("Executive summary", lambda: summary_screen(rows)),
        "5": ("Export CSV / Markdown / TXT reports", lambda: export_reports(rows)),
        "6": ("Bulk CSV import", lambda: bulk_import(rows))
    }
    while True:
        print("\\nMAIN MENU")
        for key,(label,_) in actions.items(): print(f"{key}. {label}")
        print("0. Save and Exit")
        choice = input("Choose an option: ").strip()
        if choice == "0":
            storage.save(rows); print("All records saved. Goodbye!"); break
        if choice in actions:
            try: actions[choice][1]()
            except (EOFError, KeyboardInterrupt): print("\\nReturning to menu.")
        else: print("Invalid option. Enter 0 to 6.")

if __name__ == "__main__": main()
