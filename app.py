import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="SmartMart Analytics", page_icon="📊", layout="wide")
st.title("📊 SmartMart Retail Sales Dashboard")
st.write("Explore revenue, profit, orders and sales trends.")

uploaded_file = st.file_uploader("Upload a SmartMart CSV file (optional)", type="csv")

@st.cache_data
def load_sample():
    return pd.read_csv("smartmart_retail_sales.csv")

try:
    df = pd.read_csv(uploaded_file) if uploaded_file is not None else load_sample()
    required = {"OrderID", "OrderDate", "City", "Category", "Revenue", "Profit", "DiscountPct"}
    missing = required - set(df.columns)
    if missing:
        st.error("Missing required columns: " + ", ".join(sorted(missing)))
        st.stop()
    df["OrderDate"] = pd.to_datetime(df["OrderDate"], errors="coerce")
    for col in ["Revenue", "Profit", "DiscountPct"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["OrderDate", "Revenue", "Profit", "DiscountPct"])
    if df.empty:
        st.warning("No valid records found in this file.")
        st.stop()
except Exception as exc:
    st.error(f"Unable to read the data: {exc}")
    st.stop()

cities = sorted(df["City"].dropna().unique().tolist())
categories = sorted(df["Category"].dropna().unique().tolist())
col_a, col_b = st.columns(2)
with col_a:
    selected_cities = st.multiselect("Cities", cities, default=cities)
with col_b:
    selected_categories = st.multiselect("Categories", categories, default=categories)

filtered = df[df["City"].isin(selected_cities) & df["Category"].isin(selected_categories)].copy()
if filtered.empty:
    st.info("No records match the selected filters. Select at least one city and category.")
    st.stop()

revenue = filtered["Revenue"].sum()
profit = filtered["Profit"].sum()
orders = filtered["OrderID"].nunique()
margin = (profit / revenue * 100) if revenue != 0 else 0
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Revenue", f"₹{revenue:,.0f}")
k2.metric("Total Profit", f"₹{profit:,.0f}")
k3.metric("Total Orders", f"{orders:,}")
k4.metric("Profit Margin", f"{margin:.1f}%")

monthly = filtered.groupby(pd.Grouper(key="OrderDate", freq="MS"), as_index=False)["Revenue"].sum()
category_sales = filtered.groupby("Category", as_index=False)["Revenue"].sum()
city_sales = filtered.groupby("City", as_index=False)["Revenue"].sum()

left, right = st.columns(2)
with left:
    fig = px.line(monthly, x="OrderDate", y="Revenue", markers=True, title="Monthly Revenue Trend")
    st.plotly_chart(fig, use_container_width=True)
with right:
    fig = px.bar(category_sales, x="Category", y="Revenue", color="Category", title="Revenue by Category")
    st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)
with left:
    fig = px.bar(city_sales, x="City", y="Revenue", color="City", title="Revenue by City")
    st.plotly_chart(fig, use_container_width=True)
with right:
    fig = px.scatter(filtered, x="DiscountPct", y="Profit", color="Category", title="Discount vs Profit")
    st.plotly_chart(fig, use_container_width=True)

if st.checkbox("Show filtered sales data"):
    st.dataframe(filtered, use_container_width=True)
    st.download_button("Download filtered CSV", filtered.to_csv(index=False).encode("utf-8"), "smartmart_filtered.csv", "text/csv")
