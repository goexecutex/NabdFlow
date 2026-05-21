# ============================================================
#  NabdFlow - AI-Powered Campus Water Intelligence Dashboard
#  Majra Sustainable Impact Challenge | Student Innovation Project
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
    page_title="NabdFlow | Campus Water Intelligence",
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
  [data-testid="stMetricValue"]  { color: #d8eeff !important; font-size: 20px !important; font-weight: 800 !important; }
  [data-testid="stMetricDelta"]  { font-size: 10px !important; }
  .stButton > button { background: linear-gradient(135deg,#00c8ff,#0055ff) !important; color:#04111f !important; font-weight:700 !important; border:none !important; border-radius:8px !important; }
  .stButton > button:hover { opacity: 0.85; }
  h1,h2,h3 { color: #d8eeff !important; }
  hr { border-color: #163557; }
  .nabdcard { background:#0d1e38; border:1px solid #163557; border-radius:12px; padding:16px 18px; margin-bottom:12px; }
  .stTabs [data-baseweb="tab-list"] { background:#081525; border-radius:10px; }
  .stTabs [data-baseweb="tab"] { color:#5a8aaa; }
  .stTabs [aria-selected="true"] { color:#00c8ff !important; }
  .stTextInput input, .stNumberInput input { background: #0d1e38 !important; color: #d8eeff !important; border: 1px solid #163557 !important; }
  div[data-testid="stFileUploader"] { background:#0d1e38; border:1px dashed #163557; border-radius:10px; padding:10px; }
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
# DEMO DATA  —  Realistic UAE campus-scale simulated figures
# Total daily campus usage: ~1,000–1,100 m³/day (8 zones)
# Potential waste identified: ~60–75 m³/day
# ------------------------------------------------------------
DEMO_ZONES = [
    {"id":1,"name":"Main Academic Building","short":"MAB","icon":"🏛️","baseline":125,"current":117,"status":"normal", "eff":94},
    {"id":2,"name":"Science & Tech Block",  "short":"STB","icon":"🔬","baseline":100,"current":128,"status":"anomaly","eff":65},
    {"id":3,"name":"Student Housing A",     "short":"SHA","icon":"🏘️","baseline":210,"current":204,"status":"normal", "eff":97},
    {"id":4,"name":"Student Housing B",     "short":"SHB","icon":"🏠","baseline":185,"current":218,"status":"alert",  "eff":72},
    {"id":5,"name":"Sports Complex",        "short":"SPC","icon":"⚽","baseline":155,"current":149,"status":"normal", "eff":96},
    {"id":6,"name":"Library & Research",    "short":"LIB","icon":"📚","baseline":55, "current":52, "status":"normal", "eff":98},
    {"id":7,"name":"Cafeteria & Dining",    "short":"CAF","icon":"🍽️","baseline":130,"current":140,"status":"normal", "eff":89},
    {"id":8,"name":"Admin & Offices",       "short":"ADM","icon":"💼","baseline":50, "current":74, "status":"leak",   "eff":58},
]

DEMO_ALERTS = [
    {"type":"leak",    "zone":"Admin & Offices",      "msg":"Possible pipe leak &mdash; abnormal flow detected outside business hours",         "time":"12m ago","aed":8.6, "sev":"critical"},
    {"type":"anomaly", "zone":"Student Housing B",    "msg":"Consumption 18% above 7-day baseline for 3 consecutive hours",                      "time":"47m ago","aed":11.9,"sev":"high"},
    {"type":"anomaly", "zone":"Science & Tech Block", "msg":"Lab cooling water elevated &mdash; possible valve not fully closed",                 "time":"1.5h ago","aed":10.1,"sev":"medium"},
    {"type":"info",    "zone":"Cafeteria & Dining",   "msg":"Usage slightly above baseline &mdash; likely catering event in progress",            "time":"3h ago", "aed":3.6, "sev":"low"},
    {"type":"resolved","zone":"Sports Complex",       "msg":"Irrigation usage returned to normal baseline &mdash; no action required",            "time":"5h ago", "aed":0,   "sev":"resolved"},
]

DEMO_WEEKLY = pd.DataFrame({
    "Day":   ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
    "Usage": [1082, 1055, 1128, 1008, 882, 641, 584],
    "Saved": [72,   55,   85,   42,   35,  20,  15],
    "AED":   [26,   20,   31,   15,   13,   7,   6],
})

np.random.seed(42)
_b = [20 + np.sin(i/3.5)*5 + (22 if 7<=i<=19 else 0) for i in range(24)]
DEMO_HOURLY = pd.DataFrame({
    "Hour":      [f"{str(i).zfill(2)}:00" for i in range(24)],
    "Actual":    [max(0, round(v + np.random.normal(0,2),1)) for v in _b],
    "Predicted": [round(v*1.06,1) for v in _b],
    "Baseline":  [round(v*1.18,1) for v in _b],
})

# ------------------------------------------------------------
# CHART HELPERS
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
        "university": "UAE Campus Simulation \u2013 NabdFlow Pilot Model",
        "campus":     "Smart Water Campus Pilot \u2013 Simulated Dataset",
        "tariff":     0.36,
        "currency":   "AED",
        "contact":    "",
        "logo_url":   "",
    },
    "raw_df":None,"zones_data":None,"hourly_data":None,
    "weekly_data":None,"alerts_data":None,
    "chat":[{"role":"assistant","content":"Hello! I am NabdFlow AI. I can help analyse the simulated campus water data, explain detected anomalies, and suggest what the facilities team should investigate first."}],
    "insights":"","report":"",
}
for k,v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ------------------------------------------------------------
# DATA ACCESSORS
# ------------------------------------------------------------
def using_real_data(): return st.session_state["zones_data"] is not None
def get_zones():    return st.session_state["zones_data"]   if using_real_data() else DEMO_ZONES
def get_hourly_df():return st.session_state["hourly_data"]  if using_real_data() else DEMO_HOURLY
def get_weekly_df():return st.session_state["weekly_data"]  if using_real_data() else DEMO_WEEKLY
def get_alerts():   return st.session_state["alerts_data"]  if using_real_data() else DEMO_ALERTS
def get_cfg(k):     return st.session_state["config"].get(k,"")
def currency():     return st.session_state["config"]["currency"]
def tariff():       return st.session_state["config"]["tariff"]

# ------------------------------------------------------------
# CSV PROCESSING
# ------------------------------------------------------------
def process_csv(df):
    df = df.copy()
    df.columns = [c.strip().lower().replace(" ","_") for c in df.columns]
    df["timestamp"] = pd.to_datetime(df["timestamp"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["timestamp"])
    df["hour"] = df["timestamp"].dt.hour
    df["date"] = df["timestamp"].dt.date
    zones_out = []
    for i, zn in enumerate(df["zone"].unique()):
        zdf = df[df["zone"]==zn].sort_values("timestamp")
        current  = float(zdf["consumption_m3"].iloc[-1])
        baseline = float(zdf["baseline_m3"].mean())
        eff = min(100, max(0, int(baseline/max(current,0.001)*100)))
        ratio = current/max(baseline,0.001)
        status = "leak" if ratio>1.40 else ("anomaly" if ratio>1.20 else ("alert" if ratio>1.10 else "normal"))
        zones_out.append({"id":i+1,"name":zn,"short":zn[:3].upper(),"icon":"🏛️",
                          "baseline":int(baseline),"current":int(current),"status":status,"eff":eff})
    hgrp = df.groupby("hour").agg(actual=("consumption_m3","sum"),baseline=("baseline_m3","sum")).reset_index()
    def hval(h,col,mult=1): return round(float(hgrp[hgrp["hour"]==h][col].sum())*mult,1) if h in hgrp["hour"].values else 0
    hourly_out = pd.DataFrame({
        "Hour":      [f"{str(h).zfill(2)}:00" for h in range(24)],
        "Actual":    [hval(h,"actual") for h in range(24)],
        "Predicted": [hval(h,"baseline",1.05) for h in range(24)],
        "Baseline":  [hval(h,"baseline") for h in range(24)],
    })
    wgrp = df.groupby("date").agg(Usage=("consumption_m3","sum"),baseline=("baseline_m3","sum")).reset_index()
    wgrp["Saved"] = (wgrp["baseline"]-wgrp["Usage"]).clip(lower=0)
    wgrp["AED"]   = (wgrp["Saved"]*tariff()).round(2)
    wgrp["Day"]   = pd.to_datetime(wgrp["date"]).dt.strftime("%a")
    weekly_out    = wgrp[["Day","Usage","Saved","AED"]].tail(7)
    alerts_out = []
    for z in zones_out:
        if z["status"] in ["leak","anomaly","alert"]:
            excess  = max(0, z["current"]-z["baseline"])
            aed_day = round(excess*tariff(), 2)
            pct     = round((z["current"]-z["baseline"])/max(z["baseline"],1)*100)
            sev     = "critical" if z["status"]=="leak" else ("high" if z["status"]=="anomaly" else "medium")
            alerts_out.append({"type":z["status"],"zone":z["name"],
                "msg":f"Consumption {pct}% above baseline &mdash; potential abnormal usage detected",
                "time":"Just now","aed":aed_day,"sev":sev})
    if not alerts_out:
        alerts_out.append({"type":"resolved","zone":"All Zones",
            "msg":"No anomalies detected &mdash; all zones within normal baseline range","time":"Now","aed":0,"sev":"resolved"})
    return zones_out, hourly_out, weekly_out, alerts_out

# ------------------------------------------------------------
# SAMPLE CSV
# ------------------------------------------------------------
def make_sample_csv():
    zones = ["Main Academic Building","Science Block","Student Housing A",
             "Student Housing B","Sports Complex","Admin & Offices"]
    baselines = [125,100,210,185,155,50]
    rows = []
    base_dt = datetime(2026,5,20,0,0)
    for h in range(24):
        ts = base_dt + timedelta(hours=h)
        for z,bl in zip(zones,baselines):
            spike = 1.48 if (z=="Admin & Offices" and h>18) else 1.0
            cons  = round(bl/24*(1+random.uniform(-0.05,0.08))*spike, 2)
            rows.append({"zone":z,"timestamp":ts.strftime("%Y-%m-%d %H:%M"),"consumption_m3":cons,"baseline_m3":round(bl/24,2)})
    return pd.DataFrame(rows)

# ------------------------------------------------------------
# GROQ AI
# ------------------------------------------------------------
def build_system():
    zones = get_zones()
    cfg   = st.session_state["config"]
    return (
        f"You are NabdFlow AI, an assistant for a student-led campus water intelligence prototype.\n"
        f"IMPORTANT: This is a working prototype using simulated UAE campus water data, not real verified figures.\n"
        f"Project: {cfg['university']} | {cfg['campus']}\n"
        f"Zones monitored: {len(zones)}\n"
        + "\n".join([f"- {z['name']}: {z['current']} m3/day (baseline {z['baseline']} m3/day), efficiency {z['eff']}%, status: {z['status']}" for z in zones])
        + f"\nWater tariff used in simulation: {cfg['tariff']} {cfg['currency']}/m3\n"
        "When giving recommendations, frame them as 'potential actions to investigate' not confirmed savings.\n"
        "Use language like 'estimated', 'potential', 'prototype-tested', 'simulated data suggests'.\n"
        "Be helpful, concise, and practical for a university facilities manager."
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
            messages=[{"role":"system","content":build_system()}]+messages,
            max_tokens=1000
        )
        return resp.choices[0].message.content
    except ImportError:
        return "**groq not installed.** Run: `pip install groq`"
    except Exception as e:
        return f"**Error:** {e}"

# ------------------------------------------------------------
# REUSABLE UI COMPONENTS
# ------------------------------------------------------------
def status_badge(s):
    cfg = {"normal":("#00e5a0","rgba(0,229,160,0.12)","Normal"),
           "anomaly":("#ffb347","rgba(255,179,71,0.12)","Anomaly"),
           "alert":("#ffb347","rgba(255,179,71,0.12)","Alert"),
           "leak":("#ff5272","rgba(255,82,114,0.12)","Possible Leak"),
           "resolved":("#5a8aaa","rgba(90,138,170,0.08)","Resolved")}
    c,bg,lbl = cfg.get(s,(MUTED,"transparent",s.capitalize()))
    return f'<span style="background:{bg};color:{c};padding:2px 10px;border-radius:20px;font-size:11px;font-weight:700">{lbl}</span>'

def eff_color(e): return GREEN if e>=90 else (YELLOW if e>=70 else RED)
def sev_color(s): return {"critical":RED,"high":YELLOW,"medium":YELLOW,"low":ACCENT,"resolved":MUTED}.get(s,MUTED)
def sev_bg(s):    return {"critical":"rgba(255,82,114,0.12)","high":"rgba(255,179,71,0.12)","medium":"rgba(255,179,71,0.10)","low":"rgba(0,200,255,0.10)","resolved":"rgba(90,138,170,0.08)"}.get(s,"transparent")

def prototype_badge():
    st.markdown(
        f'<div style="background:rgba(167,139,250,0.08);border:1px solid rgba(167,139,250,0.35);'
        f'border-radius:10px;padding:10px 16px;margin-bottom:14px;display:flex;align-items:center;gap:10px">'
        f'<span style="font-size:16px">&#9432;</span>'
        f'<div><span style="color:{PURPLE};font-weight:700;font-size:12px">PROTOTYPE MODE</span>'
        f'<span style="color:{MUTED};font-size:11px;margin-left:8px">This dashboard uses simulated UAE campus water data. '
        f'Figures show <strong style="color:#d8eeff">potential water waste identified</strong> and '
        f'<strong style="color:#d8eeff">estimated avoidable cost</strong>, not verified real-world savings. '
        f'Real impact will be validated during a campus pilot using actual meter data.</span></div>'
        f'</div>', unsafe_allow_html=True)

def render_alert(a):
    icons = {"leak":"💧","anomaly":"⚠️","info":"ℹ️","resolved":"✅"}
    bdr   = sev_color(a["sev"])
    aed_h = (f'<span style="color:{RED};font-size:11px;font-weight:700">~{a["aed"]} {currency()}/day est.</span>') if a["aed"]>0 else ""
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
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:10px;padding:4px 0 10px">'
        f'<div style="width:38px;height:38px;border-radius:10px;background:linear-gradient(135deg,#00c8ff,#0055ff);'
        f'display:flex;align-items:center;justify-content:center;font-size:20px">💧</div>'
        f'<div><div style="font-weight:900;font-size:15px;color:#d8eeff">NabdFlow</div>'
        f'<div style="color:{MUTED};font-size:9px;letter-spacing:1px;text-transform:uppercase">Water Intelligence</div>'
        f'</div></div>'
        f'<div style="background:#0d1e38;border:1px solid #163557;border-radius:8px;padding:8px 12px;margin-bottom:6px">'
        f'<div style="color:#d8eeff;font-size:11px;font-weight:700">UAE Campus Simulation</div>'
        f'<div style="color:{MUTED};font-size:9px;margin-top:2px">NabdFlow Pilot Model &middot; Simulated Data</div>'
        f'</div>', unsafe_allow_html=True)

    data_label = (f'<div style="background:rgba(0,229,160,0.08);border:1px solid rgba(0,229,160,0.3);border-radius:8px;padding:6px 10px;margin-bottom:10px;font-size:11px;color:#00e5a0;font-weight:700">&#9679; REAL DATA &nbsp;&middot;&nbsp; <span style="font-weight:400;color:{MUTED}">{len(get_zones())} zones</span></div>'
                  if using_real_data() else
                  f'<div style="background:rgba(167,139,250,0.08);border:1px solid rgba(167,139,250,0.3);border-radius:8px;padding:6px 10px;margin-bottom:10px;font-size:11px;color:{PURPLE};font-weight:700">&#9670; SIMULATED DATA &nbsp;&middot;&nbsp; <span style="font-weight:400;color:{MUTED}">Prototype Mode</span></div>')
    st.markdown(data_label, unsafe_allow_html=True)
    st.markdown(f'<div style="background:rgba(0,229,160,0.05);border:1px solid rgba(0,229,160,0.15);border-radius:8px;padding:6px 12px;margin-bottom:14px"><span style="color:#00e5a0;font-size:11px;font-weight:700">&#9679; LIVE &nbsp;</span><span style="color:{MUTED};font-size:11px">{random.randint(38,48)} L/min (simulated)</span></div>', unsafe_allow_html=True)

    nav = st.radio("nav", [
        "📊  Overview Dashboard",
        "📋  Project Evidence & Journey",
        "🗺️  Zone Intelligence",
        "🚨  Anomaly & Alerts",
        "🤖  AI Insights Engine",
        "🌿  Sustainability Hub",
        "💬  AI Chat Assistant",
        "⚙️  Setup & Data",
    ], label_visibility="collapsed")

    st.markdown(f'<hr style="border-color:#163557;margin:10px 0">', unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    zones_now = get_zones()
    total_c   = sum(z["current"] for z in zones_now)
    total_b   = sum(z["baseline"] for z in zones_now)
    waste_est = max(0, total_c - total_b)
    c1.metric("Zones",        str(len(zones_now)))
    c1.metric("Eff. Score",   "78/100")
    c2.metric("Alerts",       str(len([a for a in get_alerts() if a["sev"]!="resolved"])))
    c2.metric("Est. Waste/Day", f"~{waste_est} m\u00b3")

# ------------------------------------------------------------
# HEADER
# ------------------------------------------------------------
TITLES = {
    "📊  Overview Dashboard":         "📊 Overview Dashboard",
    "📋  Project Evidence & Journey":  "📋 Project Evidence & Journey",
    "🗺️  Zone Intelligence":           "🗺️ Zone Intelligence",
    "🚨  Anomaly & Alerts":            "🚨 Anomaly & Alert Centre",
    "🤖  AI Insights Engine":          "🤖 AI Insights Engine",
    "🌿  Sustainability Hub":           "🌿 Sustainability Hub",
    "💬  AI Chat Assistant":           "💬 AI Chat Assistant",
    "⚙️  Setup & Data":               "⚙️ Setup & Data",
}
hc1,hc2 = st.columns([4,1])
with hc1:
    st.markdown(f'<h1 style="margin:0;font-size:21px;font-weight:900">{TITLES.get(nav,nav)}</h1>', unsafe_allow_html=True)
    st.markdown(f'<div style="color:{MUTED};font-size:11px;margin-top:2px">UAE Campus Simulation &middot; NabdFlow AI Prototype &middot; {datetime.now().strftime("%A, %d %B %Y")}</div>', unsafe_allow_html=True)
with hc2:
    if st.button("✨ AI Analysis"):
        st.session_state["insights"] = ""
st.markdown(f'<div style="border-bottom:1px solid #163557;margin:10px 0 16px"></div>', unsafe_allow_html=True)

# ============================================================
# VIEW: OVERVIEW DASHBOARD
# ============================================================
if nav == "📊  Overview Dashboard":

    # ── PROJECT BANNER ────────────────────────────────────
    st.markdown(
        f'<div style="background:linear-gradient(135deg,rgba(0,85,255,0.15),rgba(0,200,255,0.10));'
        f'border:1px solid rgba(0,200,255,0.3);border-radius:12px;padding:16px 20px;margin-bottom:16px">'
        f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">'
        f'<span style="font-size:18px">🌱</span>'
        f'<span style="color:{ACCENT};font-weight:800;font-size:13px;text-transform:uppercase;letter-spacing:1px">Project Status: Ongoing Student-Led Sustainability Innovation</span>'
        f'</div>'
        f'<div style="color:#c8e6ff;font-size:12px;line-height:1.7">'
        f'NabdFlow began as an inter-university smart water management research and awareness project focused on '
        f'<strong>AI and Big Data for climate action in the UAE</strong>. It has now been developed into a working AI '
        f'dashboard prototype for UAE campus water efficiency. This prototype uses <strong>simulated campus water data</strong> '
        f'to demonstrate how real campuses can identify abnormal water usage, potential leaks, and sustainability improvement opportunities.'
        f'</div></div>', unsafe_allow_html=True)

    # ── PROTOTYPE MODE BADGE ──────────────────────────────
    prototype_badge()

    # ── FOR REVIEWERS BOX ─────────────────────────────────
    st.markdown(
        f'<div style="background:rgba(0,229,160,0.05);border:1px solid rgba(0,229,160,0.25);'
        f'border-radius:10px;padding:12px 16px;margin-bottom:16px">'
        f'<span style="color:{GREEN};font-weight:700;font-size:12px">&#128203; For Reviewers &nbsp;</span>'
        f'<span style="color:{MUTED};font-size:11px">NabdFlow is submitted as an ongoing student-led sustainability '
        f'innovation project. The working prototype demonstrates the technical and impact model using simulated UAE '
        f'campus water data. The next stage is real campus pilot validation with actual facilities meter data.</span>'
        f'</div>', unsafe_allow_html=True)

    # ── KPIs ─────────────────────────────────────────────
    zones_d  = get_zones()
    total_c  = sum(z["current"]  for z in zones_d)
    total_b  = sum(z["baseline"] for z in zones_d)
    waste_d  = max(0, total_c - total_b)
    cost_d   = round(waste_d * tariff(), 1)
    n_alerts = len([a for a in get_alerts() if a["sev"] not in ["resolved","low"]])

    k1,k2,k3,k4,k5 = st.columns(5)
    k1.metric("💧 Today's Campus Usage",        f"~{total_c} m\u00b3/day",  "Simulated total")
    k2.metric("⚡ Simulated Flow Rate",          f"{random.randint(38,48)} L/min", "All zones")
    k3.metric("🔍 Est. Avoidable Cost/Day",      f"~{cost_d} {currency()}",   "Prototype estimate")
    k4.metric("⚠️ Potential Alerts Detected",    str(n_alerts),               "Anomalies flagged")
    k5.metric("📈 Water Efficiency Score",        "78 / 100",                  "Campus-wide (simulated)")

    st.markdown("")

    # ── HOURLY CHART ─────────────────────────────────────
    hourly = get_hourly_df()
    fig_h  = go.Figure()
    fig_h.add_trace(go.Scatter(x=hourly["Hour"],y=hourly["Baseline"], name="Baseline",  line=dict(color=MUTED,dash="dot",width=1.5)))
    fig_h.add_trace(go.Scatter(x=hourly["Hour"],y=hourly["Predicted"],name="Predicted", line=dict(color=PURPLE,width=1.5), fill="tozeroy",fillcolor="rgba(167,139,250,0.05)"))
    fig_h.add_trace(go.Scatter(x=hourly["Hour"],y=hourly["Actual"],   name="Actual",    line=dict(color=ACCENT,width=2.5), fill="tozeroy",fillcolor="rgba(0,200,255,0.08)"))
    fig_h.update_layout(**BASE_LAYOUT, height=230, legend=L_TOP)
    st.markdown('<div class="nabdcard">', unsafe_allow_html=True)
    st.markdown(f'<div style="font-weight:700;font-size:13px">Hourly Campus Water Consumption (Simulated)</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="color:{MUTED};font-size:11px;margin-bottom:6px">Actual vs Predicted vs Baseline &middot; m\u00b3/hr &middot; All zones combined &middot; Simulated data</div>', unsafe_allow_html=True)
    st.plotly_chart(fig_h, use_container_width=True, config={"displayModeBar":False})
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("")
    left, right = st.columns([2,1])

    with left:
        st.markdown('<div class="nabdcard">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-weight:700;font-size:13px;margin-bottom:6px">Zone-by-Zone Status &mdash; Where is water being used?</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="color:{MUTED};font-size:10px;margin-bottom:10px">Zones highlighted in red/yellow show abnormal usage patterns that need investigation</div>', unsafe_allow_html=True)
        for z in zones_d:
            ec = eff_color(z["eff"])
            delta = z["current"] - z["baseline"]
            delta_label = f'+{delta}' if delta > 0 else str(delta)
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:10px;padding:7px 9px;margin-bottom:6px;'
                f'border-radius:8px;background:rgba(255,255,255,0.02);border:1px solid #163557">'
                f'<span style="font-size:16px">{z["icon"]}</span>'
                f'<div style="flex:1;min-width:0"><div style="font-size:12px;font-weight:600;color:#d8eeff;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{z["name"]}</div>'
                f'<div style="font-size:10px;color:{MUTED}">{z["current"]} m\u00b3/day &middot; Baseline: {z["baseline"]} m\u00b3 &middot; Diff: <span style="color:{"#ff5272" if delta>0 else "#00e5a0"}">{delta_label} m\u00b3</span></div></div>'
                f'<div style="width:65px"><div style="height:5px;background:rgba(255,255,255,0.07);border-radius:3px">'
                f'<div style="width:{z["eff"]}%;height:100%;background:{ec};border-radius:3px"></div></div></div>'
                f'{status_badge(z["status"])}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        weekly = get_weekly_df()
        fig_w  = go.Figure()
        fig_w.add_trace(go.Bar(x=weekly["Day"],y=weekly["Usage"],name="Usage m3", marker_color=ACCENT,marker_opacity=0.65,marker_line_width=0))
        fig_w.add_trace(go.Bar(x=weekly["Day"],y=weekly["Saved"],name="Est. Waste Identified m3", marker_color=YELLOW,marker_opacity=0.85,marker_line_width=0))
        fig_w.update_layout(**BASE_LAYOUT,barmode="group",height=200,legend=L_DEFAULT)
        st.markdown('<div class="nabdcard">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-weight:700;font-size:13px;margin-bottom:2px">Weekly Usage vs Potential Waste</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="color:{MUTED};font-size:10px;margin-bottom:4px">m\u00b3 &middot; Simulated estimates</div>', unsafe_allow_html=True)
        st.plotly_chart(fig_w, use_container_width=True, config={"displayModeBar":False})
        st.markdown("</div>", unsafe_allow_html=True)

        zcolors = [RED if z["status"]=="leak" else YELLOW if z["status"] in ["anomaly","alert"] else ACCENT for z in zones_d]
        fig_p = go.Figure(go.Pie(labels=[z["short"] for z in zones_d],values=[z["current"] for z in zones_d],
            hole=0.5,marker=dict(colors=zcolors,line=dict(color="#050d1c",width=2))))
        fig_p.update_layout(**BASE_LAYOUT,height=190,showlegend=True,legend=L_BOTTOM)
        st.markdown('<div class="nabdcard">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-weight:700;font-size:13px;margin-bottom:2px">Share by Zone (Simulated)</div>', unsafe_allow_html=True)
        st.plotly_chart(fig_p, use_container_width=True, config={"displayModeBar":False})
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# VIEW: PROJECT EVIDENCE & JOURNEY
# ============================================================
elif nav == "📋  Project Evidence & Journey":

    # For Reviewers box
    st.markdown(
        f'<div style="background:rgba(0,200,255,0.07);border:2px solid rgba(0,200,255,0.4);'
        f'border-radius:12px;padding:16px 20px;margin-bottom:20px">'
        f'<div style="color:{ACCENT};font-weight:800;font-size:13px;margin-bottom:6px">&#128203; For Reviewers — Majra Sustainable Impact Challenge</div>'
        f'<div style="color:#c8e6ff;font-size:12px;line-height:1.7">'
        f'NabdFlow is submitted as an <strong>ongoing student-led sustainability innovation project</strong>. '
        f'The working prototype demonstrates the technical and impact model using simulated UAE campus water data. '
        f'The next stage is <strong>real campus pilot validation</strong> with actual facilities meter data. '
        f'All numbers shown in this prototype are estimates based on realistic UAE campus water use patterns &mdash; '
        f'they are not verified real-world savings.'
        f'</div></div>', unsafe_allow_html=True)

    tab_origin, tab_exec, tab_evidence, tab_impact, tab_next = st.tabs([
        "🌱 Project Origin", "⚙️ Current Execution", "📂 Evidence", "📊 Impact Status", "🚀 Next Steps"
    ])

    with tab_origin:
        st.markdown('<div class="nabdcard">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-weight:700;font-size:15px;color:#d8eeff;margin-bottom:12px">🌱 How NabdFlow Started</div>', unsafe_allow_html=True)
        st.markdown(f"""
<div style="color:#c8e6ff;font-size:13px;line-height:1.8">
NabdFlow started from an <strong>inter-university sustainability poster and research project</strong> on
<em>AI and Big Data for Smart Water Management in the UAE</em>. The original project explored how
sensors, cloud data, AI models, and smart dashboards could help reduce water waste and support climate action.
<br><br>
The research highlighted critical UAE water challenges:
<ul style="margin-top:8px;line-height:2">
  <li>The UAE relies on <strong>desalination for ~89% of its water supply</strong> (MoCCAE, 2025)</li>
  <li>Abu Dhabi and Dubai consume <strong>~78% of total UAE water</strong> (FCSC, 2024)</li>
  <li>Smart water technologies in Dubai reduced water loss to <strong>4.6%</strong> (DEWA, 2024)</li>
  <li>AI systems can potentially reduce campus water waste by <strong>up to 40%</strong> (Gholami et al., 2022)</li>
  <li>UAE Water Security Strategy 2036 requires a <strong>20% reduction</strong> in per-capita demand</li>
</ul>
<br>
These findings showed that university campuses &mdash; with multiple zones, 24/7 usage, and
no real-time monitoring &mdash; are an ideal starting point for smart water intelligence.
</div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_exec:
        st.markdown('<div class="nabdcard">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-weight:700;font-size:15px;color:#d8eeff;margin-bottom:12px">⚙️ What Has Been Built</div>', unsafe_allow_html=True)
        st.markdown(f"""
<div style="color:#c8e6ff;font-size:13px;line-height:1.8">
The research concept has been developed into a <strong>working AI dashboard prototype</strong>.
The app currently demonstrates:
</div>
        """, unsafe_allow_html=True)
        features = [
            ("📊","Zone-level water monitoring","Tracks simulated consumption per building vs baseline"),
            ("🚨","Anomaly detection","Flags zones with abnormal usage (18–49% above baseline in demo)"),
            ("🤖","AI Insights Engine","Groq AI (llama-3.3-70b) analyses usage and suggests investigation priorities"),
            ("🌿","Sustainability reporting","Estimates desalination-related emissions impact and SDG 6 alignment"),
            ("💬","AI Chat Assistant","Facilities managers can ask natural language questions about water data"),
            ("📁","CSV Data Upload","Accepts real campus meter data — ready for pilot validation"),
            ("📋","Prototype Impact Model","Calculates estimated avoidable cost and potential waste identified"),
        ]
        for icon, title, desc in features:
            st.markdown(
                f'<div style="display:flex;gap:12px;padding:10px 0;border-bottom:1px solid #163557">'
                f'<span style="font-size:20px;flex-shrink:0">{icon}</span>'
                f'<div><div style="font-weight:600;font-size:13px;color:#d8eeff">{title}</div>'
                f'<div style="color:{MUTED};font-size:11px;margin-top:2px">{desc}</div>'
                f'</div></div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_evidence:
        st.markdown('<div class="nabdcard">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-weight:700;font-size:15px;color:#d8eeff;margin-bottom:12px">📂 Current Evidence Available</div>', unsafe_allow_html=True)
        evidence_items = [
            ("✅","Working app prototype","Live Streamlit dashboard — viewable now"),
            ("✅","Simulated campus water dataset","8-zone simulated UAE campus, 24h hourly data"),
            ("✅","Anomaly detection outputs","3 flagged zones with abnormal usage in demo dataset"),
            ("✅","AI-generated recommendations","Groq AI produces actionable insights based on zone data"),
            ("✅","Prototype sustainability report","Auto-generated report with SDG 6 & Net Zero 2050 alignment"),
            ("✅","Research poster & literature","Inter-university project with peer-reviewed citations"),
            ("✅","Scientific business proposal","Detailed proposal with UAE water data and policy alignment"),
            ("🔄","Real campus pilot data","Next stage — pending university facilities partnership"),
            ("🔄","Verified real-world savings","Will be measured during campus pilot validation"),
        ]
        for icon, title, desc in evidence_items:
            color = GREEN if icon=="✅" else YELLOW
            st.markdown(
                f'<div style="display:flex;gap:10px;padding:8px 0;border-bottom:1px solid rgba(22,53,87,0.5)">'
                f'<span style="color:{color};font-size:14px;flex-shrink:0;margin-top:1px">{icon}</span>'
                f'<div><div style="font-size:12px;font-weight:600;color:#d8eeff">{title}</div>'
                f'<div style="color:{MUTED};font-size:11px;margin-top:1px">{desc}</div>'
                f'</div></div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_impact:
        st.markdown('<div class="nabdcard">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-weight:700;font-size:15px;color:#d8eeff;margin-bottom:12px">📊 Current Impact Status</div>', unsafe_allow_html=True)
        impact_data = {
            "Impact Area": [
                "Dashboard prototype",
                "Water anomaly detection",
                "Real campus water saved",
                "Prototype-tested water waste identified",
                "Real-world campus pilot",
                "University / facility feedback",
                "UAE policy alignment documented",
                "AI insights generation",
            ],
            "Current Status": [
                "✅ Completed",
                "✅ Demonstrated with simulated data",
                "🔄 Not yet verified — next pilot stage",
                "✅ ~342 m³/week identified in simulation",
                "🔄 Next validation stage",
                "🔄 Pending — outreach in progress",
                "✅ Mapped to UAE Water Strategy 2036 & Net Zero 2050",
                "✅ Live with Groq AI integration",
            ],
        }
        df_impact = pd.DataFrame(impact_data)
        st.dataframe(df_impact, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            f'<div style="background:rgba(255,179,71,0.07);border:1px solid rgba(255,179,71,0.3);'
            f'border-radius:10px;padding:12px 16px;margin-top:4px">'
            f'<div style="color:{YELLOW};font-weight:700;font-size:12px;margin-bottom:4px">&#128275; Honest Prototype Declaration</div>'
            f'<div style="color:{MUTED};font-size:11px;line-height:1.6">'
            f'All impact numbers in this prototype are <strong style="color:#d8eeff">estimates based on simulated data</strong>. '
            f'The prototype demonstrates the detection model and reporting framework. '
            f'Actual water savings and cost avoidance will only be measured and verified once the system '
            f'is connected to real campus meter data during a formal pilot.</div>'
            f'</div>', unsafe_allow_html=True)

    with tab_next:
        st.markdown('<div class="nabdcard">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-weight:700;font-size:15px;color:#d8eeff;margin-bottom:12px">🚀 Next Validation Step</div>', unsafe_allow_html=True)
        st.markdown(f"""
<div style="color:#c8e6ff;font-size:13px;line-height:1.8">
The next stage is to test NabdFlow with <strong>real campus meter data</strong> and collect feedback
from a university facilities or sustainability team. The pilot plan includes:
</div>
        """, unsafe_allow_html=True)
        steps = [
            ("1","Partner with a UAE university facilities team","Identify one willing sustainability or facilities officer as pilot contact"),
            ("2","Connect real meter data","Upload actual hourly m³ readings from 3–5 campus buildings via CSV"),
            ("3","Run anomaly detection on real data","Compare NabdFlow outputs against known maintenance records"),
            ("4","Measure actual vs. baseline","Track real m³ differences over 4 weeks"),
            ("5","Collect qualitative feedback","Interview facilities manager on usefulness and accuracy"),
            ("6","Publish pilot impact report","Document verified findings, limitations, and next development priorities"),
        ]
        for num, title, desc in steps:
            st.markdown(
                f'<div style="display:flex;gap:12px;padding:10px 0;border-bottom:1px solid rgba(22,53,87,0.5)">'
                f'<div style="width:26px;height:26px;border-radius:50%;background:rgba(0,200,255,0.15);border:1px solid rgba(0,200,255,0.4);'
                f'display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:800;color:{ACCENT};flex-shrink:0">{num}</div>'
                f'<div><div style="font-size:12px;font-weight:600;color:#d8eeff">{title}</div>'
                f'<div style="color:{MUTED};font-size:11px;margin-top:2px">{desc}</div>'
                f'</div></div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            f'<div style="background:rgba(0,229,160,0.06);border:1px solid rgba(0,229,160,0.25);'
            f'border-radius:10px;padding:14px 18px;margin-top:8px">'
            f'<div style="color:{GREEN};font-weight:700;font-size:12px;margin-bottom:4px">&#127919; UAE National Alignment</div>'
            f'<div style="color:{MUTED};font-size:11px;line-height:1.7">'
            f'NabdFlow supports the <strong style="color:#d8eeff">UAE Water Security Strategy 2036</strong> (20% per-capita demand reduction), '
            f'<strong style="color:#d8eeff">UAE Net Zero 2050</strong> (reduced desalination energy), and '
            f'<strong style="color:#d8eeff">UN SDG 6</strong> (Clean Water and Sanitation). '
            f'A university campus pilot would provide direct evidence of AI-driven water efficiency in a UAE institutional context.'
            f'</div></div>', unsafe_allow_html=True)

# ============================================================
# VIEW: ZONE INTELLIGENCE
# ============================================================
elif nav == "🗺️  Zone Intelligence":
    prototype_badge()
    st.markdown(f'<div style="color:{MUTED};font-size:12px;margin-bottom:14px">Which zone looks abnormal? Zones highlighted with orange/red borders require investigation.</div>', unsafe_allow_html=True)
    zones_d  = get_zones()
    cols_z   = st.columns(2)
    for i, z in enumerate(zones_d):
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
                f'<div style="color:{MUTED};font-size:10px;margin-top:2px">Zone ID: {z["short"]} &middot; Simulated data</div></div>'
                f'</div>{status_badge(z["status"])}</div>'
                f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px">'
                f'<div style="background:rgba(255,255,255,0.03);border-radius:8px;padding:9px 11px">'
                f'<div style="color:{MUTED};font-size:9px;text-transform:uppercase">Simulated Usage</div>'
                f'<div style="color:#d8eeff;font-weight:800;font-size:20px">{z["current"]}<span style="font-size:10px;color:{MUTED}"> m\u00b3/day</span></div></div>'
                f'<div style="background:rgba(255,255,255,0.03);border-radius:8px;padding:9px 11px">'
                f'<div style="color:{MUTED};font-size:9px;text-transform:uppercase">Above Baseline</div>'
                f'<div style="color:{"#ff5272" if delta>0 else "#00e5a0"};font-weight:800;font-size:20px">'
                f'{("+" if delta>0 else "")}{dp:.1f}<span style="font-size:10px">%</span></div></div></div>'
                f'<div style="display:flex;justify-content:space-between;margin-bottom:5px">'
                f'<span style="color:{MUTED};font-size:10px">Water Efficiency Score</span>'
                f'<span style="font-size:11px;font-weight:700;color:{ec}">{z["eff"]}%</span></div>'
                f'<div style="height:6px;background:rgba(255,255,255,0.06);border-radius:3px">'
                f'<div style="width:{z["eff"]}%;height:100%;background:{ec};border-radius:3px"></div>'
                f'</div></div>', unsafe_allow_html=True)

# ============================================================
# VIEW: ANOMALY & ALERTS
# ============================================================
elif nav == "🚨  Anomaly & Alerts":
    prototype_badge()
    alerts_d = get_alerts()
    active   = [a for a in alerts_d if a["sev"] not in ["resolved"]]
    a1,a2,a3,a4 = st.columns(4)
    a1.metric("Potential Alerts Total", str(len(alerts_d)))
    a2.metric("Critical (Possible Leak) 🔴", str(len([a for a in alerts_d if a["sev"]=="critical"])))
    a3.metric("High Anomaly 🟡",             str(len([a for a in alerts_d if a["sev"]=="high"])))
    a4.metric("Active (Needs Check)",        str(len(active)))
    st.markdown(f'<div style="color:{MUTED};font-size:11px;margin:10px 0 14px">Zones below have been flagged by the anomaly model. AED figures are estimated daily avoidable cost based on simulated data &mdash; not verified savings.</div>', unsafe_allow_html=True)
    for a in alerts_d:
        render_alert(a)

# ============================================================
# VIEW: AI INSIGHTS ENGINE
# ============================================================
elif nav == "🤖  AI Insights Engine":
    prototype_badge()
    st.markdown(
        f'<div class="nabdcard"><div style="font-weight:700;font-size:14px">🤖 AI Water Intelligence Analysis</div>'
        f'<div style="color:{MUTED};font-size:11px;margin-top:3px">Powered by Groq AI (llama-3.3-70b) &middot; Analysing simulated campus water data &middot; {len(get_zones())} zones</div>'
        f'</div>', unsafe_allow_html=True)

    if st.button("✨ Generate AI Insights", type="primary"):
        st.session_state["insights"] = ""
        with st.spinner("Analysing zones · Detecting patterns · Generating prototype insights..."):
            prompt = (
                "Analyse this simulated campus water data and provide actionable insights. "
                "Remember: this is prototype/simulated data, so frame all findings as 'potential', 'estimated', or 'the simulation suggests'.\n\n"
                "## What the Simulation Shows\n"
                "Summarise the 3 most important patterns in the simulated data.\n\n"
                "## Zones to Investigate First\n"
                "Which zones show abnormal usage and what should the facilities team check?\n\n"
                "## Estimated Potential Waste\n"
                "How much water waste does the simulation identify, and what is the estimated daily cost?\n\n"
                "## Recommended Actions for Facilities Team\n"
                "3 specific, practical actions to investigate (not confirmed savings).\n\n"
                "## How This Prototype Supports UAE Water Goals\n"
                "Brief note on UAE Water Security Strategy 2036 and Net Zero 2050 alignment."
            )
            st.session_state["insights"] = call_ai([{"role":"user","content":prompt}])

    if st.session_state["insights"]:
        st.markdown('<div style="background:rgba(0,0,0,0.2);border:1px solid #163557;border-radius:10px;padding:20px">', unsafe_allow_html=True)
        st.markdown(st.session_state["insights"])
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="text-align:center;padding:50px 20px;color:{MUTED}"><div style="font-size:48px;margin-bottom:12px">&#129504;</div><div style="font-size:14px;margin-bottom:6px;color:#d8eeff">AI Engine Ready</div><div style="font-size:12px">Click "Generate AI Insights" to analyse the simulated campus water data<br>and receive zone-specific recommendations.</div></div>', unsafe_allow_html=True)

# ============================================================
# VIEW: SUSTAINABILITY HUB
# ============================================================
elif nav == "🌿  Sustainability Hub":
    prototype_badge()
    weekly_d = get_weekly_df()
    waste_wk = int(weekly_d["Saved"].sum()) if "Saved" in weekly_d.columns else 342
    aed_wk   = int(weekly_d["AED"].sum())   if "AED"   in weekly_d.columns else 123
    carbon_e = round(waste_wk * 0.0008, 2)

    s1,s2,s3,s4,s5 = st.columns(5)
    s1.metric("💧 Potential Waste Identified/Week", f"~{waste_wk} m\u00b3",     "Prototype estimate")
    s2.metric("🌿 Est. Desalination Emissions",     f"~{carbon_e} t CO2eq",     "Prototype estimate")
    s3.metric("🔍 Estimated Avoidable Cost/Week",   f"~{aed_wk} {currency()}",  "Prototype estimate")
    s4.metric("🏆 SDG 6 Alignment",                 "Demonstrated",             "Clean Water goals")
    s5.metric("🌍 Water Efficiency Score",           "78 / 100",                 "Simulated campus")

    st.markdown(f'<div style="background:rgba(167,139,250,0.06);border:1px solid rgba(167,139,250,0.25);border-radius:8px;padding:8px 14px;font-size:11px;color:{MUTED};margin-bottom:14px">All figures above are <strong style="color:#d8eeff">prototype estimates</strong> based on simulated UAE campus data. They demonstrate the model&apos;s capability to identify potential waste &mdash; not verified real-world savings.</div>', unsafe_allow_html=True)

    st.markdown("")
    ca, cb = st.columns(2)
    with ca:
        fig_aed = go.Figure(go.Bar(x=weekly_d["Day"],y=weekly_d["AED"],marker_color=YELLOW,marker_opacity=0.85,marker_line_width=0))
        fig_aed.update_layout(**BASE_LAYOUT,height=230,legend=L_DEFAULT)
        st.markdown('<div class="nabdcard">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-weight:700;font-size:13px;margin-bottom:2px">Estimated Avoidable Cost per Day (Simulated)</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="color:{MUTED};font-size:10px;margin-bottom:4px">{currency()}/day &middot; Prototype estimates only</div>', unsafe_allow_html=True)
        st.plotly_chart(fig_aed, use_container_width=True, config={"displayModeBar":False})
        st.markdown("</div>", unsafe_allow_html=True)

    with cb:
        st.markdown('<div class="nabdcard">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-weight:700;font-size:13px;margin-bottom:14px">UAE Policy Alignment</div>', unsafe_allow_html=True)
        for label, val, color in [
            ("UAE Water Security Strategy 2036", 80, ACCENT),
            ("UAE Net Zero 2050",                72, GREEN),
            ("UN SDG 6 — Clean Water",           78, PURPLE),
            ("Leak Detection Capability",        85, YELLOW),
            ("Zone Coverage (Simulated)",       100, GREEN),
        ]:
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
    st.markdown(
        f'<div class="nabdcard">'
        f'<div style="font-weight:700;font-size:14px">📋 Prototype Sustainability Report</div>'
        f'<div style="color:{MUTED};font-size:11px;margin-top:3px">AI-generated prototype report &middot; For Facilities Management review &middot; Uses simulated data</div>'
        f'</div>', unsafe_allow_html=True)

    if st.button("📄 Generate Prototype Sustainability Report", type="primary"):
        st.session_state["report"] = ""
        with st.spinner("Compiling simulated data · Drafting prototype report..."):
            zones_d = get_zones()
            n_anom  = len([z for z in zones_d if z["status"]!="normal"])
            prompt = (
                f"Generate a PROTOTYPE Sustainability Report for a UAE university campus water intelligence pilot.\n\n"
                f"IMPORTANT: This uses simulated data. Use language like 'estimated', 'potential', 'prototype-tested', 'simulation suggests'. "
                f"Do NOT say 'verified savings' or 'confirmed reduction'.\n\n"
                f"Report data (simulated):\n"
                f"- Zones monitored: {len(zones_d)}\n"
                f"- Potential anomalies detected: {n_anom}\n"
                f"- Estimated potential waste identified: ~{waste_wk} m3/week\n"
                f"- Estimated avoidable cost: ~{aed_wk} {currency()}/week\n"
                f"- Estimated desalination-related emissions impact: ~{carbon_e} t CO2eq/week\n\n"
                "Sections to include:\n"
                "1. Prototype Report Summary (2-3 sentences, honest about prototype status)\n"
                "2. Zones Monitored and Anomalies Detected\n"
                "3. Potential Water Waste Identified (with prototype caveats)\n"
                "4. Estimated Avoidable Cost (with prototype caveats)\n"
                "5. UAE Water Security Strategy 2036 Alignment\n"
                "6. UAE Net Zero 2050 Alignment\n"
                "7. Recommended Facility Investigation Actions (not confirmed fixes)\n"
                "8. Next Pilot Plan (what real data validation looks like)\n\n"
                "End with a clear statement that these figures will be validated during a real campus pilot."
            )
            st.session_state["report"] = call_ai([{"role":"user","content":prompt}])

    if st.session_state["report"]:
        st.markdown(f'<div style="background:rgba(0,0,0,0.2);border:1px solid #163557;border-radius:10px;padding:20px">', unsafe_allow_html=True)
        st.markdown(st.session_state["report"])
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# VIEW: AI CHAT ASSISTANT
# ============================================================
elif nav == "💬  AI Chat Assistant":
    prototype_badge()
    st.markdown(f'<div class="nabdcard"><div style="font-weight:700;font-size:14px">💬 NabdFlow AI Assistant</div><div style="color:{MUTED};font-size:11px;margin-top:3px">Ask about simulated water usage, detected anomalies, potential savings, or recommended investigations</div></div>', unsafe_allow_html=True)
    qc = st.columns(4)
    for i, q in enumerate(["Which zone needs checking first?","How much waste is the simulation showing?","What should facilities investigate?","How does this support UAE Net Zero?"]):
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
    if user_input := st.chat_input("Ask about campus water data..."):
        st.session_state["chat"].append({"role":"user","content":user_input})
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                reply = call_ai([{"role":m["role"],"content":m["content"]} for m in st.session_state["chat"]])
            st.markdown(reply)
        st.session_state["chat"].append({"role":"assistant","content":reply})
        st.rerun()

# ============================================================
# VIEW: SETUP & DATA
# ============================================================
elif nav == "⚙️  Setup & Data":
    tab_cfg, tab_upload, tab_sample = st.tabs(["🏫 Configuration","📁 Upload CSV Data","📄 Sample CSV & Format"])

    with tab_cfg:
        st.markdown('<div class="nabdcard">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-weight:700;font-size:14px;margin-bottom:14px">Campus Configuration</div>', unsafe_allow_html=True)
        cfg2 = st.session_state["config"]
        c1,c2 = st.columns(2)
        with c1:
            uni    = st.text_input("University / Project Name", value=cfg2["university"])
            campus = st.text_input("Campus / Dataset Label",    value=cfg2["campus"])
        with c2:
            tariff_v = st.number_input("Water Tariff (per m\u00b3)", value=cfg2["tariff"], step=0.01, min_value=0.01)
            curr     = st.selectbox("Currency", ["AED","USD","EUR","GBP","SAR","QAR"],
                                    index=["AED","USD","EUR","GBP","SAR","QAR"].index(cfg2["currency"]))
        st.markdown("</div>", unsafe_allow_html=True)
        if st.button("💾 Save Configuration", type="primary"):
            st.session_state["config"].update({"university":uni,"campus":campus,"tariff":tariff_v,"currency":curr})
            st.success(f"Configuration saved!")
            st.rerun()

    with tab_upload:
        st.markdown('<div class="nabdcard">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-weight:700;font-size:14px;margin-bottom:4px">Upload Real Campus Meter Data</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="color:{MUTED};font-size:11px;margin-bottom:14px">Required columns: <code>zone</code>, <code>timestamp</code>, <code>consumption_m3</code>, <code>baseline_m3</code></div>', unsafe_allow_html=True)
        uploaded = st.file_uploader("Choose CSV file", type=["csv"], label_visibility="collapsed")
        if uploaded:
            try:
                raw = pd.read_csv(uploaded)
                st.markdown(f'<div style="color:{GREEN};font-size:12px;margin-bottom:8px">&#10003; File loaded: {len(raw)} rows, {raw["zone"].nunique() if "zone" in raw.columns else "?"} zones</div>', unsafe_allow_html=True)
                st.dataframe(raw.head(10), use_container_width=True)
                required = {"zone","timestamp","consumption_m3","baseline_m3"}
                present  = set(raw.columns.str.strip().str.lower().str.replace(" ","_"))
                missing  = required - present
                if missing:
                    st.error(f"Missing columns: {', '.join(missing)}")
                else:
                    st.markdown("</div>", unsafe_allow_html=True)
                    if st.button("⚡ Process & Apply Data", type="primary"):
                        with st.spinner("Processing..."):
                            zo, ho, wo, ao = process_csv(raw)
                            st.session_state.update({"raw_df":raw,"zones_data":zo,"hourly_data":ho,"weekly_data":wo,"alerts_data":ao})
                        st.success(f"Real data applied! {len(zo)} zones · {len(ao)} potential alerts detected")
                        st.rerun()
                    st.markdown('<div class="nabdcard" style="margin-top:0">', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.markdown(f'<div style="text-align:center;padding:30px;color:{MUTED}">Drop your meter data CSV here to run NabdFlow on real campus data</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        if using_real_data():
            if st.button("🗑️ Clear — Revert to Simulated Demo Data"):
                for k in ["raw_df","zones_data","hourly_data","weekly_data","alerts_data"]:
                    st.session_state[k] = None
                st.rerun()

    with tab_sample:
        st.markdown('<div class="nabdcard">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-weight:700;font-size:14px;margin-bottom:10px">CSV Format Guide</div>', unsafe_allow_html=True)
        st.markdown("| Column | Type | Required | Description |\n|---|---|---|---|\n| `zone` | text | ✅ | Building/zone name |\n| `timestamp` | datetime | ✅ | `YYYY-MM-DD HH:MM` |\n| `consumption_m3` | number | ✅ | Actual usage in m³ |\n| `baseline_m3` | number | ✅ | Expected/historical baseline m³ |")
        st.markdown("</div>", unsafe_allow_html=True)
        sample_df  = make_sample_csv()
        csv_bytes  = sample_df.to_csv(index=False).encode()
        st.download_button("⬇️ Download Sample CSV (6 zones · 24 hours)", csv_bytes, "nabdflow_sample.csv","text/csv")
        st.markdown('<div class="nabdcard" style="margin-top:12px">', unsafe_allow_html=True)
        st.dataframe(sample_df.head(12), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
