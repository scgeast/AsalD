import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# =================== NEON THEME & CSS ===================
st.set_page_config(page_title="🚚 Neon Dashboard Delivery & Sales", layout="wide")

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
    .legendtext {{
        color: {TEXT_WHITE} !important;
    }}
    </style>
    """,
        unsafe_allow_html=True,
    )

neon_css()

# =================== SIDEBAR FILTERS ===================
st.sidebar.image("https://img.icons8.com/fluency/96/excel.png", width=64)
st.sidebar.markdown("<h2 style='color:#fff;text-align:center;'>NEON DASHBOARD</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")

date_today = datetime.now().date()
date_min = date_today.replace(day=1)
date_max = date_today
filter_date = st.sidebar.date_input("Tanggal", value=(date_min, date_max), format="DD/MM/YYYY")

bulan_list = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]
bulan = st.sidebar.selectbox("Bulan", bulan_list, index=date_today.month-1)
tahun = st.sidebar.selectbox("Tahun", [2023, 2024, 2025], index=2)
st.sidebar.markdown("---")

uploaded = st.sidebar.file_uploader("📂 Upload Data Excel", type=["xlsx", "xls"])
if uploaded is None:
    st.warning("Upload file Excel untuk mulai.", icon="⚡")
    st.stop()

# =================== COLUMN NORMALIZATION ===================
KOL_MAPPER = {
    "dp_date": [
        "dp date", "delivery date", "tanggal pengiriman", "tanggal_pengiriman", "deliverydate"
    ],
    "qty": [
        "qty", "volume", "quantity", "vol", "volum"
    ],
    "sales_man": [
        "sales man", "salesman", "sales name", "salesname", "sales_man"
    ],
    "dp_no": [
        "dp no", "ritase", "trip", "dp_no"
    ],
    "distance": [
        "distance", "jarak", "dist", "distan"
    ]
}

def normalize_colname(col):
    import re
    c = col.lower()
    c = re.sub(r'[\s_]+', '', c)
    c = re.sub(r'[^a-z0-9]', '', c)
    return c

def find_column(df, alias_list):
    normed_cols = {normalize_colname(c): c for c in df.columns}
    for alias in alias_list:
        norm_alias = normalize_colname(alias)
        for norm_col, orig_col in normed_cols.items():
            if norm_col == norm_alias:
                return orig_col
    for alias in alias_list:
        norm_alias = normalize_colname(alias)
        for norm_col, orig_col in normed_cols.items():
            if norm_alias in norm_col:
                return orig_col
    return None

# =================== DATA PREP ===================
try:
    df = pd.read_excel(uploaded)
except Exception as e:
    st.error(f"Gagal membaca file: {e}")
    st.stop()

col_dp_date = find_column(df, KOL_MAPPER["dp_date"])
col_qty     = find_column(df, KOL_MAPPER["qty"])
col_sales   = find_column(df, KOL_MAPPER["sales_man"])
col_dp_no   = find_column(df, KOL_MAPPER["dp_no"])
col_dist    = find_column(df, KOL_MAPPER["distance"])

if not all([col_dp_date, col_qty, col_sales, col_dp_no]):
    st.error(f"Kolom utama tidak ditemukan: {', '.join([k for k,v in zip(['Dp Date','Qty','Sales Man','Dp No'], [col_dp_date, col_qty, col_sales, col_dp_no]) if v is None])}")
    st.stop()

for col in [col_dp_date]:
    df[col] = pd.to_datetime(df[col], errors="coerce")
df = df.dropna(subset=[col_dp_date])
df[col_qty] = pd.to_numeric(df[col_qty], errors="coerce").fillna(0)

mask = (df[col_dp_date].dt.month == (bulan_list.index(bulan)+1)) & (df[col_dp_date].dt.year == tahun)
if isinstance(filter_date, tuple) or isinstance(filter_date, list):
    mask = mask & (df[col_dp_date].dt.date >= filter_date[0]) & (df[col_dp_date].dt.date <= filter_date[1])
else:
    mask = mask & (df[col_dp_date].dt.date == filter_date)
df = df[mask]

# =================== DASHBOARD HEADER ===================
st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: center;">
    <span class="dashboard-title">🚀 Neon Dashboard Delivery & Sales</span>
    <span style="color:{NEON_BLUE};font-size:20px;font-weight:bold;">{bulan} {tahun}</span>
</div>
""", unsafe_allow_html=True)
st.markdown("<hr style='opacity:.11;'>", unsafe_allow_html=True)

# =================== KPI GRID ===================
trip_count = df[col_dp_no].nunique()
total_volume = df[col_qty].sum()
avg_load = total_volume / trip_count if trip_count > 0 else 0
avg_trip = trip_count

KPI = [
    {"label": "Total Volume", "value": f"{total_volume:,.0f}", "icon": "📦", "color": NEON_BLUE},
    {"label": "Total Trip", "value": f"{trip_count}", "icon": "🧾", "color": NEON_PINK},
    {"label": "Avg Load/Trip", "value": f"{avg_load:,.2f}", "icon": "⚖️", "color": NEON_GREEN},
    {"label": "Avg Trip", "value": f"{avg_trip}", "icon": "✈️", "color": NEON_ORANGE},
    {"label": "Distance Available", "value": "Ya" if col_dist else "Tidak", "icon": "📏", "color": NEON_PURPLE},
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

# =================== MAIN CHARTS GRID ===================
st.markdown('<div class="section-title">📊 Delivery & Sales</div>', unsafe_allow_html=True)
mainrow = st.columns([2,1])

# --- Bar Chart: Volume per Sales Man ---
df_sales = df.groupby(col_sales, as_index=False)[col_qty].sum().sort_values(col_qty, ascending=False)
bar_colors = [NEON_BLUE, NEON_PINK, NEON_ORANGE, NEON_PURPLE, NEON_GREEN]
fig_bar = px.bar(
    df_sales, x=col_sales, y=col_qty, text=col_qty,
    color=col_sales, color_discrete_sequence=bar_colors, template="plotly_dark"
)
fig_bar.update_traces(texttemplate='%{text:,.0f}', marker_line_width=0, textposition='outside')
fig_bar.update_layout(showlegend=False, plot_bgcolor=CARD_BG, paper_bgcolor=CARD_BG, margin=dict(l=10,r=10,b=30,t=40),
                      font_color=TEXT_WHITE, yaxis=dict(title=None), xaxis=dict(title=None))
mainrow[0].plotly_chart(fig_bar, use_container_width=True)

# --- Pie Chart: Proporsi Trip ---
df_trip = df.groupby(col_dp_no, as_index=False)[col_qty].sum()
fig_pie = px.pie(
    df_trip, names=col_dp_no, values=col_qty,
    color=col_dp_no, color_discrete_sequence=bar_colors, hole=0.55, template="plotly_dark"
)
fig_pie.update_traces(textinfo="percent+label", textfont_size=13, marker_line=dict(color=DARK_BG, width=2))
fig_pie.update_layout(showlegend=False, font_color=TEXT_WHITE, plot_bgcolor=CARD_BG, paper_bgcolor=CARD_BG, margin=dict(l=10,r=10,b=20,t=30))
mainrow[1].plotly_chart(fig_pie, use_container_width=True)

# =================== TREND CHART ===================
st.markdown('<div class="section-title">📈 Trend Volume per Hari</div>', unsafe_allow_html=True)
df_trend = df.groupby(df[col_dp_date].dt.date, as_index=False)[col_qty].sum()
old_date_col = df_trend.columns[0]
old_qty_col = df_trend.columns[1]
df_trend.rename(columns={old_date_col: "Tanggal", old_qty_col: "Volume"}, inplace=True)
if df_trend.empty:
    st.warning("Tidak ada data untuk chart trend (cek filter atau data kosong).")
else:
    fig_line = px.line(df_trend, x="Tanggal", y="Volume", markers=True, template="plotly_dark", color_discrete_sequence=[NEON_PINK])
    fig_line.update_traces(line_width=3, marker=dict(size=7, color=NEON_BLUE))
    fig_line.update_layout(plot_bgcolor=CARD_BG, paper_bgcolor=CARD_BG, margin=dict(l=10,r=10,b=30,t=40),
        font_color=TEXT_WHITE, yaxis=dict(title=""), xaxis=dict(title="Tanggal"))
    st.plotly_chart(fig_line, use_container_width=True)

# =================== DATA TABLE & EXPORT ===================
st.markdown('<div class="section-title">📄 Data Terkini</div>', unsafe_allow_html=True)
st.dataframe(df.head(30), use_container_width=True, hide_index=True)

csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="⬇️ Download Data Terfilter (CSV)",
    data=csv,
    file_name=f"data_{bulan}_{tahun}.csv",
    mime="text/csv",
    help="Unduh data sesuai filter yang aktif."
)
