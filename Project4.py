import streamlit as st
import pandas as pd
import plotly.express as px
import io
from datetime import datetime

# =========================
# Halaman & Tema
# =========================
st.set_page_config(page_title="📦 Dashboard Monitoring Delivery & Sales", layout="wide")

# Pilihan Mode
mode = st.sidebar.radio("Mode Tampilan", ["Light", "Dark"])

# CSS untuk Dark & Light Mode
if mode == "Dark":
    text_color = "white"
    bg_color = "#0e1117"
else:
    text_color = "black"
    bg_color = "white"

st.markdown(
    f"""
    <style>
    body, .stApp {{
        color: {text_color};
        background-color: {bg_color};
    }}
    .css-18e3th9, .css-1d391kg, .css-1kyxreq, .stMarkdown, .stMetric, h1, h2, h3, h4, h5, h6, p {{
        color: {text_color} !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# Upload Data
# =========================
uploaded_file = st.file_uploader("📂 Upload Excel File", type=["xlsx"])

if uploaded_file is not None:
    # Baca Excel
    df = pd.read_excel(uploaded_file)

    # Normalisasi nama kolom
    df.columns = df.columns.str.strip().str.lower()
    col_mapping = {
        "dp date": "date", "tanggal pengiriman": "date", "delivery date": "date",
        "qty": "qty", "volume": "qty",
        "sales man": "salesman", "sales name": "salesman",
        "dp no": "trip", "ritase": "trip",
        "truck no": "truck",
        "distance": "distance",
        "area": "area",
        "plant name": "plant",
        "end customer name": "customer"
    }
    df = df.rename(columns=lambda x: col_mapping.get(x, x))

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # =========================
    # Filter Data
    # =========================
    st.sidebar.subheader("🔍 Filter Data")
    start_date = st.sidebar.date_input("Start Date", df["date"].min() if "date" in df.columns else datetime.today())
    end_date = st.sidebar.date_input("End Date", df["date"].max() if "date" in df.columns else datetime.today())

    area_filter = st.sidebar.multiselect("Pilih Area", options=df["area"].unique() if "area" in df.columns else [])
    plant_filter = []
    if area_filter and "plant" in df.columns:
        plant_filter = st.sidebar.multiselect("Pilih Plant", options=df[df["area"].isin(area_filter)]["plant"].unique())

    if st.sidebar.button("Reset Filter"):
        area_filter, plant_filter = [], []

    df_filtered = df.copy()
    if "date" in df.columns:
        df_filtered = df_filtered[(df_filtered["date"] >= pd.to_datetime(start_date)) & (df_filtered["date"] <= pd.to_datetime(end_date))]
    if area_filter:
        df_filtered = df_filtered[df_filtered["area"].isin(area_filter)]
    if plant_filter:
        df_filtered = df_filtered[df_filtered["plant"].isin(plant_filter)]

    # =========================
    # Header Dashboard
    # =========================
    st.markdown(
        f"""
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <h1>🚀 Dashboard Monitoring Delivery & Sales</h1>
            <h3 style="color:{text_color};">L23-51XE</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # =========================
    # Summarize
    # =========================
    st.subheader("🧭 Summarize")
    total_area = df_filtered["area"].nunique() if "area" in df_filtered.columns else 0
    total_plant = df_filtered["plant"].nunique() if "plant" in df_filtered.columns else 0
    total_volume = df_filtered["qty"].sum() if "qty" in df_filtered.columns else 0
    avg_volume_day = df_filtered.groupby("date")["qty"].sum().mean() if "date" in df_filtered.columns else 0
    total_truck = df_filtered["truck"].nunique() if "truck" in df_filtered.columns else 0
    total_trip = df_filtered["trip"].nunique() if "trip" in df_filtered.columns else 0

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("🌍 Total Area", f"{total_area:,}")
    col2.metric("🏭 Total Plant", f"{total_plant:,}")
    col3.metric("📦 Total Volume", f"{total_volume:,.0f}")
    col4.metric("📅 Avg Volume / Day", f"{avg_volume_day:,.0f}")
    col5.metric("🚚 Total Truck", f"{total_truck:,}")
    col6.metric("📝 Total Trip", f"{total_trip:,}")

    # =========================
    # Delivery Performance
    # =========================
    st.subheader("📦 Delivery Performance")
    if "date" in df_filtered.columns and "qty" in df_filtered.columns:
        delivery_perf = df_filtered.groupby("date")["qty"].sum().reset_index()
        fig = px.line(delivery_perf, x="date", y="qty", title="Delivery Volume Trend")
        st.plotly_chart(fig, use_container_width=True)

    # =========================
    # Truck Utilization
    # =========================
    st.subheader("🚚 Truck Utilization")
    if "truck" in df_filtered.columns and "trip" in df_filtered.columns:
        truck_util = df_filtered.groupby("truck")["trip"].count().reset_index().sort_values(by="trip", ascending=False).head(10)
        fig = px.bar(truck_util, x="truck", y="trip", title="Top 10 Truck Utilization")
        st.plotly_chart(fig, use_container_width=True)

    # =========================
    # Distance Analysis
    # =========================
    st.subheader("📍 Distance Analysis")
    if "area" in df_filtered.columns and "distance" in df_filtered.columns:
        distance_analysis = df_filtered.groupby("area")["distance"].sum().reset_index()
        fig = px.bar(distance_analysis, x="area", y="distance", title="Distance per Area")
        st.plotly_chart(fig, use_container_width=True)

    # =========================
    # Sales & Customer Performance
    # =========================
    st.subheader("💼 Sales & Customer Performance")
    if "salesman" in df_filtered.columns and "qty" in df_filtered.columns:
        sales_perf = df_filtered.groupby("salesman")["qty"].sum().reset_index().sort_values(by="qty", ascending=False).head(10)
        fig = px.bar(sales_perf, x="salesman", y="qty", title="Top 10 Sales by Volume")
        st.plotly_chart(fig, use_container_width=True)

    if "customer" in df_filtered.columns and "qty" in df_filtered.columns:
        cust_perf = df_filtered.groupby("customer")["qty"].sum().reset_index().sort_values(by="qty", ascending=False).head(10)
        fig = px.bar(cust_perf, x="customer", y="qty", title="Top 10 Customers by Volume")
        st.plotly_chart(fig, use_container_width=True)

    # =========================
    # Visualisasi Tren
    # =========================
    st.subheader("📈 Visualisasi Tren")
    if "date" in df_filtered.columns:
        trend_ritase = df_filtered.groupby("date")["trip"].count().reset_index()
        trend_volume = df_filtered.groupby("date")["qty"].sum().reset_index()
        fig1 = px.line(trend_ritase, x="date", y="trip", title="Trend Ritase per Day")
        fig2 = px.line(trend_volume, x="date", y="qty", title="Trend Volume per Day")
        st.plotly_chart(fig1, use_container_width=True)
        st.plotly_chart(fig2, use_container_width=True)

    # =========================
    # Export ke Excel
    # =========================
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_filtered.to_excel(writer, index=False, sheet_name="Filtered Data")
    st.download_button("📥 Export Data ke Excel", data=output.getvalue(), file_name="dashboard_export.xlsx")

else:
    st.warning("⚠️ Silakan upload file Excel terlebih dahulu.")
