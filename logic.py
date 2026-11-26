from collections import defaultdict
from datetime import date
from .validation import validate_text, validate_quantity, validate_price, validate_category, validate_date

def create_record(records, meal_date, item, category, quantity, unit_price, notes=""):
    clean_item = validate_text(item, "Food item", 80)
    clean_category = validate_category(category)
    clean_date = validate_date(meal_date)
    qty, price = validate_quantity(quantity), validate_price(unit_price)
    clean_notes = str(notes).strip()
    if len(clean_notes) > 250:
        raise ValueError("Notes must not exceed 250 characters.")
    new_id = max((int(r["id"]) for r in records), default=0) + 1
    return {"id": new_id, "date": clean_date, "item": clean_item, "category": clean_category,
            "quantity": qty, "unit_price": price, "total_cost": round(qty * price, 2), "notes": clean_notes}

def search_records(records, keyword="", category="All", start_date=None, end_date=None):
    result, needle = [], str(keyword).strip().casefold()
    for row in records:
        if needle and needle not in row["item"].casefold() and needle not in row.get("notes", "").casefold():
            continue
        if category != "All" and row["category"] != category:
            continue
        if start_date and row["date"] < str(start_date): continue
        if end_date and row["date"] > str(end_date): continue
        result.append(row)
    return result

def calculate_summary(records, today=None):
    today = today.isoformat() if hasattr(today, "isoformat") else (str(today) if today else date.today().isoformat())
    daily, categories = defaultdict(float), defaultdict(float)
    for r in records:
        daily[r["date"]] += float(r["total_cost"])
        categories[r["category"]] += float(r["total_cost"])
    total, days = sum(float(r["total_cost"]) for r in records), len(daily)
    return {
        "entry_count": len(records), "recorded_days": days, "total_spending": round(total, 2),
        "average_per_day": round(total / days, 2) if days else 0.0,
        "average_per_entry": round(total / len(records), 2) if records else 0.0,
        "today_spending": round(daily.get(today, 0.0), 2),
        "daily_totals": {k: round(v, 2) for k, v in sorted(daily.items())},
        "category_totals": {k: round(v, 2) for k, v in sorted(categories.items(), key=lambda x: (-x[1], x[0]))}
    }

def build_markdown_report(records, summary, generated_at):
    lines = ["# Daily Meal Cost Calculator - Executive Summary", "", f"Generated: {generated_at}", "",
             "## Key metrics", "", f"- Total entries: {summary['entry_count']}",
             f"- Recorded days: {summary['recorded_days']}", f"- Total spending: ₹{summary['total_spending']:.2f}",
             f"- Average per recorded day: ₹{summary['average_per_day']:.2f}",
             f"- Average per entry: ₹{summary['average_per_entry']:.2f}",
             f"- Today's spending: ₹{summary['today_spending']:.2f}", "", "## Spending by category", ""]
    lines += [f"- {k}: ₹{v:.2f}" for k, v in summary["category_totals"].items()] or ["- No records"]
    lines += ["", "## Daily totals", ""]
    lines += [f"- {k}: ₹{v:.2f}" for k, v in summary["daily_totals"].items()] or ["- No records"]
    lines += ["", "## Meal records", "", "| Date | Item | Category | Quantity | Unit price | Total |", "|---|---|---|---:|---:|---:|"]
    for r in records:
        lines.append(f"| {r['date']} | {r['item']} | {r['category']} | {r['quantity']} | ₹{r['unit_price']:.2f} | ₹{r['total_cost']:.2f} |")
    return "\n".join(lines) + "\n"
