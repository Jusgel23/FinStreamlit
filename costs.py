import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import calendar

st.set_page_config(page_title="Expense Calendar", page_icon="📅", layout="wide")

# --- Custom Styling ---
st.markdown("""
<style>
/* Layout + backgrounds */
[data-testid="stAppViewContainer"] {
    background: #f2f4f7;
}
[data-testid="stSidebar"] {
    background: #f7f8fa;
}
.block-container {
    background: #ffffff;
    padding-top: 1rem;
    padding-bottom: 3rem;
    border-radius: 10px;
    box-shadow: 0 0 8px rgba(0,0,0,0.05);
}

/* Titles and metric text in black */
h1, h2, h3, h4, h5, h6,
div[data-testid="stMetricLabel"],
div[data-testid="stMetricValue"],
.month-year-header {
    color: #000000 !important;
}

/* Metrics style */
div[data-testid="metric-container"] {
    background: #ffffff;
    border: 1px solid #dce0e5;
    border-radius: 10px;
    padding: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

/* Calendar cells */
.cal {width: 100%; border-collapse: collapse; table-layout: fixed;}
.cal th {
    background: #e9efff;
    padding: 8px;
    text-align: center;
    border: 1px solid #d1d9f0;
    font-weight: 600;
    font-size: 0.85rem;
    color: #1a2d63;
}
.cal td {
    vertical-align: top;
    height: 120px;
    border: 1px solid #e1e1e1;
    padding: 8px;
    background: #fff;
}
.daynum {
    font-weight: 600;
    margin-bottom: 4px;
    font-size: 0.85rem;
    color: #333;
}
.not-month {
    background: #f3f3f3;
    color: #aaa;
}

/* Highlight today's date */
.today {
    background: #dbeafe !important;  /* light blue */
    border: 2px solid #1e40af !important;
    font-weight: 700;
}

/* Pill styling */
.pill {
    display: block;
    padding: 6px 8px;
    margin-bottom: 6px;
    border-radius: 8px;
    font-size: 0.8rem;
    font-weight: 600;
    line-height: 1.2;
}
.expense {
    background: #ffd7d7;
    color: #7a0000;
    border: 1px solid #ffb3b3;
}
.income {
    background: #e5ffe6;
    color: #0b5a1d;
    border: 1px solid #c4f7c8;
}

/* Month-Year header style */
.month-year-header {
    font-size: 1.3rem;
    font-weight: 700;
    text-align: left;
    margin-top: 1rem;
    margin-bottom: 0.5rem;
    color: #000000 !important;
}
</style>
""", unsafe_allow_html=True)

st.title("📅 Expense & Cash-Out Calendar")

# ---------------- Fixed Parameters ----------------
CONDO_FEE = 294.19
MORTGAGE_PAYMENT = 1243.47
INVESTMENT_OUT = 750.0
SALARY_AMOUNT = 3200.0
SALARY_START = date(2025, 10, 28)
INVESTMENT_START = date(2025, 10, 14)

# ---------------- Helper Functions ----------------
def first_business_day(year, month):
    d = date(year, month, 1)
    while d.weekday() >= 5:  # Sat/Sun
        d += timedelta(days=1)
    return d

def mortgage_date(year, month):
    d = date(year, month, 26)
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return d

def generate_every_14_days(start_dt: date, end_dt: date):
    d = start_dt
    while d <= end_dt:
        yield d
        d += timedelta(days=14)

def build_transactions(year, month):
    first_of_month = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_of_month = date(year, month, last_day)

    txns = []

    # Condo
    txns.append({
        "date": first_business_day(year, month),
        "label": f"Condo ${CONDO_FEE:,.2f}",
        "amount": -CONDO_FEE
    })

    # Mortgage
    txns.append({
        "date": mortgage_date(year, month),
        "label": f"Mortgage ${MORTGAGE_PAYMENT:,.2f}",
        "amount": -MORTGAGE_PAYMENT
    })

    # Investment out every 14 days
    for d in generate_every_14_days(INVESTMENT_START, end_of_month):
        if first_of_month <= d <= end_of_month:
            txns.append({
                "date": d,
                "label": f"Investment out ${INVESTMENT_OUT:,.2f}",
                "amount": -INVESTMENT_OUT
            })

    # Salary every 14 days
    for d in generate_every_14_days(SALARY_START, end_of_month):
        if first_of_month <= d <= end_of_month:
            txns.append({
                "date": d,
                "label": f"Salary ${SALARY_AMOUNT:,.2f}",
                "amount": SALARY_AMOUNT
            })

    return txns

def render_calendar(year, month, transactions):
    cal = calendar.Calendar(firstweekday=6)
    month_weeks = cal.monthdatescalendar(year, month)
    tx_by_day = {}
    for t in transactions:
        tx_by_day.setdefault(t["date"], []).append(t)

    today = date.today()

    html = "<table class='cal'>"
    html += "<tr>" + "".join(f"<th>{d}</th>" for d in ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]) + "</tr>"
    for week in month_weeks:
        html += "<tr>"
        for day in week:
            classes = []
            if day.month != month:
                classes.append("not-month")
            elif day == today:
                classes.append("today")
            html += f"<td class='{' '.join(classes)}'>"
            html += f"<div class='daynum'>{day.day}</div>"
            for tx in tx_by_day.get(day, []):
                pill_class = "income" if tx["amount"] > 0 else "expense"
                html += f"<div class='pill {pill_class}'>{tx['label']}</div>"
            html += "</td>"
        html += "</tr>"
    html += "</table>"
    st.markdown(html, unsafe_allow_html=True)

# ---------------- Sidebar ----------------
st.sidebar.header("Calendar Settings")
months = list(calendar.month_name)[1:]
month_name = st.sidebar.selectbox("Month", months, index=datetime.today().month - 1)
month = months.index(month_name) + 1
year = datetime.today().year

# ---------------- Build & Display ----------------
txns = build_transactions(year, month)
total_expenses = sum(t["amount"] for t in txns if t["amount"] < 0)
total_income = sum(t["amount"] for t in txns if t["amount"] > 0)
net = total_income + total_expenses

c1, c2, c3 = st.columns(3)
c1.metric("Total Expenses", f"${abs(total_expenses):,.2f}")
c2.metric("Total Income", f"${total_income:,.2f}")
c3.metric("Net for Month", f"${net:,.2f}")

# Month + Year header in dark font
st.markdown(f"<h3 class='month-year-header'>{month_name} {year}</h3>", unsafe_allow_html=True)
render_calendar(year, month, txns)

# ---------------- Remove Legend ----------------
with st.expander("Show raw transactions"):
    st.dataframe(pd.DataFrame(txns))
