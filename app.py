"""Streamlit web interface for the Daily Meal Cost Calculator."""
from pathlib import Path
from datetime import date, datetime
import streamlit as st
import pandas as pd
from meal_calculator.storage import MealStorage, StorageError
from meal_calculator.logic import create_record, search_records, calculate_summary, build_markdown_report
from meal_calculator.validation import CATEGORIES
from meal_calculator.import_export import import_csv

BASE = Path(__file__).resolve().parent
storage = MealStorage(BASE / "data")
st.set_page_config(page_title="Daily Meal Cost Calculator", page_icon="🍽️", layout="wide")
st.title("🍽️ Daily Meal Cost Calculator")
st.caption("DataSpark Challenge · Project #64 · Food & Agriculture")
st.write("A local meal-cost utility for validated entry, reliable record keeping, searching and executive summaries.")

try:
    if "records" not in st.session_state: st.session_state.records = storage.load()
except StorageError as exc:
    st.error(f"Unable to load saved records: {exc}"); st.stop()

records = st.session_state.records
def save_rows(updated):
    storage.save(updated); st.session_state.records = updated

page = st.sidebar.radio("APPLICATION MENU", ["Dashboard","Add Meal","All Records","Search & Filter","Reports & Export","Bulk CSV Import"])
st.sidebar.metric("Saved meal entries", len(records))
st.sidebar.caption("CSV + JSON local persistence")

if page == "Dashboard":
    st.header("Executive Summary")
    s = calculate_summary(records)
    cols = st.columns(4)
    cols[0].metric("Total spending", f"₹{s['total_spending']:,.2f}")
    cols[1].metric("Recorded days", s["recorded_days"])
    cols[2].metric("Average / day", f"₹{s['average_per_day']:,.2f}")
    cols[3].metric("Today's spending", f"₹{s['today_spending']:,.2f}")
    st.metric("Average per entry", f"₹{s['average_per_entry']:,.2f}")
    if not records:
        st.info("No records yet. Add a meal record to begin.")
    else:
        c1,c2 = st.columns(2)
        with c1:
            st.subheader("Spending by category")
            st.bar_chart(pd.Series(s["category_totals"], dtype=float))
        with c2:
            st.subheader("Daily spending trend")
            st.line_chart(pd.Series(s["daily_totals"], dtype=float))
        st.subheader("Daily threshold status")
        limit = st.number_input("Daily budget threshold (₹)", min_value=1.0, value=300.0, step=25.0)
        exceeded = [(d,v) for d,v in s["daily_totals"].items() if v > limit]
        if exceeded:
            st.warning(f"{len(exceeded)} day(s) exceeded ₹{limit:,.2f}.")
            st.dataframe(pd.DataFrame(exceeded, columns=["Date","Daily total (₹)"]), use_container_width=True, hide_index=True)
        else: st.success("No recorded day exceeded the selected threshold.")
        st.subheader("Recent records")
        st.dataframe(pd.DataFrame(sorted(records,key=lambda r:(r["date"],r["id"]),reverse=True)[:10]), use_container_width=True, hide_index=True)

elif page == "Add Meal":
    st.header("Add a Meal Record")
    with st.form("add_meal_form", clear_on_submit=True):
        a,b = st.columns(2)
        with a:
            day = st.date_input("Meal date", date.today())
            item = st.text_input("Food item *", max_chars=80, placeholder="e.g. Vegetable biryani")
            category = st.selectbox("Category", CATEGORIES)
            notes = st.text_area("Notes (optional)", max_chars=250)
        with b:
            quantity = st.number_input("Quantity", min_value=0.001, max_value=100000.0, value=1.0, step=0.5, format="%.3f")
            price = st.number_input("Unit price (₹)", min_value=0.0, max_value=10000000.0, value=50.0, step=5.0)
            st.info(f"Estimated cost: ₹{quantity*price:,.2f}")
        submit = st.form_submit_button("Save meal record", type="primary", use_container_width=True)
    if submit:
        try:
            row = create_record(records, day, item, category, quantity, price, notes)
            save_rows(records + [row])
            st.success(f"Saved {row['item']} for ₹{row['total_cost']:.2f}.")
            st.rerun()
        except ValueError as exc: st.error(str(exc))

elif page == "All Records":
    st.header("All Meal Records")
    if records:
        table = pd.DataFrame(records).sort_values(["date","id"], ascending=[False,False])
        st.dataframe(table, use_container_width=True, hide_index=True)
        st.download_button("Download records CSV", table.to_csv(index=False).encode("utf-8"), "meal_records.csv", "text/csv")
        if st.button("Reload from local files"):
            st.session_state.records = storage.load(); st.rerun()
    else: st.info("No saved records.")

elif page == "Search & Filter":
    st.header("Record Query & Search")
    a,b = st.columns(2)
    keyword = a.text_input("Keyword in food item or notes")
    category = b.selectbox("Category", ["All",*CATEGORIES])
    use_range = st.checkbox("Apply date range")
    start = end = None
    if use_range:
        x,y = st.columns(2)
        start = x.date_input("From date", date.today())
        end = y.date_input("To date", date.today())
    if use_range and start > end: st.error("Start date cannot be after end date.")
    else:
        result = search_records(records, keyword, category, start, end)
        st.caption(f"{len(result)} matching record(s)")
        if result: st.dataframe(pd.DataFrame(result), use_container_width=True, hide_index=True)
        else: st.info("No records match these filters.")

elif page == "Reports & Export":
    st.header("Executive Report & Export")
    if not records: st.info("Add records to generate a report.")
    else:
        report = build_markdown_report(records, calculate_summary(records), datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        st.text_area("Report preview", report, height=350)
        st.download_button("Export Markdown", report, "meal_summary.md", "text/markdown")
        st.download_button("Export plain text", report, "meal_summary.txt", "text/plain")
        st.download_button("Export CSV", pd.DataFrame(records).to_csv(index=False), "meal_report.csv", "text/csv")

elif page == "Bulk CSV Import":
    st.header("Bulk Dataset Import")
    st.write("Required columns: date, item, category, quantity, unit_price. Optional: notes.")
    uploaded = st.file_uploader("Select CSV dataset", type=["csv"])
    if uploaded and st.button("Validate and import", type="primary"):
        temp = BASE / "data" / "_import_temp.csv"
        try:
            temp.write_bytes(uploaded.getvalue())
            updated,count,errors = import_csv(temp, records)
            save_rows(updated)
            st.success(f"Imported {count} valid record(s).")
            if errors:
                st.warning(f"{len(errors)} row(s) were rejected:")
                for err in errors: st.write("• " + err)
            st.rerun()
        except (OSError,ValueError) as exc: st.error(f"Import failed: {exc}")
        finally:
            if temp.exists(): temp.unlink()
st.sidebar.caption("Python 3.10+ · Streamlit · CSV / JSON")
