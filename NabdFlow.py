import { useState, useEffect, useRef } from "react";
import {
  AreaChart, Area, BarChart, Bar, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell
} from "recharts";

// TOKENS
const C = {
  bg:       '#050d1c',
  surface:  '#081525',
  card:     '#0d1e38',
  border:   '#163557',
  accent:   '#00c8ff',
  aAlpha:   'rgba(0,200,255,0.12)',
  green:    '#00e5a0',
  gAlpha:   'rgba(0,229,160,0.10)',
  yellow:   '#ffb347',
  yAlpha:   'rgba(255,179,71,0.10)',
  red:      '#ff5272',
  rAlpha:   'rgba(255,82,114,0.10)',
  purple:   '#a78bfa',
  pAlpha:   'rgba(167,139,250,0.10)',
  text:     '#d8eeff',
  muted:    '#5a8aaa',
  grid:     'rgba(255,255,255,0.04)',
};

// DATA
const ZONES = [
  { id:1, name:"Main Academic Building", short:"MAB", icon:"🏛️", baseline:450, current:421, status:"normal",  eff:94 },
  { id:2, name:"Science & Tech Block",   short:"STB", icon:"🔬", baseline:380, current:512, status:"anomaly", eff:65 },
  { id:3, name:"Student Housing A",      short:"SHA", icon:"🏘️", baseline:820, current:798, status:"normal",  eff:97 },
  { id:4, name:"Student Housing B",      short:"SHB", icon:"🏠", baseline:750, current:901, status:"alert",   eff:72 },
  { id:5, name:"Sports Complex",         short:"SPC", icon:"⚽", baseline:600, current:578, status:"normal",  eff:96 },
  { id:6, name:"Library & Research",     short:"LIB", icon:"📚", baseline:220, current:215, status:"normal",  eff:98 },
  { id:7, name:"Cafeteria & Dining",     short:"CAF", icon:"🍽️", baseline:480, current:503, status:"normal",  eff:89 },
  { id:8, name:"Admin & Offices",        short:"ADM", icon:"💼", baseline:180, current:267, status:"leak",    eff:58 },
];

const ALERTS = [
  { id:1, type:"leak",     zone:"Admin & Offices",      msg:"Pipe leak detected — 87 L/hr excess flow after business hours",          time:"12m ago", aed:43.5, sev:"critical" },
  { id:2, type:"anomaly",  zone:"Student Housing B",    msg:"Consumption 20% above 7-day baseline for 3+ consecutive hours",           time:"47m ago", aed:28.2, sev:"high"     },
  { id:3, type:"anomaly",  zone:"Science & Tech Block", msg:"Lab cooling water spike — possible thermostatic valve failure",            time:"1.5h ago",aed:18.7, sev:"medium"   },
  { id:4, type:"info",     zone:"Cafeteria & Dining",   msg:"Usage slightly above average — catering event likely in progress",         time:"3h ago",  aed:6.3,  sev:"low"      },
  { id:5, type:"resolved", zone:"Sports Complex",       msg:"Irrigation anomaly resolved — system returned to normal baseline",         time:"5h ago",  aed:0,    sev:"resolved" },
];

const WEEKLY = [
  { d:"Mon", usage:18240, saved:2840, aed:1022 },
  { d:"Tue", usage:17890, saved:3190, aed:1148 },
  { d:"Wed", usage:19100, saved:1900, aed:684  },
  { d:"Thu", usage:17200, saved:3800, aed:1368 },
  { d:"Fri", usage:15600, saved:4200, aed:1512 },
  { d:"Sat", usage:9800,  saved:5600, aed:2016 },
  { d:"Sun", usage:8900,  saved:6100, aed:2196 },
];

const genHourly = () => Array.from({ length:24 }, (_,i) => {
  const b = 120 + Math.sin(i/3.5)*55 + (i>=7&&i<=19 ? 105 : 0);
  return { h:`${String(i).padStart(2,'0')}:00`, actual:Math.round(b+(Math.random()*25-5)), predicted:Math.round(b*1.06), baseline:Math.round(b*1.22) };
});
const HOURLY = genHourly();

const PIE_DATA = ZONES.map(z => ({
  name: z.short,
  value: z.current,
  fill: z.status==='leak' ? C.red : z.status==='anomaly'||z.status==='alert' ? C.yellow : C.accent
}));

// HELPERS
const sColor = s => ({ normal:C.green, anomaly:C.yellow, alert:C.yellow, leak:C.red, resolved:C.muted }[s]||C.muted);
const sLabel = s => ({ normal:'Normal', anomaly:'Anomaly', alert:'Alert', leak:'⚠ Leak', resolved:'Resolved' }[s]||s);
const sevBg  = s => ({ critical:C.rAlpha, high:C.yAlpha, medium:C.yAlpha, low:C.aAlpha, resolved:'rgba(90,138,170,0.08)' }[s]||'transparent');
const sevClr = s => ({ critical:C.red, high:C.yellow, medium:C.yellow, low:C.accent, resolved:C.muted }[s]||C.muted);
const ttStyle = { background:C.card, border:`1px solid ${C.border}`, borderRadius:8, fontSize:11, color:C.text };

const Dot = ({ color }) => (
  <span style={{ display:'inline-block', width:7, height:7, borderRadius:'50%', background:color, marginRight:5, flexShrink:0 }} />
);

const KPICard = ({ label, value, unit, sub, color, icon }) => (
  <div style={{ background:C.card, border:`1px solid ${C.border}`, borderRadius:12, padding:'16px 18px', flex:1, minWidth:130 }}>
    <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start' }}>
      <div style={{ flex:1 }}>
        <div style={{ color:C.muted, fontSize:10, fontWeight:700, textTransform:'uppercase', letterSpacing:1 }}>{label}</div>
        <div style={{ color:color||C.text, fontSize:24, fontWeight:800, marginTop:5, lineHeight:1 }}>
          {value}<span style={{ fontSize:12, fontWeight:400, marginLeft:3, color:C.muted }}>{unit}</span>
        </div>
        {sub && <div style={{ color:C.muted, fontSize:10, marginTop:5 }}>{sub}</div>}
      </div>
      <div style={{ fontSize:22, opacity:0.85 }}>{icon}</div>
    </div>
  </div>
);

const Section = ({ title, sub, children, action }) => (
  <div style={{ background:C.card, border:`1px solid ${C.border}`, borderRadius:12, padding:20 }}>
    <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:16 }}>
      <div>
        <div style={{ fontWeight:700, fontSize:14 }}>{title}</div>
        {sub && <div style={{ color:C.muted, fontSize:11, marginTop:3 }}>{sub}</div>}
      </div>
      {action}
    </div>
    {children}
  </div>
);

const Btn = ({ onClick, disabled, color, children }) => (
  <button onClick={onClick} disabled={disabled}
    style={{ background: disabled?'rgba(255,255,255,0.05)':color==='green'?C.green:C.accent,
      color: disabled?C.muted:'#04111f', border:'none', borderRadius:8,
      padding:'9px 18px', fontWeight:700, fontSize:12, cursor: disabled?'not-allowed':'pointer', transition:'opacity 0.2s',
      whiteSpace:'nowrap' }}>
    {children}
  </button>
);

// MAIN
export default function NabdFlow() {
  const [tab, setTab]             = useState("dashboard");
  const [live, setLive]           = useState(847);
  const [aiText, setAiText]       = useState("");
  const [aiLoading, setAiLoading] = useState(false);
  const [rptText, setRptText]     = useState("");
  const [rptLoading, setRptLoading]= useState(false);
  const [msgs, setMsgs]           = useState([{ role:"assistant", text:"Hello! I'm NabdFlow AI. Ask me anything about your campus water systems — anomalies, leaks, consumption patterns, or sustainability insights." }]);
  const [chatIn, setChatIn]       = useState("");
  const [chatLoad, setChatLoad]   = useState(false);
  const [selZone, setSelZone]     = useState(null);
  const chatRef = useRef(null);

  useEffect(() => {
    const iv = setInterval(() => setLive(v => +(v+(Math.random()*12-6)).toFixed(1)), 1800);
    return () => clearInterval(iv);
  }, []);

  useEffect(() => {
    if (chatRef.current) chatRef.current.scrollTop = chatRef.current.scrollHeight;
  }, [msgs]);

  const SYS = `You are NabdFlow AI Engine — an expert water intelligence system for a UAE university campus.
Current campus snapshot (real-time):
• 8 monitored zones, 3 active anomalies
• CRITICAL: Admin & Offices — pipe leak, 87L/hr excess, efficiency 58%
• HIGH: Student Housing B — 20% above baseline, efficiency 72%  
• MEDIUM: Science & Tech Block — cooling water spike, efficiency 65%
• Today's total: 18,247 m³ | Baseline: 20,587 m³ | Saved: 2,340 m³ (11.4%)
• AED saved today: 847 AED | Water tariff: ~0.36 AED/m³
• Campus efficiency score: 78/100 (↑4 pts vs last week)
Be precise, professional, and data-driven. Format with clear sections using markdown headers.`;

  const callAI = async (messages) => {
    const r = await fetch("https://api.anthropic.com/v1/messages", {
      method:"POST", headers:{"Content-Type":"application/json"},
      body: JSON.stringify({ model:"claude-sonnet-4-20250514", max_tokens:1000, system:SYS, messages })
    });
    const d = await r.json();
    return d.content?.[0]?.text || "No response received.";
  };

  const runInsights = async () => {
    setAiLoading(true); setTab("ai");
    try {
      const t = await callAI([{ role:"user", content:`Analyze today's campus water data and provide:

## 🔍 Key Findings
(3 critical observations with specific figures)

## 🚨 Priority Actions Required
(ranked by urgency — include estimated resolution time)

## 📈 24-Hour Demand Forecast
(expected pattern and risk windows)

## 💡 Quick-Win Optimizations
(3 actions with estimated AED + m³ savings each)

## 📊 Efficiency Score Breakdown
(what's driving 78/100 and how to reach 90+)` }]);
      setAiText(t);
    } catch { setAiText("⚠️ AI connection error. Please try again."); }
    setAiLoading(false);
  };

  const runReport = async () => {
    setRptLoading(true);
    try {
      const t = await callAI([{ role:"user", content:`Generate a formal Weekly Water Sustainability Intelligence Report for the University Facilities Director and Sustainability Committee.

Figures to include:
- Week avg: 13,820 m³/day | Total saved: 21,630 m³ | AED savings: 7,787 AED
- Carbon offset equivalent: ~21.6 tonnes CO₂
- 3 anomaly incidents detected and logged
- SDG 6 compliance status

Sections required:
1. Executive Summary
2. Weekly Consumption Overview (with week-on-week comparison)
3. Anomaly & Leak Detection Summary
4. AI Predictive Outlook for Next 7 Days
5. Sustainability Impact (carbon, SDG 6 alignment, water stewardship score)
6. Financial Impact Analysis (AED savings, projected annual savings)
7. Recommended Actions for Facilities Management (prioritized)
8. Conclusion

Use formal report language. Be specific with all numbers.` }]);
      setRptText(t);
    } catch { setRptText("⚠️ Report generation failed. Please try again."); }
    setRptLoading(false);
  };

  const sendChat = async () => {
    if (!chatIn.trim() || chatLoad) return;
    const msg = chatIn.trim(); setChatIn("");
    const updated = [...msgs, { role:"user", text:msg }];
    setMsgs(updated); setChatLoad(true);
    try {
      const history = updated.slice(1).map(m => ({ role:m.role==="user"?"user":"assistant", content:m.text }));
      const reply = await callAI(history);
      setMsgs(prev => [...prev, { role:"assistant", text:reply }]);
    } catch { setMsgs(prev => [...prev, { role:"assistant", text:"Connection error. Please try again." }]); }
    setChatLoad(false);
  };

  const NAV = [
    { id:"dashboard",     label:"Overview",       icon:"📊" },
    { id:"zones",         label:"Zones",          icon:"🗺️" },
    { id:"alerts",        label:"Alerts",         icon:"🚨", badge: ALERTS.filter(a=>a.sev!=='resolved').length },
    { id:"ai",            label:"AI Insights",    icon:"🤖" },
    { id:"sustainability",label:"Sustainability", icon:"🌿" },
    { id:"chat",          label:"AI Chat",        icon:"💬" },
  ];

  // VIEWS
  const Dashboard = () => (
    <div style={{ display:'flex', flexDirection:'column', gap:16 }}>
      <div style={{ display:'flex', gap:10, flexWrap:'wrap' }}>
        <KPICard label="Today's Consumption" value="18,247" unit="m³" sub="↓ 11.4% vs projected baseline" color={C.green}   icon="💧"/>
        <KPICard label="Live Flow Rate"       value={live.toFixed(0)} unit="L/min" sub="All zones · updating live" color={C.accent}  icon="⚡"/>
        <KPICard label="AED Saved Today"      value="847"    unit="AED"   sub="At AED 0.36/m³ tariff"     color={C.yellow}  icon="💰"/>
        <KPICard label="Active Alerts"        value="3"      unit=""      sub="1 critical · 1 high · 1 med" color={C.red}    icon="🚨"/>
        <KPICard label="Efficiency Score"     value="78"     unit="/100"  sub="↑ 4 pts from last week"    color={C.purple}  icon="📈"/>
      </div>

      <Section title="Today's Hourly Water Consumption" sub="Actual vs. Predicted vs. Baseline · m³/hr · All zones combined"
        action={<div style={{ display:'flex', gap:14, fontSize:11 }}>
          <span style={{ display:'flex', alignItems:'center' }}><Dot color={C.accent}/>Actual</span>
          <span style={{ display:'flex', alignItems:'center' }}><Dot color={C.purple}/>Predicted</span>
          <span style={{ display:'flex', alignItems:'center' }}><Dot color={C.muted}/>Baseline</span>
        </div>}>
        <ResponsiveContainer width="100%" height={210}>
          <AreaChart data={HOURLY} margin={{ top:5, right:8, bottom:0, left:-12 }}>
            <defs>
              <linearGradient id="gA" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor={C.accent} stopOpacity={0.35}/>
                <stop offset="95%" stopColor={C.accent} stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="gP" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor={C.purple} stopOpacity={0.2}/>
                <stop offset="95%" stopColor={C.purple} stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid stroke={C.grid}/>
            <XAxis dataKey="h" tick={{ fill:C.muted, fontSize:9 }} interval={3}/>
            <YAxis tick={{ fill:C.muted, fontSize:9 }}/>
            <Tooltip contentStyle={ttStyle} labelStyle={{ color:C.text }}/>
            <Area type="monotone" dataKey="baseline"  stroke={C.muted}   fill="none"     strokeDasharray="4 3" strokeWidth={1.5} name="Baseline"/>
            <Area type="monotone" dataKey="predicted" stroke={C.purple}  fill="url(#gP)" strokeWidth={1.5} name="Predicted"/>
            <Area type="monotone" dataKey="actual"    stroke={C.accent}  fill="url(#gA)" strokeWidth={2}   name="Actual"/>
          </AreaChart>
        </ResponsiveContainer>
      </Section>

      <div style={{ display:'flex', gap:14, flexWrap:'wrap' }}>
        {/* Zone List */}
        <div style={{ background:C.card, border:`1px solid ${C.border}`, borderRadius:12, padding:18, flex:2, minWidth:280 }}>
          <div style={{ fontWeight:700, fontSize:13, marginBottom:14 }}>Zone Status Overview</div>
          <div style={{ display:'flex', flexDirection:'column', gap:7 }}>
            {ZONES.map(z => (
              <div key={z.id} onClick={() => { setSelZone(z.id); setTab('zones'); }}
                style={{ display:'flex', alignItems:'center', gap:9, padding:'7px 9px', borderRadius:8, cursor:'pointer', background:'rgba(255,255,255,0.02)', border:`1px solid ${C.border}` }}>
                <span style={{ fontSize:15 }}>{z.icon}</span>
                <div style={{ flex:1, minWidth:0 }}>
                  <div style={{ fontSize:11, fontWeight:600, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{z.name}</div>
                  <div style={{ fontSize:10, color:C.muted, marginTop:1 }}>{z.current} m³/hr</div>
                </div>
                <div style={{ width:60, height:5, background:'rgba(255,255,255,0.07)', borderRadius:3, overflow:'hidden', flexShrink:0 }}>
                  <div style={{ width:`${z.eff}%`, height:'100%', background: z.eff>=90?C.green:z.eff>=70?C.yellow:C.red, borderRadius:3 }}/>
                </div>
                <span style={{ fontSize:10, fontWeight:700, color:sColor(z.status), background:z.status==='normal'?C.gAlpha:z.status==='leak'?C.rAlpha:C.yAlpha, padding:'2px 8px', borderRadius:20, minWidth:58, textAlign:'center', flexShrink:0 }}>
                  {sLabel(z.status)}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Weekly Bar */}
        <div style={{ background:C.card, border:`1px solid ${C.border}`, borderRadius:12, padding:18, flex:1.5, minWidth:200 }}>
          <div style={{ fontWeight:700, fontSize:13, marginBottom:4 }}>Weekly Usage vs. Savings</div>
          <div style={{ color:C.muted, fontSize:10, marginBottom:12 }}>m³ · this week</div>
          <ResponsiveContainer width="100%" height={190}>
            <BarChart data={WEEKLY} barGap={3} margin={{ top:0, right:0, bottom:0, left:-22 }}>
              <CartesianGrid stroke={C.grid} vertical={false}/>
              <XAxis dataKey="d" tick={{ fill:C.muted, fontSize:9 }}/>
              <YAxis tick={{ fill:C.muted, fontSize:9 }}/>
              <Tooltip contentStyle={ttStyle}/>
              <Bar dataKey="usage" fill={C.accent}  fillOpacity={0.6} radius={[3,3,0,0]} name="Usage m³"/>
              <Bar dataKey="saved" fill={C.green}   fillOpacity={0.8} radius={[3,3,0,0]} name="Saved m³"/>
            </BarChart>
          </ResponsiveContainer>
          <div style={{ display:'flex', gap:12, fontSize:10, marginTop:6 }}>
            <span style={{ display:'flex', alignItems:'center' }}><Dot color={C.accent}/>Usage</span>
            <span style={{ display:'flex', alignItems:'center' }}><Dot color={C.green}/>Saved</span>
          </div>
        </div>

        {/* Pie */}
        <div style={{ background:C.card, border:`1px solid ${C.border}`, borderRadius:12, padding:18, flex:1, minWidth:180 }}>
          <div style={{ fontWeight:700, fontSize:13, marginBottom:2 }}>Consumption Share</div>
          <div style={{ color:C.muted, fontSize:10, marginBottom:6 }}>by zone · m³/hr</div>
          <ResponsiveContainer width="100%" height={160}>
            <PieChart>
              <Pie data={PIE_DATA} cx="50%" cy="50%" innerRadius={42} outerRadius={65} paddingAngle={2} dataKey="value">
                {PIE_DATA.map((e,i) => <Cell key={i} fill={e.fill} fillOpacity={0.85}/>)}
              </Pie>
              <Tooltip contentStyle={ttStyle} formatter={v=>[`${v} m³`,'']}/>
            </PieChart>
          </ResponsiveContainer>
          <div style={{ display:'flex', flexWrap:'wrap', gap:'3px 10px', fontSize:10, color:C.muted }}>
            {ZONES.map(z=><span key={z.id} style={{ display:'flex', alignItems:'center' }}><Dot color={sColor(z.status)}/>{z.short}</span>)}
          </div>
        </div>
      </div>
    </div>
  );

  const Zones = () => (
    <div style={{ display:'flex', flexDirection:'column', gap:12 }}>
      <div style={{ display:'flex', flexWrap:'wrap', gap:12 }}>
        {ZONES.map(z => {
          const delta = z.current - z.baseline;
          const deltaP = ((delta/z.baseline)*100).toFixed(1);
          const sel = selZone===z.id;
          return (
            <div key={z.id} onClick={() => setSelZone(sel?null:z.id)}
              style={{ background:C.card, border:`1.5px solid ${sel?sColor(z.status):C.border}`, borderRadius:12, padding:18, flex:'1 1 220px', cursor:'pointer', transition:'border-color 0.2s' }}>
              <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start', marginBottom:14 }}>
                <div style={{ display:'flex', alignItems:'center', gap:10 }}>
                  <span style={{ fontSize:22 }}>{z.icon}</span>
                  <div>
                    <div style={{ fontWeight:600, fontSize:13 }}>{z.name}</div>
                    <div style={{ color:C.muted, fontSize:10, marginTop:2 }}>ID: {z.short}</div>
                  </div>
                </div>
                <span style={{ fontSize:10, fontWeight:700, color:sColor(z.status), background:z.status==='normal'?C.gAlpha:z.status==='leak'?C.rAlpha:C.yAlpha, padding:'3px 10px', borderRadius:20 }}>
                  {sLabel(z.status)}
                </span>
              </div>
              <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:8, marginBottom:12 }}>
                <div style={{ background:'rgba(255,255,255,0.03)', borderRadius:8, padding:'8px 10px' }}>
                  <div style={{ color:C.muted, fontSize:9, textTransform:'uppercase', letterSpacing:0.8 }}>Current</div>
                  <div style={{ color:C.text, fontWeight:700, fontSize:20, marginTop:2 }}>{z.current}<span style={{ fontSize:10, color:C.muted }}> m³/hr</span></div>
                </div>
                <div style={{ background:'rgba(255,255,255,0.03)', borderRadius:8, padding:'8px 10px' }}>
                  <div style={{ color:C.muted, fontSize:9, textTransform:'uppercase', letterSpacing:0.8 }}>vs Baseline</div>
                  <div style={{ color:delta>0?C.red:C.green, fontWeight:700, fontSize:20, marginTop:2 }}>{delta>0?'+':''}{deltaP}<span style={{ fontSize:10 }}>%</span></div>
                </div>
              </div>
              <div>
                <div style={{ display:'flex', justifyContent:'space-between', marginBottom:5 }}>
                  <span style={{ color:C.muted, fontSize:10 }}>Efficiency Score</span>
                  <span style={{ fontSize:11, fontWeight:700, color:z.eff>=90?C.green:z.eff>=70?C.yellow:C.red }}>{z.eff}%</span>
                </div>
                <div style={{ height:6, background:'rgba(255,255,255,0.06)', borderRadius:3, overflow:'hidden' }}>
                  <div style={{ width:`${z.eff}%`, height:'100%', background:z.eff>=90?C.green:z.eff>=70?C.yellow:C.red, borderRadius:3, transition:'width 0.5s' }}/>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );

  const Alerts = () => (
    <div style={{ display:'flex', flexDirection:'column', gap:12 }}>
      <div style={{ display:'flex', gap:10, flexWrap:'wrap', marginBottom:4 }}>
        {[['Total Alerts', ALERTS.length, C.muted],['Critical', 1, C.red],['High', 1, C.yellow],['Active', 4, C.accent]].map(([l,v,c]) => (
          <div key={l} style={{ background:C.card, border:`1px solid ${C.border}`, borderRadius:10, padding:'12px 18px', display:'flex', gap:10, alignItems:'center' }}>
            <span style={{ fontSize:22, fontWeight:800, color:c }}>{v}</span>
            <span style={{ color:C.muted, fontSize:12 }}>{l}</span>
          </div>
        ))}
      </div>
      {ALERTS.map(a => (
        <div key={a.id} style={{ background:C.card, border:`1px solid ${a.sev==='critical'?C.red:a.sev==='high'?C.yellow:C.border}`, borderRadius:12, padding:'15px 18px', display:'flex', gap:14, alignItems:'flex-start' }}>
          <div style={{ fontSize:22, marginTop:1 }}>{{ leak:'💧', anomaly:'⚠️', info:'ℹ️', resolved:'✅' }[a.type]}</div>
          <div style={{ flex:1 }}>
            <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', flexWrap:'wrap', gap:8 }}>
              <span style={{ fontWeight:700, fontSize:13 }}>{a.zone}</span>
              <div style={{ display:'flex', gap:8, alignItems:'center' }}>
                {a.aed>0 && <span style={{ color:C.red, fontSize:11, fontWeight:700 }}>−{a.aed} AED/hr</span>}
                <span style={{ fontSize:10, fontWeight:700, color:sevClr(a.sev), background:sevBg(a.sev), padding:'2px 10px', borderRadius:20, textTransform:'uppercase' }}>{a.sev}</span>
              </div>
            </div>
            <div style={{ color:C.muted, fontSize:12, marginTop:5, lineHeight:1.5 }}>{a.msg}</div>
            <div style={{ color:C.muted, fontSize:11, marginTop:6 }}>🕐 {a.time}</div>
          </div>
        </div>
      ))}
    </div>
  );

  const AIView = () => (
    <div style={{ display:'flex', flexDirection:'column', gap:16 }}>
      <Section title="🤖 AI Water Intelligence Analysis" sub="Powered by NabdFlow AI Engine · Analyzing 8 zones · Live campus data"
        action={<Btn onClick={runInsights} disabled={aiLoading}>{aiLoading ? '⏳ Analyzing...' : '✨ Generate Insights'}</Btn>}>
        {!aiText && !aiLoading && (
          <div style={{ textAlign:'center', padding:'48px 20px', color:C.muted }}>
            <div style={{ fontSize:48, marginBottom:12 }}>🧠</div>
            <div style={{ fontSize:14, marginBottom:8 }}>AI Analysis Engine Ready</div>
            <div style={{ fontSize:12 }}>Click "Generate Insights" to run a full AI analysis on current campus water data including anomaly triage, demand forecasting, and optimization opportunities.</div>
          </div>
        )}
        {aiLoading && (
          <div style={{ textAlign:'center', padding:'48px 20px', color:C.accent }}>
            <div style={{ fontSize:36, marginBottom:12 }}>⚙️</div>
            <div style={{ fontSize:14 }}>Analyzing 8 zones · 24h consumption history · 3 active anomalies · predicting demand...</div>
          </div>
        )}
        {aiText && !aiLoading && (
          <div style={{ background:'rgba(0,0,0,0.25)', borderRadius:10, padding:'16px 20px', whiteSpace:'pre-wrap', fontSize:12.5, lineHeight:1.75, color:C.text }}>
            {aiText}
          </div>
        )}
      </Section>
    </div>
  );

  const Sustainability = () => (
    <div style={{ display:'flex', flexDirection:'column', gap:16 }}>
      <div style={{ display:'flex', gap:10, flexWrap:'wrap' }}>
        <KPICard label="Water Saved This Week" value="21,630" unit="m³"         sub="vs projected baseline"          color={C.accent}  icon="💧"/>
        <KPICard label="Carbon Offset Equiv."  value="21.6"  unit="t CO₂"       sub="~1,440 trees · 30 days"         color={C.green}   icon="🌿"/>
        <KPICard label="AED Savings This Week" value="7,787" unit="AED"          sub="Projected annual: ~405K AED"    color={C.yellow}  icon="💰"/>
        <KPICard label="SDG 6 Alignment"       value="B+"    unit=""             sub="Clean Water & Sanitation"       color={C.purple}  icon="🏆"/>
        <KPICard label="Sustainability Score"  value="78"    unit="/100"         sub="↑ 6 pts YoY · Target: 90"      color={C.green}   icon="🌍"/>
      </div>

      <div style={{ display:'flex', gap:14, flexWrap:'wrap' }}>
        <div style={{ background:C.card, border:`1px solid ${C.border}`, borderRadius:12, padding:18, flex:1, minWidth:240 }}>
          <div style={{ fontWeight:700, fontSize:13, marginBottom:14 }}>Weekly AED Savings per Day</div>
          <ResponsiveContainer width="100%" height={170}>
            <BarChart data={WEEKLY} margin={{ top:0, right:0, bottom:0, left:-18 }}>
              <CartesianGrid stroke={C.grid} vertical={false}/>
              <XAxis dataKey="d" tick={{ fill:C.muted, fontSize:9 }}/>
              <YAxis tick={{ fill:C.muted, fontSize:9 }}/>
              <Tooltip contentStyle={ttStyle} formatter={v=>[`${v} AED`,'']}/>
              <Bar dataKey="aed" fill={C.yellow} fillOpacity={0.8} radius={[4,4,0,0]} name="AED Saved"/>
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div style={{ background:C.card, border:`1px solid ${C.border}`, borderRadius:12, padding:18, flex:1, minWidth:240 }}>
          <div style={{ fontWeight:700, fontSize:13, marginBottom:6 }}>Sustainability Impact Summary</div>
          <div style={{ display:'flex', flexDirection:'column', gap:10, marginTop:12 }}>
            {[
              ['UN SDG 6 – Clean Water', '78%', C.accent],
              ['UN SDG 13 – Climate Action', '72%', C.green],
              ['Water Reuse Rate', '34%', C.purple],
              ['Leak Response Rate', '91%', C.yellow],
              ['Campus Coverage (Monitored)', '100%', C.green],
            ].map(([l,v,c]) => (
              <div key={l}>
                <div style={{ display:'flex', justifyContent:'space-between', marginBottom:4 }}>
                  <span style={{ fontSize:11, color:C.muted }}>{l}</span>
                  <span style={{ fontSize:11, fontWeight:700, color:c }}>{v}</span>
                </div>
                <div style={{ height:5, background:'rgba(255,255,255,0.05)', borderRadius:3, overflow:'hidden' }}>
                  <div style={{ width:v, height:'100%', background:c, borderRadius:3 }}/>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <Section title="📋 Weekly Sustainability Intelligence Report" sub="AI-generated for Facilities Management & Sustainability Committee"
        action={<Btn onClick={runReport} disabled={rptLoading} color="green">{rptLoading ? '⏳ Generating...' : '📄 Generate Report'}</Btn>}>
        {!rptText && !rptLoading && (
          <div style={{ textAlign:'center', padding:'48px 20px', color:C.muted }}>
            <div style={{ fontSize:48, marginBottom:12 }}>📊</div>
            <div style={{ fontSize:14, marginBottom:8 }}>Formal AI-Drafted Report</div>
            <div style={{ fontSize:12 }}>Click "Generate Report" to create a complete weekly sustainability report including consumption analysis, anomaly summary, carbon impact, and SDG alignment metrics.</div>
          </div>
        )}
        {rptLoading && (
          <div style={{ textAlign:'center', padding:'48px 20px', color:C.green }}>
            <div style={{ fontSize:36, marginBottom:12 }}>📝</div>
            <div style={{ fontSize:14 }}>Compiling weekly data · Calculating carbon metrics · Drafting formal report...</div>
          </div>
        )}
        {rptText && !rptLoading && (
          <div style={{ background:'rgba(0,0,0,0.25)', borderRadius:10, padding:'16px 20px', whiteSpace:'pre-wrap', fontSize:12.5, lineHeight:1.8, color:C.text }}>
            {rptText}
          </div>
        )}
      </Section>
    </div>
  );

  const Chat = () => (
    <div style={{ background:C.card, border:`1px solid ${C.border}`, borderRadius:12, padding:20, display:'flex', flexDirection:'column', height:'72vh' }}>
      <div style={{ marginBottom:14 }}>
        <div style={{ fontWeight:700, fontSize:14 }}>💬 NabdFlow AI Assistant</div>
        <div style={{ color:C.muted, fontSize:11, marginTop:3 }}>Ask about leaks, anomalies, savings, predictions, zone data, or sustainability metrics</div>
      </div>

      <div style={{ display:'flex', gap:8, flexWrap:'wrap', marginBottom:12 }}>
        {["What zones have anomalies?","How much water can I save?","Explain the Admin Block leak","Predict tomorrow's demand"].map(q => (
          <button key={q} onClick={() => { setChatIn(q); }}
            style={{ background:C.aAlpha, border:`1px solid rgba(0,200,255,0.2)`, color:C.accent, borderRadius:20, padding:'4px 12px', fontSize:11, cursor:'pointer' }}>
            {q}
          </button>
        ))}
      </div>

      <div ref={chatRef} style={{ flex:1, overflowY:'auto', display:'flex', flexDirection:'column', gap:10, marginBottom:14, paddingRight:4 }}>
        {msgs.map((m,i) => (
          <div key={i} style={{ display:'flex', justifyContent:m.role==='user'?'flex-end':'flex-start' }}>
            <div style={{
              background: m.role==='user' ? C.aAlpha : 'rgba(255,255,255,0.04)',
              border: `1px solid ${m.role==='user' ? 'rgba(0,200,255,0.25)' : C.border}`,
              borderRadius: m.role==='user' ? '12px 12px 2px 12px' : '2px 12px 12px 12px',
              padding:'10px 14px', maxWidth:'82%', fontSize:12.5, lineHeight:1.65, color:C.text, whiteSpace:'pre-wrap'
            }}>
              {m.role==='assistant' && <span style={{ color:C.accent, fontWeight:700, fontSize:10, display:'block', marginBottom:5 }}>🤖 NabdFlow AI</span>}
              {m.text}
            </div>
          </div>
        ))}
        {chatLoad && (
          <div style={{ display:'flex', justifyContent:'flex-start' }}>
            <div style={{ background:'rgba(255,255,255,0.04)', border:`1px solid ${C.border}`, borderRadius:'2px 12px 12px 12px', padding:'10px 16px', color:C.muted, fontSize:12 }}>
              ⏳ Thinking...
            </div>
          </div>
        )}
      </div>

      <div style={{ display:'flex', gap:10 }}>
        <input value={chatIn} onChange={e=>setChatIn(e.target.value)} onKeyDown={e=>e.key==='Enter'&&sendChat()}
          placeholder="Ask about leaks, savings, predictions, zones..."
          style={{ flex:1, background:'rgba(255,255,255,0.04)', border:`1px solid ${C.border}`, borderRadius:8, padding:'10px 14px', color:C.text, fontSize:13, outline:'none' }}/>
        <Btn onClick={sendChat} disabled={chatLoad}>Send</Btn>
      </div>
    </div>
  );

  const activeCount = ALERTS.filter(a=>a.sev!=='resolved').length;

  // SHELL
  return (
    <div style={{ background:C.bg, color:C.text, fontFamily:"system-ui,-apple-system,sans-serif", minHeight:'100vh', display:'flex', fontSize:14 }}>
      {/* SIDEBAR */}
      <div style={{ width:210, background:C.surface, borderRight:`1px solid ${C.border}`, display:'flex', flexDirection:'column', flexShrink:0, position:'sticky', top:0, height:'100vh', overflowY:'auto' }}>
        {/* Logo */}
        <div style={{ padding:'18px 16px', borderBottom:`1px solid ${C.border}` }}>
          <div style={{ display:'flex', alignItems:'center', gap:10 }}>
            <div style={{ width:36, height:36, borderRadius:10, background:`linear-gradient(135deg,${C.accent},#0055ff)`, display:'flex', alignItems:'center', justifyContent:'center', fontSize:18, flexShrink:0 }}>💧</div>
            <div>
              <div style={{ fontWeight:900, fontSize:16, letterSpacing:0.5 }}>NabdFlow</div>
              <div style={{ color:C.muted, fontSize:9, letterSpacing:1.5, textTransform:'uppercase' }}>Water Intelligence</div>
            </div>
          </div>
          <div style={{ marginTop:10, fontSize:10, color:C.muted, letterSpacing:0.5 }}>نبض المياه الذكي · UAE Campus</div>
        </div>

        {/* Live Badge */}
        <div style={{ padding:'10px 16px', background:'rgba(0,229,160,0.05)', borderBottom:`1px solid ${C.border}` }}>
          <div style={{ display:'flex', alignItems:'center', gap:7 }}>
            <span style={{ display:'inline-block', width:7, height:7, borderRadius:'50%', background:C.green, boxShadow:`0 0 8px ${C.green}` }}/>
            <span style={{ fontSize:11, color:C.green, fontWeight:700 }}>LIVE</span>
            <span style={{ fontSize:11, color:C.muted }}>{live.toFixed(1)} L/min</span>
          </div>
        </div>

        {/* Nav */}
        <nav style={{ padding:'10px 8px', flex:1 }}>
          {NAV.map(n => (
            <div key={n.id} onClick={() => setTab(n.id)}
              style={{ display:'flex', alignItems:'center', gap:9, padding:'9px 11px', borderRadius:8, marginBottom:2, cursor:'pointer',
                background: tab===n.id ? C.aAlpha : 'transparent',
                borderLeft: `3px solid ${tab===n.id ? C.accent : 'transparent'}`,
                color: tab===n.id ? C.accent : C.muted,
                fontWeight: tab===n.id ? 600 : 400, transition:'all 0.15s' }}>
              <span style={{ fontSize:15 }}>{n.icon}</span>
              <span style={{ fontSize:12 }}>{n.label}</span>
              {n.badge && <span style={{ marginLeft:'auto', background:C.red, color:'#fff', fontSize:9, fontWeight:800, borderRadius:20, padding:'1px 6px' }}>{n.badge}</span>}
            </div>
          ))}
        </nav>

        {/* Summary */}
        <div style={{ padding:'14px 16px', borderTop:`1px solid ${C.border}` }}>
          <div style={{ color:C.muted, fontSize:9, letterSpacing:1.2, textTransform:'uppercase', marginBottom:9 }}>Campus Status</div>
          {[['Monitored Zones','8',C.text],['Active Anomalies','3',C.red],['Eff. Score','78/100',C.green],['Saved Today','847 AED',C.yellow]].map(([l,v,c]) => (
            <div key={l} style={{ display:'flex', justifyContent:'space-between', fontSize:11, marginBottom:5 }}>
              <span style={{ color:C.muted }}>{l}</span>
              <span style={{ fontWeight:700, color:c }}>{v}</span>
            </div>
          ))}
        </div>
      </div>

      {/* MAIN */}
      <div style={{ flex:1, overflowY:'auto', padding:22 }}>
        {/* Header */}
        <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:20, flexWrap:'wrap', gap:10 }}>
          <div>
            <h1 style={{ margin:0, fontWeight:800, fontSize:18 }}>
              {{ dashboard:'📊 Overview Dashboard', zones:'🗺️ Zone Intelligence', alerts:'🚨 Anomaly & Alert Center', ai:'🤖 AI Insights Engine', sustainability:'🌿 Sustainability Hub', chat:'💬 AI Chat Assistant' }[tab]}
            </h1>
            <div style={{ color:C.muted, fontSize:11, marginTop:4 }}>
              University Campus · NabdFlow AI · {new Date().toLocaleDateString('en-AE',{ weekday:'long', year:'numeric', month:'long', day:'numeric' })}
            </div>
          </div>
          <div style={{ display:'flex', gap:8 }}>
            {activeCount>0 && tab!=='alerts' && (
              <button onClick={()=>setTab('alerts')}
                style={{ background:C.rAlpha, border:`1px solid ${C.red}`, color:C.red, borderRadius:8, padding:'7px 14px', fontSize:11, fontWeight:700, cursor:'pointer' }}>
                🚨 {activeCount} Alerts
              </button>
            )}
            <button onClick={runInsights}
              style={{ background:C.aAlpha, border:`1px solid ${C.accent}`, color:C.accent, borderRadius:8, padding:'7px 14px', fontSize:11, fontWeight:700, cursor:'pointer' }}>
              ✨ AI Analysis
            </button>
          </div>
        </div>

        {tab==='dashboard'      && <Dashboard/>}
        {tab==='zones'          && <Zones/>}
        {tab==='alerts'         && <Alerts/>}
        {tab==='ai'             && <AIView/>}
        {tab==='sustainability' && <Sustainability/>}
        {tab==='chat'           && <Chat/>}
      </div>
    </div>
  );
}
