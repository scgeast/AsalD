import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ============ NEON THEME & CSS ============
st.set_page_config(page_title="🚚 RMC Plant Achievement Dashboard", layout="wide")

DARK_BG = "#181c2f"
CARD_BG = "#23294a"
NEON_PINK = "#ff1fae"
NEON_BLUE = "#00e7ff"
NEON_ORANGE = "#ffb86c"
NEON_PURPLE = "#8e54e9"
NEON_GREEN = "#00ffb2"
TEXT_WHITE = "#f3f6fa"

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
        background: linear-gradient(135deg, {CARD_BG} 70%, {NEON_PINK}22 100%);
        border: 1.5px solid {NEON_BLUE}55;
        border-radius: 18px;
        box-shadow: 0 2px 18px {NEON_BLUE}44;
        padding: 18px 22px;
        margin-bottom: 15px;
    }}
    .neon-metric {{
        font-size: 28px;
        font-weight: 800;
        color: {NEON_BLUE};
        text-shadow: 0px 0px 8px {NEON_BLUE}80;
    }}
    .neon-metric-label {{
        font-size: 13px;
        letter-spacing: .02em;
        color: {NEON_PINK};
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

# ============ SIDEBAR & DATA LOAD ============
st.sidebar.image("https://img.icons8.com/fluency/96/excel.png", width=64)
st.sidebar.markdown("<h2 style='color:#fff;text-align:center;'>RMC PLANT DASHBOARD</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")
uploaded = st.sidebar.file_uploader("📂 Upload Data Excel", type=["xlsx", "xls"])
if uploaded is None:
    st.warning("Upload file Excel seperti contoh screenshot untuk mulai.", icon="⚡")
    st.stop()

try:
    df = pd.read_excel(uploaded)
except Exception as e:
    st.error(f"Gagal membaca file: {e}")
    st.stop()

# Robust: treat all column names as string
def find_col(df, keys):
    normed = {str(c).lower().replace(" ", "").replace("_", ""): str(c) for c in df.columns}
    for k in keys:
        k_norm = k.lower().replace(" ", "").replace("_", "")
        for col_norm, orig in normed.items():
            if k_norm == col_norm or k_norm in col_norm:
                return orig
    return None

col_area = find_col(df, ["AREA"])
col_plant = find_col(df, ["PLANT"])
col_status = find_col(df, ["Status Plant"])
col_annfm = find_col(df, ["ANN FM Target"])
col_mtd = find_col(df, ["MTD Vol"])
col_achv = find_col(df, ["Achievement", "% Achievement of Target", "%"])
col_avgvol = find_col(df, ["AVG Vol.day"])
col_sched = find_col(df, ["Schedule RMC"])
col_actual = find_col(df, ["Actual Supply"])

# Validasi kolom utama
missing_cols = []
for col, label in [(col_area,"AREA"), (col_plant,"PLANT"), (col_status,"Status Plant"),
                   (col_annfm,"ANN FM Target"), (col_mtd,"MTD Vol"), (col_achv,"% Achievement"),
                   (col_avgvol,"AVG Vol.day"), (col_sched,"Schedule RMC"), (col_actual,"Actual Supply")]:
    if col is None:
        missing_cols.append(label)
if missing_cols:
    st.error(f"Kolom berikut tidak ditemukan di file: {', '.join(missing_cols)}")
    st.stop()

# Normalisasi data achievement %
def parse_percent(x):
    try:
        if pd.isnull(x): return None
        if isinstance(x, float): return x
        x = str(x).replace("%", "").replace(",", ".")
        return float(x)
    except:
        return None

df[col_achv] = df[col_achv].astype(str).str.replace("#DIV/0!", "0").str.replace("%", "").str.replace(",", ".")
df[col_achv] = pd.to_numeric(df[col_achv], errors="coerce").fillna(0)

# Sidebar filter
areas = ["All"] + sorted(df[col_area].dropna().unique().tolist())
plants = ["All"] + sorted(df[col_plant].dropna().unique().tolist())
area = st.sidebar.selectbox("Filter Area", areas)
plant = st.sidebar.selectbox("Filter Plant", plants)
st.sidebar.markdown("---")

mask = ((df[col_area]==area) if area != "All" else True) & ((df[col_plant]==plant) if plant != "All" else True)
df_disp = df[mask].copy() if (area!="All" or plant!="All") else df.copy()

# ============ DASHBOARD HEADER ============
st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: center;">
    <span class="dashboard-title">🚀 RMC Plant Achievement Dashboard</span>
    <span style="color:{NEON_BLUE};font-size:20px;font-weight:bold;">{datetime.now().strftime('%B %Y')}</span>
</div>
""", unsafe_allow_html=True)
st.markdown("<hr style='opacity:.11;'>", unsafe_allow_html=True)

# ============ KPI CARDS ============
def safe_mean(series):
    vals = pd.to_numeric(series, errors="coerce").dropna()
    return vals.mean() if not vals.empty else 0

def safe_sum(series):
    vals = pd.to_numeric(series, errors="coerce").dropna()
    return vals.sum() if not vals.empty else 0

kpi_data = [
    {
        "label": "Total Plant",
        "value": df_disp[col_plant].nunique(),
        "icon": "🏭",
        "color": NEON_ORANGE,
    },
    {
        "label": "Total MTD Vol",
        "value": f"{safe_sum(df_disp[col_mtd]):,.0f}",
        "icon": "📦",
        "color": NEON_BLUE,
    },
    {
        "label": "AVG Vol/Day",
        "value": f"{safe_mean(df_disp[col_avgvol]):.2f}",
        "icon": "📊",
        "color": NEON_GREEN,
    },
    {
        "label": "AVG Achievement (%)",
        "value": f"{safe_mean(df_disp[col_achv]):.1f}%",
        "icon": "🎯",
        "color": NEON_PINK,
    },
    {
        "label": "AVG Actual Supply (%)",
        "value": f"{safe_mean(df_disp[col_actual].apply(parse_percent)):.1f}%",
        "icon": "🚚",
        "color": NEON_PURPLE,
    }
]
kpi_row = st.columns(len(kpi_data))
for col, k in zip(kpi_row, kpi_data):
    with col:
        st.markdown(
            f"""
            <div class="neon-card" style="text-align:center;">
                <div style="font-size:29px;margin-bottom:4px;">{k['icon']}</div>
                <div class="neon-metric" style="color:{k['color']};">{k['value']}</div>
                <div class="neon-metric-label">{k['label']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ============ CHARTS ============
st.markdown('<div class="section-title">📊 Performance Charts</div>', unsafe_allow_html=True)
chartrow = st.columns([2,1])

# --- Bar: % Achievement per Plant ---
if not df_disp.empty:
    bar_colors = df_disp[col_achv].apply(
        lambda x: NEON_GREEN if x>=100 else NEON_ORANGE if x>=80 else NEON_PINK
    )
    fig_bar = px.bar(
        df_disp, x=col_plant, y=col_achv, color=col_achv,
        color_discrete_sequence=[NEON_GREEN, NEON_ORANGE, NEON_PINK],
        template="plotly_dark",
        text=col_achv
    )
    fig_bar.update_traces(texttemplate='%{text:.0f}%', marker_color=bar_colors, marker_line_width=0, textposition='outside')
    fig_bar.update_layout(
        xaxis_title="Plant", yaxis_title="% Achievement", 
        showlegend=False, plot_bgcolor=CARD_BG, paper_bgcolor=CARD_BG, 
        margin=dict(l=10,r=10,b=30,t=40), font_color=TEXT_WHITE
    )
    chartrow[0].plotly_chart(fig_bar, use_container_width=True)
else:
    chartrow[0].info("Tidak ada data untuk chart ini.")

# --- Pie: Plant Achievement Grouping ---
def ach_group(x):
    if x >= 100: return ">100%"
    elif x >= 80: return "80-100%"
    else: return "<80%"
if not df_disp.empty:
    df_disp["ach_group"] = df_disp[col_achv].apply(ach_group)
    pie_df = df_disp.groupby("ach_group").size().reset_index(name="Count")
    fig_pie = px.pie(
        pie_df, names="ach_group", values="Count",
        color="ach_group", 
        color_discrete_map={">100%": NEON_GREEN, "80-100%": NEON_ORANGE, "<80%": NEON_PINK},
        template="plotly_dark", hole=0.55
    )
    fig_pie.update_traces(textinfo="percent+label", textfont_size=13, marker_line=dict(color=DARK_BG, width=2))
    fig_pie.update_layout(
        showlegend=True, legend=dict(font=dict(color=TEXT_WHITE)), font_color=TEXT_WHITE,
        plot_bgcolor=CARD_BG, paper_bgcolor=CARD_BG, margin=dict(l=10,r=10,b=20,t=30)
    )
    chartrow[1].plotly_chart(fig_pie, use_container_width=True)
else:
    chartrow[1].info("Tidak ada data untuk chart ini.")

# --- Bar: Schedule vs Actual Supply per Plant ---
st.markdown('<div class="section-title">🚚 Schedule vs Actual Supply</div>', unsafe_allow_html=True)
sched_df = df_disp.copy()
sched_df["Schedule RMC"] = pd.to_numeric(sched_df[col_sched], errors="coerce").fillna(0)
sched_df["Actual Supply"] = sched_df[col_actual].apply(parse_percent)
sched_df = sched_df.dropna(subset=[col_sched, col_actual])
if not sched_df.empty:
    sched_bar = px.bar(
        sched_df, x=col_plant, y=["Schedule RMC", "Actual Supply"],
        barmode="group", template="plotly_dark",
        color_discrete_map={"Schedule RMC": NEON_BLUE, "Actual Supply": NEON_GREEN}
    )
    sched_bar.update_layout(
        yaxis_title="Ton / %", xaxis_title="Plant",
        plot_bgcolor=CARD_BG, paper_bgcolor=CARD_BG, font_color=TEXT_WHITE,
        margin=dict(l=10,r=10,b=30,t=40)
    )
    st.plotly_chart(sched_bar, use_container_width=True)
else:
    st.info("Tidak ada data untuk chart ini.")

# --- Table with highlight ---
st.markdown('<div class="section-title">📋 Plant Table</div>', unsafe_allow_html=True)
def color_achv(val):
    try:
        v = float(str(val).replace(",", "."))
        if v >= 100: return f"background-color:{NEON_GREEN}33"
        elif v >= 80: return f"background-color:{NEON_ORANGE}33"
        else: return f"background-color:{NEON_PINK}33"
    except: return ""
show_cols = [col_area, col_plant, col_status, col_annfm, col_mtd, col_achv, col_avgvol, col_sched, col_actual]
if not df_disp.empty:
    st.dataframe(df_disp[show_cols].style.applymap(color_achv, subset=[col_achv]), use_container_width=True, hide_index=True)
else:
    st.info("Tidak ada data untuk ditampilkan di tabel.")

# --- Download Button ---
csv = df_disp.to_csv(index=False).encode('utf-8')
st.download_button(
    label="⬇️ Download Data Plant (CSV)",
    data=csv,
    file_name=f"plant_achievement_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv",
    help="Unduh data plant yang sedang difilter."
)
