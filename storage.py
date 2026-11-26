import csv, json, os, tempfile
from pathlib import Path

FIELDS = ["id", "date", "item", "category", "quantity", "unit_price", "total_cost", "notes"]

class StorageError(Exception):
    pass

class MealStorage:
    def __init__(self, data_dir=None):
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).resolve().parent.parent / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.csv_path = self.data_dir / "meals.csv"
        self.json_path = self.data_dir / "meals.json"
        self.initialize()

    def initialize(self):
        if not self.csv_path.exists():
            self._write_csv([])
        if not self.json_path.exists():
            self._write_json([])

    def _write_csv(self, records):
        fd, name = tempfile.mkstemp(prefix="meals_", suffix=".csv", dir=self.data_dir)
        try:
            with os.fdopen(fd, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=FIELDS)
                writer.writeheader()
                writer.writerows([{k: r.get(k, "") for k in FIELDS} for r in records])
            os.replace(name, self.csv_path)
        finally:
            if os.path.exists(name): os.remove(name)

    def _write_json(self, records):
        fd, name = tempfile.mkstemp(prefix="meals_", suffix=".json", dir=self.data_dir)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2, ensure_ascii=False)
            os.replace(name, self.json_path)
        finally:
            if os.path.exists(name): os.remove(name)

    def _normalize(self, row):
        try:
            record = {
                "id": int(row["id"]), "date": str(row["date"]),
                "item": str(row["item"]).strip(), "category": str(row["category"]).strip(),
                "quantity": round(float(row["quantity"]), 3),
                "unit_price": round(float(row["unit_price"]), 2),
                "total_cost": round(float(row["total_cost"]), 2),
                "notes": str(row.get("notes", "")).strip()
            }
            if record["id"] <= 0 or not record["item"] or record["quantity"] <= 0:
                raise ValueError("ID, item and quantity must be valid.")
            if record["unit_price"] < 0 or record["total_cost"] < 0:
                raise ValueError("Price and total cannot be negative.")
            return record
        except (KeyError, TypeError, ValueError) as exc:
            raise StorageError(f"Invalid meal record: {exc}") from exc

    def save(self, records):
        normalized = [self._normalize(r) for r in records]
        self._write_csv(normalized)
        self._write_json(normalized)

    def load(self):
        try:
            with self.csv_path.open("r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                if not reader.fieldnames or not set(FIELDS).issubset(reader.fieldnames):
                    raise StorageError("CSV schema is missing required columns.")
                return [self._normalize(r) for r in reader]
        except (OSError, csv.Error, UnicodeDecodeError, StorageError, ValueError):
            try:
                with self.json_path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                if not isinstance(data, list):
                    raise StorageError("JSON root must be a list.")
                return [self._normalize(r) for r in data]
            except FileNotFoundError:
                return []
            except (OSError, json.JSONDecodeError, TypeError, StorageError, ValueError) as exc:
                raise StorageError(f"Could not load CSV or JSON data: {exc}") from exc
