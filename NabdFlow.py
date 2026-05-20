# ============================================================
#  NabdFlow - AI-Powered Water Intelligence | Streamlit App
#  pip install streamlit plotly pandas numpy groq
#  Secrets: GROQ_API_KEY = "gsk_..." in .streamlit/secrets.toml
# ============================================================

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import random
import io
from datetime import datetime, timedelta

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
# CSS
# ------------------------------------------------------------
st.markdown("""
<style>
  .stApp { background-color: #050d1c; color: #d8eeff; }
  section[data-testid="stSidebar"] { background-color: #081525 !important; border-right: 1px solid #163557; }
  .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
  div[data-testid="metric-container"] {
      background: #0d1e38; border: 1px solid #163557; border-radius: 12px; padding: 14px 16px !important;
  }
  [data-testid="stMetricLabel"]  { color: #5a8aaa !important; font-size: 10px !important; text-transform: uppercase; letter-spacing: 1px; }
  [data-testid="stMetricValue"]  { color: #d8eeff !important; font-size: 22px !important; font-weight: 800 !important; }
  [data-testid="stMetricDelta"]  { font-size: 10px !important; }
  .stButton > button { background: linear-gradient(135deg,#00c8ff,#0055ff) !important; color:#04111f !important; font-weight:700 !important; border:none !important; border-radius:8px !important; }
  .stButton > button:hover { opacity: 0.85; }
  h1,h2,h3 { color: #d8eeff !important; }
  hr { border-color: #163557; }
  .nabdcard { background:#0d1e38; border:1px solid #163557; border-radius:12px; padding:16px 18px; margin-bottom:12px; }
  .stTabs [data-baseweb="tab-list"] { background:#081525; border-radius:10px; }
  .stTabs [data-baseweb="tab"] { color:#5a8aaa; }
  .stTabs [aria-selected="true"] { color:#00c8ff !important; }
  .stDataFrame { background: #0d1e38 !important; }
  div[data-testid="stFileUploader"] { background:#0d1e38; border:1px dashed #163557; border-radius:10px; padding:10px; }
  .stTextInput input, .stNumberInput input, .stSelectbox select {
      background: #0d1e38 !important; color: #d8eeff !important; border: 1px solid #163557 !important;
  }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# COLORS
# ------------------------------------------------------------
BG     = "#0d1e38"
GRID   = "rgba(255,255,255,0.04)"
MUTED  = "#5a8aaa"
ACCENT = "#00c8ff"
GREEN  = "#00e5a0"
YELLOW = "#ffb347"
RED    = "#ff5272"
PURPLE = "#a78bfa"

# ------------------------------------------------------------
# DEMO DATA (used when no CSV is uploaded)
# ------------------------------------------------------------
DEMO_ZONES = [
    {"id":1,"name":"Main Academic Building","short":"MAB","icon":"🏛️","baseline":450,"current":421,"status":"normal", "eff":94},
    {"id":2,"name":"Science & Tech Block",  "short":"STB","icon":"🔬","baseline":380,"current":512,"status":"anomaly","eff":65},
    {"id":3,"name":"Student Housing A",     "short":"SHA","icon":"🏘️","baseline":820,"current":798,"status":"normal", "eff":97},
    {"id":4,"name":"Student Housing B",     "short":"SHB","icon":"🏠","baseline":750,"current":901,"status":"alert",  "eff":72},
    {"id":5,"name":"Sports Complex",        "short":"SPC","icon":"⚽","baseline":600,"current":578,"status":"normal", "eff":96},
    {"id":6,"name":"Library & Research",    "short":"LIB","icon":"📚","baseline":220,"current":215,"status":"normal", "eff":98},
    {"id":7,"name":"Cafeteria & Dining",    "short":"CAF","icon":"🍽️","baseline":480,"current":503,"status":"normal", "eff":89},
    {"id":8,"name":"Admin & Offices",       "short":"ADM","icon":"💼","baseline":180,"current":267,"status":"leak",   "eff":58},
]
DEMO_ALERTS = [
    {"type":"leak",    "zone":"Admin & Offices",      "msg":"Pipe leak &mdash; 87 L/hr excess flow detected after business hours",   "time":"12m ago","aed":43.5,"sev":"critical"},
    {"type":"anomaly", "zone":"Student Housing B",    "msg":"Consumption 20% above 7-day baseline for 3+ consecutive hours",          "time":"47m ago","aed":28.2,"sev":"high"},
    {"type":"anomaly", "zone":"Science & Tech Block", "msg":"Lab cooling water spike &mdash; possible thermostatic valve failure",     "time":"1.5h ago","aed":18.7,"sev":"medium"},
    {"type":"info",    "zone":"Cafeteria & Dining",   "msg":"Usage slightly above average &mdash; catering event likely in progress",  "time":"3h ago","aed":6.3,"sev":"low"},
    {"type":"resolved","zone":"Sports Complex",       "msg":"Irrigation anomaly resolved &mdash; returned to normal baseline",         "time":"5h ago","aed":0,"sev":"resolved"},
]
DEMO_WEEKLY = pd.DataFrame({
    "Day":["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
    "Usage":[18240,17890,19100,17200,15600,9800,8900],
    "Saved":[2840,3190,1900,3800,4200,5600,6100],
    "AED":  [1022,1148,684,1368,1512,2016,2196],
})
np.random.seed(42)
_b = [120 + np.sin(i/3.5)*55 + (105 if 7<=i<=19 else 0) for i in range(24)]
DEMO_HOURLY = pd.DataFrame({
    "Hour":      [f"{str(i).zfill(2)}:00" for i in range(24)],
    "Actual":    [max(0, int(v+np.random.normal(0,14))) for v in _b],
    "Predicted": [int(v*1.06) for v in _b],
    "Baseline":  [int(v*1.22) for v in _b],
})

# ------------------------------------------------------------
# CHART LAYOUT HELPERS
# ------------------------------------------------------------
BASE_LAYOUT = dict(
    paper_bgcolor=BG, plot_bgcolor=BG,
    font=dict(color=MUTED, size=11),
    margin=dict(l=40,r=10,t=10,b=30),
    xaxis=dict(gridcolor=GRID,showgrid=True,zeroline=False),
    yaxis=dict(gridcolor=GRID,showgrid=True,zeroline=False),
)
L_DEFAULT = dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10))
L_TOP     = dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10), orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
L_BOTTOM  = dict(bgcolor="rgba(0,0,0,0)", font=dict(size=9), orientation="h", y=-0.15)

# ------------------------------------------------------------
# SESSION STATE
# ------------------------------------------------------------
DEFAULTS = {
    "config": {
        "university": "Demo University",
        "campus":     "Main Campus",
        "tariff":     0.36,
        "currency":   "AED",
        "contact":    "",
        "logo_url":   "",
    },
    "raw_df":       None,
    "zones_data":   None,
    "hourly_data":  None,
    "weekly_data":  None,
    "alerts_data":  None,
    "chat":         [{"role":"assistant","content":"Hello! I am NabdFlow AI. Ask me anything about your campus water systems."}],
    "insights":     "",
    "report":       "",
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ------------------------------------------------------------
# DATA ACCESSORS (real CSV or demo)
# ------------------------------------------------------------
def using_real_data():
    return st.session_state["zones_data"] is not None

def get_zones():
    return st.session_state["zones_data"] if using_real_data() else DEMO_ZONES

def get_hourly_df():
    return st.session_state["hourly_data"] if using_real_data() else DEMO_HOURLY

def get_weekly_df():
    return st.session_state["weekly_data"] if using_real_data() else DEMO_WEEKLY

def get_alerts():
    return st.session_state["alerts_data"] if using_real_data() else DEMO_ALERTS

def get_cfg(key):
    return st.session_state["config"].get(key, "")

def currency():
    return st.session_state["config"]["currency"]

def tariff():
    return st.session_state["config"]["tariff"]

# ------------------------------------------------------------
# CSV PROCESSING
# ------------------------------------------------------------
def process_csv(df):
    df = df.copy()
    df.columns = [c.strip().lower().replace(" ","_") for c in df.columns]

    # Timestamp
    df["timestamp"] = pd.to_datetime(df["timestamp"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["timestamp"])
    df["hour"] = df["timestamp"].dt.hour
    df["date"] = df["timestamp"].dt.date

    # Zone stats
    zones_out = []
    for i, zone_name in enumerate(df["zone"].unique()):
        zdf = df[df["zone"] == zone_name].sort_values("timestamp")
        current  = float(zdf["consumption_m3"].iloc[-1])
        baseline = float(zdf["baseline_m3"].mean())
        eff = min(100, max(0, int(baseline / max(current, 0.001) * 100)))
        ratio = current / max(baseline, 0.001)
        if ratio > 1.40:   status = "leak"
        elif ratio > 1.20: status = "anomaly"
        elif ratio > 1.10: status = "alert"
        else:              status = "normal"
        zones_out.append({
            "id": i+1, "name": zone_name,
            "short": zone_name[:3].upper(), "icon": "🏛️",
            "baseline": int(baseline), "current": int(current),
            "status": status, "eff": eff,
        })

    # Hourly (aggregate all zones per hour)
    hourly_grp = df.groupby("hour").agg(
        actual=("consumption_m3","sum"),
        baseline=("baseline_m3","sum")
    ).reset_index()
    hourly_out = pd.DataFrame({"Hour": [f"{str(h).zfill(2)}:00" for h in range(24)]})
    hourly_out["Actual"]    = hourly_out["Hour"].apply(lambda h: int(hourly_grp[hourly_grp["hour"]==int(h[:2])]["actual"].sum()) if int(h[:2]) in hourly_grp["hour"].values else 0)
    hourly_out["Predicted"] = hourly_out["Hour"].apply(lambda h: int(hourly_grp[hourly_grp["hour"]==int(h[:2])]["baseline"].sum()*1.05) if int(h[:2]) in hourly_grp["hour"].values else 0)
    hourly_out["Baseline"]  = hourly_out["Hour"].apply(lambda h: int(hourly_grp[hourly_grp["hour"]==int(h[:2])]["baseline"].sum()) if int(h[:2]) in hourly_grp["hour"].values else 0)

    # Weekly
    weekly_grp = df.groupby("date").agg(
        Usage=("consumption_m3","sum"), baseline=("baseline_m3","sum")
    ).reset_index()
    weekly_grp["Saved"] = (weekly_grp["baseline"] - weekly_grp["Usage"]).clip(lower=0)
    weekly_grp["AED"]   = (weekly_grp["Saved"] * tariff()).round(2)
    weekly_grp["Day"]   = pd.to_datetime(weekly_grp["date"]).dt.strftime("%a")
    weekly_out = weekly_grp[["Day","Usage","Saved","AED"]].tail(7)

    # Alerts from anomalies
    alerts_out = []
    for z in zones_out:
        if z["status"] in ["leak","anomaly","alert"]:
            excess = max(0, z["current"] - z["baseline"])
            aed_hr = round(excess * tariff() / 24, 2)
            pct    = round((z["current"]-z["baseline"])/max(z["baseline"],1)*100)
            sev    = "critical" if z["status"]=="leak" else ("high" if z["status"]=="anomaly" else "medium")
            alerts_out.append({
                "type": z["status"], "zone": z["name"],
                "msg": f"Consumption {pct}% above baseline &mdash; auto-detected by NabdFlow AI",
                "time": "Just now", "aed": aed_hr, "sev": sev,
            })
    if not alerts_out:
        alerts_out.append({"type":"resolved","zone":"All Zones","msg":"No anomalies detected &mdash; all zones within normal range","time":"Now","aed":0,"sev":"resolved"})

    return zones_out, hourly_out, weekly_out, alerts_out

# ------------------------------------------------------------
# SAMPLE CSV GENERATOR
# ------------------------------------------------------------
def make_sample_csv():
    zones = ["Main Academic Building","Science Block","Student Housing A",
             "Student Housing B","Sports Complex","Admin & Offices"]
    baselines = [450,380,820,750,600,180]
    rows = []
    base_dt = datetime(2026,5,20,0,0)
    for h in range(24):
        ts = base_dt + timedelta(hours=h)
        for z, bl in zip(zones, baselines):
            noise = random.uniform(-0.05,0.08)
            spike = 1.45 if (z=="Admin & Offices" and h>18) else 1.0
            cons = round(bl * (1 + noise) * spike, 2)
            rows.append({"zone":z,"timestamp":ts.strftime("%Y-%m-%d %H:%M"),
                         "consumption_m3":cons,"baseline_m3":bl})
    return pd.DataFrame(rows)

# ------------------------------------------------------------
# GROQ AI
# ------------------------------------------------------------
def build_system():
    zones = get_zones()
    anomalies = [z for z in zones if z["status"]!="normal"]
    cfg = st.session_state["config"]
    return (
        f"You are NabdFlow AI Engine for {cfg['university']} - {cfg['campus']}.\n"
        f"Zones monitored: {len(zones)} | Anomalies: {len(anomalies)}\n"
        + "\n".join([f"- {z['name']}: {z['current']} m3 vs {z['baseline']} m3 baseline, eff {z['eff']}%, status: {z['status']}" for z in zones])
        + f"\nWater tariff: {cfg['tariff']} {cfg['currency']}/m3\n"
        "Be precise, professional, and data-driven. Use markdown headers."
    )

def call_ai(messages):
    try:
        from groq import Groq
        key = st.secrets.get("GROQ_API_KEY","")
        if not key:
            return "**No API key.** Add `GROQ_API_KEY = 'gsk_...'` to `.streamlit/secrets.toml`"
        client = Groq(api_key=key)
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"system","content":build_system()}] + messages,
            max_tokens=1000
        )
        return resp.choices[0].message.content
    except ImportError:
        return "**groq not installed.** Run: `pip install groq`"
    except Exception as e:
        return f"**Error:** {e}"

# ------------------------------------------------------------
# HTML HELPERS
# ------------------------------------------------------------
def status_badge(s):
    cfg = {"normal":("#00e5a0","rgba(0,229,160,0.12)","Normal"),
           "anomaly":("#ffb347","rgba(255,179,71,0.12)","Anomaly"),
           "alert":("#ffb347","rgba(255,179,71,0.12)","Alert"),
           "leak":("#ff5272","rgba(255,82,114,0.12)","Leak"),
           "resolved":("#5a8aaa","rgba(90,138,170,0.08)","Resolved")}
    c,bg,lbl = cfg.get(s,(MUTED,"transparent",s.capitalize()))
    return f'<span style="background:{bg};color:{c};padding:2px 10px;border-radius:20px;font-size:11px;font-weight:700">{lbl}</span>'

def eff_color(e):
    return GREEN if e>=90 else (YELLOW if e>=70 else RED)

def sev_color(s):
    return {"critical":RED,"high":YELLOW,"medium":YELLOW,"low":ACCENT,"resolved":MUTED}.get(s,MUTED)

def sev_bg(s):
    return {"critical":"rgba(255,82,114,0.12)","high":"rgba(255,179,71,0.12)","medium":"rgba(255,179,71,0.10)",
            "low":"rgba(0,200,255,0.10)","resolved":"rgba(90,138,170,0.08)"}.get(s,"transparent")

def render_alert(a):
    icons = {"leak":"💧","anomaly":"⚠️","info":"ℹ️","resolved":"✅"}
    bdr = sev_color(a["sev"])
    aed_h = f'<span style="color:{RED};font-size:11px;font-weight:700">-{a["aed"]} {currency()}/hr</span>' if a["aed"]>0 else ""
    st.markdown(
        f'<div style="background:#0d1e38;border:1px solid {bdr};border-left:4px solid {bdr};'
        f'border-radius:12px;padding:15px 18px;margin-bottom:10px">'
        f'<div style="display:flex;gap:12px;align-items:flex-start">'
        f'<span style="font-size:20px">{icons.get(a["type"],"i")}</span>'
        f'<div style="flex:1">'
        f'<div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:6px">'
        f'<span style="font-weight:700;font-size:13px;color:#d8eeff">{a["zone"]}</span>'
        f'<div style="display:flex;gap:8px;align-items:center">{aed_h}'
        f'<span style="font-size:10px;font-weight:700;color:{sev_color(a["sev"])};background:{sev_bg(a["sev"])};'
        f'padding:2px 10px;border-radius:20px;text-transform:uppercase">{a["sev"]}</span>'
        f'</div></div>'
        f'<div style="color:{MUTED};font-size:12px;margin-top:6px">{a["msg"]}</div>'
        f'<div style="color:{MUTED};font-size:11px;margin-top:6px">&#128336; {a["time"]}</div>'
        f'</div></div></div>', unsafe_allow_html=True)

# ------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------
cfg = st.session_state["config"]
with st.sidebar:
    uni_name = cfg.get("university","NabdFlow")
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:10px;padding:4px 0 10px">'
        f'<div style="width:38px;height:38px;border-radius:10px;background:linear-gradient(135deg,#00c8ff,#0055ff);'
        f'display:flex;align-items:center;justify-content:center;font-size:20px">💧</div>'
        f'<div><div style="font-weight:900;font-size:15px;color:#d8eeff">NabdFlow</div>'
        f'<div style="color:{MUTED};font-size:9px;letter-spacing:1px;text-transform:uppercase">Water Intelligence</div>'
        f'</div></div>'
        f'<div style="background:#0d1e38;border:1px solid #163557;border-radius:8px;padding:8px 12px;margin-bottom:6px">'
        f'<div style="color:#d8eeff;font-size:11px;font-weight:700">{uni_name}</div>'
        f'<div style="color:{MUTED};font-size:10px">{cfg.get("campus","Main Campus")}</div>'
        f'</div>', unsafe_allow_html=True)

    # Data status badge
    if using_real_data():
        st.markdown(f'<div style="background:rgba(0,229,160,0.08);border:1px solid rgba(0,229,160,0.3);border-radius:8px;padding:6px 10px;margin-bottom:10px;font-size:11px;color:#00e5a0;font-weight:700">&#9679; LIVE DATA &nbsp;·&nbsp; <span style="font-weight:400;color:{MUTED}">{len(get_zones())} zones</span></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="background:rgba(167,139,250,0.08);border:1px solid rgba(167,139,250,0.3);border-radius:8px;padding:6px 10px;margin-bottom:10px;font-size:11px;color:{PURPLE};font-weight:700">&#9650; DEMO DATA &nbsp;·&nbsp; <span style="font-weight:400;color:{MUTED}">Upload CSV to go live</span></div>', unsafe_allow_html=True)

    st.markdown(f'<div style="background:rgba(0,229,160,0.05);border:1px solid rgba(0,229,160,0.15);border-radius:8px;padding:6px 12px;margin-bottom:14px"><span style="color:#00e5a0;font-size:11px;font-weight:700">&#9679; LIVE &nbsp;</span><span style="color:{MUTED};font-size:11px">{random.randint(840,860)} L/min</span></div>', unsafe_allow_html=True)

    nav = st.radio("nav", [
        "⚙️  Setup & Data",
        "📊  Overview Dashboard",
        "🗺️  Zone Intelligence",
        "🚨  Anomaly & Alerts",
        "🤖  AI Insights Engine",
        "🌿  Sustainability Hub",
        "💬  AI Chat Assistant",
    ], label_visibility="collapsed")

    st.markdown(f'<hr style="border-color:#163557;margin:10px 0">', unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    c1.metric("Zones",      str(len(get_zones())));  c1.metric("Efficiency","78%")
    c2.metric("Alerts 🔴",  str(len([a for a in get_alerts() if a["sev"]!="resolved"]))); c2.metric("Tariff", f"{tariff()} {currency()}")

# ------------------------------------------------------------
# HEADER
# ------------------------------------------------------------
TITLES = {
    "⚙️  Setup & Data":      "⚙️ Setup & Data",
    "📊  Overview Dashboard": "📊 Overview Dashboard",
    "🗺️  Zone Intelligence":  "🗺️ Zone Intelligence",
    "🚨  Anomaly & Alerts":   "🚨 Anomaly & Alert Center",
    "🤖  AI Insights Engine": "🤖 AI Insights Engine",
    "🌿  Sustainability Hub":  "🌿 Sustainability Hub",
    "💬  AI Chat Assistant":  "💬 AI Chat Assistant",
}
hc1,hc2 = st.columns([4,1])
with hc1:
    st.markdown(f'<h1 style="margin:0;font-size:21px;font-weight:900">{TITLES.get(nav,nav)}</h1>', unsafe_allow_html=True)
    st.markdown(f'<div style="color:{MUTED};font-size:11px;margin-top:2px">{cfg["university"]} &middot; {cfg["campus"]} &middot; {datetime.now().strftime("%A, %d %B %Y")}</div>', unsafe_allow_html=True)
with hc2:
    if st.button("✨ AI Analysis"):
        st.session_state["insights"] = ""
st.markdown(f'<div style="border-bottom:1px solid #163557;margin:10px 0 16px"></div>', unsafe_allow_html=True)

# ============================================================
# VIEW: SETUP & DATA
# ============================================================
if nav == "⚙️  Setup & Data":
    tab_cfg, tab_upload, tab_sample = st.tabs(["🏫  University Config", "📁  Upload CSV Data", "📄  Sample CSV & Format"])

    # ── TAB 1: CONFIG ──────────────────────────────────────
    with tab_cfg:
        st.markdown('<div class="nabdcard">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-weight:700;font-size:14px;margin-bottom:14px">University / Customer Settings</div>', unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        with c1:
            uni   = st.text_input("University Name",  value=cfg["university"])
            campus= st.text_input("Campus Name",       value=cfg["campus"])
            contact=st.text_input("Contact Email",     value=cfg["contact"])
        with c2:
            tariff_val = st.number_input("Water Tariff (per m³)", value=cfg["tariff"], step=0.01, min_value=0.01)
            curr = st.selectbox("Currency", ["AED","USD","EUR","GBP","SAR","QAR","KWD"],
                                index=["AED","USD","EUR","GBP","SAR","QAR","KWD"].index(cfg["currency"]))
            logo_url = st.text_input("Logo URL (optional)", value=cfg["logo_url"])
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("💾 Save Configuration", type="primary"):
            st.session_state["config"].update({
                "university": uni, "campus": campus, "contact": contact,
                "tariff": tariff_val, "currency": curr, "logo_url": logo_url,
            })
            st.success(f"✅ Configuration saved for **{uni}**!")
            st.rerun()

        # Current config preview
        st.markdown('<div class="nabdcard" style="margin-top:12px">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-weight:700;font-size:13px;margin-bottom:10px">Current Configuration</div>', unsafe_allow_html=True)
        p1,p2,p3,p4 = st.columns(4)
        p1.metric("University",   cfg["university"])
        p2.metric("Campus",       cfg["campus"])
        p3.metric("Tariff",       f'{cfg["tariff"]} {cfg["currency"]}/m³')
        p4.metric("Contact",      cfg["contact"] or "Not set")
        st.markdown("</div>", unsafe_allow_html=True)

    # ── TAB 2: UPLOAD CSV ─────────────────────────────────
    with tab_upload:
        st.markdown('<div class="nabdcard">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-weight:700;font-size:14px;margin-bottom:4px">Upload Meter Data CSV</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="color:{MUTED};font-size:11px;margin-bottom:14px">Required columns: <code>zone</code>, <code>timestamp</code>, <code>consumption_m3</code>, <code>baseline_m3</code></div>', unsafe_allow_html=True)

        uploaded = st.file_uploader("Choose CSV file", type=["csv"], label_visibility="collapsed")

        if uploaded:
            try:
                raw = pd.read_csv(uploaded)
                st.markdown(f'<div style="color:{GREEN};font-size:12px;margin-bottom:8px">&#10003; File loaded: {len(raw)} rows, {raw["zone"].nunique() if "zone" in raw.columns else "?"} zones detected</div>', unsafe_allow_html=True)

                # Preview
                st.markdown(f'<div style="font-weight:600;font-size:12px;margin:10px 0 6px">Data Preview (first 10 rows)</div>', unsafe_allow_html=True)
                st.dataframe(raw.head(10), use_container_width=True)

                # Column check
                required = {"zone","timestamp","consumption_m3","baseline_m3"}
                present  = set(raw.columns.str.strip().str.lower().str.replace(" ","_"))
                missing  = required - present
                if missing:
                    st.error(f"Missing columns: {', '.join(missing)}")
                else:
                    st.markdown("</div>", unsafe_allow_html=True)
                    if st.button("⚡ Process & Apply Data", type="primary"):
                        with st.spinner("Processing CSV · Computing zones · Detecting anomalies..."):
                            zones_out, hourly_out, weekly_out, alerts_out = process_csv(raw)
                            st.session_state["raw_df"]      = raw
                            st.session_state["zones_data"]  = zones_out
                            st.session_state["hourly_data"] = hourly_out
                            st.session_state["weekly_data"] = weekly_out
                            st.session_state["alerts_data"] = alerts_out
                        st.success(f"✅ Data applied! {len(zones_out)} zones · {len(alerts_out)} alerts detected")
                        st.rerun()
                    st.markdown('<div class="nabdcard" style="margin-top:0">', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error reading CSV: {e}")
        else:
            st.markdown(f'<div style="text-align:center;padding:30px;color:{MUTED}">&#8679; Drop your CSV file here or click to browse</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Clear data button
        if using_real_data():
            st.markdown("")
            if st.button("🗑️ Clear Uploaded Data (revert to demo)"):
                for k in ["raw_df","zones_data","hourly_data","weekly_data","alerts_data"]:
                    st.session_state[k] = None
                st.rerun()

    # ── TAB 3: SAMPLE CSV ─────────────────────────────────
    with tab_sample:
        st.markdown('<div class="nabdcard">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-weight:700;font-size:14px;margin-bottom:10px">CSV Format Guide</div>', unsafe_allow_html=True)
        st.markdown(f"""
| Column | Type | Required | Description |
|---|---|---|---|
| `zone` | text | ✅ | Zone / building name |
| `timestamp` | datetime | ✅ | Format: `YYYY-MM-DD HH:MM` |
| `consumption_m3` | number | ✅ | Actual water usage in m³ |
| `baseline_m3` | number | ✅ | Expected / historical baseline in m³ |
        """)
        st.markdown(f'<div style="color:{MUTED};font-size:11px;margin-top:8px">One row per zone per hour. NabdFlow auto-detects anomalies, computes efficiency scores, and generates alerts from this data.</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        sample_df = make_sample_csv()
        csv_bytes  = sample_df.to_csv(index=False).encode()
        st.download_button(
            label="⬇️ Download Sample CSV (6 zones · 24 hours)",
            data=csv_bytes,
            file_name="nabdflow_sample_data.csv",
            mime="text/csv",
        )
        st.markdown('<div class="nabdcard" style="margin-top:12px">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-weight:600;font-size:12px;margin-bottom:8px">Sample data preview</div>', unsafe_allow_html=True)
        st.dataframe(sample_df.head(12), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# VIEW: OVERVIEW DASHBOARD
# ============================================================
elif nav == "📊  Overview Dashboard":
    zones   = get_zones()
    hourly  = get_hourly_df()
    weekly  = get_weekly_df()
    alerts  = get_alerts()
    total_c = sum(z["current"] for z in zones)
    total_b = sum(z["baseline"] for z in zones)
    saved   = max(0, total_b - total_c)
    aed_s   = round(saved * tariff())
    n_alert = len([a for a in alerts if a["sev"] not in ["resolved","low"]])

    k1,k2,k3,k4,k5 = st.columns(5)
    k1.metric(f"💧 Consumption", f"{total_c:,} m³", f"vs {total_b:,} baseline")
    k2.metric("⚡ Live Flow",   f"{random.randint(843,856)} L/min", "All zones")
    k3.metric(f"💰 {currency()} Saved", f"{aed_s:,} {currency()}", "+vs projected")
    k4.metric("🚨 Alerts",      str(n_alert), f"{len(zones)} zones monitored")
    k5.metric("📈 Efficiency",  f"{int(min(100,total_b/max(total_c,1)*100))}/100", "Campus-wide")

    st.markdown("")

    # Hourly chart
    fig_h = go.Figure()
    fig_h.add_trace(go.Scatter(x=hourly["Hour"],y=hourly["Baseline"], name="Baseline",  line=dict(color=MUTED,dash="dot",width=1.5)))
    fig_h.add_trace(go.Scatter(x=hourly["Hour"],y=hourly["Predicted"],name="Predicted", line=dict(color=PURPLE,width=1.5), fill="tozeroy",fillcolor="rgba(167,139,250,0.05)"))
    fig_h.add_trace(go.Scatter(x=hourly["Hour"],y=hourly["Actual"],   name="Actual",    line=dict(color=ACCENT,width=2.5), fill="tozeroy",fillcolor="rgba(0,200,255,0.08)"))
    fig_h.update_layout(**BASE_LAYOUT, height=230, legend=L_TOP)
    st.markdown('<div class="nabdcard">', unsafe_allow_html=True)
    st.markdown(f'<div style="font-weight:700;font-size:13px">Hourly Water Consumption &mdash; All Zones</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="color:{MUTED};font-size:11px;margin-bottom:6px">Actual vs Predicted vs Baseline &middot; m&sup3;/hr</div>', unsafe_allow_html=True)
    st.plotly_chart(fig_h, use_container_width=True, config={"displayModeBar":False})
    st.markdown("</div>", unsafe_allow_html=True)

    left, right = st.columns([2,1])
    with left:
        st.markdown('<div class="nabdcard">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-weight:700;font-size:13px;margin-bottom:12px">Zone Status Overview</div>', unsafe_allow_html=True)
        for z in zones:
            ec = eff_color(z["eff"])
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:10px;padding:7px 9px;margin-bottom:6px;'
                f'border-radius:8px;background:rgba(255,255,255,0.02);border:1px solid #163557">'
                f'<span style="font-size:16px">{z["icon"]}</span>'
                f'<div style="flex:1;min-width:0"><div style="font-size:12px;font-weight:600;color:#d8eeff;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{z["name"]}</div>'
                f'<div style="font-size:10px;color:{MUTED}">{z["current"]} m&sup3;/hr &middot; {z["eff"]}% eff</div></div>'
                f'<div style="width:70px"><div style="height:5px;background:rgba(255,255,255,0.07);border-radius:3px">'
                f'<div style="width:{z["eff"]}%;height:100%;background:{ec};border-radius:3px"></div></div></div>'
                f'{status_badge(z["status"])}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        fig_w = go.Figure()
        fig_w.add_trace(go.Bar(x=weekly["Day"],y=weekly["Usage"],name="Usage m3", marker_color=ACCENT,marker_opacity=0.65,marker_line_width=0))
        fig_w.add_trace(go.Bar(x=weekly["Day"],y=weekly["Saved"],name="Saved m3", marker_color=GREEN, marker_opacity=0.85,marker_line_width=0))
        fig_w.update_layout(**BASE_LAYOUT,barmode="group",height=200,legend=L_DEFAULT)
        st.markdown('<div class="nabdcard">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-weight:700;font-size:13px;margin-bottom:4px">Weekly Usage vs Savings</div>', unsafe_allow_html=True)
        st.plotly_chart(fig_w, use_container_width=True, config={"displayModeBar":False})
        st.markdown("</div>", unsafe_allow_html=True)

        zcolors = [RED if z["status"]=="leak" else YELLOW if z["status"] in ["anomaly","alert"] else ACCENT for z in zones]
        fig_p = go.Figure(go.Pie(labels=[z["short"] for z in zones],values=[z["current"] for z in zones],
            hole=0.5,marker=dict(colors=zcolors,line=dict(color="#050d1c",width=2))))
        fig_p.update_layout(**BASE_LAYOUT,height=190,showlegend=True,legend=L_BOTTOM)
        st.markdown('<div class="nabdcard">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-weight:700;font-size:13px;margin-bottom:4px">Consumption by Zone</div>', unsafe_allow_html=True)
        st.plotly_chart(fig_p, use_container_width=True, config={"displayModeBar":False})
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# VIEW: ZONE INTELLIGENCE
# ============================================================
elif nav == "🗺️  Zone Intelligence":
    zones = get_zones()
    cols_z = st.columns(2)
    for i,z in enumerate(zones):
        delta = z["current"]-z["baseline"]
        dp    = delta/max(z["baseline"],1)*100
        ec    = eff_color(z["eff"])
        bdr   = RED if z["status"]=="leak" else (YELLOW if z["status"] in ["anomaly","alert"] else "#163557")
        with cols_z[i%2]:
            st.markdown(
                f'<div style="background:#0d1e38;border:1.5px solid {bdr};border-radius:12px;padding:18px;margin-bottom:12px">'
                f'<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px">'
                f'<div style="display:flex;align-items:center;gap:10px">'
                f'<span style="font-size:24px">{z["icon"]}</span>'
                f'<div><div style="font-weight:700;font-size:13px;color:#d8eeff">{z["name"]}</div>'
                f'<div style="color:{MUTED};font-size:10px;margin-top:2px">Zone ID: {z["short"]}</div></div>'
                f'</div>{status_badge(z["status"])}</div>'
                f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px">'
                f'<div style="background:rgba(255,255,255,0.03);border-radius:8px;padding:9px 11px">'
                f'<div style="color:{MUTED};font-size:9px;text-transform:uppercase">Current</div>'
                f'<div style="color:#d8eeff;font-weight:800;font-size:20px">{z["current"]}<span style="font-size:10px;color:{MUTED}"> m&sup3;/hr</span></div></div>'
                f'<div style="background:rgba(255,255,255,0.03);border-radius:8px;padding:9px 11px">'
                f'<div style="color:{MUTED};font-size:9px;text-transform:uppercase">vs Baseline</div>'
                f'<div style="color:{"#ff5272" if delta>0 else "#00e5a0"};font-weight:800;font-size:20px">'
                f'{("+" if delta>0 else "")}{dp:.1f}<span style="font-size:10px">%</span></div></div></div>'
                f'<div style="display:flex;justify-content:space-between;margin-bottom:5px">'
                f'<span style="color:{MUTED};font-size:10px">Efficiency Score</span>'
                f'<span style="font-size:11px;font-weight:700;color:{ec}">{z["eff"]}%</span></div>'
                f'<div style="height:6px;background:rgba(255,255,255,0.06);border-radius:3px">'
                f'<div style="width:{z["eff"]}%;height:100%;background:{ec};border-radius:3px"></div>'
                f'</div></div>', unsafe_allow_html=True)

# ============================================================
# VIEW: ANOMALY & ALERTS
# ============================================================
elif nav == "🚨  Anomaly & Alerts":
    alerts = get_alerts()
    active = [a for a in alerts if a["sev"] not in ["resolved"]]
    a1,a2,a3,a4 = st.columns(4)
    a1.metric("Total Alerts",  str(len(alerts)))
    a2.metric("Critical 🔴",   str(len([a for a in alerts if a["sev"]=="critical"])))
    a3.metric("High 🟡",       str(len([a for a in alerts if a["sev"]=="high"])))
    a4.metric("Active",        str(len(active)))
    st.markdown("")
    for a in alerts:
        render_alert(a)

# ============================================================
# VIEW: AI INSIGHTS ENGINE
# ============================================================
elif nav == "🤖  AI Insights Engine":
    st.markdown(
        f'<div class="nabdcard"><div style="font-weight:700;font-size:14px">🤖 AI Water Intelligence Analysis</div>'
        f'<div style="color:{MUTED};font-size:11px;margin-top:3px">Powered by Groq AI (llama-3.3-70b) &middot; {"Real data" if using_real_data() else "Demo data"} &middot; {len(get_zones())} zones</div>'
        f'</div>', unsafe_allow_html=True)

    if st.button("✨ Generate AI Insights", type="primary"):
        st.session_state["insights"] = ""
        with st.spinner("Analyzing zones · Detecting patterns · Generating insights..."):
            prompt = ("Analyze this campus water data and provide:\n\n"
                      "## Key Findings\n3 critical observations with specific figures.\n\n"
                      "## Priority Actions Required\nRanked by urgency with estimated resolution time.\n\n"
                      "## 24-Hour Demand Forecast\nExpected peaks and risk windows.\n\n"
                      "## Quick-Win Optimizations\n3 specific actions each with estimated savings.\n\n"
                      "## Efficiency Score Breakdown\nWhat drives the current score and how to improve it.")
            st.session_state["insights"] = call_ai([{"role":"user","content":prompt}])

    if st.session_state["insights"]:
        st.markdown('<div style="background:rgba(0,0,0,0.2);border:1px solid #163557;border-radius:10px;padding:20px">', unsafe_allow_html=True)
        st.markdown(st.session_state["insights"])
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="text-align:center;padding:60px 20px;color:{MUTED}"><div style="font-size:52px;margin-bottom:14px">&#129504;</div><div style="font-size:15px;margin-bottom:8px;color:#d8eeff">AI Analysis Engine Ready</div><div style="font-size:12px">Click "Generate AI Insights" to analyze your campus water data.</div></div>', unsafe_allow_html=True)

# ============================================================
# VIEW: SUSTAINABILITY HUB
# ============================================================
elif nav == "🌿  Sustainability Hub":
    weekly = get_weekly_df()
    total_saved = int(weekly["Saved"].sum()) if "Saved" in weekly.columns else 21630
    total_aed   = int(weekly["AED"].sum())   if "AED"   in weekly.columns else 7787
    carbon      = round(total_saved * 0.001, 1)

    s1,s2,s3,s4,s5 = st.columns(5)
    s1.metric(f"💧 Water Saved/Week",  f"{total_saved:,} m³",  "vs baseline")
    s2.metric("🌿 Carbon Offset",      f"{carbon} t CO2",       "~equivalent trees")
    s3.metric(f"💰 {currency()} Saved/Week", f"{total_aed:,} {currency()}", "vs projected")
    s4.metric("🏆 SDG 6 Score",        "B+",                    "Clean Water")
    s5.metric("🌍 Sustainability",      "78 / 100",              "Target: 90+")

    st.markdown("")
    ca,cb = st.columns(2)
    with ca:
        fig_aed = go.Figure(go.Bar(x=weekly["Day"],y=weekly["AED"],marker_color=YELLOW,marker_opacity=0.85,marker_line_width=0))
        fig_aed.update_layout(**BASE_LAYOUT,height=230,legend=L_DEFAULT)
        st.markdown('<div class="nabdcard">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-weight:700;font-size:13px;margin-bottom:4px">{currency()} Savings per Day This Week</div>', unsafe_allow_html=True)
        st.plotly_chart(fig_aed, use_container_width=True, config={"displayModeBar":False})
        st.markdown("</div>", unsafe_allow_html=True)
    with cb:
        st.markdown('<div class="nabdcard">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-weight:700;font-size:13px;margin-bottom:14px">Sustainability Impact Metrics</div>', unsafe_allow_html=True)
        for label,val,color in [("UN SDG 6 - Clean Water",78,ACCENT),("UN SDG 13 - Climate Action",72,GREEN),
                                  ("Water Reuse Rate",34,PURPLE),("Leak Response Rate",91,YELLOW),("Campus Coverage",100,GREEN)]:
            st.markdown(
                f'<div style="margin-bottom:10px">'
                f'<div style="display:flex;justify-content:space-between;margin-bottom:4px">'
                f'<span style="font-size:11px;color:{MUTED}">{label}</span>'
                f'<span style="font-size:11px;font-weight:700;color:{color}">{val}%</span></div>'
                f'<div style="height:5px;background:rgba(255,255,255,0.06);border-radius:3px">'
                f'<div style="width:{val}%;height:100%;background:{color};border-radius:3px"></div>'
                f'</div></div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("")
    st.markdown(f'<div class="nabdcard"><div style="font-weight:700;font-size:14px">📋 Weekly Sustainability Intelligence Report</div><div style="color:{MUTED};font-size:11px;margin-top:3px">AI-generated for Facilities Management &amp; Sustainability Committee</div></div>', unsafe_allow_html=True)
    if st.button("📄 Generate Sustainability Report", type="primary"):
        st.session_state["report"] = ""
        with st.spinner("Compiling data · Calculating impact · Drafting report..."):
            prompt = (f"Generate a formal Weekly Water Sustainability Intelligence Report for {cfg['university']} - {cfg['campus']}.\n\n"
                      f"Key figures: Water saved: {total_saved:,} m3, {currency()} saved: {total_aed:,}, Carbon offset: {carbon} tonnes CO2\n\n"
                      "Sections:\n1. Executive Summary\n2. Weekly Consumption Overview\n3. Anomaly & Leak Detection Summary\n"
                      "4. AI Predictive Outlook for Next 7 Days\n5. Sustainability Impact (carbon, SDG 6)\n"
                      f"6. Financial Impact (projected annual {currency()} savings)\n7. Recommended Actions\n8. Conclusion\n\nUse formal report language.")
            st.session_state["report"] = call_ai([{"role":"user","content":prompt}])
    if st.session_state["report"]:
        st.markdown('<div style="background:rgba(0,0,0,0.2);border:1px solid #163557;border-radius:10px;padding:20px">', unsafe_allow_html=True)
        st.markdown(st.session_state["report"])
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# VIEW: AI CHAT ASSISTANT
# ============================================================
elif nav == "💬  AI Chat Assistant":
    st.markdown(f'<div class="nabdcard"><div style="font-weight:700;font-size:14px">💬 NabdFlow AI Chat</div><div style="color:{MUTED};font-size:11px;margin-top:3px">Ask about leaks, anomalies, savings, predictions, zones, or sustainability metrics</div></div>', unsafe_allow_html=True)
    qc = st.columns(4)
    for i,q in enumerate(["What zones have anomalies?","How much water can I save?","Explain the biggest leak","Predict tomorrow's demand"]):
        if qc[i].button(q, key=f"qp_{i}"):
            st.session_state["chat"].append({"role":"user","content":q})
            with st.spinner("Thinking..."):
                history = [{"role":m["role"],"content":m["content"]} for m in st.session_state["chat"]]
                st.session_state["chat"].append({"role":"assistant","content":call_ai(history)})
            st.rerun()
    st.markdown("")
    for m in st.session_state["chat"]:
        with st.chat_message(m["role"], avatar="🤖" if m["role"]=="assistant" else "👤"):
            st.markdown(m["content"])
    if user_input := st.chat_input("Ask about campus water systems..."):
        st.session_state["chat"].append({"role":"user","content":user_input})
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                history = [{"role":m["role"],"content":m["content"]} for m in st.session_state["chat"]]
                reply = call_ai(history)
            st.markdown(reply)
        st.session_state["chat"].append({"role":"assistant","content":reply})
        st.rerun()
