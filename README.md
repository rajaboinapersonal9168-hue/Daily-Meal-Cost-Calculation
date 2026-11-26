# Daily Meal Cost Calculator — Project #64

This Python project follows the supplied DataSpark Challenge brief. It includes both a **menu-driven terminal application** (explicitly required in the PDF) and a **Streamlit web interface**.

## Mandatory requirements mapped to implementation

| PDF requirement | Implementation |
|---|---|
| Interactive Terminal Interface | `main.py` menu: add, view, search, summary, export, import, exit |
| Defensive Input Validation | `meal_calculator/validation.py` and terminal input loops |
| Core Business Logic Engine | `meal_calculator/logic.py`: quantity × unit price and aggregation |
| Local Data Persistence | `meal_calculator/storage.py`: CSV + JSON read/write and fallback |
| Record Query & Search | Keyword, category and date-range filters in both interfaces |
| Executive Summary Generation | Totals, averages, today total, category/daily totals and threshold status |

## Additional features
- Markdown, TXT and CSV report exports
- Daily budget threshold warnings
- Streamlit GUI
- Bulk CSV import with row-by-row validation errors
- 40 sample records in CSV and JSON
- Modular code and automated unit tests

## Project structure

```text
Daily_Meal_Cost_Calculator_Pro/
├── app.py
├── main.py
├── requirements.txt
├── README.md
├── PROJECT_CHECKLIST.md
├── meal_calculator/
│   ├── __init__.py
│   ├── validation.py
│   ├── storage.py
│   ├── logic.py
│   └── import_export.py
├── data/
│   ├── meals.csv
│   └── meals.json
├── reports/
└── tests/
    └── test_meal_calculator.py
```

## Install

Use Python 3.10 or newer. Open a terminal in this project folder:

```bash
python -m pip install -r requirements.txt
```

## Run Streamlit website

```bash
python -m streamlit run app.py
```

Open the local URL printed in the terminal (normally `http://localhost:8501`).

## Run terminal application

```bash
python main.py
```

This launches the required interactive command-prompt menu.

## Run automated tests

```bash
python -m unittest discover -s tests -v
```

## Bulk CSV format

Required headers: `date,item,category,quantity,unit_price`. Optional: `notes`.

```csv
date,item,category,quantity,unit_price,notes
2026-11-25,Idli,Breakfast,2,15,Campus breakfast
2026-11-25,Veg thali,Lunch,1,90,College lunch
```

Invalid rows are rejected with row-numbered error messages; valid rows are imported.

## Persistence

The app initializes `data/meals.csv` and `data/meals.json` automatically and saves every record to both files. CSV is the primary read source, with JSON fallback if CSV cannot be read. Keep the folder structure intact.

## Suggested demo sequence

1. Start Streamlit and show the dashboard.
2. Add a meal and show the calculated amount.
3. Try a blank item to demonstrate validation.
4. Search by item keyword and category.
5. Show totals, averages, charts and budget warning.
6. Export Markdown, TXT and CSV.
7. Restart and verify saved records remain.
8. Run `python main.py` to show the required terminal menu.
9. Optionally import a sample CSV to show bulk import validation.

**Scoring note:** The implementation is aligned to the requirements visible in the supplied PDF, but a third-party evaluator's exact score cannot be guaranteed.
