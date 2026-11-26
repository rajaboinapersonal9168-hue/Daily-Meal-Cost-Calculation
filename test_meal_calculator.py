import tempfile, unittest
from pathlib import Path
from meal_calculator.logic import create_record, search_records, calculate_summary
from meal_calculator.storage import MealStorage

class MealTests(unittest.TestCase):
    def test_cost_calculation(self):
        r = create_record([], "2026-11-25", "Idli", "Breakfast", 2, 15)
        self.assertEqual(r["total_cost"], 30.0)
    def test_blank_item_rejected(self):
        with self.assertRaises(ValueError):
            create_record([], "2026-11-25", " ", "Breakfast", 1, 10)
    def test_zero_quantity_rejected(self):
        with self.assertRaises(ValueError):
            create_record([], "2026-11-25", "Tea", "Beverages", 0, 10)
    def test_negative_price_rejected(self):
        with self.assertRaises(ValueError):
            create_record([], "2026-11-25", "Tea", "Beverages", 1, -2)
    def test_search(self):
        rows=[create_record([], "2026-11-25", "Masala Dosa", "Breakfast", 1, 40)]
        self.assertEqual(len(search_records(rows,"dosa","Breakfast")),1)
        self.assertEqual(len(search_records(rows,"rice","Breakfast")),0)
    def test_summary(self):
        rows=[create_record([], "2026-11-25", "Idli", "Breakfast", 2, 15)]
        s=calculate_summary(rows,today="2026-11-25")
        self.assertEqual(s["total_spending"],30)
        self.assertEqual(s["average_per_day"],30)
        self.assertEqual(s["today_spending"],30)
    def test_csv_json_persistence(self):
        with tempfile.TemporaryDirectory() as tmp:
            store=MealStorage(tmp)
            rows=[create_record([], "2026-11-25", "Tea", "Beverages", 1, 10)]
            store.save(rows)
            self.assertEqual(store.load(),rows)
            self.assertTrue(Path(tmp,"meals.csv").exists())
            self.assertTrue(Path(tmp,"meals.json").exists())

if __name__ == "__main__": unittest.main()
