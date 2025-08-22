import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# =============== CONFIG & THEME ===============
st.set_page_config(page_title="🚚 Neon Dashboard Delivery & Sales", layout="wide")

# --- Neon Color Palettes ---
DARK_BG = "#181c2f"
CARD_BG = "#23294a"
NEON_PINK = "#ff1fae"
NEON_BLUE = "#00e7ff"
NEON_ORANGE = "#ffb86c"
NEON_PURPLE = "#8e54e9"
NEON_GREEN = "#00ffb2"
TEXT_WHITE = "#f3f6fa"
ACCENT = NEON_PINK
ACCENT2 = NEON_BLUE

def neon_css():
    st.markdown(
        f"""
    <style>
    body, .stApp {{
        background: {DARK_BG};
        color: {TEXT_WHITE};
    }}
    .block-container {{
        background: {DARK_BG} !important;
    }}
    .neon-card {{
        background: linear-gradient(135deg, {CARD_BG} 60%, {ACCENT}22 100%);
        border: 1.5px solid {ACCENT2}55;
        border-radius: 18px;
        box-shadow: 0 2px 18px {ACCENT2}44;
        padding: 20px 24px;
        margin-bottom: 18px;
    }}
    .neon-metric {{
        font-size: 28px;
        font-weight: 800;
        color: {NEON_BLUE};
        text-shadow: 0px 0px 8px {ACCENT2}80;
    }}
    .neon-metric-label {{
        font-size: 13px;
        letter-spacing: .02em;
        color: {ACCENT};
        opacity: 0.9;
        font-weight: 700;
        text-transform: uppercase;
    }}
    .dashboard-title {{
        color: {NEON_PINK};
        font-weight: 900;
        font-size: 32px;
        letter-spacing: .03em;
        text-shadow: 0 0 18px {NEON_PINK}80;
    }}
    .section-title {{
        font-size: 22px; font-weight: 800; margin: 8px 0 10px 0; color: {NEON_BLUE}; letter-spacing: .01em;
    }}
    .subtitle {{
        font-size: 16px; opacity:.95; margin: 8px 0 8px 0; color: {NEON_ORANGE};
    }}
    .stSelectbox > div, .stDateInput label, .stRadio label, .stButton button, .stDownloadButton button {{
        color: {NEON_PINK} !important;
        font-weight: 600;
    }}
    .css-1cpxqw2, .css-16idsys, .css-1n76uvr {{
        color: {TEXT_WHITE} !important;
    }}
    /* Pie/Donut legend */
    .legendtext {{
        color: {TEXT_WHITE} !important;
    }}
    </style>
    """,
        unsafe_allow_html=True,
    )

neon_css()

# =============== SIDEBAR FILTERS ===============
st.sidebar.image("https://img.icons8.com/fluency/96/excel.png", width=64)
st.sidebar.markdown("<h2 style='color:#fff;text-align:center;'>NEON DASHBOARD</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")

# --- Date Filter ---
date_today = datetime.now().date()
date_min = date_today.replace(day=1)
date_max = date_today
filter_date = st.sidebar.date_input("Tanggal", value=(date_min, date_max), format="DD/MM/YYYY")

# --- Bulan / Tahun ---
bulan_list = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]
bulan_now = bulan_list[date_today.month - 1]
bulan = st.sidebar.selectbox("Bulan", bulan_list, index=date_today.month-1)
tahun = st.sidebar.selectbox("Tahun", [2023, 2024, 2025], index=2)
st.sidebar.markdown("---")

# =============== DATA UPLOAD ===============
uploaded = st.sidebar.file_uploader("📂 Upload Data Excel", type=["xlsx", "xls"])
if uploaded is None:
    st.warning("Upload file Excel untuk mulai.", icon="⚡")
    st.stop()

# =============== DATA PREP ===============
try:
    df = pd.read_excel(uploaded)
except Exception as e:
    st.error(f"Gagal membaca file: {e}")
    st.stop()

def norm_col(x):
    return str(x).strip().lower().replace("\n"," ").replace("_"," ").replace("-"," ").replace("  "," ")

df.columns = [norm_col(c) for c in df.columns]

# Otomatis deteksi kolom
col_date   = next((c for c in df.columns if "date" in c or "tanggal" in c), df.columns[0])
col_qty    = next((c for c in df.columns if "qty" in c or "volume" in c), df.columns[1])
col_sales  = next((c for c in df.columns if "sales" in c), None)
col_area   = next((c for c in df.columns if "area" in c), None)
col_plant  = next((c for c in df.columns if "plant" in c), None)
col_truck  = next((c for c in df.columns if "truck" in c or "nopol" in c), None)
col_endcust= next((c for c in df.columns if "customer" in c), None)

# --- Data Tipe ---
df[col_date] = pd.to_datetime(df[col_date], errors="coerce")
df = df.dropna(subset=[col_date])
df[col_qty] = pd.to_numeric(df[col_qty], errors="coerce").fillna(0)

# --- Filter berdasarkan sidebar ---
mask = (df[col_date].dt.month == (bulan_list.index(bulan)+1)) & (df[col_date].dt.year == tahun)
if isinstance(filter_date, tuple) or isinstance(filter_date, list):
    mask = mask & (df[col_date].dt.date >= filter_date[0]) & (df[col_date].dt.date <= filter_date[1])
else:
    mask = mask & (df[col_date].dt.date == filter_date)
df = df[mask]

# =============== DASHBOARD HEADER ===============
st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: center;">
    <span class="dashboard-title">🚀 Neon Dashboard Delivery & Sales</span>
    <span style="color:{NEON_BLUE};font-size:20px;font-weight:bold;">{bulan} {tahun}</span>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr style='opacity:.11;'>", unsafe_allow_html=True)

# =============== KPI GRID ===============
KPI = [
    {
        "label": "Total Volume",
        "value": f"{df[col_qty].sum():,.0f}",
        "icon": "📦",
        "color": NEON_BLUE,
    },
    {
        "label": "Jumlah Area",
        "value": f"{df[col_area].nunique() if col_area else 0}",
        "icon": "🗺️",
        "color": NEON_PINK,
    },
    {
        "label": "Jumlah Plant",
        "value": f"{df[col_plant].nunique() if col_plant else 0}",
        "icon": "🏭",
        "color": NEON_ORANGE,
    },
    {
        "label": "Jumlah Sales",
        "value": f"{df[col_sales].nunique() if col_sales else 0}",
        "icon": "🧑‍💼",
        "color": NEON_GREEN,
    },
    {
        "label": "Jumlah Truck",
        "value": f"{df[col_truck].nunique() if col_truck else 0}",
        "icon": "🚚",
        "color": NEON_PURPLE,
    },
    {
        "label": "Jumlah Customer",
        "value": f"{df[col_endcust].nunique() if col_endcust else 0}",
        "icon": "👥",
        "color": NEON_ORANGE,
    },
]

kpi_row = st.columns(len(KPI))
for col, item in zip(kpi_row, KPI):
    with col:
        st.markdown(
            f"""
            <div class="neon-card" style="text-align:center;">
                <div style="font-size:29px;margin-bottom:4px;">{item['icon']}</div>
                <div class="neon-metric" style="color:{item['color']};">{item['value']}</div>
                <div class="neon-metric-label">{item['label']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# =============== MAIN CHARTS GRID ===============

st.markdown('<div class="section-title">📊 Total Sales By Segment</div>', unsafe_allow_html=True)
mainrow = st.columns([2,1])

# --- Main Bar Chart: Volume per Segmen (misal Area/Plant/Customer) ---
segmen_col = col_area or col_plant or col_endcust
if segmen_col:
    df_seg = df.groupby(segmen_col, as_index=False)[col_qty].sum().sort_values(col_qty, ascending=False)
    bar_colors = [NEON_BLUE, NEON_PINK, NEON_ORANGE, NEON_PURPLE, NEON_GREEN]
    fig_bar = px.bar(
        df_seg,
        x=segmen_col, y=col_qty,
        text=col_qty,
        color=segmen_col,
        color_discrete_sequence=bar_colors,
        template="plotly_dark"
    )
    fig_bar.update_traces(texttemplate='%{text:,.0f}', marker_line_width=0, textposition='outside')
    fig_bar.update_layout(showlegend=False, plot_bgcolor=CARD_BG, paper_bgcolor=CARD_BG, margin=dict(l=10,r=10,b=30,t=40),
                          font_color=TEXT_WHITE, yaxis=dict(title=None), xaxis=dict(title=None))
    mainrow[0].plotly_chart(fig_bar, use_container_width=True)
else:
    mainrow[0].info("Tidak ada kolom segmentasi (area/plant/customer) di data.")

# --- Pie/Donut: Proporsi Volume per Segmen ---
if segmen_col:
    fig_pie = px.pie(
        df_seg, names=segmen_col, values=col_qty,
        color=segmen_col, color_discrete_sequence=bar_colors,
        hole=0.55,
        template="plotly_dark"
    )
    fig_pie.update_traces(textinfo="percent+label", textfont_size=13, marker_line=dict(color=DARK_BG, width=2))
    fig_pie.update_layout(showlegend=True, legend=dict(font=dict(color=TEXT_WHITE)), font_color=TEXT_WHITE, plot_bgcolor=CARD_BG, paper_bgcolor=CARD_BG, margin=dict(l=10,r=10,b=20,t=30))
    mainrow[1].plotly_chart(fig_pie, use_container_width=True)

# ==== ROW 2: Sales & Profit per Segmen, Trend ====
st.markdown('<div class="section-title">📈 Sales Trend & Profit</div>', unsafe_allow_html=True)
row2 = st.columns([1,1])

# --- Line Chart: Trend Volume per Hari ---
df_trend = df.groupby(df[col_date].dt.date, as_index=False)[col_qty].sum()
fig_line = px.line(df_trend, x=col_date, y=col_qty, markers=True, template="plotly_dark", color_discrete_sequence=[NEON_PINK])
fig_line.update_traces(line_width=3, marker=dict(size=7, color=NEON_BLUE))
fig_line.update_layout(
    plot_bgcolor=CARD_BG,
    paper_bgcolor=CARD_BG,
    margin=dict(l=10,r=10,b=30,t=40),
    font_color=TEXT_WHITE,
    yaxis=dict(title=""),
    xaxis=dict(title="Tanggal")
)
row2[0].plotly_chart(fig_line, use_container_width=True)

# --- Donut Chart: Distribusi Truck/Sales/Customer ---
donut_col = col_truck or col_sales or col_endcust
if donut_col:
    df_donut = df.groupby(donut_col, as_index=False)[col_qty].sum()
    df_donut = df_donut.sort_values(col_qty, ascending=False).head(5)
    fig_donut = px.pie(
        df_donut, names=donut_col, values=col_qty,
        color=donut_col, hole=0.65,
        color_discrete_sequence=bar_colors,
        template="plotly_dark"
    )
    fig_donut.update_traces(textinfo="percent+label", textfont_size=13, marker_line=dict(color=DARK_BG, width=2))
    fig_donut.update_layout(
        showlegend=True, legend=dict(font=dict(color=TEXT_WHITE)),
        font_color=TEXT_WHITE,
        plot_bgcolor=CARD_BG, paper_bgcolor=CARD_BG,
        margin=dict(l=10,r=10,b=20,t=30)
    )
    row2[1].plotly_chart(fig_donut, use_container_width=True)

# ==== ROW 3: Table & Export ====
st.markdown('<div class="section-title">📄 Data Terkini</div>', unsafe_allow_html=True)
st.dataframe(df.head(30), use_container_width=True, hide_index=True)

# ---- DOWNLOAD BUTTON ----
csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="⬇️ Download Data Terfilter (CSV)",
    data=csv,
    file_name=f"data_{bulan}_{tahun}.csv",
    mime="text/csv",
    help="Unduh data sesuai filter yang aktif."
)
