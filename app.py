import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="E-commerce Dashboard", page_icon="🛍️", layout="wide")

GREEN = "#287763"
st.markdown("""
<style>
    .stApp { background: #f4f6fa; }
    [data-testid="stMetric"] { background: white; padding: 16px; border-radius: 12px; border: 1px solid #edf0f4; }
    div[data-testid="stVerticalBlock"] div[data-testid="stContainer"] { background: white; }
    h1, h2, h3 { color: #172b4d; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    path = Path(__file__).parent / "cleaned_orders.csv"
    data = pd.read_csv(path, parse_dates=["Date"])
    data["TotalPrice"] = pd.to_numeric(data["TotalPrice"], errors="coerce").fillna(0)
    data["Quantity"] = pd.to_numeric(data["Quantity"], errors="coerce").fillna(0)
    return data

df = load_data()

st.title("🛍️ E-commerce Dashboard")
st.caption("Orders · Products · Customer Insights")
st.divider()

st.subheader("Filters")
min_date, max_date = df["Date"].min().date(), df["Date"].max().date()
c1, c2, c3, c4 = st.columns(4)
with c1:
    date_range = st.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
with c2:
    statuses = ["All statuses"] + sorted(df["OrderStatus"].dropna().unique().tolist())
    selected_status = st.selectbox("Order status", statuses)
with c3:
    products = ["All products"] + sorted(df["Product"].dropna().unique().tolist())
    selected_product = st.selectbox("Product", products)
with c4:
    sources = ["All sources"] + sorted(df["ReferralSource"].dropna().unique().tolist())
    selected_source = st.selectbox("Referral source", sources)

filtered = df.copy()
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered = filtered[filtered["Date"].dt.date.between(start_date, end_date)]
elif isinstance(date_range, (tuple, list)) and len(date_range) == 1:
    filtered = filtered[filtered["Date"].dt.date == date_range[0]]
if selected_status != "All statuses":
    filtered = filtered[filtered["OrderStatus"] == selected_status]
if selected_product != "All products":
    filtered = filtered[filtered["Product"] == selected_product]
if selected_source != "All sources":
    filtered = filtered[filtered["ReferralSource"] == selected_source]

st.subheader("Business Overview")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Order Value", f"₹{filtered['TotalPrice'].sum():,.2f}")
m2.metric("Total Orders", f"{filtered['OrderID'].nunique():,}")
m3.metric("Units Ordered", f"{filtered['Quantity'].sum():,.0f}")
m4.metric("Unique Customers", f"{filtered['CustomerID'].nunique():,}")

st.divider()
left, right = st.columns(2)
with left:
    st.subheader("Monthly Order Value")
    if filtered.empty:
        st.info("No data matches the selected filters.")
    else:
        monthly = (filtered.assign(Month=filtered["Date"].dt.to_period("M").dt.to_timestamp())
                   .groupby("Month", as_index=False)["TotalPrice"].sum())
        fig = px.line(monthly, x="Month", y="TotalPrice", markers=True,
                      labels={"Month": "Month", "TotalPrice": "Order value"})
        fig.update_traces(line_color=GREEN, marker_color=GREEN, line_width=3)
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="white",
                          paper_bgcolor="white", yaxis_tickprefix="₹", xaxis_title="", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)
with right:
    st.subheader("Orders by Status")
    if filtered.empty:
        st.info("No data matches the selected filters.")
    else:
        status_counts = filtered.groupby("OrderStatus", as_index=False)["OrderID"].nunique().rename(columns={"OrderID":"Orders"})
        status_counts = status_counts.sort_values("Orders", ascending=True)
        fig = px.bar(status_counts, x="Orders", y="OrderStatus", orientation="h",
                     labels={"Orders":"Number of orders", "OrderStatus":"Status"})
        fig.update_traces(marker_color=GREEN)
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="white",
                          paper_bgcolor="white", xaxis_title="", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("Product Performance")
if filtered.empty:
    st.info("No product performance to show for these filters.")
else:
    performance = (filtered.groupby("Product", as_index=False)
                   .agg(Quantity=("Quantity", "sum"),
                        Order_Value=("TotalPrice", "sum"),
                        Orders=("OrderID", "nunique"))
                   .sort_values("Order_Value", ascending=False))
    performance["Order_Value"] = performance["Order_Value"].map(lambda x: f"₹{x:,.2f}")
    st.dataframe(performance.rename(columns={"Product":"Product", "Quantity":"Units ordered",
                                            "Order_Value":"Order value", "Orders":"Orders"}),
                 use_container_width=True, hide_index=True)

with st.expander("View filtered order records"):
    st.dataframe(filtered, use_container_width=True, hide_index=True)

csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button("Download filtered data (CSV)", data=csv, file_name="filtered_orders.csv", mime="text/csv")

st.caption(f"Showing {len(filtered):,} of {len(df):,} cleaned records.")
