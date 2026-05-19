# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  NabdFlow — AI-Powered Water Intelligence for University Campus             ║
# ║  Sustainability Competition Project · UAE · 2026                           ║
# ║  Run: streamlit run app.py                                                 ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NabdFlow | Water Intelligence",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .stApp { background:#f0f4f8; }
  [data-testid="stSidebar"] {
    background: linear-gradient(180deg,#0a2342 0%,#1a4a7a 100%);
  }
  [data-testid="stSidebar"] * { color:#e8f4f8 !important; }

  /* KPI cards */
  .kpi { background:white; border-radius:12px; padding:18px 14px;
         text-align:center; box-shadow:0 2px 10px rgba(0,0,0,.07);
         border-left:4px solid #1a6eb5; margin-bottom:6px; }
  .kpi.warn  { border-left-color:#f39c12; }
  .kpi.alert { border-left-color:#e74c3c; }
  .kpi.good  { border-left-color:#27ae60; }
  .kpi-label { font-size:11px; color:#7f8c8d; font-weight:700;
               text-transform:uppercase; letter-spacing:.5px; }
  .kpi-val   { font-size:26px; font-weight:800; color:#2c3e50; margin:4px 0; }
  .kpi-sub   { font-size:11px; color:#aaa; }

  /* Section header bar */
  .sec { background:linear-gradient(90deg,#1a6eb5,#0a9396); color:white;
         padding:9px 18px; border-radius:8px; font-size:15px;
         font-weight:700; margin:18px 0 8px 0; }

  /* Recommendation cards */
  .rec { background:white; border-radius:10px; padding:16px 18px;
         margin-bottom:10px; box-shadow:0 2px 8px rgba(0,0,0,.06);
         border-left:4px solid #0a9396; }
  .rec.high   { border-left-color:#e74c3c; }
  .rec.medium { border-left-color:#f39c12; }
  .rec.low    { border-left-color:#27ae60; }

  /* Page headings */
  .pg-title { font-size:26px; font-weight:800; color:#0a2342; }
  .pg-sub   { font-size:13px; color:#7f8c8d; margin-bottom:18px; }

  hr { border:none; border-top:1px solid #e0e6ed; margin:20px 0; }
  #MainMenu,footer { visibility:hidden; }
  [data-testid="metric-container"] {
    background:white; border-radius:10px; padding:14px;
    box-shadow:0 2px 8px rgba(0,0,0,.06);
  }
</style>
""", unsafe_allow_html=True)

# ── Colour palette ─────────────────────────────────────────────────────────────
C = dict(primary="#1a6eb5", secondary="#0a9396", accent="#94d2bd",
         warn="#f39c12", danger="#e74c3c", ok="#27ae60", dark="#0a2342")

ALERT_COL = {
    "Normal Variation": "#2ecc71",
    "Monitor":          "#f1c40f",
    "High Usage Alert": "#e67e22",
    "Possible Leak":    "#e74c3c",
    "Priority Inspection": "#8e44ad",
}

# ══════════════════════════════════════════════════════════════════════════════
# SAMPLE DATA
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data
def make_sample():
    """Generate 30-day realistic campus water dataset with embedded anomalies."""
    np.random.seed(42)
    locs = ["Washroom Block A","Cafeteria/Pantry","Garden Irrigation",
            "Admin Building","Student Common Area"]
    periods = ["Morning","Afternoon","Evening","Night"]

    # Expected litres per (location, period)
    base = {
        ("Washroom Block A",  "Morning"):800,  ("Washroom Block A",  "Afternoon"):600,
        ("Washroom Block A",  "Evening"):500,  ("Washroom Block A",  "Night"):80,
        ("Cafeteria/Pantry",  "Morning"):400,  ("Cafeteria/Pantry",  "Afternoon"):900,
        ("Cafeteria/Pantry",  "Evening"):700,  ("Cafeteria/Pantry",  "Night"):50,
        ("Garden Irrigation", "Morning"):1200, ("Garden Irrigation", "Afternoon"):200,
        ("Garden Irrigation", "Evening"):1000, ("Garden Irrigation", "Night"):100,
        ("Admin Building",    "Morning"):300,  ("Admin Building",    "Afternoon"):400,
        ("Admin Building",    "Evening"):200,  ("Admin Building",    "Night"):30,
        ("Student Common Area","Morning"):500, ("Student Common Area","Afternoon"):700,
        ("Student Common Area","Evening"):600, ("Student Common Area","Night"):60,
    }
    notes_pool = ["","","","","Tap reported dripping","Irrigation timer checked",
                  "Cleaning crew active","Weekend low activity",
                  "Event in cafeteria","Maintenance check done","Meter reading verified"]

    rows, start = [], datetime(2026, 3, 1)
    for day in range(30):
        dt = start + timedelta(days=day)
        for loc in locs:
            for tp in periods:
                exp = base[(loc, tp)]
                r   = np.random.random()

                # Inject scenario-specific anomalies
                if loc == "Washroom Block A" and 10 <= day <= 18:
                    m = np.random.uniform(1.28,1.45) if tp=="Night" else np.random.uniform(1.1,1.3)
                elif loc == "Garden Irrigation" and day >= 20:
                    m = np.random.uniform(1.18,1.35)
                elif loc == "Cafeteria/Pantry" and tp=="Afternoon" and day in [5,6,12,13,19,20]:
                    m = np.random.uniform(1.20,1.32)
                elif r > 0.92:
                    m = np.random.uniform(1.26,1.42)
                elif r < 0.05:
                    m = np.random.uniform(0.50,0.75)
                else:
                    m = np.random.uniform(0.88,1.14)

                actual = max(0, round(exp*m + np.random.normal(0, exp*0.03), 1))
                rows.append({
                    "Date": dt.strftime("%Y-%m-%d"),
                    "Location": loc,
                    "Time_Period": tp,
                    "Actual_Usage_Litres": actual,
                    "Expected_Usage_Litres": float(exp),
                    "Occupancy_Count": int(np.random.randint(5,200)),
                    "Notes": np.random.choice(notes_pool),
                })
    return pd.DataFrame(rows)

# ══════════════════════════════════════════════════════════════════════════════
# DATA PROCESSING
# ══════════════════════════════════════════════════════════════════════════════
def process(df):
    required = ["Date","Location","Time_Period","Actual_Usage_Litres","Expected_Usage_Litres"]
    missing  = [c for c in required if c not in df.columns]
    if missing:
        st.error(f"❌ Missing required columns: {', '.join(missing)}")
        st.stop()

    df = df.copy()
    df["Date"]                  = pd.to_datetime(df["Date"])
    df["Actual_Usage_Litres"]   = pd.to_numeric(df["Actual_Usage_Litres"],   errors="coerce").fillna(0)
    df["Expected_Usage_Litres"] = pd.to_numeric(df["Expected_Usage_Litres"], errors="coerce").fillna(0)

    df["Excess_Litres"]         = df["Actual_Usage_Litres"] - df["Expected_Usage_Litres"]
    df["Avoidable_Litres"]      = df["Excess_Litres"].clip(lower=0)
    df["Diff_Pct"]              = np.where(
        df["Expected_Usage_Litres"] > 0,
        df["Excess_Litres"] / df["Expected_Usage_Litres"] * 100, 0)
    df["AED_Savings"]           = df["Avoidable_Litres"] / 1000 * 4.5

    # Alert classification
    def classify(row):
        p = row["Diff_Pct"]
        t = str(row.get("Time_Period","")).lower()
        if p >= 25 and t == "night": return "Possible Leak"
        if p >= 25:                  return "High Usage Alert"
        if p >= 15:                  return "Monitor"
        return "Normal Variation"

    df["Alert"] = df.apply(classify, axis=1)

    # Upgrade to Priority Inspection: same location High Usage on 2+ distinct days
    hi_days = (df[df["Alert"]=="High Usage Alert"]
               .groupby("Location")["Date"].nunique())
    p_locs = hi_days[hi_days >= 2].index.tolist()
    mask = (df["Alert"]=="High Usage Alert") & (df["Location"].isin(p_locs))
    df.loc[mask, "Alert"] = "Priority Inspection"

    return df

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def kpi(label, val, sub="", cls=""):
    st.markdown(
        f'<div class="kpi {cls}"><div class="kpi-label">{label}</div>'
        f'<div class="kpi-val">{val}</div><div class="kpi-sub">{sub}</div></div>',
        unsafe_allow_html=True)

def sec(title):
    st.markdown(f'<div class="sec">{title}</div>', unsafe_allow_html=True)

def chart_layout(fig, h=320, xtick_angle=0):
    fig.update_layout(
        height=h, plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=8,r=8,t=20,b=8), hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        font=dict(family="Inter,sans-serif", size=12),
        xaxis_tickangle=xtick_angle)
    return fig

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
def sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:20px 0 10px">
          <div style="font-size:44px">💧</div>
          <div style="font-size:22px;font-weight:800;color:#94d2bd;letter-spacing:1px">NabdFlow</div>
          <div style="font-size:11px;color:#a8d5e8">Water Intelligence Platform</div>
        </div>
        <hr style="border-color:#2a5a8a;margin:8px 0 14px">
        """, unsafe_allow_html=True)

        page = st.radio("Navigate", [
            "🏠  Overview Dashboard",
            "📍  Location Analysis",
            "🚨  Leak Detection",
            "🤖  AI Recommendations",
            "📊  Impact Report",
            "ℹ️  About NabdFlow",
        ], label_visibility="collapsed")

        st.markdown("<hr style='border-color:#2a5a8a;margin:14px 0'>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:12px;font-weight:700;color:#94d2bd;margin-bottom:6px'>📁 DATA SOURCE</div>",
                    unsafe_allow_html=True)
        uploaded   = st.file_uploader("Upload CSV / Excel", type=["csv","xlsx","xls"],
                                       label_visibility="collapsed")
        use_sample = st.checkbox("Use built-in sample data",
                                  value=(uploaded is None))

        st.markdown("<hr style='border-color:#2a5a8a;margin:14px 0'>", unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size:10px;color:#7aacca;text-align:center;padding-bottom:8px">
          NabdFlow v1.0 · 2026<br>
          <span style="color:#94d2bd">🌱 Powered by Sustainability</span>
        </div>""", unsafe_allow_html=True)
    return page, uploaded, use_sample

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
def pg_overview(df):
    st.markdown('<div class="pg-title">🏠 Overview Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="pg-sub">Campus-wide water consumption snapshot — real-time intelligence at a glance</div>',
                unsafe_allow_html=True)

    # KPIs
    tot_act  = df["Actual_Usage_Litres"].sum()
    tot_exp  = df["Expected_Usage_Litres"].sum()
    tot_exc  = df["Avoidable_Litres"].sum()
    tot_save = df["AED_Savings"].sum()
    n_high   = df[df["Alert"].isin(["High Usage Alert","Priority Inspection"])].shape[0]
    n_leak   = df[df["Alert"]=="Possible Leak"].shape[0]
    top_loc  = df.groupby("Location")["Actual_Usage_Litres"].sum().idxmax()
    avg_day  = df.groupby("Date")["Actual_Usage_Litres"].sum().mean()

    c1,c2,c3,c4 = st.columns(4)
    with c1: kpi("💧 Total Water Used",   f"{tot_act/1000:,.1f} m³",   f"{tot_act:,.0f} L")
    with c2: kpi("📋 Expected Usage",     f"{tot_exp/1000:,.1f} m³",   f"{tot_exp:,.0f} L")
    with c3: kpi("♻️ Avoidable Excess",   f"{tot_exc/1000:,.1f} m³",   f"{tot_exc:,.0f} L", "warn")
    with c4: kpi("💰 Est. AED Savings",   f"AED {tot_save:,.1f}",      "Recoverable cost",  "good")

    c5,c6,c7,c8 = st.columns(4)
    with c5: kpi("🚨 High Usage Alerts",  str(n_high),  "Incidents detected", "alert")
    with c6: kpi("🔴 Possible Leaks",     str(n_leak),  "Night anomalies",    "alert")
    with c7: kpi("📍 Top Usage Location", top_loc,      "Most water-intensive")
    with c8: kpi("📅 Avg Daily Usage",    f"{avg_day/1000:,.1f} m³", "Per day campus-wide")

    st.markdown("<hr>", unsafe_allow_html=True)

    # Chart 1 — Daily actual vs expected
    sec("📈 Daily Usage: Actual vs Expected")
    daily = (df.groupby("Date")
               .agg(Actual=("Actual_Usage_Litres","sum"),
                    Expected=("Expected_Usage_Litres","sum"))
               .reset_index())
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=daily["Date"], y=daily["Actual"]/1000,
        name="Actual", mode="lines+markers",
        line=dict(color=C["primary"], width=2.5), marker=dict(size=5),
        fill="tozeroy", fillcolor="rgba(26,110,181,.09)"))
    fig.add_trace(go.Scatter(x=daily["Date"], y=daily["Expected"]/1000,
        name="Expected", mode="lines",
        line=dict(color=C["secondary"], width=2, dash="dash")))
    fig.update_yaxes(title_text="m³")
    st.plotly_chart(chart_layout(fig), use_container_width=True)

    c_left, c_right = st.columns(2)

    # Chart 2 — Usage by location
    with c_left:
        sec("📍 Usage by Location")
        ls = (df.groupby("Location")
                .agg(Actual=("Actual_Usage_Litres","sum"),
                     Expected=("Expected_Usage_Litres","sum"))
                .reset_index().sort_values("Actual"))
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(y=ls["Location"], x=ls["Actual"]/1000,
            name="Actual", orientation="h", marker_color=C["primary"]))
        fig2.add_trace(go.Bar(y=ls["Location"], x=ls["Expected"]/1000,
            name="Expected", orientation="h", marker_color=C["accent"]))
        fig2.update_layout(barmode="group", xaxis_title="m³")
        st.plotly_chart(chart_layout(fig2, h=280), use_container_width=True)

    # Chart 3 — Alert donut
    with c_right:
        sec("🎯 Alert Distribution")
        ac = df["Alert"].value_counts().reset_index()
        ac.columns = ["Alert","Count"]
        fig3 = px.pie(ac, names="Alert", values="Count",
                      color="Alert", color_discrete_map=ALERT_COL, hole=.5)
        fig3.update_traces(textposition="outside", textinfo="percent+label")
        fig3.update_layout(height=280, paper_bgcolor="white",
                           margin=dict(l=8,r=8,t=18,b=8), showlegend=False,
                           font=dict(family="Inter,sans-serif", size=12))
        st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — LOCATION ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
def pg_location(df):
    st.markdown('<div class="pg-title">📍 Location Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="pg-sub">Drill into each campus zone — identify hotspots and savings opportunities</div>',
                unsafe_allow_html=True)

    # Summary table
    lt = (df.groupby("Location")
            .agg(Actual   =("Actual_Usage_Litres","sum"),
                 Expected =("Expected_Usage_Litres","sum"),
                 Excess   =("Avoidable_Litres","sum"),
                 Savings  =("AED_Savings","sum"),
                 Alerts   =("Alert", lambda x: x.isin(
                     ["High Usage Alert","Possible Leak","Priority Inspection"]).sum()))
            .reset_index())
    lt["Diff_%"]      = ((lt["Actual"]-lt["Expected"])/lt["Expected"]*100).round(1)
    lt["Actual_m3"]   = (lt["Actual"]/1000).round(2)
    lt["Expected_m3"] = (lt["Expected"]/1000).round(2)
    lt["Excess_m3"]   = (lt["Excess"]/1000).round(2)
    lt["Savings"]     = lt["Savings"].round(1)

    show = lt[["Location","Actual_m3","Expected_m3","Excess_m3","Diff_%","Savings","Alerts"]]
    show.columns = ["Location","Actual (m³)","Expected (m³)","Excess (m³)","Diff %","AED Savings","Alerts"]
    show = show.sort_values("Diff %", ascending=False)

    def hl(v):
        if not isinstance(v,(int,float)): return ""
        if v>=25: return "background:#fadbd8;color:#c0392b;font-weight:700"
        if v>=15: return "background:#fdebd0;color:#ca6f1e;font-weight:700"
        if v>0:   return "background:#fef9e7;color:#d4ac0d"
        return ""

    sec("📊 Location Summary")
    st.dataframe(show.style.applymap(hl, subset=["Diff %"]),
                 use_container_width=True, hide_index=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    # Actual vs Expected bars
    sec("📈 Actual vs Expected by Location")
    mlt = lt.melt(id_vars="Location", value_vars=["Actual_m3","Expected_m3"],
                  var_name="Type", value_name="m³")
    mlt["Type"] = mlt["Type"].map({"Actual_m3":"Actual","Expected_m3":"Expected"})
    fig = px.bar(mlt, x="Location", y="m³", color="Type", barmode="group",
                 color_discrete_map={"Actual":C["primary"],"Expected":C["accent"]})
    st.plotly_chart(chart_layout(fig, h=340, xtick_angle=-15), use_container_width=True)

    c1, c2 = st.columns(2)

    with c1:
        # Top risk — avoidable excess
        sec("🔥 Top High-Risk Areas by Excess")
        risk = lt.sort_values("Excess_m3", ascending=False).head(5)
        fig2 = px.bar(risk, x="Excess_m3", y="Location", orientation="h",
                      color="Excess_m3",
                      color_continuous_scale=["#94d2bd","#e9c46a","#e76f51"],
                      labels={"Excess_m3":"Excess (m³)"})
        fig2.update_layout(height=280, plot_bgcolor="white", paper_bgcolor="white",
                           margin=dict(l=8,r=8,t=20,b=8), coloraxis_showscale=False,
                           font=dict(family="Inter,sans-serif", size=12))
        st.plotly_chart(fig2, use_container_width=True)

    with c2:
        # Stacked by time period
        sec("⏰ Usage by Time Period")
        tp_data = df.groupby(["Location","Time_Period"])["Actual_Usage_Litres"].sum().reset_index()
        fig3 = px.bar(tp_data, x="Location", y="Actual_Usage_Litres",
                      color="Time_Period", barmode="stack",
                      color_discrete_sequence=["#023e8a","#0096c7","#48cae4","#90e0ef"],
                      labels={"Actual_Usage_Litres":"Litres"})
        st.plotly_chart(chart_layout(fig3, h=280, xtick_angle=-15), use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — LEAK DETECTION
# ══════════════════════════════════════════════════════════════════════════════
def pg_leak(df):
    st.markdown('<div class="pg-title">🚨 Leak Detection & Alert Monitor</div>', unsafe_allow_html=True)
    st.markdown('<div class="pg-sub">Identify suspicious usage, night-time anomalies, and priority inspection zones</div>',
                unsafe_allow_html=True)

    # Filters
    sec("🔍 Filters")
    c1,c2,c3 = st.columns(3)
    with c1:
        sel_loc = st.selectbox("Location",
            ["All Locations"] + sorted(df["Location"].unique().tolist()))
    with c2:
        sel_alert = st.selectbox("Alert Type",
            ["All Alerts","Monitor","High Usage Alert","Possible Leak","Priority Inspection"])
    with c3:
        mn, mx = df["Date"].min().date(), df["Date"].max().date()
        dr = st.date_input("Date Range", value=(mn, mx), min_value=mn, max_value=mx)

    # Apply
    filt = df[df["Alert"] != "Normal Variation"].copy()
    if sel_loc   != "All Locations": filt = filt[filt["Location"] == sel_loc]
    if sel_alert != "All Alerts":    filt = filt[filt["Alert"]    == sel_alert]
    if len(dr) == 2:
        filt = filt[(filt["Date"].dt.date >= dr[0]) & (filt["Date"].dt.date <= dr[1])]

    # Sub-KPIs
    c1,c2,c3,c4 = st.columns(4)
    with c1: kpi("🔍 Monitor",        str(filt[filt["Alert"]=="Monitor"].shape[0]),           "Needs watching")
    with c2: kpi("⚠️ High Usage",     str(filt[filt["Alert"]=="High Usage Alert"].shape[0]),  "Exceeds 25%",  "warn")
    with c3: kpi("🔴 Possible Leaks", str(filt[filt["Alert"]=="Possible Leak"].shape[0]),     "Night anomaly","alert")
    with c4: kpi("🟣 Priority Insp.", str(filt[filt["Alert"]=="Priority Inspection"].shape[0]),"Repeat offend.","alert")
    st.markdown("<hr>", unsafe_allow_html=True)

    # Alert log table
    sec("📋 Alert Log")
    if filt.empty:
        st.success("✅ No alerts found for selected filters.")
    else:
        cols = ["Date","Location","Time_Period","Actual_Usage_Litres",
                "Expected_Usage_Litres","Diff_Pct","Alert"]
        disp = filt[cols].copy()
        disp["Date"]     = disp["Date"].dt.strftime("%Y-%m-%d")
        disp["Diff_Pct"] = disp["Diff_Pct"].round(1)
        disp.columns     = ["Date","Location","Period","Actual (L)","Expected (L)","Diff %","Alert"]

        def style_a(v):
            m = {"Monitor":"background:#fef9e7;color:#b7950b",
                 "High Usage Alert":"background:#fdebd0;color:#ca6f1e",
                 "Possible Leak":"background:#fadbd8;color:#c0392b",
                 "Priority Inspection":"background:#f5eef8;color:#7d3c98"}
            return m.get(v,"")

        st.dataframe(disp.style.applymap(style_a, subset=["Alert"]),
                     use_container_width=True, hide_index=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    # Priority action table
    sec("🎯 Priority Action Table — For Facility Manager")
    st.caption("Consolidated critical zones requiring immediate attention")
    rows_pt = []

    for loc, cnt in df[df["Alert"]=="Possible Leak"].groupby("Location").size().items():
        rows_pt.append({"Priority":"🔴 CRITICAL","Location":loc,
            "Reason":f"Night-time excess detected ({cnt} incidents)",
            "Recommended Action":"Inspect pipes & fixtures at night; check silent leaks & meter readings"})

    for loc, cnt in df[df["Alert"]=="Priority Inspection"].groupby("Location").size().items():
        rows_pt.append({"Priority":"🟠 HIGH","Location":loc,
            "Reason":f"Repeated high usage across multiple days ({cnt} incidents)",
            "Recommended Action":"Schedule formal maintenance within 48 h; audit fixtures & sub-meters"})

    done = [r["Location"] for r in rows_pt]
    for loc, cnt in df[df["Alert"]=="High Usage Alert"].groupby("Location").size().items():
        if loc not in done:
            rows_pt.append({"Priority":"🟡 MODERATE","Location":loc,
                "Reason":f"Usage >25% above baseline ({cnt} incidents)",
                "Recommended Action":"Monitor closely; verify occupancy data & meter accuracy"})

    if rows_pt:
        pt = pd.DataFrame(rows_pt).drop_duplicates(subset=["Location"])
        st.dataframe(pt, use_container_width=True, hide_index=True)
    else:
        st.success("✅ No critical priority issues in current dataset.")

    st.markdown("<hr>", unsafe_allow_html=True)

    # Heatmap
    sec("🗓️ Anomaly Heatmap — Location × Date")
    h_df = df[df["Alert"]!="Normal Variation"].copy()
    h_df["Date_s"] = h_df["Date"].dt.strftime("%b %d")
    pivot = (h_df.groupby(["Location","Date_s"])["Diff_Pct"]
                 .mean().reset_index()
                 .pivot(index="Location", columns="Date_s", values="Diff_Pct")
                 .fillna(0))
    if not pivot.empty:
        fig = px.imshow(pivot, color_continuous_scale=["#d5f5e3","#f9e79f","#e74c3c"],
                        zmin=0, zmax=50, labels=dict(color="Excess %"), aspect="auto")
        fig.update_layout(height=260, paper_bgcolor="white",
                          margin=dict(l=8,r=8,t=16,b=8),
                          font=dict(family="Inter,sans-serif",size=11))
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — AI RECOMMENDATIONS
# ══════════════════════════════════════════════════════════════════════════════
def pg_recs(df):
    st.markdown('<div class="pg-title">🤖 AI Recommendations</div>', unsafe_allow_html=True)
    st.markdown('<div class="pg-sub">Data-driven insights generated from your campus usage patterns</div>',
                unsafe_allow_html=True)

    ls = df.groupby("Location").agg(
        avg_diff    =("Diff_Pct","mean"),
        excess_m3   =("Avoidable_Litres", lambda x: x.sum()/1000),
        leaks       =("Alert", lambda x: (x=="Possible Leak").sum()),
        priority    =("Alert", lambda x: (x=="Priority Inspection").sum()),
        high        =("Alert", lambda x: (x=="High Usage Alert").sum()),
        savings     =("AED_Savings","sum"),
    ).reset_index()

    recs = []

    for _, r in ls.iterrows():
        loc, diff, exc, sav = r["Location"], r["avg_diff"], r["excess_m3"], r["savings"]

        if r["leaks"] > 0:
            recs.append(dict(p="HIGH", loc=loc, icon="🔴",
                title=f"Suspected Leak in {loc}",
                insight=(f"NabdFlow detected {int(r['leaks'])} night-time anomaly incidents. "
                         f"Night usage exceeded 25% of expected baseline — strong indicator "
                         f"of a silent leak or unattended open fixture."),
                action=(f"Conduct an immediate night-time walk-through inspection. "
                        f"Check running toilets, dripping taps, and pipe joints. "
                        f"Estimated waste: {exc:.1f} m³ · AED {sav:.1f} recoverable."),
                save=f"AED {sav:.1f}"))

        if r["priority"] > 0:
            recs.append(dict(p="HIGH", loc=loc, icon="🟠",
                title=f"Priority Inspection — {loc}",
                insight=(f"Repeated high-usage pattern across {int(r['priority'])} time slots "
                         f"suggests a systemic problem, not a one-off event."),
                action=(f"Schedule formal maintenance within 48 hours. "
                        f"Review sub-meters, sensor accuracy, and cleaning procedures. "
                        f"Potential savings: AED {sav:.1f}."),
                save=f"AED {sav:.1f}"))

        if r["high"] >= 3 and r["priority"] == 0 and r["leaks"] == 0:
            cut = min(20, diff*0.6)
            recs.append(dict(p="MEDIUM", loc=loc, icon="🟡",
                title=f"Reduce Usage at {loc} by ~{cut:.0f}%",
                insight=(f"Average usage is {diff:.1f}% above expected baseline across "
                         f"multiple recorded time periods."),
                action=(f"Audit operational schedules, reduce idle run times, and implement "
                        f"occupancy-based triggers. A {cut:.0f}% cut saves ~{exc*0.6:.1f} m³ "
                        f"and AED {sav*0.6:.1f}."),
                save=f"AED {sav*0.6:.1f}"))

        if diff < 0:
            recs.append(dict(p="LOW", loc=loc, icon="🟢",
                title=f"{loc} — Below Baseline (Good Practice)",
                insight=(f"{loc} uses {abs(diff):.1f}% less than expected. "
                         f"Positive result but warrants validation to confirm meter accuracy."),
                action="Verify readings; document as a best-practice model for other zones.",
                save="—"))

    # Campus-wide night check
    night_avg = df[df["Time_Period"]=="Night"]["Diff_Pct"].mean()
    if night_avg > 10:
        recs.append(dict(p="MEDIUM", loc="Campus-wide", icon="🌙",
            title="Audit Night-Time Water Flow Campus-Wide",
            insight=(f"Average night-time usage is {night_avg:.1f}% above expected. "
                     f"Most facilities should show near-zero consumption after hours."),
            action=("Install automatic shut-off valves. Set smart alerts for >5 L/min "
                    "between 11 PM–5 AM. Consider a certified water auditor."),
            save="Variable"))

    # Garden irrigation
    g = df[df["Location"]=="Garden Irrigation"]
    if not g.empty and g["Diff_Pct"].mean() > 15:
        recs.append(dict(p="MEDIUM", loc="Garden Irrigation", icon="🌿",
            title="Optimise Irrigation Schedule",
            insight=(f"Irrigation usage is {g['Diff_Pct'].mean():.1f}% above baseline. "
                     f"Overwatering is the most avoidable campus water waste."),
            action=("Reduce duration by 15–20%. Switch to early morning (5–7 AM) to cut "
                    "evaporation. Install soil-moisture sensors or a smart controller "
                    "calibrated to UAE climate data."),
            save=f"AED {g['AED_Savings'].sum():.1f}"))

    # Cafeteria afternoon peak
    caf = df[(df["Location"]=="Cafeteria/Pantry") & (df["Time_Period"]=="Afternoon")]
    if not caf.empty and caf["Diff_Pct"].mean() > 15:
        recs.append(dict(p="LOW", loc="Cafeteria/Pantry", icon="🍽️",
            title="Review Afternoon Cafeteria Routines",
            insight=(f"Afternoon usage in the Cafeteria/Pantry exceeds expected "
                     f"by {caf['Diff_Pct'].mean():.1f}%."),
            action=("Audit dishwasher cycles and food-prep routines. "
                    "Train staff on water-saving practices during peak hours."),
            save=f"AED {caf['AED_Savings'].sum():.1f}"))

    # Sort HIGH → MEDIUM → LOW
    ord_map = {"HIGH":0,"MEDIUM":1,"LOW":2}
    recs.sort(key=lambda x: ord_map.get(x["p"],3))

    if not recs:
        st.success("✅ No significant issues detected. Campus water usage appears normal.")
        return

    st.info(f"💡 **{len(recs)} smart recommendations** generated from your data — sorted by urgency.")

    for rec in recs:
        cls = {"HIGH":"high","MEDIUM":"medium","LOW":"low"}.get(rec["p"],"")
        st.markdown(f"""
        <div class="rec {cls}">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px">
            <span style="font-size:15px;font-weight:700;color:#2c3e50">
              {rec['icon']} {rec['title']}
            </span>
            <div>
              <span style="background:#eaf4fb;color:#1a6eb5;padding:2px 10px;
                border-radius:20px;font-size:11px;font-weight:700">📍 {rec['loc']}</span>
              <span style="background:#eafaf1;color:#1e8449;padding:2px 10px;
                border-radius:20px;font-size:11px;font-weight:700;margin-left:6px">
                💰 {rec['save']}</span>
            </div>
          </div>
          <div style="font-size:13px;color:#555;margin-bottom:6px">
            <strong>📊 Insight:</strong> {rec['insight']}</div>
          <div style="font-size:13px;color:#1a6eb5">
            <strong>✅ Action:</strong> {rec['action']}</div>
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — IMPACT REPORT
# ══════════════════════════════════════════════════════════════════════════════
def pg_impact(df):
    st.markdown('<div class="pg-title">📊 Impact Report</div>', unsafe_allow_html=True)
    st.markdown('<div class="pg-sub">Sustainability summary ready for stakeholder reporting and competition submission</div>',
                unsafe_allow_html=True)

    col_main, col_inp = st.columns([3,1])
    with col_inp:
        people   = st.number_input("Est. Students/Staff Reached", min_value=0, value=250, step=10)
        pilot    = st.text_input("Pilot Location", value="Main Campus, UAE University")

    tot_act  = df["Actual_Usage_Litres"].sum()
    tot_exp  = df["Expected_Usage_Litres"].sum()
    tot_exc  = df["Avoidable_Litres"].sum()
    tot_sav  = df["AED_Savings"].sum()
    n_high   = df[df["Alert"].isin(["High Usage Alert","Priority Inspection"])].shape[0]
    n_leak   = df[df["Alert"]=="Possible Leak"].shape[0]
    red_pct  = (tot_exc/tot_act*100) if tot_act > 0 else 0
    d_range  = f"{df['Date'].min().strftime('%d %b %Y')} – {df['Date'].max().strftime('%d %b %Y')}"

    with col_main:
        st.markdown(f"""
        <div style="background:white;border-radius:14px;padding:28px 30px;
                    box-shadow:0 4px 20px rgba(0,0,0,.09);">
          <div style="display:flex;align-items:center;margin-bottom:18px">
            <div style="font-size:40px;margin-right:14px">💧</div>
            <div>
              <div style="font-size:22px;font-weight:800;color:#0a2342">NabdFlow</div>
              <div style="font-size:12px;color:#7f8c8d">
                AI-Powered Water Intelligence · University Campus Facility Managers</div>
            </div>
          </div>
          <hr style="border-color:#ecf0f1">
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;
                      font-size:13px;margin-bottom:16px">
            <div>📍 <strong>Pilot Location:</strong> {pilot}</div>
            <div>⏱️ <strong>Pilot Duration:</strong> 4–6 Weeks</div>
            <div>📅 <strong>Data Period:</strong> {d_range}</div>
            <div>👥 <strong>People Reached:</strong> {people:,}</div>
            <div>💧 <strong>Total Monitored:</strong> {tot_act/1000:,.1f} m³</div>
            <div>♻️ <strong>Avoidable Waste:</strong> {tot_exc/1000:,.1f} m³</div>
            <div>💰 <strong>Est. AED Savings:</strong> AED {tot_sav:,.1f}</div>
            <div>🚨 <strong>Alerts Detected:</strong> {n_high+n_leak}</div>
            <div>📉 <strong>Potential Reduction:</strong> {red_pct:.1f}% of usage</div>
            <div>🎯 <strong>Reduction Target:</strong> 10–20%</div>
          </div>
          <hr style="border-color:#ecf0f1">
          <div style="margin-bottom:8px"><strong>🌍 SDG Alignment</strong></div>
          <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px">
            <span style="background:#0a9396;color:white;padding:5px 14px;
              border-radius:20px;font-size:12px;font-weight:700">
              🌊 SDG 6 — Clean Water & Sanitation</span>
            <span style="background:#94d2bd;color:#0a2342;padding:5px 14px;
              border-radius:20px;font-size:12px;font-weight:700">
              ♻️ SDG 12 — Responsible Consumption</span>
          </div>
          <div style="margin-bottom:8px"><strong>🇦🇪 UAE Strategic Alignment</strong></div>
          <div style="font-size:13px;color:#555;line-height:2">
            ✅ UAE Water Security Strategy 2036<br>
            ✅ Smart Water Management & Digital Infrastructure Direction<br>
            ✅ Quality of Life and Sustainable Communities Initiative<br>
            ✅ UAE Net Zero by 2050 Strategic Initiative
          </div>
          <hr style="border-color:#ecf0f1;margin-top:14px">
          <div style="font-size:11px;color:#aaa;text-align:right">
            Generated by NabdFlow v1.0 · {datetime.now().strftime('%d %b %Y')}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    sec("⬇️ Download Impact Report")

    txt = f"""
=================================================================
  NABDFLOW — SUSTAINABILITY IMPACT REPORT
  AI-Powered Water Intelligence for University Campuses
=================================================================
Project Name       : NabdFlow
Target User        : University Campus Facility Manager
Pilot Location     : {pilot}
Pilot Duration     : 4–6 Weeks
Data Period        : {d_range}
People Reached     : {people:,}
Report Generated   : {datetime.now().strftime('%d %B %Y, %H:%M')}

-----------------------------------------------------------------
  WATER USAGE SUMMARY
-----------------------------------------------------------------
Total Monitored    : {tot_act/1000:,.2f} m³  ({tot_act:,.0f} L)
Expected Usage     : {tot_exp/1000:,.2f} m³
Avoidable Waste    : {tot_exc/1000:,.2f} m³  ({tot_exc:,.0f} L)
Est. AED Savings   : AED {tot_sav:,.2f}
Potential Reduction: {red_pct:.1f}% of total campus usage
Target             : 10–20%

-----------------------------------------------------------------
  ALERTS
-----------------------------------------------------------------
High Usage Alerts  : {n_high}
Possible Leaks     : {n_leak}
Total Critical     : {n_high + n_leak}

-----------------------------------------------------------------
  SDG & UAE ALIGNMENT
-----------------------------------------------------------------
SDG 6  : Clean Water and Sanitation
SDG 12 : Responsible Consumption and Production
UAE    : Water Security Strategy 2036
UAE    : Smart Water Management Direction
UAE    : Quality of Life & Sustainable Communities
UAE    : Net Zero by 2050

-----------------------------------------------------------------
  IMPACT DIMENSIONS
-----------------------------------------------------------------
Social       : Improved campus living standards & awareness
Environmental: Reduced water waste & conservation
Economic     : Lower utility bills & maintenance costs

=================================================================
  NabdFlow — Shifting campuses from reactive maintenance
  to proactive water intelligence.
=================================================================
"""
    csv_df = pd.DataFrame({
        "Metric":["Pilot Location","Duration","Data Period","People Reached",
                  "Total Monitored (m3)","Expected (m3)","Avoidable Waste (m3)",
                  "AED Savings","Reduction %","High Alerts","Possible Leaks"],
        "Value": [pilot,"4-6 Weeks",d_range,people,
                  round(tot_act/1000,2), round(tot_exp/1000,2), round(tot_exc/1000,2),
                  round(tot_sav,2), round(red_pct,1), n_high, n_leak]
    }).to_csv(index=False)

    ca, cb = st.columns(2)
    with ca:
        st.download_button("📄 Download as TXT", txt,
            f"NabdFlow_Report_{datetime.now().strftime('%Y%m%d')}.txt",
            "text/plain", use_container_width=True)
    with cb:
        st.download_button("📊 Download as CSV", csv_df,
            f"NabdFlow_Report_{datetime.now().strftime('%Y%m%d')}.csv",
            "text/csv", use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    sec("📈 Visual Impact Summary")
    v1, v2 = st.columns(2)

    with v1:
        fig = go.Figure(go.Pie(
            labels=["Efficient Usage","Avoidable Excess"],
            values=[max(0, tot_act-tot_exc), tot_exc],
            hole=.58, marker_colors=["#94d2bd","#e74c3c"],
            textinfo="percent+label"))
        fig.update_layout(title="Water Usage Breakdown", height=270,
            paper_bgcolor="white", margin=dict(l=8,r=8,t=40,b=8),
            showlegend=False, font=dict(family="Inter,sans-serif",size=12))
        st.plotly_chart(fig, use_container_width=True)

    with v2:
        ac = df["Alert"].value_counts().reset_index()
        ac.columns = ["Alert","Count"]
        fig2 = px.bar(ac, x="Alert", y="Count", color="Alert",
                      color_discrete_map=ALERT_COL)
        fig2.update_layout(title="Alert Categories", height=270,
            plot_bgcolor="white", paper_bgcolor="white", showlegend=False,
            margin=dict(l=8,r=8,t=40,b=8), font=dict(family="Inter,sans-serif",size=11),
            xaxis_tickangle=-15)
        st.plotly_chart(fig2, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 6 — ABOUT
# ══════════════════════════════════════════════════════════════════════════════
def pg_about():
    st.markdown('<div class="pg-title">ℹ️ About NabdFlow</div>', unsafe_allow_html=True)
    st.markdown('<div class="pg-sub">Intelligent water management for a sustainable campus future</div>',
                unsafe_allow_html=True)
    st.markdown("""
    <div style="background:white;border-radius:14px;padding:32px;
                box-shadow:0 4px 20px rgba(0,0,0,.08)">
      <div style="text-align:center;padding-bottom:22px">
        <div style="font-size:52px">💧</div>
        <div style="font-size:26px;font-weight:800;color:#0a2342;letter-spacing:1px">NabdFlow</div>
        <div style="font-size:13px;color:#7f8c8d">
          AI-Powered Water Intelligence · University Campus Facility Managers</div>
        <div style="display:inline-block;background:linear-gradient(90deg,#1a6eb5,#0a9396);
            color:white;padding:5px 18px;border-radius:20px;font-size:12px;
            font-weight:700;margin-top:10px">
          v1.0 · Sustainability Competition · UAE · 2026</div>
      </div>
      <hr style="border-color:#ecf0f1">

      <h3 style="color:#0a2342">🎯 What is NabdFlow?</h3>
      <p style="color:#555;line-height:1.9;font-size:14px">
        <strong>NabdFlow</strong> (نبض — "pulse" in Arabic) is a campus-level water intelligence
        platform for university facility managers. It analyses historical water usage data to detect
        abnormal consumption, identify possible leaks, predict demand, estimate financial savings,
        and generate actionable sustainability reports — no smart-meter infrastructure required.
      </p>
      <div style="background:#eaf7fb;border-left:4px solid #0a9396;padding:14px 18px;
          border-radius:6px;margin:16px 0;font-size:14px">
        ⚠️ <strong>Important:</strong> NabdFlow is not designed to replace existing smart meter
        systems. It acts as a campus-level intelligence layer working alongside existing meter
        readings and facility records — helping managers move from
        <em>reactive maintenance to proactive water management</em>.
      </div>

      <h3 style="color:#0a2342;margin-top:22px">🌍 Impact Dimensions</h3>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;margin-top:10px">
        <div style="background:#eafaf1;border-radius:10px;padding:18px;text-align:center">
          <div style="font-size:26px">👥</div>
          <div style="font-weight:700;color:#1e8449;margin:5px 0">Social</div>
          <div style="font-size:12px;color:#555">Better campus living standards and increased
            awareness of water conservation among students and staff</div>
        </div>
        <div style="background:#eaf4fb;border-radius:10px;padding:18px;text-align:center">
          <div style="font-size:26px">🌿</div>
          <div style="font-weight:700;color:#1a6eb5;margin:5px 0">Environmental</div>
          <div style="font-size:12px;color:#555">Reduced water waste, lower carbon footprint
            from water treatment, preservation of natural resources</div>
        </div>
        <div style="background:#fef9e7;border-radius:10px;padding:18px;text-align:center">
          <div style="font-size:26px">💰</div>
          <div style="font-weight:700;color:#d4ac0d;margin:5px 0">Economic</div>
          <div style="font-size:12px;color:#555">Lower utility and maintenance costs; early
            leak detection prevents expensive infrastructure damage</div>
        </div>
      </div>

      <h3 style="color:#0a2342;margin-top:22px">⚙️ How It Works</h3>
      <div style="font-size:14px;color:#555;line-height:2.2">
        1. 📁 <strong>Upload</strong> your campus CSV/Excel or use the built-in sample dataset<br>
        2. 📊 <strong>Analyse</strong> — NabdFlow calculates excess, savings, and alert categories<br>
        3. 🔍 <strong>Detect</strong> — Leak detection surfaces the highest-risk zones instantly<br>
        4. 🤖 <strong>Act</strong> — AI-generated recommendations guide maintenance priorities<br>
        5. 📄 <strong>Report</strong> — Download impact reports for leadership and stakeholders
      </div>

      <h3 style="color:#0a2342;margin-top:22px">🇦🇪 UAE & Global Alignment</h3>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;
          font-size:13px;color:#555;margin-top:10px">
        <div>✅ UAE Water Security Strategy 2036</div>
        <div>✅ SDG 6 — Clean Water and Sanitation</div>
        <div>✅ Smart Water Management Direction</div>
        <div>✅ SDG 12 — Responsible Consumption</div>
        <div>✅ Quality of Life & Sustainable Communities</div>
        <div>✅ UAE Net Zero by 2050 Strategic Initiative</div>
      </div>

      <hr style="border-color:#ecf0f1;margin-top:22px">
      <div style="text-align:center;font-size:12px;color:#aaa">
        Built with ❤️ for sustainability · NabdFlow · 2026
      </div>
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    page, uploaded, use_sample = sidebar()

    # Load data
    df_raw = None
    if uploaded is not None:
        try:
            df_raw = (pd.read_csv(uploaded) if uploaded.name.endswith(".csv")
                      else pd.read_excel(uploaded))
            st.sidebar.success(f"✅ Loaded {len(df_raw):,} rows")
        except Exception as e:
            st.sidebar.error(f"❌ Load error: {e}")

    if df_raw is None or use_sample:
        df_raw = make_sample()
        if uploaded is None:
            st.sidebar.info("📊 Using built-in sample data (30 days · 5 locations)")

    df = process(df_raw)

    # Route
    if   "Overview"        in page: pg_overview(df)
    elif "Location"        in page: pg_location(df)
    elif "Leak"            in page: pg_leak(df)
    elif "Recommendations" in page: pg_recs(df)
    elif "Impact"          in page: pg_impact(df)
    elif "About"           in page: pg_about()

if __name__ == "__main__":
    main()
