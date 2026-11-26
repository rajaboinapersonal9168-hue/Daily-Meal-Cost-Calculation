from datetime import date

CATEGORIES = ("Breakfast", "Lunch", "Dinner", "Snacks", "Beverages", "Other")

def validate_text(value, field_name="Value", max_length=100):
    value = str(value).strip()
    if not value:
        raise ValueError(f"{field_name} cannot be blank.")
    if len(value) > max_length:
        raise ValueError(f"{field_name} must not exceed {max_length} characters.")
    return value

def validate_quantity(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError("Quantity must be a valid number.")
    if not 0 < number <= 100000:
        raise ValueError("Quantity must be greater than zero and no more than 100000.")
    return round(number, 3)

def validate_price(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError("Unit price must be a valid number.")
    if not 0 <= number <= 10000000:
        raise ValueError("Unit price must be between 0 and 10000000.")
    return round(number, 2)

def validate_category(value):
    value = validate_text(value, "Category", 30).title()
    if value not in CATEGORIES:
        raise ValueError("Choose a valid category: " + ", ".join(CATEGORIES))
    return value

def validate_date(value):
    if isinstance(value, date):
        return value.isoformat()
    try:
        return date.fromisoformat(str(value).strip()).isoformat()
    except (TypeError, ValueError):
        raise ValueError("Date must be a valid date in YYYY-MM-DD format.")
