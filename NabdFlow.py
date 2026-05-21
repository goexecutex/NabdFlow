# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  NabdFlow — Campus Water Intelligence Platform                              ║
# ║  Prototype v1.0 · Simulated UAE Campus Data · Pre-Pilot Stage              ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
#
# Requirements:
#   pip install streamlit pandas numpy plotly
#
# Run:
#   streamlit run app.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ──────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="NabdFlow | Campus Water Intelligence",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS — Dark Navy / Cyan Theme
# ──────────────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
/* ── Base ─────────────────────────────────────────────── */
.stApp { background-color: #060d1a; color: #dce8f5; }
[data-testid="stSidebar"] {
    background-color: #0a1220;
    border-right: 1px solid #162844;
}
[data-testid="stSidebar"] .stRadio > label { color: #7a9bbf !important; font-size: 0.8rem; }
[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p { color: #dce8f5; }

/* ── Typography ───────────────────────────────────────── */
h1, h2, h3 { color: #00d4ff !important; }
.page-title {
    font-size: 1.7rem; font-weight: 700; color: #dce8f5;
    line-height: 1.3; margin-bottom: 2px;
}
.page-sub {
    font-size: 0.84rem; color: #5a7a9a; margin-bottom: 18px;
}

/* ── Metric Card ──────────────────────────────────────── */
.kpi-card {
    background: linear-gradient(145deg, #0c1e38, #091628);
    border: 1px solid #162844;
    border-radius: 14px;
    padding: 18px 14px;
    text-align: center;
}
.kpi-value  { font-size: 1.85rem; font-weight: 700; color: #00d4ff; }
.kpi-unit   { font-size: 0.85rem; color: #4a6a8a; }
.kpi-label  {
    font-size: 0.72rem; color: #4a6a8a;
    text-transform: uppercase; letter-spacing: 0.07em;
    margin-top: 5px;
}

/* ── Section Header ───────────────────────────────────── */
.sec-header {
    font-size: 1rem; font-weight: 600; color: #00d4ff;
    border-bottom: 1px solid #162844;
    padding-bottom: 6px; margin: 20px 0 12px;
}

/* ── Disclaimer ───────────────────────────────────────── */
.disclaimer {
    background: #091628;
    border-left: 3px solid #00d4ff;
    border-radius: 6px;
    padding: 10px 14px;
    font-size: 0.8rem; color: #7a9bbf;
    margin: 0 0 18px;
    line-height: 1.55;
}

/* ── Zone Row ─────────────────────────────────────────── */
.zone-row {
    background: #0c1e38;
    border: 1px solid #162844;
    border-radius: 10px;
    padding: 13px 18px;
    margin: 5px 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
}

/* ── Alert cards ──────────────────────────────────────── */
.alert-leak    { background:#1c0808; border-left:4px solid #ff4040; border-radius:10px; padding:14px 18px; margin:7px 0; }
.alert-anomaly { background:#1c1008; border-left:4px solid #f87171; border-radius:10px; padding:14px 18px; margin:7px 0; }
.alert-warning { background:#1a1608; border-left:4px solid #fbbf24; border-radius:10px; padding:14px 18px; margin:7px 0; }

/* ── Insight card ─────────────────────────────────────── */
.insight-high   { background:#180606; border-left:4px solid #ff4040; border-radius:10px; padding:15px 18px; margin:9px 0; }
.insight-medium { background:#181206; border-left:4px solid #fbbf24; border-radius:10px; padding:15px 18px; margin:9px 0; }
.insight-low    { background:#06101a; border-left:4px solid #00d4ff; border-radius:10px; padding:15px 18px; margin:9px 0; }

/* ── Chat ─────────────────────────────────────────────── */
.chat-user {
    background:#0c2040; border:1px solid #1e4a7a;
    border-radius:14px 14px 4px 14px;
    padding:10px 15px; max-width:76%;
    font-size:0.88rem; color:#dce8f5;
    margin-left:auto; margin-bottom:8px;
}
.chat-bot {
    background:#091628; border:1px solid #162844;
    border-radius:4px 14px 14px 14px;
    padding:12px 15px; max-width:82%;
    font-size:0.86rem; color:#b0c8e0; line-height:1.65;
    margin-bottom:8px;
}

/* ── Misc ─────────────────────────────────────────────── */
#MainMenu {visibility:hidden;} footer {visibility:hidden;}
.note-xs { font-size: 0.7rem; color: #3a5a7a; margin-top: 3px; }
.stTextInput input { background:#091628 !important; color:#dce8f5 !important; border:1px solid #162844 !important; }
.stSelectbox [data-baseweb="select"] { background:#091628 !important; }
.stForm { border: none !important; }
div[data-testid="stFormSubmitButton"] button {
    background: #00d4ff !important; color: #060d1a !important;
    font-weight: 700 !important; border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ──────────────────────────────────────────────────────────────────────────────

ZONES = [
    "Main Academic Building",
    "Science & Technology Block",
    "Student Housing A",
    "Student Housing B",
    "Sports Complex",
    "Library & Research Area",
    "Cafeteria & Dining",
    "Administration & Offices",
]

WATER_TARIFF_AED = 12.5   # AED per m³ (indicative UAE municipal rate)
CO2_FACTOR       = 0.30   # kg CO₂-eq per m³ (UAE desalination energy estimate, indicative)


# ──────────────────────────────────────────────────────────────────────────────
# SIMULATED DATA GENERATOR
# ──────────────────────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def generate_simulated_data() -> pd.DataFrame:
    """
    Generate 30 days of daily simulated UAE university campus water data.
    Anomalies are deliberately injected for demonstration purposes.
    """
    np.random.seed(42)
    base_date = datetime(2025, 3, 1)

    zone_profiles = {
        "Main Academic Building":    {"b": 85,  "noise": 0.10, "ah_risk": 0.03},
        "Science & Technology Block":{"b": 55,  "noise": 0.09, "ah_risk": 0.02},
        "Student Housing A":         {"b": 120, "noise": 0.07, "ah_risk": 0.01},
        "Student Housing B":         {"b": 115, "noise": 0.08, "ah_risk": 0.01},
        "Sports Complex":            {"b": 70,  "noise": 0.13, "ah_risk": 0.04},
        "Library & Research Area":   {"b": 30,  "noise": 0.09, "ah_risk": 0.02},
        "Cafeteria & Dining":        {"b": 95,  "noise": 0.11, "ah_risk": 0.05},
        "Administration & Offices":  {"b": 40,  "noise": 0.09, "ah_risk": 0.03},
    }

    records = []
    for day in range(30):
        date = base_date + timedelta(days=day)
        is_weekend = date.weekday() >= 4  # Fri–Sat in UAE

        for zone, p in zone_profiles.items():
            baseline = p["b"]
            if is_weekend:
                baseline *= 0.4 if "Housing" not in zone else 0.88

            mult = 1.0
            inject_leak = False

            # Inject deliberate anomalies for prototype demonstration
            if zone == "Cafeteria & Dining"        and day in [7, 8, 22, 23]:      mult = 1.62
            if zone == "Sports Complex"            and day in [14, 15, 16]:        mult = 1.47
            if zone == "Science & Technology Block" and day >= 20:
                mult = 1.36
                inject_leak = day >= 25
            if zone == "Student Housing B"         and day in [10, 11, 12]:        mult = 1.27

            actual = max(0, baseline * mult * (1 + np.random.normal(0, p["noise"])))

            records.append({
                "Zone":                zone,
                "Date":                date.strftime("%Y-%m-%d"),
                "Actual_Consumption":  round(actual, 2),
                "Baseline_Consumption":round(baseline, 2),
                "Is_Weekend":          is_weekend,
                "_inject_leak":        inject_leak,
            })

    df = pd.DataFrame(records)
    df = _add_derived_columns(df)
    return df


def _add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Deviation_Pct"] = (
        (df["Actual_Consumption"] - df["Baseline_Consumption"])
        / df["Baseline_Consumption"] * 100
    ).round(1)

    def _status(row):
        if row.get("_inject_leak", False):
            return "Potential Leak"
        dev = row["Deviation_Pct"]
        if dev > 40:  return "Anomaly"
        if dev > 15:  return "Warning"
        return "Normal"

    df["Status"] = df.apply(_status, axis=1)
    df["Avoidable_Waste_m3"] = df.apply(
        lambda r: max(0, r["Actual_Consumption"] - r["Baseline_Consumption"] * 1.10)
        if r["Status"] != "Normal" else 0, axis=1
    ).round(2)
    df["Avoidable_Cost_AED"] = (df["Avoidable_Waste_m3"] * WATER_TARIFF_AED).round(2)
    return df


# ──────────────────────────────────────────────────────────────────────────────
# HELPER RENDERERS
# ──────────────────────────────────────────────────────────────────────────────

STATUS_COLORS = {
    "Normal":         ("#4ade80", "#1a4a2e"),
    "Warning":        ("#fbbf24", "#4a3a0a"),
    "Anomaly":        ("#f87171", "#4a1a0a"),
    "Potential Leak": ("#ff4040", "#5a0808"),
}


def badge(status: str) -> str:
    fg, bg = STATUS_COLORS.get(status, ("#ffffff", "#222"))
    return (f'<span style="background:{bg};color:{fg};padding:3px 11px;'
            f'border-radius:20px;font-size:0.78rem;font-weight:600">{status}</span>')


def kpi(label: str, value, unit: str = "") -> str:
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}<span class="kpi-unit"> {unit}</span></div>
    </div>"""


def disc(text: str):
    st.markdown(f'<div class="disclaimer">ℹ️ {text}</div>', unsafe_allow_html=True)


def chart_layout(fig, title="", height=340):
    fig.update_layout(
        title=title, height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(9,22,40,0.7)",
        font=dict(color="#8aaac8", size=11),
        title_font=dict(color="#00d4ff", size=13),
        legend=dict(bgcolor="rgba(0,0,0,0)", font_color="#8aaac8"),
        xaxis=dict(gridcolor="#162844", linecolor="#162844", tickfont_color="#5a7a9a"),
        yaxis=dict(gridcolor="#162844", linecolor="#162844", tickfont_color="#5a7a9a"),
        margin=dict(l=40, r=20, t=46, b=36),
    )
    return fig


# ──────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────────────────────────────────────────

if "uploaded_data" not in st.session_state:
    st.session_state.uploaded_data = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ──────────────────────────────────────────────────────────────────────────────
# ACTIVE DATASET
# ──────────────────────────────────────────────────────────────────────────────

df = (st.session_state.uploaded_data
      if st.session_state.uploaded_data is not None
      else generate_simulated_data())

# Zone-level aggregate (full 30-day window)
zone_agg = df.groupby("Zone").agg(
    Total_Actual     =("Actual_Consumption",  "sum"),
    Total_Baseline   =("Baseline_Consumption","sum"),
    Avg_Deviation    =("Deviation_Pct",        "mean"),
    Total_Waste      =("Avoidable_Waste_m3",   "sum"),
    Total_Cost       =("Avoidable_Cost_AED",   "sum"),
    Last_Status      =("Status",               "last"),
).reset_index()


# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:22px 0 10px">
        <div style="font-size:2rem">💧</div>
        <div style="font-size:1.45rem;font-weight:700;color:#00d4ff;letter-spacing:0.04em">NabdFlow</div>
        <div style="font-size:0.72rem;color:#4a6a8a;margin-top:3px">Campus Water Intelligence</div>
    </div>
    <hr style="border-color:#162844;margin:8px 0 16px">
    """, unsafe_allow_html=True)

    page = st.radio(
        "nav",
        [
            "🏠  Campus Overview",
            "🗺️  Zone Intelligence",
            "🚨  Alert Center",
            "🤖  AI Insights Engine",
            "🌿  Sustainability Hub",
            "🧪  Pilot Validation",
            "📂  Data Upload",
            "💬  AI Chat Assistant",
        ],
        label_visibility="collapsed",
    )

    st.markdown("<hr style='border-color:#162844;margin:14px 0 10px'>", unsafe_allow_html=True)
    data_label = "Uploaded CSV" if st.session_state.uploaded_data is not None else "Simulated UAE Campus Data"
    st.markdown(f"""
    <div style="font-size:0.7rem;color:#3a5a7a;line-height:1.9;padding:4px 0">
        <b style="color:#5a7a9a">Data Source:</b> {data_label}<br>
        <b style="color:#5a7a9a">Version:</b> Prototype v1.0<br>
        <b style="color:#5a7a9a">Stage:</b> Pre-Pilot Validation<br>
        <b style="color:#5a7a9a">Campus:</b> UAE University Campus
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — CAMPUS OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════

if "Campus Overview" in page:
    st.markdown('<div class="page-title">Campus Overview Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">UAE University Campus · 30-Day Simulation Window · Prototype Demonstration</div>', unsafe_allow_html=True)
    disc("Current results are prototype demonstration outputs based on simulated UAE campus water data. "
         "Real-world savings will only be claimed after pilot validation using actual campus meter data.")

    total_actual  = df["Actual_Consumption"].sum()
    total_waste   = df["Avoidable_Waste_m3"].sum()
    total_cost    = df["Avoidable_Cost_AED"].sum()
    active_alerts = zone_agg[zone_agg["Last_Status"] != "Normal"].shape[0]
    eff_score     = max(0, min(100, round(100 - (total_waste / total_actual * 100), 1)))

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.markdown(kpi("Total Consumption",       f"{total_actual/1000:.1f}", "k m³"),  unsafe_allow_html=True)
    with c2: st.markdown(kpi("Water Efficiency Score",  f"{eff_score}",            "/ 100"), unsafe_allow_html=True)
    with c3: st.markdown(kpi("Alert Zones",             f"{active_alerts}",        "zones"),  unsafe_allow_html=True)
    with c4: st.markdown(kpi("Est. Avoidable Waste",    f"{total_waste:.0f}",      "m³ *"),   unsafe_allow_html=True)
    with c5: st.markdown(kpi("Est. Avoidable Cost",     f"{total_cost:,.0f}",      "AED *"),  unsafe_allow_html=True)

    st.markdown('<div class="note-xs">* Estimated figures based on simulated data. Require pilot validation before formal reporting.</div>', unsafe_allow_html=True)
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Trend + Donut
    col_l, col_r = st.columns([2.1, 1])

    with col_l:
        daily = df.groupby("Date").agg(Actual=("Actual_Consumption","sum"),
                                        Baseline=("Baseline_Consumption","sum")).reset_index()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=daily["Date"], y=daily["Baseline"],
                                  name="Expected Baseline",
                                  line=dict(color="#2a5a8a", dash="dash", width=1.8)))
        fig.add_trace(go.Scatter(x=daily["Date"], y=daily["Actual"],
                                  name="Actual Consumption",
                                  line=dict(color="#00d4ff", width=2.5),
                                  fill="tonexty", fillcolor="rgba(0,212,255,0.07)"))
        fig = chart_layout(fig, "Campus-Wide Daily Water Consumption vs Baseline (m³)", 300)
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        sc = df.groupby("Status").size().reset_index(name="Count")
        cmap = {"Normal":"#4ade80","Warning":"#fbbf24","Anomaly":"#f87171","Potential Leak":"#ff4040"}
        fig2 = px.pie(sc, values="Count", names="Status", color="Status",
                      color_discrete_map=cmap, hole=0.52)
        fig2.update_traces(textposition="inside", textinfo="percent+label",
                           textfont_size=10, pull=[0.03]*len(sc))
        fig2 = chart_layout(fig2, "Status Distribution", 300)
        st.plotly_chart(fig2, use_container_width=True)

    # ── Zone summary
    st.markdown('<div class="sec-header">Zone-Level Summary</div>', unsafe_allow_html=True)
    for _, row in zone_agg.sort_values("Avg_Deviation", ascending=False).iterrows():
        dv_color = ("#4ade80" if row["Avg_Deviation"] <= 10
                    else "#fbbf24" if row["Avg_Deviation"] <= 25
                    else "#f87171")
        st.markdown(f"""
        <div class="zone-row">
            <div style="min-width:210px">
                <div style="font-weight:600;color:#dce8f5">{row['Zone']}</div>
                <div style="font-size:0.76rem;color:#4a6a8a;margin-top:2px">
                    {row['Total_Actual']:.0f} m³ consumed (30 days)
                </div>
            </div>
            <div style="text-align:center">
                <div style="font-size:0.7rem;color:#4a6a8a">Avg Deviation</div>
                <div style="font-weight:700;color:{dv_color}">{row['Avg_Deviation']:+.1f}%</div>
            </div>
            <div style="text-align:center">
                <div style="font-size:0.7rem;color:#4a6a8a">Est. Avoidable Waste</div>
                <div style="font-weight:700;color:#00d4ff">{row['Total_Waste']:.1f} m³ *</div>
            </div>
            <div>{badge(row['Last_Status'])}</div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — ZONE INTELLIGENCE
# ══════════════════════════════════════════════════════════════════════════════

elif "Zone Intelligence" in page:
    st.markdown('<div class="page-title">Zone Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Consumption baseline comparison and zone-level status analysis</div>', unsafe_allow_html=True)
    disc("Zone statuses are derived from simulated baseline deviation logic. "
         "Real deployment requires calibrated baselines from historical meter data.")

    sel = st.selectbox("Select Campus Zone", ZONES)
    zdf = df[df["Zone"] == sel].copy()
    zdf["Date"] = pd.to_datetime(zdf["Date"])

    z_total   = zdf["Actual_Consumption"].sum()
    z_waste   = zdf["Avoidable_Waste_m3"].sum()
    z_cost    = zdf["Avoidable_Cost_AED"].sum()
    z_dev     = zdf["Deviation_Pct"].mean()
    z_status  = zdf["Status"].value_counts().idxmax()

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(kpi("30-Day Consumption", f"{z_total:.0f}", "m³"),         unsafe_allow_html=True)
    with c2: st.markdown(kpi("Avg vs Baseline",    f"{z_dev:+.1f}", "%"),           unsafe_allow_html=True)
    with c3: st.markdown(kpi("Est. Avoidable Waste",f"{z_waste:.0f}", "m³ *"),      unsafe_allow_html=True)
    with c4: st.markdown(kpi("Est. Avoidable Cost", f"{z_cost:,.0f}", "AED *"),     unsafe_allow_html=True)

    # Status explanation
    explanations = {
        "Normal":         ("#4ade80", "✅", "Consumption is within the expected operational range. No immediate action required."),
        "Warning":        ("#fbbf24", "⚠️", "Consumption is moderately above baseline. Recommend monitoring and investigating possible inefficiencies."),
        "Anomaly":        ("#f87171", "🔴", "Significant deviation from baseline detected. Facilities team should investigate potential equipment faults or occupancy changes."),
        "Potential Leak": ("#ff4040", "🚨", "Persistent or after-hours high-usage pattern detected. This is an early warning signal — not a confirmed leak. Physical inspection of this zone is strongly recommended."),
    }
    color, icon, explanation = explanations.get(z_status, ("#8899aa", "ℹ️", ""))
    st.markdown(f"""
    <div style="background:#0c1e38;border:1px solid {color};border-radius:10px;padding:15px 18px;margin:14px 0">
        <div style="font-weight:700;color:{color};margin-bottom:6px">{icon} Zone Status: {z_status}</div>
        <div style="font-size:0.86rem;color:#b0c8e0">{explanation}</div>
    </div>""", unsafe_allow_html=True)

    # Consumption chart
    fig = go.Figure()
    fig.add_trace(go.Bar(x=zdf["Date"], y=zdf["Baseline_Consumption"],
                          name="Baseline", marker_color="#1e4a7a", opacity=0.75))
    fig.add_trace(go.Scatter(x=zdf["Date"], y=zdf["Actual_Consumption"],
                              name="Actual", line=dict(color="#00d4ff", width=2.2),
                              mode="lines+markers", marker=dict(size=4.5)))
    fig = chart_layout(fig, f"{sel} — Daily Consumption vs Baseline (m³)", 320)
    st.plotly_chart(fig, use_container_width=True)

    # Deviation chart
    c_map = zdf["Status"].map({k:v[0] for k,v in STATUS_COLORS.items()})
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=zdf["Date"], y=zdf["Deviation_Pct"],
                           marker_color=c_map, name="Deviation %"))
    fig2.add_hline(y=15, line_dash="dash", line_color="#fbbf24",
                   annotation_text="Warning +15%", annotation_font_color="#fbbf24")
    fig2.add_hline(y=40, line_dash="dash", line_color="#f87171",
                   annotation_text="Anomaly +40%", annotation_font_color="#f87171")
    fig2.add_hline(y=0,  line_color="#162844", line_width=1)
    fig2 = chart_layout(fig2, f"{sel} — Daily Deviation from Baseline (%)", 260)
    st.plotly_chart(fig2, use_container_width=True)

    # High-risk all-zone summary
    st.markdown('<div class="sec-header">⚡ High-Risk Zones (Campus-Wide)</div>', unsafe_allow_html=True)
    hi = zone_agg[zone_agg["Last_Status"].isin(["Anomaly","Potential Leak"])].sort_values("Avg_Deviation", ascending=False)
    if hi.empty:
        st.success("No high-risk zones detected in the current dataset.")
    else:
        for _, r in hi.iterrows():
            c = STATUS_COLORS[r["Last_Status"]][0]
            st.markdown(f"""
            <div style="background:#150606;border-left:4px solid {c};border-radius:9px;
                 padding:12px 16px;margin:6px 0;display:flex;justify-content:space-between;
                 align-items:center;flex-wrap:wrap;gap:8px">
                <div>
                    <span style="font-weight:600;color:#dce8f5">{r['Zone']}</span>
                    <span style="font-size:0.77rem;color:#5a7a9a;margin-left:10px">
                        Avg deviation: {r['Avg_Deviation']:+.1f}%
                    </span>
                </div>
                {badge(r['Last_Status'])}
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — ALERT CENTER
# ══════════════════════════════════════════════════════════════════════════════

elif "Alert Center" in page:
    st.markdown('<div class="page-title">Anomaly & Alert Center</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Prioritized investigation signals for facility and operations teams</div>', unsafe_allow_html=True)
    disc("Alerts shown by NabdFlow indicate abnormal consumption patterns or possible leak-prone zones. "
         "They should be treated as investigation signals, not confirmed leak diagnoses.")

    n_leak    = zone_agg[zone_agg["Last_Status"] == "Potential Leak"].shape[0]
    n_anomaly = zone_agg[zone_agg["Last_Status"] == "Anomaly"].shape[0]
    n_warning = zone_agg[zone_agg["Last_Status"] == "Warning"].shape[0]

    ca, cb, cc = st.columns(3)
    with ca:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#1c0404,#120303);border:1px solid #5a1010;
             border-radius:13px;padding:20px;text-align:center">
            <div style="font-size:2rem;font-weight:700;color:#ff4040">{n_leak}</div>
            <div style="font-size:0.78rem;color:#cc7070;text-transform:uppercase;margin-top:2px">Potential Leak Zones</div>
            <div style="font-size:0.7rem;color:#7a4040;margin-top:4px">Immediate inspection recommended</div>
        </div>""", unsafe_allow_html=True)
    with cb:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#1c0c04,#120804);border:1px solid #5a2010;
             border-radius:13px;padding:20px;text-align:center">
            <div style="font-size:2rem;font-weight:700;color:#f87171">{n_anomaly}</div>
            <div style="font-size:0.78rem;color:#cc9080;text-transform:uppercase;margin-top:2px">Anomaly Zones</div>
            <div style="font-size:0.7rem;color:#7a5040;margin-top:4px">Investigate consumption changes</div>
        </div>""", unsafe_allow_html=True)
    with cc:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#1a1604,#121003);border:1px solid #5a3a08;
             border-radius:13px;padding:20px;text-align:center">
            <div style="font-size:2rem;font-weight:700;color:#fbbf24">{n_warning}</div>
            <div style="font-size:0.78rem;color:#ccaa60;text-transform:uppercase;margin-top:2px">Warning Zones</div>
            <div style="font-size:0.7rem;color:#7a6030;margin-top:4px">Monitor closely</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    alert_meta = {
        "Potential Leak": {
            "css": "alert-leak", "color": "#ff4040",
            "label": "🔴 HIGH PRIORITY",
            "action": "Conduct an immediate physical inspection of water mains, fixtures, and pipes in this zone. Check for after-hours flow on automated metering if available.",
        },
        "Anomaly": {
            "css": "alert-anomaly", "color": "#f87171",
            "label": "🟠 MEDIUM PRIORITY",
            "action": "Review usage logs and check for equipment changes, scheduled events, or significant occupancy shifts that could explain the spike.",
        },
        "Warning": {
            "css": "alert-warning", "color": "#fbbf24",
            "label": "🟡 LOW PRIORITY",
            "action": "Monitor trend over the next 3–5 days. Escalate if deviation persists or worsens.",
        },
    }

    for status_type, meta in alert_meta.items():
        flagged = zone_agg[zone_agg["Last_Status"] == status_type].sort_values("Avg_Deviation", ascending=False)
        if flagged.empty:
            continue
        st.markdown(f'<div style="font-size:0.9rem;font-weight:600;color:{meta["color"]};margin:18px 0 8px">{meta["label"]}</div>',
                    unsafe_allow_html=True)
        for _, r in flagged.iterrows():
            st.markdown(f"""
            <div class="{meta['css']}">
                <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;align-items:flex-start">
                    <div style="flex:1;min-width:200px">
                        <div style="font-weight:700;color:#dce8f5;font-size:0.95rem">{r['Zone']}</div>
                        <div style="font-size:0.8rem;color:#7a9abb;margin-top:5px">
                            Avg deviation: <b style="color:{meta['color']}">{r['Avg_Deviation']:+.1f}%</b>
                            &nbsp;|&nbsp; Est. avoidable waste: <b style="color:#00d4ff">{r['Total_Waste']:.1f} m³ *</b>
                            &nbsp;|&nbsp; Est. cost impact: <b style="color:#00d4ff">{r['Total_Cost']:,.0f} AED *</b>
                        </div>
                        <div style="background:rgba(255,255,255,0.04);border-radius:6px;
                             padding:8px 12px;margin-top:10px;font-size:0.81rem;color:#9ab8d0">
                            <b>Recommended Action:</b> {meta['action']}
                        </div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

    # Timeline
    st.markdown('<div class="sec-header">📅 Alert Timeline (30-Day View)</div>', unsafe_allow_html=True)
    at = df[df["Status"] != "Normal"].groupby(["Date","Status"]).size().reset_index(name="Count")
    cmap2 = {"Warning":"#fbbf24","Anomaly":"#f87171","Potential Leak":"#ff4040"}
    fig = px.bar(at, x="Date", y="Count", color="Status", color_discrete_map=cmap2, barmode="stack")
    fig = chart_layout(fig, "Daily Alert Events by Status Type", 270)
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — AI INSIGHTS ENGINE
# ══════════════════════════════════════════════════════════════════════════════

elif "AI Insights" in page:
    st.markdown('<div class="page-title">AI Insights Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Data-driven decision-support insights for facility and sustainability teams</div>', unsafe_allow_html=True)
    disc("NabdFlow is currently in the validation stage. Insights are decision-support outputs generated from simulated data. "
         "Verified findings require real meter data, facility team feedback, and pilot testing.")

    leak_zones    = zone_agg[zone_agg["Last_Status"] == "Potential Leak"]["Zone"].tolist()
    anomaly_zones = zone_agg[zone_agg["Last_Status"] == "Anomaly"]["Zone"].tolist()
    top_waste_z   = zone_agg.loc[zone_agg["Total_Waste"].idxmax(), "Zone"]
    total_waste   = df["Avoidable_Waste_m3"].sum()
    total_cost    = df["Avoidable_Cost_AED"].sum()
    priority_zone = leak_zones[0] if leak_zones else (anomaly_zones[0] if anomaly_zones else top_waste_z)

    insights = [
        {
            "icon": "🔍",
            "urg": "high",
            "title": f"Priority Investigation Zone: {priority_zone}",
            "body": (
                f"{'This zone exhibits a persistent after-hours usage pattern that significantly exceeds its expected baseline — a common early signal of slow leaks, irrigation timer faults, or open water lines.'  if leak_zones else 'This zone records the highest average deviation from its expected baseline across the 30-day simulation window.'} "
                "Physical inspection is the recommended first response."
            ),
            "action": "Assign the facilities team to conduct a site walkthrough and check for dripping fixtures, malfunctioning irrigation systems, or unclosed water lines. Log findings for pilot validation records.",
        },
        {
            "icon": "💧",
            "urg": "medium",
            "title": f"Estimated Avoidable Waste: {total_waste:.0f} m³ over 30 Days",
            "body": (
                f"Based on baseline deviation analysis, an estimated {total_waste:.0f} m³ of water may represent avoidable consumption above the expected operational threshold. "
                "This is a prototype estimate — real-world verification requires pilot validation with actual meter data."
            ),
            "action": f"Prioritize zones flagged as Anomaly or Potential Leak. Review each individually to distinguish between operational changes, occupancy spikes, and actual infrastructure issues.",
        },
        {
            "icon": "💰",
            "urg": "medium",
            "title": f"Estimated Cost Impact: {total_cost:,.0f} AED over 30 Days",
            "body": (
                f"Applying a UAE municipal water tariff estimate of {WATER_TARIFF_AED} AED/m³, the estimated avoidable waste corresponds to approximately {total_cost:,.0f} AED. "
                "These figures are indicative only and are based on simulated data."
            ),
            "action": "Use this figure as a preliminary justification for a pilot validation project. Present to facilities management and finance teams alongside the prototype methodology.",
        },
        {
            "icon": "🕐",
            "urg": "high" if leak_zones else "medium",
            "title": "After-Hours Usage Patterns Detected",
            "body": (
                "Certain zones in the simulation show elevated consumption during expected non-operational hours. "
                "This pattern is commonly associated with slow infrastructure leaks, irrigation timer misconfiguration, or HVAC condensate drainage faults."
            ),
            "action": "Cross-reference consumption timestamps with building occupancy and HVAC schedules. "
                      "Consider installing automated post-hours flow alerts at the zone meter level during the pilot phase.",
        },
        {
            "icon": "📊",
            "urg": "low",
            "title": f"Highest Estimated Waste Zone: {top_waste_z}",
            "body": (
                f"{top_waste_z} accounts for the largest share of estimated avoidable waste in this simulation. "
                "This may reflect higher baseline activity, unmetered sub-zones, or water-intensive equipment operation patterns."
            ),
            "action": "Review operational schedules in this zone. Consider sub-meter installation or flow sensor deployment in the pilot phase to improve data granularity.",
        },
        {
            "icon": "📈",
            "urg": "low",
            "title": "Baseline Calibration Recommendation",
            "body": (
                "In this prototype, baselines are set as fixed reference values per zone. "
                "In a real deployment, baselines should be dynamically calibrated using historical data, segmented by weekday/weekend, occupancy, and UAE seasonal factors."
            ),
            "action": "During the pilot phase, collect at least 3 months of real meter data before establishing zone-specific consumption baselines. "
                      "Segment by working/non-working hours and validate against facilities team knowledge.",
        },
    ]

    urg_meta = {
        "high":   ("insight-high",   "#ff4040", "🔴 High Priority"),
        "medium": ("insight-medium", "#fbbf24", "🟡 Medium Priority"),
        "low":    ("insight-low",    "#00d4ff", "🔵 Informational"),
    }

    for ins in insights:
        css, color, label = urg_meta[ins["urg"]]
        st.markdown(f"""
        <div class="{css}">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;flex-wrap:wrap">
                <span style="font-size:1.25rem">{ins['icon']}</span>
                <span style="font-weight:700;color:{color};font-size:0.92rem">{ins['title']}</span>
                <span style="font-size:0.7rem;color:#3a5a7a;margin-left:auto">{label}</span>
            </div>
            <div style="font-size:0.84rem;color:#b0c8e0;line-height:1.65;margin-bottom:10px">{ins['body']}</div>
            <div style="background:rgba(255,255,255,0.04);border-radius:7px;padding:9px 13px;
                 font-size:0.81rem;color:#8aaac8">
                <b style="color:#00d4ff">Recommended Action: </b>{ins['action']}
            </div>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — SUSTAINABILITY HUB
# ══════════════════════════════════════════════════════════════════════════════

elif "Sustainability Hub" in page:
    st.markdown('<div class="page-title">Sustainability Hub</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Sustainability indicators, SDG alignment, and UAE national strategy mapping</div>', unsafe_allow_html=True)
    disc("All sustainability indicators are estimated from simulated prototype data. "
         "Verified contributions to UAE sustainability goals require pilot validation using real campus meter data.")

    total_actual = df["Actual_Consumption"].sum()
    total_waste  = df["Avoidable_Waste_m3"].sum()
    total_cost   = df["Avoidable_Cost_AED"].sum()
    co2_saving   = total_waste * CO2_FACTOR

    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(kpi("Est. Avoidable Waste",       f"{total_waste:.0f}",  "m³ *"),    unsafe_allow_html=True)
    with c2: st.markdown(kpi("Water Use Intensity",        f"{total_actual/30:.0f}", "m³/day *"), unsafe_allow_html=True)
    with c3: st.markdown(kpi("Indicative CO₂-eq Savings",  f"{co2_saving:.0f}",  "kg *"),     unsafe_allow_html=True)

    st.markdown('<div class="note-xs">* Prototype estimates. CO₂ factor: ~0.30 kg CO₂-eq per m³ (UAE desalination energy, indicative). All figures require pilot validation.</div>',
                unsafe_allow_html=True)

    # ── SDG Alignment
    st.markdown('<div class="sec-header">🌍 SDG Alignment</div>', unsafe_allow_html=True)

    sdgs = [
        {
            "num": "SDG 6", "name": "Clean Water and Sanitation", "color": "#1e88e5", "icon": "💧",
            "target": "Target 6.4 — Substantially increase water-use efficiency across all sectors by 2030.",
            "text": ("NabdFlow supports SDG 6 by equipping campus facility teams with tools to identify and "
                     "reduce avoidable water waste, improving the efficiency of freshwater use in an already "
                     "water-scarce UAE environment. Efficient campus water management is a direct, measurable "
                     "contribution to this goal."),
        },
        {
            "num": "SDG 11", "name": "Sustainable Cities and Communities", "color": "#fb8c00", "icon": "🏙️",
            "target": "Target 11.6 — Reduce the environmental impact of cities, including resource consumption.",
            "text": ("Smart campus water monitoring supports the development of data-driven, resource-efficient "
                     "institutions — a foundational element of sustainable communities and smart city infrastructure. "
                     "Universities as institutional hubs can model best practices for the broader urban environment."),
        },
        {
            "num": "SDG 13", "name": "Climate Action", "color": "#43a047", "icon": "🌱",
            "target": "Target 13.3 — Improve education, awareness, and institutional capacity on climate mitigation.",
            "text": ("Water desalination in the UAE is highly energy-intensive. Reducing avoidable water consumption "
                     "indirectly reduces carbon emissions. NabdFlow contributes to campus-level climate action "
                     "through demand-side water efficiency and by building institutional data capacity for "
                     "evidence-based sustainability decision-making."),
        },
    ]

    for sdg in sdgs:
        st.markdown(f"""
        <div style="background:#0c1e38;border:1px solid #162844;border-radius:12px;padding:15px 18px;margin:8px 0">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:9px">
                <span style="font-size:1.5rem">{sdg['icon']}</span>
                <div>
                    <div style="font-weight:700;color:{sdg['color']};font-size:0.92rem">{sdg['num']}: {sdg['name']}</div>
                    <div style="font-size:0.72rem;color:#3a5a7a;margin-top:2px">{sdg['target']}</div>
                </div>
            </div>
            <div style="font-size:0.84rem;color:#b0c8e0;line-height:1.65">{sdg['text']}</div>
        </div>""", unsafe_allow_html=True)

    # ── UAE Strategies
    st.markdown('<div class="sec-header">🇦🇪 UAE National Strategy Alignment</div>', unsafe_allow_html=True)

    strategies = [
        {
            "name": "UAE Water Security Strategy 2036",
            "icon": "🌊", "color": "#00b4d8",
            "text": ("NabdFlow aligns with the UAE's commitment to improving water-use efficiency and reducing "
                     "non-revenue water loss across all sectors. By providing early detection of abnormal "
                     "consumption patterns and actionable facility-team insights, the platform supports "
                     "data-driven water stewardship at the institutional level — a key pillar of the 2036 strategy."),
        },
        {
            "name": "UAE Net Zero 2050 Strategic Initiative",
            "icon": "♻️", "color": "#4caf50",
            "text": ("The UAE Net Zero 2050 strategy requires sector-wide reductions in resource consumption "
                     "and associated emissions. University campuses, as significant energy and water consumers, "
                     "have a direct role to play. NabdFlow's efficiency insights contribute to this national "
                     "decarbonization pathway through campus-level demand-side water management."),
        },
    ]

    for s in strategies:
        st.markdown(f"""
        <div style="background:#0c1e38;border-left:4px solid {s['color']};border-radius:10px;
             padding:15px 18px;margin:8px 0">
            <div style="font-weight:700;color:{s['color']};margin-bottom:8px">{s['icon']} {s['name']}</div>
            <div style="font-size:0.84rem;color:#b0c8e0;line-height:1.65">{s['text']}</div>
        </div>""", unsafe_allow_html=True)

    # ── Evidence section
    st.markdown('<div class="sec-header">📚 Evidence & Alignment Notes</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#091628;border:1px solid #162844;border-radius:10px;
         padding:15px 20px;font-size:0.82rem;color:#7a9abb;line-height:1.85">
        <ul style="margin:0;padding-left:20px">
            <li>AI and machine learning are increasingly applied to water network monitoring, anomaly detection,
                and demand forecasting — supporting more efficient and adaptive infrastructure management worldwide.</li>
            <li>The UAE ranks among the world's most water-scarce nations, with per-capita freshwater availability
                far below the global average, making institutional efficiency a national security priority.</li>
            <li>University campuses are significant water consumers, with substantial potential for demand-side
                reduction through smart monitoring, occupancy-aware scheduling, and behavioral insights.</li>
            <li>NabdFlow is currently in the pre-pilot prototype stage. All savings potential figures are
                indicative and based on simulated data. They must not be used in formal sustainability
                reporting until validated through a real-data pilot.</li>
        </ul>
    </div>""", unsafe_allow_html=True)

    # ── Waste bar chart
    st.markdown('<div class="sec-header">Estimated Avoidable Waste by Zone (Prototype, m³)</div>', unsafe_allow_html=True)
    wbz = zone_agg[zone_agg["Total_Waste"] > 0].sort_values("Total_Waste")
    fig = go.Figure(go.Bar(
        x=wbz["Total_Waste"], y=wbz["Zone"],
        orientation="h", marker=dict(color="#00d4ff", opacity=0.75),
    ))
    fig = chart_layout(fig, "", 280)
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 6 — PILOT VALIDATION
# ══════════════════════════════════════════════════════════════════════════════

elif "Pilot Validation" in page:
    st.markdown('<div class="page-title">Pilot Validation Plan</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Roadmap from simulated prototype to verified real-world deployment</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="background:linear-gradient(135deg,#0c1e38,#091628);border:1px solid #1e4a7a;
         border-radius:13px;padding:20px 22px;margin-bottom:22px">
        <div style="font-size:1.05rem;font-weight:700;color:#00d4ff;margin-bottom:10px">🎯 Pilot Objective</div>
        <div style="font-size:0.88rem;color:#b0c8e0;line-height:1.75">
            NabdFlow's pilot validation stage aims to transition the platform from a simulated-data prototype
            to a data-verified, decision-ready operational tool. The pilot will establish real consumption
            baselines, validate the anomaly detection methodology using actual meter readings, and generate
            the first verified sustainability impact report — produced in collaboration with university
            facility management and sustainability teams.
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sec-header">📋 Pilot Execution Steps</div>', unsafe_allow_html=True)

    steps = [
        ("1", "Select Pilot Zone or Building",
         "Identify one or two high-priority zones (e.g., Cafeteria & Dining or Science & Technology Block) based on data availability and meter accessibility."),
        ("2", "Collect Historical Meter Data",
         "Gather a minimum of 3–6 months of historical water meter readings from the selected zones. Coordinate with facilities management for data access and format specification."),
        ("3", "Upload and Clean the Data",
         "Import meter data into NabdFlow's data upload interface. Handle missing values, remove outliers, and standardize timestamps and consumption units (m³/day)."),
        ("4", "Establish Consumption Baselines",
         "Calculate zone-specific baselines using historical averages, segmented by weekday/weekend, working hours, and occupancy levels. Validate with the facilities team."),
        ("5", "Run Anomaly Detection",
         "Apply NabdFlow's deviation logic to flag abnormal consumption. Tune alert thresholds based on real-world data variability and facilities team domain knowledge."),
        ("6", "Generate AI Recommendations",
         "Produce structured insight reports for the facilities and sustainability teams, highlighting priority investigation zones and recommended corrective actions."),
        ("7", "Review with Facilities and Sustainability Teams",
         "Conduct a structured review session to validate flagged zones, assess recommendation relevance, and refine model sensitivity based on expert feedback."),
        ("8", "Produce Pilot Impact Report",
         "Document confirmed anomalies, verified waste reduction estimates, and stakeholder feedback in a structured impact report for university leadership."),
        ("9", "Improve Model Based on Feedback",
         "Incorporate review findings to refine baseline methodology, alert thresholds, and recommendation language ahead of broader campus rollout."),
    ]

    for num, title, desc in steps:
        st.markdown(f"""
        <div style="display:flex;gap:14px;margin:8px 0;align-items:flex-start">
            <div style="background:#00d4ff;color:#060d1a;border-radius:50%;width:27px;height:27px;
                 display:flex;align-items:center;justify-content:center;
                 font-weight:700;font-size:0.82rem;flex-shrink:0;margin-top:3px">{num}</div>
            <div style="background:#0c1e38;border:1px solid #162844;border-radius:10px;
                 padding:12px 16px;flex:1">
                <div style="font-weight:600;color:#dce8f5;font-size:0.9rem">{title}</div>
                <div style="font-size:0.81rem;color:#5a7a9a;margin-top:4px;line-height:1.6">{desc}</div>
            </div>
        </div>""", unsafe_allow_html=True)

    # Success metrics
    st.markdown('<div class="sec-header">✅ Pilot Success Metrics</div>', unsafe_allow_html=True)

    metrics_p = [
        ("📂", "Data Readiness",
         "Historical meter data successfully uploaded, cleaned, and formatted for at least one campus zone."),
        ("📊", "Baseline Accuracy",
         "Established baselines reflect real operational patterns with <15% unexplained variance."),
        ("🚨", "Anomaly Detection Usefulness",
         "At least one NabdFlow-flagged zone is confirmed by the facilities team as a genuine consumption irregularity."),
        ("👥", "Facility Team Feedback",
         "Formal feedback collected from facilities managers and sustainability officers on platform usefulness."),
        ("📄", "Sustainability Report Quality",
         "A pilot impact report is produced, reviewed, and signed off by university stakeholders."),
        ("🚀", "Readiness for Scale-Up",
         "Pilot findings are sufficient to justify expansion to additional zones or full-campus deployment."),
    ]

    left, right = st.columns(2)
    for i, (icon, title, desc) in enumerate(metrics_p):
        col = left if i % 2 == 0 else right
        with col:
            st.markdown(f"""
            <div style="background:#0c1e38;border:1px solid #162844;border-radius:10px;
                 padding:14px 16px;margin:6px 0">
                <div style="font-size:0.88rem">{icon} <b style="color:#00d4ff">{title}</b></div>
                <div style="font-size:0.79rem;color:#4a6a8a;margin-top:5px;line-height:1.55">{desc}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#0c1e38;border-left:3px solid #4ade80;border-radius:8px;
         padding:14px 18px;margin-top:22px;font-size:0.83rem;color:#5a7a9a;line-height:1.75">
        <b style="color:#4ade80">Current Status:</b>
        NabdFlow is in the pre-pilot prototype stage. The platform demonstrates technical feasibility and
        decision-support potential using simulated UAE campus water data. Pilot validation with real meter
        data is the next critical milestone before verified impact claims can be formally asserted.
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 7 — DATA UPLOAD
# ══════════════════════════════════════════════════════════════════════════════

elif "Data Upload" in page:
    st.markdown('<div class="page-title">Data Upload</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Upload a campus water meter CSV — or use the built-in simulated UAE campus dataset</div>', unsafe_allow_html=True)
    disc("NabdFlow will apply the same anomaly detection and baseline comparison logic to any uploaded dataset. "
         "Ensure your data includes the required columns listed below.")

    c_info, c_up = st.columns([1, 1])

    with c_info:
        st.markdown("""
        <div style="background:#0c1e38;border:1px solid #162844;border-radius:12px;padding:18px 20px">
            <div style="font-weight:700;color:#00d4ff;margin-bottom:12px">📋 Required CSV Columns</div>
            <table style="width:100%;font-size:0.82rem;color:#b0c8e0;border-collapse:collapse">
                <tr style="border-bottom:1px solid #162844">
                    <td style="padding:7px 0;color:#00d4ff;font-weight:600">Column</td>
                    <td style="padding:7px 0;color:#00d4ff;font-weight:600">Description</td>
                </tr>
                <tr style="border-bottom:1px solid #0c1428"><td style="padding:5px 0">Zone</td><td>Campus zone or building name</td></tr>
                <tr style="border-bottom:1px solid #0c1428"><td style="padding:5px 0">Date</td><td>Date in YYYY-MM-DD format</td></tr>
                <tr style="border-bottom:1px solid #0c1428"><td style="padding:5px 0">Actual_Consumption</td><td>Measured water use (m³/day)</td></tr>
                <tr><td style="padding:5px 0">Baseline_Consumption</td><td>Expected water use (m³/day)</td></tr>
            </table>
            <div style="margin-top:14px;font-size:0.8rem;color:#5a7a9a;font-weight:600">Optional Columns</div>
            <div style="font-size:0.79rem;color:#3a5a7a;margin-top:5px;line-height:1.8">
                Building_Type · Working_Hours · Occupancy · Notes
            </div>
            <div style="margin-top:14px;font-size:0.79rem;color:#3a5a7a;line-height:1.6">
                If required columns are missing, NabdFlow will show a clear error message and fall back to simulated data.
            </div>
        </div>""", unsafe_allow_html=True)

    with c_up:
        uploaded = st.file_uploader("Upload CSV", type=["csv"],
                                     help="Must contain Zone, Date, Actual_Consumption, Baseline_Consumption")
        if uploaded:
            try:
                udf = pd.read_csv(uploaded)
                req = ["Zone", "Date", "Actual_Consumption", "Baseline_Consumption"]
                missing_cols = [c for c in req if c not in udf.columns]

                if missing_cols:
                    st.error(f"❌ Missing required columns: **{', '.join(missing_cols)}**\n\n"
                             "Please check your CSV format and re-upload.")
                else:
                    udf["Date"] = pd.to_datetime(udf["Date"]).dt.strftime("%Y-%m-%d")
                    udf["_inject_leak"] = False
                    udf = _add_derived_columns(udf)
                    st.session_state.uploaded_data = udf
                    st.success(f"✅ Uploaded successfully — {len(udf):,} rows, {udf['Zone'].nunique()} zones.")
                    st.dataframe(udf.head(10), use_container_width=True)
            except Exception as e:
                st.error(f"❌ Error reading file: {e}")
        else:
            mode = "Uploaded CSV" if st.session_state.uploaded_data is not None else "Simulated UAE Campus Data"
            st.info(f"Active dataset: **{mode}**")
            if st.session_state.uploaded_data is not None:
                if st.button("🔄 Clear Uploaded Data & Restore Simulated Dataset"):
                    st.session_state.uploaded_data = None
                    st.rerun()

    st.markdown('<div class="sec-header">Preview: Active Dataset (First 25 Rows)</div>', unsafe_allow_html=True)
    display_cols = ["Zone", "Date", "Actual_Consumption", "Baseline_Consumption",
                    "Deviation_Pct", "Status", "Avoidable_Waste_m3", "Avoidable_Cost_AED"]
    st.dataframe(df[display_cols].head(25), use_container_width=True)

    template_csv = generate_simulated_data()[["Zone", "Date", "Actual_Consumption", "Baseline_Consumption"]].to_csv(index=False)
    st.download_button(
        "⬇️ Download CSV Template (Simulated Data)",
        template_csv,
        file_name="nabdflow_template.csv",
        mime="text/csv",
    )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 8 — AI CHAT ASSISTANT
# ══════════════════════════════════════════════════════════════════════════════

elif "AI Chat" in page:
    st.markdown('<div class="page-title">AI Chat Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Ask questions about campus water data — decision-support powered by NabdFlow</div>', unsafe_allow_html=True)
    disc("The AI assistant answers based on the currently loaded prototype data only. "
         "It does not access real-world water systems or external databases. "
         "Responses are decision-support insights, not engineering diagnoses.")

    # Context
    leak_zones    = zone_agg[zone_agg["Last_Status"] == "Potential Leak"]["Zone"].tolist()
    anomaly_zones = zone_agg[zone_agg["Last_Status"] == "Anomaly"]["Zone"].tolist()
    warning_zones = zone_agg[zone_agg["Last_Status"] == "Warning"]["Zone"].tolist()
    total_waste   = df["Avoidable_Waste_m3"].sum()
    total_cost    = df["Avoidable_Cost_AED"].sum()
    priority_zone = leak_zones[0] if leak_zones else (anomaly_zones[0] if anomaly_zones else "Main Academic Building")

    def bot_response(q: str) -> str:
        q = q.lower().strip()

        if any(w in q for w in ["highest risk","most risk","riskiest","priority","inspect first","check first","dangerous"]):
            if leak_zones:
                z = zone_agg[zone_agg["Zone"] == leak_zones[0]].iloc[0]
                return (f"🔴 **{leak_zones[0]}** is the highest-risk zone in the current prototype dataset.\n\n"
                        f"It shows a persistent after-hours usage pattern with an average deviation of "
                        f"**{z['Avg_Deviation']:+.1f}%** above baseline — a common early signal of slow leaks, "
                        f"irrigation faults, or open water lines.\n\n"
                        f"**Recommended action:** Assign the facilities team to physically inspect water supply "
                        f"infrastructure, fixtures, and irrigation systems in this zone.\n\n"
                        f"⚠️ *This is an investigation signal from prototype data, not a confirmed leak diagnosis.*")
            elif anomaly_zones:
                z = zone_agg[zone_agg["Zone"] == anomaly_zones[0]].iloc[0]
                return (f"🟠 **{anomaly_zones[0]}** is the top priority zone, flagged as **Anomaly** "
                        f"with an average deviation of **{z['Avg_Deviation']:+.1f}%** above baseline.\n\n"
                        f"Physical inspection is recommended.\n\n"
                        f"⚠️ *No zones are currently at Potential Leak status in this dataset.*")
            return "✅ No high-risk zones detected. All zones are at Warning or Normal status. Continue monitoring."

        if any(w in q for w in ["how much water","avoidable","waste","saved","save","reduction"]):
            return (f"💧 Based on the 30-day prototype simulation, an estimated **{total_waste:.0f} m³** of "
                    f"water represents potentially avoidable consumption above operational baselines.\n\n"
                    f"At an indicative UAE tariff of {WATER_TARIFF_AED} AED/m³, this corresponds to an "
                    f"estimated **{total_cost:,.0f} AED** in potential cost impact.\n\n"
                    f"⚠️ *These are prototype estimates from simulated data only. Real-world savings require "
                    f"pilot validation with actual campus meter readings before any formal claim can be made.*")

        if any(w in q for w in ["facilities","team","do next","recommend","action","steps","what should"]):
            actions = []
            if leak_zones:
                actions.append(f"1. 🔴 **Physically inspect {leak_zones[0]}** — highest priority, after-hours usage pattern flagged.")
            if anomaly_zones:
                actions.append(f"{'2' if leak_zones else '1'}. 🟠 **Investigate {', '.join(anomaly_zones)}** — significant baseline deviation detected.")
            if warning_zones:
                actions.append(f"{'3' if len(actions)==2 else '2' if len(actions)==1 else '1'}. 🟡 **Monitor {', '.join(warning_zones[:2])}** — above-baseline usage, watch for escalation.")
            actions.append(f"{'4' if len(actions)==3 else str(len(actions)+1)}. 📊 **Begin pilot validation planning** — collect real meter data from at least one zone to start real-world verification.")
            return ("**Recommended next steps for the facilities team:**\n\n" +
                    "\n\n".join(actions) +
                    "\n\n*All recommendations are derived from prototype simulation data. Treat as investigation starting points, not confirmed findings.*")

        if "cafeteria" in q or "dining" in q:
            row = zone_agg[zone_agg["Zone"] == "Cafeteria & Dining"].iloc[0]
            return (f"🍽️ **Cafeteria & Dining** — Status: **{row['Last_Status']}** | "
                    f"Avg deviation: **{row['Avg_Deviation']:+.1f}%** | "
                    f"Est. avoidable waste: **{row['Total_Waste']:.0f} m³**\n\n"
                    f"This zone showed elevated consumption on several simulated days, exceeding the anomaly threshold. "
                    f"Possible causes include extended kitchen operations, dishwashing equipment outside normal hours, "
                    f"or a simulated supply line issue.\n\n*Prototype insight — real-world verification required.*")

        if "science" in q or "technology block" in q:
            row = zone_agg[zone_agg["Zone"] == "Science & Technology Block"].iloc[0]
            return (f"🔬 **Science & Technology Block** — Status: **{row['Last_Status']}** | "
                    f"Avg deviation: **{row['Avg_Deviation']:+.1f}%**\n\n"
                    f"This zone shows a gradual upward drift in the latter portion of the simulation window, "
                    f"peaking at Potential Leak status. Lab cooling systems, equipment usage changes, or "
                    f"infrastructure issues could explain this pattern.\n\n*Prototype insight — pilot validation required.*")

        if "sport" in q or "gym" in q or "complex" in q:
            row = zone_agg[zone_agg["Zone"] == "Sports Complex"].iloc[0]
            return (f"🏟️ **Sports Complex** — Status: **{row['Last_Status']}** | "
                    f"Avg deviation: **{row['Avg_Deviation']:+.1f}%**\n\n"
                    f"This zone had elevated simulated usage during an event window (days 14–16). "
                    f"Sports facilities often spike during competitions, open days, or deep-cleaning periods.\n\n"
                    f"*Prototype insight — real-world calibration needed.*")

        if "housing" in q or "residential" in q or "student" in q:
            rows = zone_agg[zone_agg["Zone"].str.contains("Housing")]
            lines = "\n".join([f"- **{r['Zone']}**: {r['Last_Status']}, avg dev {r['Avg_Deviation']:+.1f}%" for _, r in rows.iterrows()])
            return (f"🏠 **Student Housing Zones:**\n\n{lines}\n\n"
                    f"Student housing typically shows high but stable consumption. "
                    f"Flagged deviations may reflect occupancy changes during exam periods or plumbing issues.\n\n"
                    f"*Prototype insight — requires real data validation.*")

        if any(w in q for w in ["efficiency score","score","efficiency"]):
            ta = df["Actual_Consumption"].sum()
            tw = df["Avoidable_Waste_m3"].sum()
            score = max(0, min(100, round(100 - (tw / ta * 100), 1)))
            return (f"📊 The current **Water Efficiency Score** for this prototype dataset is **{score} / 100**.\n\n"
                    f"It is calculated as: 100 minus the percentage of total consumption estimated as avoidable waste. "
                    f"A score of 100 would mean zero estimated avoidable waste.\n\n"
                    f"*This is a prototype indicator. Real efficiency scoring requires validated baseline data.*")

        if any(w in q for w in ["what is nabdflow","what does nabdflow","about","explain nabdflow"]):
            return ("💧 **NabdFlow** means *the pulse of water flow*.\n\n"
                    "'**Nabd**' (نبض) means pulse in Arabic — representing the live rhythm and heartbeat of campus "
                    "water systems. '**Flow**' represents both the movement of water across campus zones and the "
                    "flow of data from raw meter readings into insights, alerts, and sustainability reports.\n\n"
                    "NabdFlow is an AI-powered campus water intelligence platform for UAE university campuses, "
                    "helping facility teams and sustainability officers monitor consumption, detect abnormal "
                    "patterns, and work toward verified water efficiency goals.")

        if any(w in q for w in ["sdg","sustainable development","sustainability","net zero","uae strategy"]):
            return ("🌍 **NabdFlow aligns with three SDGs and two UAE national strategies:**\n\n"
                    "- **SDG 6** — Clean Water and Sanitation (water-use efficiency)\n"
                    "- **SDG 11** — Sustainable Cities (smart, resource-efficient campuses)\n"
                    "- **SDG 13** — Climate Action (indirect emissions reduction via water efficiency)\n\n"
                    "**UAE Strategies:**\n"
                    "- UAE Water Security Strategy 2036\n"
                    "- UAE Net Zero 2050 Strategic Initiative\n\n"
                    "*NabdFlow supports these goals through improved water-use efficiency after pilot validation.*")

        # Fallback
        return (f"🤖 Here's a quick data summary from the current prototype dataset:\n\n"
                f"- **Potential Leak zones:** {', '.join(leak_zones) if leak_zones else 'None'}\n"
                f"- **Anomaly zones:** {', '.join(anomaly_zones) if anomaly_zones else 'None'}\n"
                f"- **Warning zones:** {', '.join(warning_zones) if warning_zones else 'None'}\n"
                f"- **Est. avoidable waste:** {total_waste:.0f} m³ (30-day window)\n"
                f"- **Est. cost impact:** {total_cost:,.0f} AED\n\n"
                f"Try asking: *'Which zone has the highest risk?'* or *'What should the facilities team do next?'*\n\n"
                f"⚠️ *This assistant answers only from simulated prototype data.*")

    # Suggested questions
    st.markdown('<div style="font-size:0.82rem;color:#4a6a8a;margin-bottom:8px">💡 Suggested questions:</div>',
                unsafe_allow_html=True)
    suggestions = [
        "Which zone has the highest risk?",
        "How much water could be avoided?",
        "Which building needs inspection first?",
        "Why was the Cafeteria flagged?",
        "What should the facilities team do next?",
    ]
    cols = st.columns(len(suggestions))
    for i, q in enumerate(suggestions):
        with cols[i]:
            if st.button(q, key=f"s_{i}", use_container_width=True):
                st.session_state.chat_history.append({"role": "user",    "content": q})
                st.session_state.chat_history.append({"role": "assistant","content": bot_response(q)})
                st.rerun()

    # Chat history display
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"""
            <div style="display:flex;justify-content:flex-end;margin:7px 0">
                <div class="chat-user">{msg['content']}</div>
            </div>""", unsafe_allow_html=True)
        else:
            content = msg["content"].replace("\n", "<br>").replace("**", "<b>").replace("**", "</b>")
            # Simple bold markdown
            import re
            content_html = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', msg["content"].replace("\n", "<br>"))
            st.markdown(f"""
            <div style="display:flex;gap:10px;margin:7px 0;align-items:flex-start">
                <div style="background:#00d4ff;color:#060d1a;border-radius:50%;width:28px;height:28px;
                     display:flex;align-items:center;justify-content:center;
                     font-size:0.85rem;flex-shrink:0;margin-top:2px">💧</div>
                <div class="chat-bot">{content_html}</div>
            </div>""", unsafe_allow_html=True)

    # Chat input
    with st.form("chat_form", clear_on_submit=True):
        col_i, col_b = st.columns([5, 1])
        with col_i:
            user_in = st.text_input("", placeholder="Ask about zones, alerts, recommendations...",
                                     label_visibility="collapsed")
        with col_b:
            send = st.form_submit_button("Send", use_container_width=True)

    if send and user_in.strip():
        st.session_state.chat_history.append({"role": "user",    "content": user_in.strip()})
        st.session_state.chat_history.append({"role": "assistant","content": bot_response(user_in.strip())})
        st.rerun()

    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()
