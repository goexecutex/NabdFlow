# ============================================================
#  NabdFlow — AI-Powered Water Intelligence | Streamlit App
#  Requirements: pip install streamlit plotly pandas numpy anthropic
#  API Key:  Add  ANTHROPIC_API_KEY = "sk-..."  to .streamlit/secrets.toml
# ============================================================

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import random
from datetime import datetime

# ------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------
st.set_page_config(
    page_title="NabdFlow | Water Intelligence",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------------------
# CUSTOM CSS
# ------------------------------------------------------------
st.markdown("""
<style>
  .stApp { background-color: #050d1c; color: #d8eeff; }
  section[data-testid="stSidebar"] {
      background-color: #081525 !important;
      border-right: 1px solid #163557;
  }
  .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
  div[data-testid="metric-container"] {
      background: #0d1e38;
      border: 1px solid #163557;
      border-radius: 12px;
      padding: 14px 16px !important;
  }
  [data-testid="stMetricLabel"]  { color: #5a8aaa !important; font-size: 10px !important;
                                    text-transform: uppercase; letter-spacing: 1px; }
  [data-testid="stMetricValue"]  { color: #d8eeff !important; font-size: 22px !important;
                                    font-weight: 800 !important; }
  [data-testid="stMetricDelta"]  { font-size: 10px !important; }
  .stButton > button {
      background: linear-gradient(135deg, #00c8ff, #0055ff) !important;
      color: #04111f !important; font-weight: 700 !important;
      border: none !important; border-radius: 8px !important;
  }
  .stButton > button:hover { opacity: 0.88; }
  .stChatMessage { background: #0d1e38 !important; border: 1px solid #163557 !important; border-radius: 10px !important; }
  .stChatInputContainer > div { background: #0d1e38 !important; border: 1px solid #163557 !important; border-radius: 8px !important; }
  .stChatInputContainer input  { color: #d8eeff !important; }
  h1, h2, h3 { color: #d8eeff !important; }
  hr { border-color: #163557; }
  .stRadio > div > label { color: #5a8aaa !important; }
  .stRadio > div > label:hover { color: #d8eeff !important; }
  div[data-baseweb="radio"] input:checked + div { background-color: #00c8ff !important; }
  .nabdcard {
      background: #0d1e38; border: 1px solid #163557;
      border-radius: 12px; padding: 16px 18px; margin-bottom: 12px;
  }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# DATA
# ------------------------------------------------------------
ZONES = [
    {"id":1,"name":"Main Academic Building","short":"MAB","icon":"🏛️","baseline":450,"current":421,"status":"normal", "eff":94},
    {"id":2,"name":"Science & Tech Block",  "short":"STB","icon":"🔬","baseline":380,"current":512,"status":"anomaly","eff":65},
    {"id":3,"name":"Student Housing A",     "short":"SHA","icon":"🏘️","baseline":820,"current":798,"status":"normal", "eff":97},
    {"id":4,"name":"Student Housing B",     "short":"SHB","icon":"🏠","baseline":750,"current":901,"status":"alert",  "eff":72},
    {"id":5,"name":"Sports Complex",        "short":"SPC","icon":"⚽","baseline":600,"current":578,"status":"normal", "eff":96},
    {"id":6,"name":"Library & Research",    "short":"LIB","icon":"📚","baseline":220,"current":215,"status":"normal", "eff":98},
    {"id":7,"name":"Cafeteria & Dining",    "short":"CAF","icon":"🍽️","baseline":480,"current":503,"status":"normal", "eff":89},
    {"id":8,"name":"Admin & Offices",       "short":"ADM","icon":"💼","baseline":180,"current":267,"status":"leak",   "eff":58},
]

ALERTS = [
    {"type":"leak",    "zone":"Admin & Offices",      "msg":"Pipe leak — 87 L/hr excess flow detected after business hours",        "time":"12m ago","aed":43.5,"sev":"critical"},
    {"type":"anomaly", "zone":"Student Housing B",    "msg":"Consumption 20% above 7-day baseline for 3+ consecutive hours",         "time":"47m ago","aed":28.2,"sev":"high"},
    {"type":"anomaly", "zone":"Science & Tech Block", "msg":"Lab cooling water spike — possible thermostatic valve failure",          "time":"1.5h ago","aed":18.7,"sev":"medium"},
    {"type":"info",    "zone":"Cafeteria & Dining",   "msg":"Usage slightly above average — catering event likely in progress",       "time":"3h ago","aed":6.3,"sev":"low"},
    {"type":"resolved","zone":"Sports Complex",       "msg":"Irrigation anomaly resolved — system returned to normal baseline",       "time":"5h ago","aed":0,"sev":"resolved"},
]

WEEKLY = pd.DataFrame({
    "Day":   ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
    "Usage": [18240,17890,19100,17200,15600,9800,8900],
    "Saved": [2840,3190,1900,3800,4200,5600,6100],
    "AED":   [1022,1148,684,1368,1512,2016,2196],
})

np.random.seed(42)
_base = [120 + np.sin(i/3.5)*55 + (105 if 7<=i<=19 else 0) for i in range(24)]
HOURLY = pd.DataFrame({
    "Hour":      [f"{str(i).zfill(2)}:00" for i in range(24)],
    "Actual":    [max(0, int(b + np.random.normal(0,14))) for b in _base],
    "Predicted": [int(b*1.06) for b in _base],
    "Baseline":  [int(b*1.22) for b in _base],
})

# ------------------------------------------------------------
# CHART THEME
# ------------------------------------------------------------
BG     = "#0d1e38"
GRID   = "rgba(255,255,255,0.04)"
MUTED  = "#5a8aaa"
ACCENT = "#00c8ff"
GREEN  = "#00e5a0"
YELLOW = "#ffb347"
RED    = "#ff5272"
PURPLE = "#a78bfa"

BASE_LAYOUT = dict(
    paper_bgcolor=BG, plot_bgcolor=BG,
    font=dict(color=MUTED, size=11),
    margin=dict(l=40, r=10, t=10, b=30),
    xaxis=dict(gridcolor=GRID, showgrid=True, zeroline=False),
    yaxis=dict(gridcolor=GRID, showgrid=True, zeroline=False),
)
LEGEND_DEFAULT  = dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10))
LEGEND_TOP      = dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10), orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
LEGEND_BOTTOM   = dict(bgcolor="rgba(0,0,0,0)", font=dict(size=9),  orientation="h", y=-0.15)

# ------------------------------------------------------------
# SESSION STATE
# ------------------------------------------------------------
defaults = {"chat": [{"role":"assistant","content":"Hello! I'm NabdFlow AI. Ask me anything about campus water systems — anomalies, leaks, predictions, savings, or sustainability metrics."}],
            "insights": "", "report": ""}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ------------------------------------------------------------
# AI HELPER
# ------------------------------------------------------------
SYSTEM = """You are NabdFlow AI Engine — an expert water intelligence system for a UAE university campus.
Current campus snapshot:
- 8 monitored zones | 3 active anomalies
- CRITICAL: Admin & Offices — pipe leak, 87L/hr excess, efficiency 58%
- HIGH: Student Housing B — 20% above baseline, efficiency 72%
- MEDIUM: Science & Tech Block — cooling spike, efficiency 65%
- Today: 18,247 m3 consumed | Baseline: 20,587 m3 | Saved: 2,340 m3 (11.4%)
- AED saved today: 847 AED | Tariff: ~0.36 AED/m3
- Campus efficiency score: 78/100 (up 4 pts from last week)
Be precise, professional, and data-driven. Use markdown headers for structure."""

def call_claude(messages: list) -> str:
    try:
        import anthropic
        key = st.secrets.get("ANTHROPIC_API_KEY", "")
        if not key:
            return "**No API key found.** Add `ANTHROPIC_API_KEY = 'sk-...'` to `.streamlit/secrets.toml`."
        client = anthropic.Anthropic(api_key=key)
        resp = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=SYSTEM,
            messages=messages
        )
        return resp.content[0].text
    except ImportError:
        return "**anthropic library not installed.** Run: `pip install anthropic`"
    except Exception as e:
        return f"**Error:** {e}"

# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------
def status_badge(s: str) -> str:
    cfg = {
        "normal":  ("#00e5a0","rgba(0,229,160,0.12)","Normal"),
        "anomaly": ("#ffb347","rgba(255,179,71,0.12)","Anomaly"),
        "alert":   ("#ffb347","rgba(255,179,71,0.12)","Alert"),
        "leak":    ("#ff5272","rgba(255,82,114,0.12)","Leak"),
        "resolved":("#5a8aaa","rgba(90,138,170,0.08)","Resolved"),
    }
    c, bg, lbl = cfg.get(s, (MUTED,"transparent",s))
    return (f'<span style="background:{bg};color:{c};padding:2px 10px;'
            f'border-radius:20px;font-size:11px;font-weight:700">{lbl}</span>')

def eff_color(e: int) -> str:
    return GREEN if e >= 90 else (YELLOW if e >= 70 else RED)

def sev_color(s: str) -> str:
    return {"critical":RED,"high":YELLOW,"medium":YELLOW,"low":ACCENT,"resolved":MUTED}.get(s, MUTED)

def sev_bg(s: str) -> str:
    return {"critical":"rgba(255,82,114,0.12)","high":"rgba(255,179,71,0.12)",
            "medium":"rgba(255,179,71,0.10)","low":"rgba(0,200,255,0.10)",
            "resolved":"rgba(90,138,170,0.08)"}.get(s, "transparent")

def section_header(title: str, subtitle: str = ""):
    st.markdown(f"""
    <div class="nabdcard" style="margin-bottom:8px">
      <div style="font-weight:700;font-size:14px">{title}</div>
      {"" if not subtitle else f'<div style="color:{MUTED};font-size:11px;margin-top:3px">{subtitle}</div>'}
    </div>""", unsafe_allow_html=True)

# ------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------
with st.sidebar:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;padding:4px 0 14px">
      <div style="width:38px;height:38px;border-radius:10px;background:linear-gradient(135deg,#00c8ff,#0055ff);
           display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0">💧</div>
      <div>
        <div style="font-weight:900;font-size:17px;color:#d8eeff">NabdFlow</div>
        <div style="color:{MUTED};font-size:9px;letter-spacing:1.5px;text-transform:uppercase">Water Intelligence</div>
      </div>
    </div>
    <div style="color:{MUTED};font-size:10px;margin-bottom:14px">&#1606;&#1576;&#1590; &#1575;&#1604;&#1605;&#1610;&#1575;&#1607; &#1575;&#1604;&#1584;&#1603;&#1610; &middot; UAE Campus</div>
    <div style="background:rgba(0,229,160,0.06);border:1px solid rgba(0,229,160,0.2);border-radius:8px;
         padding:8px 12px;margin-bottom:18px;display:flex;align-items:center;gap:8px">
      <span style="display:inline-block;width:8px;height:8px;background:#00e5a0;border-radius:50%;
            box-shadow:0 0 8px #00e5a0"></span>
      <span style="color:#00e5a0;font-size:11px;font-weight:700">LIVE</span>
      <span style="color:{MUTED};font-size:11px">{random.randint(841,857)} L/min</span>
    </div>""", unsafe_allow_html=True)

    nav = st.radio("nav", [
        "📊  Overview Dashboard",
        "🗺️  Zone Intelligence",
        "🚨  Anomaly & Alerts",
        "🤖  AI Insights Engine",
        "🌿  Sustainability Hub",
        "💬  AI Chat Assistant",
    ], label_visibility="collapsed")

    st.markdown(f"<hr style='border-color:#163557;margin:12px 0'>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:{MUTED};font-size:9px;letter-spacing:1.2px;text-transform:uppercase;margin-bottom:10px'>Campus Status</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    c1.metric("Zones",      "8");     c1.metric("Efficiency", "78%")
    c2.metric("Alerts 🔴",  "3");     c2.metric("Saved", "847 AED")

# ------------------------------------------------------------
# MAIN HEADER
# ------------------------------------------------------------
TITLES = {
    "📊  Overview Dashboard": "📊 Overview Dashboard",
    "🗺️  Zone Intelligence":  "🗺️ Zone Intelligence",
    "🚨  Anomaly & Alerts":   "🚨 Anomaly & Alert Center",
    "🤖  AI Insights Engine": "🤖 AI Insights Engine",
    "🌿  Sustainability Hub":  "🌿 Sustainability Hub",
    "💬  AI Chat Assistant":  "💬 AI Chat Assistant",
}
hc1, hc2 = st.columns([4, 1])
with hc1:
    st.markdown(f"<h1 style='margin:0;font-size:21px;font-weight:900'>{TITLES.get(nav,nav)}</h1>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:{MUTED};font-size:11px;margin-top:2px'>University Campus &middot; NabdFlow AI &middot; {datetime.now().strftime('%A, %d %B %Y')}</div>", unsafe_allow_html=True)
with hc2:
    if st.button("✨ AI Analysis"):
        st.session_state["insights"] = ""

st.markdown(f"<div style='border-bottom:1px solid #163557;margin:10px 0 16px'></div>", unsafe_allow_html=True)

# ============================================================
# VIEW: OVERVIEW DASHBOARD
# ============================================================
if nav == "📊  Overview Dashboard":

    # KPIs
    k1,k2,k3,k4,k5 = st.columns(5)
    k1.metric("💧 Consumption Today", "18,247 m³",  "↓ 11.4% vs baseline")
    k2.metric("⚡ Live Flow Rate",     f"{random.randint(843,856)} L/min", "All zones")
    k3.metric("💰 AED Saved Today",    "847 AED",    "+vs projected")
    k4.metric("🚨 Active Alerts",      "3",          "1 critical · 1 high")
    k5.metric("📈 Efficiency Score",   "78 / 100",   "↑ 4 pts this week")

    st.markdown("")

    # Hourly chart
    fig_hourly = go.Figure()
    fig_hourly.add_trace(go.Scatter(
        x=HOURLY["Hour"], y=HOURLY["Baseline"], name="Baseline",
        line=dict(color=MUTED, dash="dot", width=1.5)))
    fig_hourly.add_trace(go.Scatter(
        x=HOURLY["Hour"], y=HOURLY["Predicted"], name="Predicted",
        line=dict(color=PURPLE, width=1.5),
        fill="tozeroy", fillcolor="rgba(167,139,250,0.05)"))
    fig_hourly.add_trace(go.Scatter(
        x=HOURLY["Hour"], y=HOURLY["Actual"], name="Actual",
        line=dict(color=ACCENT, width=2.5),
        fill="tozeroy", fillcolor="rgba(0,200,255,0.08)"))
    fig_hourly.update_layout(**BASE_LAYOUT, height=240, legend=LEGEND_TOP)

    st.markdown('<div class="nabdcard">', unsafe_allow_html=True)
    st.markdown(f"<div style='font-weight:700;font-size:13px'>Today's Hourly Water Consumption</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:{MUTED};font-size:11px;margin-bottom:6px'>Actual vs Predicted vs Baseline &middot; m&sup3;/hr &middot; All zones</div>", unsafe_allow_html=True)
    st.plotly_chart(fig_hourly, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("")
    left, right = st.columns([2, 1])

    with left:
        st.markdown('<div class="nabdcard">', unsafe_allow_html=True)
        st.markdown(f"<div style='font-weight:700;font-size:13px;margin-bottom:12px'>Zone Status Overview</div>", unsafe_allow_html=True)
        for z in ZONES:
            ec = eff_color(z["eff"])
            delta_p = (z["current"] - z["baseline"]) / z["baseline"] * 100
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;padding:7px 9px;margin-bottom:6px;
                 border-radius:8px;background:rgba(255,255,255,0.02);border:1px solid #163557">
              <span style="font-size:16px">{z["icon"]}</span>
              <div style="flex:1;min-width:0">
                <div style="font-size:12px;font-weight:600;color:#d8eeff">{z["name"]}</div>
                <div style="font-size:10px;color:{MUTED};margin-top:1px">{z["current"]} m&sup3;/hr &nbsp;&middot;&nbsp; {z["eff"]}% eff</div>
              </div>
              <div style="width:70px;flex-shrink:0">
                <div style="height:5px;background:rgba(255,255,255,0.07);border-radius:3px;overflow:hidden">
                  <div style="width:{z["eff"]}%;height:100%;background:{ec};border-radius:3px"></div>
                </div>
              </div>
              {status_badge(z["status"])}
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        # Weekly bar chart
        fig_week = go.Figure()
        fig_week.add_trace(go.Bar(x=WEEKLY["Day"], y=WEEKLY["Usage"], name="Usage m³",
                                  marker_color=ACCENT, marker_opacity=0.65, marker_line_width=0))
        fig_week.add_trace(go.Bar(x=WEEKLY["Day"], y=WEEKLY["Saved"], name="Saved m³",
                                  marker_color=GREEN, marker_opacity=0.85, marker_line_width=0))
        fig_week.update_layout(**BASE_LAYOUT, barmode="group", height=200, legend=LEGEND_DEFAULT)
        st.markdown('<div class="nabdcard">', unsafe_allow_html=True)
        st.markdown(f"<div style='font-weight:700;font-size:13px;margin-bottom:4px'>Weekly Usage vs Savings</div>", unsafe_allow_html=True)
        st.plotly_chart(fig_week, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

        # Pie chart
        zone_colors = [RED if z["status"]=="leak" else YELLOW if z["status"] in ["anomaly","alert"] else ACCENT for z in ZONES]
        fig_pie = go.Figure(go.Pie(
            labels=[z["short"] for z in ZONES],
            values=[z["current"] for z in ZONES],
            hole=0.5,
            marker=dict(colors=zone_colors, line=dict(color="#050d1c", width=2))
        ))
        fig_pie.update_layout(**BASE_LAYOUT, height=190, showlegend=True, legend=LEGEND_BOTTOM)
        st.markdown('<div class="nabdcard">', unsafe_allow_html=True)
        st.markdown(f"<div style='font-weight:700;font-size:13px;margin-bottom:4px'>Consumption by Zone</div>", unsafe_allow_html=True)
        st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# VIEW: ZONE INTELLIGENCE
# ============================================================
elif nav == "🗺️  Zone Intelligence":
    cols_z = st.columns(2)
    for i, z in enumerate(ZONES):
        col = cols_z[i % 2]
        delta = z["current"] - z["baseline"]
        delta_p = delta / z["baseline"] * 100
        ec = eff_color(z["eff"])
        border = RED if z["status"]=="leak" else (YELLOW if z["status"] in ["anomaly","alert"] else "#163557")
        with col:
            st.markdown(f"""
            <div style="background:#0d1e38;border:1.5px solid {border};border-radius:12px;
                 padding:18px;margin-bottom:12px">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px">
                <div style="display:flex;align-items:center;gap:10px">
                  <span style="font-size:24px">{z["icon"]}</span>
                  <div>
                    <div style="font-weight:700;font-size:13px;color:#d8eeff">{z["name"]}</div>
                    <div style="color:{MUTED};font-size:10px;margin-top:2px">Zone ID: {z["short"]}</div>
                  </div>
                </div>
                {status_badge(z["status"])}
              </div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px">
                <div style="background:rgba(255,255,255,0.03);border-radius:8px;padding:9px 11px">
                  <div style="color:{MUTED};font-size:9px;text-transform:uppercase;letter-spacing:0.8px">Current</div>
                  <div style="color:#d8eeff;font-weight:800;font-size:21px;margin-top:3px">
                    {z["current"]}<span style="font-size:10px;color:{MUTED}"> m&sup3;/hr</span></div>
                </div>
                <div style="background:rgba(255,255,255,0.03);border-radius:8px;padding:9px 11px">
                  <div style="color:{MUTED};font-size:9px;text-transform:uppercase;letter-spacing:0.8px">vs Baseline</div>
                  <div style="color:{'#ff5272' if delta>0 else '#00e5a0'};font-weight:800;font-size:21px;margin-top:3px">
                    {'+' if delta>0 else ''}{delta_p:.1f}<span style="font-size:10px">%</span></div>
                </div>
              </div>
              <div>
                <div style="display:flex;justify-content:space-between;margin-bottom:5px">
                  <span style="color:{MUTED};font-size:10px">Efficiency Score</span>
                  <span style="font-size:11px;font-weight:700;color:{ec}">{z["eff"]}%</span>
                </div>
                <div style="height:6px;background:rgba(255,255,255,0.06);border-radius:3px;overflow:hidden">
                  <div style="width:{z["eff"]}%;height:100%;background:{ec};border-radius:3px"></div>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

# ============================================================
# VIEW: ANOMALY & ALERTS
# ============================================================
elif nav == "🚨  Anomaly & Alerts":
    a1, a2, a3, a4 = st.columns(4)
    a1.metric("Total Alerts",  str(len(ALERTS)))
    a2.metric("Critical 🔴",   "1")
    a3.metric("High 🟡",       "1")
    a4.metric("Active",        "4")
    st.markdown("")

    TYPE_ICONS = {"leak":"💧","anomaly":"⚠️","info":"ℹ️","resolved":"✅"}
    for a in ALERTS:
        border = sev_color(a["sev"])
        aed_html = (f'<span style="color:{RED};font-size:11px;font-weight:700">-{a["aed"]} AED/hr</span>'
                    if a["aed"] > 0 else "")
        st.markdown(f"""
        <div style="background:#0d1e38;border:1px solid {border};border-left:4px solid {border};
             border-radius:12px;padding:15px 18px;margin-bottom:10px">
          <div style="display:flex;gap:14px;align-items:flex-start">
            <span style="font-size:22px;margin-top:1px">{TYPE_ICONS.get(a["type"],"ℹ️")}</span>
            <div style="flex:1">
              <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px">
                <span style="font-weight:700;font-size:13px;color:#d8eeff">{a["zone"]}</span>
                <div style="display:flex;gap:8px;align-items:center">
                  {aed_html}
                  <span style="font-size:10px;font-weight:700;color:{sev_color(a['sev'])};
                        background:{sev_bg(a['sev'])};padding:2px 10px;border-radius:20px;
                        text-transform:uppercase">{a["sev"]}</span>
                </div>
              </div>
              <div style="color:{MUTED};font-size:12px;margin-top:5px;line-height:1.5">{a["msg"]}</div>
              <div style="color:{MUTED};font-size:11px;margin-top:6px">&#128336; {a["time"]}</div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

# ============================================================
# VIEW: AI INSIGHTS ENGINE
# ============================================================
elif nav == "🤖  AI Insights Engine":
    section_header("🤖 AI Water Intelligence Analysis",
                   "Powered by NabdFlow AI Engine · Real-time campus data analysis")

    if st.button("✨ Generate AI Insights", type="primary"):
        st.session_state["insights"] = ""
        with st.spinner("Analyzing 8 zones · 24h data · 3 active anomalies..."):
            prompt = """Analyze today's campus water data and provide a structured AI report:

## Key Findings
3 most critical observations with specific figures.

## Priority Actions Required
Ranked by urgency. Include estimated resolution time and responsible team.

## 24-Hour Demand Forecast
Expected demand pattern, peak risk windows, recommended pre-actions.

## Quick-Win Optimizations
3 specific actions. Each with estimated m3 and AED savings.

## Efficiency Score Breakdown
What drives the 78/100 score and a concrete roadmap to reach 90+."""
            st.session_state["insights"] = call_claude([{"role":"user","content":prompt}])

    if st.session_state["insights"]:
        st.markdown(f'<div style="background:rgba(0,0,0,0.2);border:1px solid #163557;border-radius:10px;padding:20px">', unsafe_allow_html=True)
        st.markdown(st.session_state["insights"])
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="text-align:center;padding:60px 20px;color:{MUTED}">
          <div style="font-size:52px;margin-bottom:14px">&#129504;</div>
          <div style="font-size:15px;margin-bottom:8px;color:#d8eeff">AI Analysis Engine Ready</div>
          <div style="font-size:12px">Click "Generate AI Insights" to run a full analysis on current<br>campus water data — anomaly triage, demand forecasting, and optimizations.</div>
        </div>""", unsafe_allow_html=True)

# ============================================================
# VIEW: SUSTAINABILITY HUB
# ============================================================
elif nav == "🌿  Sustainability Hub":
    s1,s2,s3,s4,s5 = st.columns(5)
    s1.metric("💧 Water Saved / Week", "21,630 m³",  "vs baseline")
    s2.metric("🌿 Carbon Offset",      "21.6 t CO₂", "~1,440 trees")
    s3.metric("💰 AED Savings / Week", "7,787 AED",  "Proj. ~405K/yr")
    s4.metric("🏆 SDG 6 Score",        "B+",         "Clean Water")
    s5.metric("🌍 Sustainability",      "78 / 100",   "↑ 6 pts YoY")

    st.markdown("")
    ca, cb = st.columns(2)

    with ca:
        fig_aed = go.Figure(go.Bar(
            x=WEEKLY["Day"], y=WEEKLY["AED"], name="AED Saved",
            marker_color=YELLOW, marker_opacity=0.85, marker_line_width=0,
        ))
        fig_aed.update_layout(**BASE_LAYOUT, height=230, legend=LEGEND_DEFAULT)
        st.markdown('<div class="nabdcard">', unsafe_allow_html=True)
        st.markdown(f"<div style='font-weight:700;font-size:13px;margin-bottom:4px'>AED Savings per Day This Week</div>", unsafe_allow_html=True)
        st.plotly_chart(fig_aed, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    with cb:
        st.markdown('<div class="nabdcard">', unsafe_allow_html=True)
        st.markdown(f"<div style='font-weight:700;font-size:13px;margin-bottom:14px'>Sustainability Impact Metrics</div>", unsafe_allow_html=True)
        for label, val, color in [
            ("UN SDG 6 — Clean Water",      78,  ACCENT),
            ("UN SDG 13 — Climate Action",  72,  GREEN),
            ("Water Reuse Rate",            34,  PURPLE),
            ("Leak Response Rate",          91,  YELLOW),
            ("Campus Coverage (Monitored)", 100, GREEN),
        ]:
            st.markdown(f"""
            <div style="margin-bottom:10px">
              <div style="display:flex;justify-content:space-between;margin-bottom:4px">
                <span style="font-size:11px;color:{MUTED}">{label}</span>
                <span style="font-size:11px;font-weight:700;color:{color}">{val}%</span>
              </div>
              <div style="height:5px;background:rgba(255,255,255,0.06);border-radius:3px;overflow:hidden">
                <div style="width:{val}%;height:100%;background:{color};border-radius:3px"></div>
              </div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("")
    section_header("📋 Weekly Sustainability Intelligence Report",
                   "AI-generated for Facilities Management & Sustainability Committee")

    if st.button("📄 Generate Sustainability Report", type="primary"):
        st.session_state["report"] = ""
        with st.spinner("Compiling weekly data · Calculating carbon metrics · Drafting report..."):
            prompt = """Generate a formal Weekly Water Sustainability Intelligence Report for the University Facilities Director and Sustainability Committee.

Sections to include:
1. Executive Summary (3-4 sentences)
2. Weekly Consumption Overview (avg 13,820 m3/day, total saved: 21,630 m3, week-on-week comparison)
3. Anomaly and Leak Detection Summary (3 incidents this week, AED impact)
4. AI Predictive Outlook for Next 7 Days
5. Sustainability Impact (carbon equiv: 21.6 tonnes CO2, SDG 6 alignment, water stewardship rating)
6. Financial Impact Analysis (7,787 AED saved this week, projected annual savings ~405,000 AED)
7. Recommended Actions for Facilities Management (prioritized, with owner and deadline)
8. Conclusion

Use formal report language. Be specific with all numbers and percentages."""
            st.session_state["report"] = call_claude([{"role":"user","content":prompt}])

    if st.session_state["report"]:
        st.markdown('<div style="background:rgba(0,0,0,0.2);border:1px solid #163557;border-radius:10px;padding:20px">', unsafe_allow_html=True)
        st.markdown(st.session_state["report"])
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# VIEW: AI CHAT ASSISTANT
# ============================================================
elif nav == "💬  AI Chat Assistant":
    section_header("💬 NabdFlow AI Chat",
                   "Ask about leaks, anomalies, savings, predictions, zone data, or sustainability metrics")

    # Quick prompt buttons
    quick_prompts = ["What zones have anomalies?", "How much water can I save?",
                     "Explain the Admin Block leak", "Predict tomorrow's demand"]
    qc = st.columns(len(quick_prompts))
    for i, qp in enumerate(quick_prompts):
        if qc[i].button(qp, key=f"qp_{i}"):
            st.session_state["chat"].append({"role":"user","content":qp})
            with st.spinner("Thinking..."):
                history = [{"role":m["role"],"content":m["content"]} for m in st.session_state["chat"]]
                reply = call_claude(history)
            st.session_state["chat"].append({"role":"assistant","content":reply})
            st.rerun()

    st.markdown("")

    # Chat history
    for m in st.session_state["chat"]:
        with st.chat_message(m["role"], avatar="🤖" if m["role"]=="assistant" else "👤"):
            st.markdown(m["content"])

    # Chat input
    if user_input := st.chat_input("Ask about campus water systems..."):
        st.session_state["chat"].append({"role":"user","content":user_input})
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                history = [{"role":m["role"],"content":m["content"]} for m in st.session_state["chat"]]
                reply = call_claude(history)
            st.markdown(reply)
        st.session_state["chat"].append({"role":"assistant","content":reply})
        st.rerun()
