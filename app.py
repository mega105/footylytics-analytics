from __future__ import annotations
import base64
from pathlib import Path
from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

px.defaults.template = "plotly_dark"

# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="Footylytics | Premier League Analytics",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATA_PATH   = Path(__file__).parent / "data"   / "E0.csv"
STATIC_PATH = Path(__file__).parent / "static" / "Football Ball and Boot on the Touchline.png"


# ==========================================
# BACKGROUND IMAGE → BASE64
# ==========================================

def _b64(path: Path) -> Optional[str]:
    try:
        return base64.b64encode(path.read_bytes()).decode()
    except FileNotFoundError:
        return None

_bg = _b64(STATIC_PATH)
if _bg:
    BG_CSS = f"url('data:image/png;base64,{_bg}')"
else:
    BG_CSS = "linear-gradient(135deg, #0d2318 0%, #1a4731 50%, #0b1c14 100%)"


# ==========================================
# GLOBAL CSS — XGOAL / Glassmorphism style
# ==========================================

st.markdown(f"""
<style>
/* ── Reset & root ──────────────────────────────── */
:root {{
    --white:      #ffffff;
    --white70:    rgba(255,255,255,0.70);
    --white40:    rgba(255,255,255,0.40);
    --white12:    rgba(255,255,255,0.12);
    --white08:    rgba(255,255,255,0.08);
    --white05:    rgba(255,255,255,0.05);
    --green:      #5de890;
    --green-dim:  rgba(93,232,144,0.20);
    --gold:       #f5c842;
    --red-dim:    rgba(255,90,80,0.22);
    --blue-dim:   rgba(80,160,255,0.22);
    --glass-blur: blur(22px);
    --r-card:     20px;
    --r-pill:     999px;
}}

/* ── Full-page background ───────────────────────── */
.stApp {{
    background-image:
        linear-gradient(
            160deg,
            rgba(0,0,0,0.62) 0%,
            rgba(5,25,15,0.72) 55%,
            rgba(0,0,0,0.80) 100%
        ),
        {BG_CSS};
    background-size:       cover;
    background-position:   center top;
    background-attachment: fixed;
    color:       var(--white);
    font-family: 'Inter', 'Segoe UI', sans-serif;
}}

/* ── Remove Streamlit default white blocks ─────── */
.block-container {{
    max-width:      1560px;
    padding-top:    1.4rem;
    padding-bottom: 4rem;
    background:     transparent !important;
}}
section[data-testid="stMain"] > div,
.element-container {{
    background: transparent !important;
}}

/* ── Sidebar glass panel ───────────────────────── */
[data-testid="stSidebar"] {{
    background: rgba(8, 26, 17, 0.82) !important;
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border-right: 1px solid var(--white12);
}}
[data-testid="stSidebar"] * {{
    color: var(--white70) !important;
}}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] strong {{
    color: var(--white) !important;
}}
[data-testid="stSidebar"] [data-testid="stMetricValue"] {{
    color: var(--green) !important;
    font-size: 1.5rem !important;
    font-weight: 700 !important;
}}
[data-testid="stSidebar"] [data-testid="stMetric"] {{
    background: var(--white08) !important;
    border: 1px solid var(--white12) !important;
    border-radius: 14px !important;
    padding: 12px 16px !important;
    backdrop-filter: none !important;
    box-shadow: none !important;
}}

/* ── KPI metric cards ───────────────────────────── */
[data-testid="stMetric"] {{
    background:       var(--white08);
    backdrop-filter:  var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border:           1px solid var(--white12);
    border-radius:    var(--r-card);
    padding:          18px 22px;
    box-shadow:       0 8px 32px rgba(0,0,0,0.25);
    transition:       border-color 0.2s, transform 0.2s;
}}
[data-testid="stMetric"]:hover {{
    border-color: rgba(93,232,144,0.45);
    transform: translateY(-3px);
}}
[data-testid="stMetricLabel"] {{
    color:          var(--white40) !important;
    font-size:      0.78rem !important;
    font-weight:    600 !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}}
[data-testid="stMetricValue"] {{
    color:       var(--white) !important;
    font-size:   1.75rem !important;
    font-weight: 800 !important;
}}
[data-testid="stMetricDelta"] {{
    color: var(--green) !important;
}}

/* ── Plotly chart wrapper ───────────────────────── */
div[data-testid="stPlotlyChart"] {{
    background:      var(--white05);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border:          1px solid var(--white12);
    border-radius:   var(--r-card);
    padding:         8px;
    box-shadow:      0 8px 32px rgba(0,0,0,0.2);
}}

/* ── DataFrame ──────────────────────────────────── */
[data-testid="stDataFrame"] {{
    background:      var(--white05) !important;
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border:          1px solid var(--white12) !important;
    border-radius:   var(--r-card) !important;
    overflow:        hidden;
}}

/* ── Tabs: pill style ───────────────────────────── */
.stTabs [data-baseweb="tab-list"] {{
    gap:             6px;
    background:      rgba(0,0,0,0.25);
    backdrop-filter: blur(14px);
    border:          1px solid var(--white12);
    border-radius:   var(--r-pill);
    padding:         5px 6px;
    margin-bottom:   1.8rem;
    width:           fit-content;
}}
.stTabs [data-baseweb="tab"] {{
    height:        42px;
    background:    transparent;
    border:        none !important;
    border-radius: var(--r-pill);
    color:         var(--white40);
    font-weight:   600;
    font-size:     0.88rem;
    padding:       0 1.4rem;
    transition:    all 0.25s ease;
    white-space:   nowrap;
}}
.stTabs [data-baseweb="tab"]:hover {{
    color:      var(--white);
    background: var(--white08);
}}
.stTabs [aria-selected="true"] {{
    background:  var(--green) !important;
    color:       #0b1c14 !important;
    font-weight: 800 !important;
    box-shadow:  0 4px 18px rgba(93,232,144,0.40);
}}
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] {{
    display: none !important;
}}

/* ── Misc ───────────────────────────────────────── */
hr {{
    border-color: var(--white12) !important;
}}
[data-baseweb="select"] > div {{
    background:    rgba(10,30,18,0.70) !important;
    border-color:  var(--white12) !important;
    color:         var(--white) !important;
    border-radius: 12px !important;
}}
[data-testid="stAlert"] {{
    background:      var(--white08) !important;
    border:          1px solid var(--white12) !important;
    border-radius:   14px !important;
    color:           var(--white70) !important;
    backdrop-filter: blur(10px);
}}

/* ══ CUSTOM COMPONENTS ═══════════════════════════ */

/* Hero banner */
.hero {{
    position:        relative;
    overflow:        hidden;
    padding:         2.4rem 2.8rem;
    margin-bottom:   0.4rem;
    border:          1px solid var(--white12);
    border-radius:   26px;
    background:      rgba(0,0,0,0.32);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    box-shadow:      0 8px 40px rgba(0,0,0,0.30);
}}
.hero::before {{
    content:          '';
    position:         absolute;
    inset:            0;
    border-radius:    26px;
    background:       radial-gradient(circle at 80% 50%, rgba(93,232,144,0.12), transparent 55%);
    pointer-events:   none;
}}
.hero-badge {{
    display:        inline-block;
    padding:        5px 14px;
    border:         1px solid var(--white12);
    border-radius:  var(--r-pill);
    background:     var(--white08);
    font-size:      0.76rem;
    font-weight:    700;
    letter-spacing: 0.10em;
    text-transform: uppercase;
    color:          var(--white70);
    margin-bottom:  1.1rem;
}}
.hero-title {{
    font-size:      clamp(2.1rem, 4.5vw, 3.4rem);
    font-weight:    800;
    line-height:    1.08;
    color:          var(--white);
    letter-spacing: -0.04em;
    margin:         0 0 0.15rem;
}}
.hero-title em {{
    color:      var(--green);
    font-style: italic;
}}
.hero-copy {{
    color:     var(--white40);
    font-size: 1rem;
    margin:    0.6rem 0 0;
    max-width: 480px;
}}

/* Glass card */
.g-card {{
    background:      rgba(255,255,255,0.06);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border:          1px solid var(--white12);
    border-radius:   var(--r-card);
    padding:         1.3rem 1.5rem;
    margin-bottom:   1rem;
    transition:      border-color 0.2s, transform 0.2s;
}}
.g-card:hover {{
    border-color: rgba(93,232,144,0.42);
    transform:    translateY(-3px);
}}
.g-label {{
    font-size:      0.74rem;
    font-weight:    700;
    color:          var(--green);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom:  0.35rem;
}}
.g-value {{
    font-size:   1.45rem;
    font-weight: 800;
    color:       var(--white);
    line-height: 1.2;
}}
.g-desc {{
    color:       var(--white40);
    font-size:   0.86rem;
    margin-top:  0.3rem;
    line-height: 1.4;
}}

/* Zone pills */
.pill {{
    display:        inline-flex;
    align-items:    center;
    gap:            5px;
    padding:        4px 12px;
    border-radius:  var(--r-pill);
    font-size:      0.76rem;
    font-weight:    700;
    margin-right:   6px;
    margin-bottom:  6px;
}}
.pill-ucl {{ background: rgba(56,139,253,0.18);  color:#58a6ff; border:1px solid rgba(56,139,253,0.35); }}
.pill-uel {{ background: rgba(210,153,34,0.18);   color:#e3b341; border:1px solid rgba(210,153,34,0.35); }}
.pill-rel {{ background: rgba(248,81,73,0.18);    color:#f85149; border:1px solid rgba(248,81,73,0.35); }}

/* Team profile card */
.team-card {{
    background:      rgba(0,0,0,0.30);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border:          1px solid var(--white12);
    border-radius:   var(--r-card);
    padding:         1.6rem 2rem;
    margin-bottom:   1.4rem;
    display:         flex;
    justify-content: space-between;
    align-items:     center;
    flex-wrap:       wrap;
    gap:             1rem;
}}
.team-name {{
    font-size:      2.4rem;
    font-weight:    900;
    color:          var(--white);
    letter-spacing: -0.04em;
    line-height:    1;
}}
.team-sub  {{ color: var(--white40); font-size: 0.9rem;  margin-top: 0.4rem; }}
.team-form {{ font-size: 1.05rem; margin-top: 0.35rem; }}

/* VS tape */
.tape-wrap {{
    display:               grid;
    grid-template-columns: 1fr auto 1fr;
    gap:                   16px;
    align-items:           center;
    margin:                1.2rem 0 1.6rem;
}}
.tape-box {{
    background:      rgba(255,255,255,0.06);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border:          1px solid var(--white12);
    border-radius:   var(--r-card);
    padding:         1.6rem 1.8rem;
    text-align:      center;
}}
.tape-club {{ font-size: 1.7rem; font-weight: 900; color: var(--white); letter-spacing: -0.03em; }}
.tape-pts  {{ font-size: 0.88rem; font-weight: 600; margin-top: 4px; }}
.tape-form {{ font-size: 0.82rem; color: var(--white40); margin-top: 6px; }}
.tape-vs   {{ text-align: center; font-size: 2rem; font-weight: 900; color: var(--white40); }}

/* H2H match card */
.match-card {{
    background:      rgba(255,255,255,0.06);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border:          1px solid var(--white12);
    border-radius:   16px;
    padding:         1rem 1.5rem;
    margin-bottom:   0.75rem;
    display:         flex;
    justify-content: space-between;
    align-items:     center;
    transition:      border-color 0.2s;
}}
.match-card:hover {{ border-color: var(--green); }}
.match-date   {{ font-size: 0.78rem; color: var(--white40); margin-bottom: 4px; }}
.match-score  {{ font-size: 1.2rem; font-weight: 800; color: var(--white); }}
.match-score span {{ color: var(--green); margin: 0 8px; }}
.match-winner {{ font-size: 0.88rem; font-weight: 700; color: var(--green); }}

/* Record card */
.record-card {{
    background:      rgba(0,0,0,0.30);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border:          1px solid rgba(248,81,73,0.30);
    border-radius:   var(--r-card);
    padding:         1.4rem 1.8rem;
    margin-top:      0.75rem;
}}

/* Section labels */
.s-label {{ font-size: 0.72rem; font-weight: 700; color: var(--green); text-transform: uppercase; letter-spacing: 0.14em; margin-bottom: 0.2rem; }}
.s-head  {{ font-size: 1.5rem;  font-weight: 800; color: var(--white); margin-bottom: 0.1rem; letter-spacing: -0.02em; }}
.s-copy  {{ color: var(--white40); font-size: 0.9rem; margin-bottom: 1.2rem; }}

/* Footer */
.ft {{ text-align: center; color: var(--white40); font-size: 0.82rem; padding: 0.5rem 0 2rem; letter-spacing: 0.04em; }}
</style>
""", unsafe_allow_html=True)


# ==========================================
# DATA LOADING
# ==========================================

@st.cache_data
def load_data():
    if not DATA_PATH.exists():
        return None
    df = pd.read_csv(DATA_PATH)
    required = ["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG"]
    if not all(c in df.columns for c in required):
        return None
    df = df.dropna(subset=required).copy()
    df["Date"]       = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    df["FTHG"]       = pd.to_numeric(df["FTHG"], errors="coerce").fillna(0).astype(int)
    df["FTAG"]       = pd.to_numeric(df["FTAG"], errors="coerce").fillna(0).astype(int)
    df["TotalGoals"] = df["FTHG"] + df["FTAG"]
    df["FTR"]        = df.apply(
        lambda r: "H" if r["FTHG"] > r["FTAG"] else ("A" if r["FTHG"] < r["FTAG"] else "D"),
        axis=1
    )
    return df.sort_values("Date").reset_index(drop=True)


def calculate_standings(df):
    teams, records = sorted(set(df["HomeTeam"]) | set(df["AwayTeam"])), []
    for team in teams:
        home = df[df["HomeTeam"] == team]
        away = df[df["AwayTeam"] == team]
        played   = len(home) + len(away)
        hw       = (home["FTR"] == "H").sum()
        aw       = (away["FTR"] == "A").sum()
        wins     = hw + aw
        hd       = (home["FTR"] == "D").sum()
        ad       = (away["FTR"] == "D").sum()
        draws    = hd + ad
        losses   = played - wins - draws
        gf       = home["FTHG"].sum() + away["FTAG"].sum()
        ga       = home["FTAG"].sum() + away["FTHG"].sum()
        pts      = int(wins * 3 + draws)
        home_pts = int(hw * 3 + hd)
        away_pts = int(aw * 3 + ad)
        cs       = int((home["FTAG"] == 0).sum() + (away["FTHG"] == 0).sum())
        tm       = df[(df["HomeTeam"] == team) | (df["AwayTeam"] == team)].sort_values("Date")
        syms = []
        for _, r in tm.tail(5).iterrows():
            res = ("W" if r["FTR"] == "H" else ("D" if r["FTR"] == "D" else "L")) if r["HomeTeam"] == team \
                  else ("W" if r["FTR"] == "A" else ("D" if r["FTR"] == "D" else "L"))
            syms.append("🟢 W" if res == "W" else ("🟡 D" if res == "D" else "🔴 L"))
        records.append({
            "Team": team, "P": played,
            "W": int(wins), "D": int(draws), "L": int(losses),
            "GF": int(gf), "GA": int(ga), "GD": int(gf - ga),
            "Pts": pts, "Home Pts": home_pts, "Away Pts": away_pts,
            "CS": cs, "Form": "  ".join(syms) or "-"
        })
    st = pd.DataFrame(records).sort_values(["Pts","GD","GF"], ascending=False).reset_index(drop=True)
    st.insert(0, "Pos", range(1, len(st) + 1))
    def zone(p, n): return "🔵 UCL" if p<=4 else ("🟠 UEL" if p==5 else ("🔴 REL" if p>n-3 else "⚪ Mid"))
    st.insert(1, "Zone", st["Pos"].apply(lambda p: zone(p, len(st))))
    return st


def _fig_style(fig, h=420):
    fig.update_layout(
        height=h, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="rgba(255,255,255,0.75)", family="Inter, Segoe UI, sans-serif"),
        margin=dict(t=48, b=8, l=8, r=8),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(255,255,255,0.1)")
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.06)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.06)")
    return fig


# ==========================================
# LOAD & VALIDATE
# ==========================================

df = load_data()
if df is None or df.empty:
    st.error("⚠️ Dataset `E0.csv` not found inside `data/` folder.")
    st.stop()

standings  = calculate_standings(df)
teams_list = standings["Team"].tolist()


# ==========================================
# HERO BANNER
# ==========================================

st.markdown("""
<div class="hero">
    <div class="hero-badge">⚽ &nbsp; AQX Sports Analytics Data Bowl 4.0</div>
    <div class="hero-title">The Analytics Home of &nbsp;<em>Football Excellence</em></div>
    <p class="hero-copy">
        Deep-dive insights into every goal, table position, and team trend
        across the 2024/25 English Premier League season.
    </p>
</div>
""", unsafe_allow_html=True)


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:
    st.markdown("## ⚽ Footylytics")
    st.caption("Premier League 2024/25 · Analytics Hub")
    st.divider()
    total_g = int(df["FTHG"].sum() + df["FTAG"].sum())
    st.metric("Total Matches",   f"{len(df):,}")
    st.metric("Total Goals",     f"{total_g:,}")
    st.metric("Goals per Match", f"{df['TotalGoals'].mean():.2f}")
    st.divider()
    st.caption(f"🗓️ **Season:**  \n{df['Date'].min():%d %b %Y} → {df['Date'].max():%d %b %Y}")
    st.caption(f"🏟️ **Clubs:**  {len(teams_list)}")
    if not _bg:
        st.warning(
            "📷 Background not found.\nPlace **Football Ball and Boot on the Touchline.png** in `static/`.",
            icon="🖼️"
        )


# ==========================================
# TABS
# ==========================================

tab1, tab2, tab3, tab4 = st.tabs([
    "🏆  League Table & Trends",
    "🛡️  Team Deep Dive",
    "⚔️  Head-to-Head",
    "🌟  Season Records",
])


# ══════════════════════════════════════════
# TAB 1 — League Table & Trends
# ══════════════════════════════════════════

with tab1:
    total_matches = len(df)
    total_goals   = int(df["TotalGoals"].sum())
    home_wins     = int((df["FTR"] == "H").sum())
    draws_n       = int((df["FTR"] == "D").sum())
    away_wins     = int((df["FTR"] == "A").sum())
    gpm           = total_goals / total_matches

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Matches",     f"{total_matches}")
    k2.metric("Total Goals", f"{total_goals}")
    k3.metric("Goals/Game",  f"{gpm:.2f}")
    k4.metric("Home Wins",   f"{home_wins}", f"{home_wins/total_matches:.0%}")
    k5.metric("Draws",       f"{draws_n}",   f"{draws_n/total_matches:.0%}")
    k6.metric("Away Wins",   f"{away_wins}", f"{away_wins/total_matches:.0%}")

    st.markdown("<br>", unsafe_allow_html=True)

    tc, dc = st.columns([1.6, 1])
    with tc:
        monthly = (
            df.assign(Month=df["Date"].dt.to_period("M").dt.to_timestamp())
            .groupby("Month", as_index=False)
            .agg(Goals=("TotalGoals","sum"), Matches=("TotalGoals","size"))
        )
        monthly["GPM"] = monthly["Goals"] / monthly["Matches"]
        fig_trend = px.area(
            monthly, x="Month", y="Goals", markers=True,
            title="Goals per Month",
            color_discrete_sequence=["#5de890"],
            hover_data={"Matches": True, "GPM": ":.2f"}
        )
        fig_trend.update_traces(fillcolor="rgba(93,232,144,0.10)", line=dict(width=3))
        st.plotly_chart(_fig_style(fig_trend, 360), use_container_width=True, config={"displayModeBar": False})

    with dc:
        fig_donut = go.Figure(go.Pie(
            labels=["Home Win","Draw","Away Win"],
            values=[home_wins, draws_n, away_wins],
            hole=0.70,
            marker=dict(colors=["#5de890","#f5c842","#5aaeff"], line=dict(color="rgba(0,0,0,0)", width=0)),
            textinfo="percent+label", textposition="outside", showlegend=False
        ))
        fig_donut.update_layout(
            title="Outcome Split",
            annotations=[dict(
                text=f"<b>{total_matches}</b><br><span style='font-size:11px'>Matches</span>",
                x=0.5, y=0.5, font_size=20, font_color="#ffffff", showarrow=False
            )],
            paper_bgcolor="rgba(0,0,0,0)", font=dict(color="rgba(255,255,255,0.75)"),
            margin=dict(t=48, b=16, l=16, r=16), height=360
        )
        st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})

    st.divider()

    st.markdown("""
    <div class="s-label">Official Standings</div>
    <div class="s-head">Premier League Table 2024/25</div>
    <div style="margin: 0.5rem 0 0.9rem;">
        <span class="pill pill-ucl">● Champions League (1–4)</span>
        <span class="pill pill-uel">● Europa League (5)</span>
        <span class="pill pill-rel">● Relegation (18–20)</span>
    </div>
    """, unsafe_allow_html=True)

    tbl = standings.rename(columns={"Zone":"Status","P":"Pld","CS":"Clean Sheets","Form":"Form (oldest → latest)"})
    st.dataframe(
        tbl, hide_index=True, use_container_width=True, height=560,
        column_config={
            "Pos":    st.column_config.NumberColumn("Pos", width="small"),
            "Status": st.column_config.TextColumn("Status", width="small"),
            "Team":   st.column_config.TextColumn("Team", width="large"),
            "Pts":    st.column_config.NumberColumn("Points", width="small"),
            "Form (oldest → latest)": st.column_config.TextColumn("Form (oldest → latest)", width="large")
        }
    )

    st.divider()

    st.markdown("""
    <div class="s-label">Performance Matrix</div>
    <div class="s-head">Attack & Defensive Breakdown</div>
    <div class="s-copy">Goals scored vs conceded, and team efficiency quadrants.</div>
    """, unsafe_allow_html=True)

    gc1, gc2 = st.columns([1.05, 1.3])
    with gc1:
        gdata = standings[["Team","GF","GA"]].rename(
            columns={"GF":"Goals Scored","GA":"Goals Conceded"}
        ).melt(id_vars="Team", var_name="Metric", value_name="Goals")
        fig_bar = px.bar(
            gdata, x="Goals", y="Team", color="Metric",
            orientation="h", barmode="group",
            title="Goals Scored vs Conceded",
            color_discrete_sequence=["#5de890","#f85149"]
        )
        fig_bar.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(_fig_style(fig_bar, 620), use_container_width=True, config={"displayModeBar": False})

    with gc2:
        avg_gf, avg_ga = standings["GF"].mean(), standings["GA"].mean()
        fig_q = px.scatter(
            standings, x="GA", y="GF", size="Pts", color="Pts",
            text="Team", hover_name="Team",
            hover_data={"Pts": True, "GD": True, "W": True, "CS": True},
            color_continuous_scale=["#1a4731","#5de890"],
            title="Efficiency Quadrants"
        )
        fig_q.add_hline(y=avg_gf, line_dash="dash", line_color="rgba(255,255,255,0.20)",
                        annotation_text=f"Avg Scored ({avg_gf:.1f})",
                        annotation_font_color="rgba(255,255,255,0.45)")
        fig_q.add_vline(x=avg_ga, line_dash="dash", line_color="rgba(255,255,255,0.20)",
                        annotation_text=f"Avg Conceded ({avg_ga:.1f})",
                        annotation_font_color="rgba(255,255,255,0.45)")
        fig_q.update_traces(textposition="top center", marker=dict(line=dict(color="rgba(255,255,255,0.3)", width=1)))
        fig_q.update_layout(coloraxis_showscale=False)
        st.plotly_chart(_fig_style(fig_q, 620), use_container_width=True, config={"displayModeBar": False})


# ══════════════════════════════════════════
# TAB 2 — Team Deep Dive
# ══════════════════════════════════════════

with tab2:
    st.markdown("""
    <div class="s-label">Club Spotlight</div>
    <div class="s-head">Team Deep Dive</div>
    <div class="s-copy">Select a club to explore match-by-match performance, goal trends, and split stats.</div>
    """, unsafe_allow_html=True)

    sel = st.selectbox("Select club:", teams_list, index=0)
    row = standings[standings["Team"] == sel].iloc[0]
    tm  = df[(df["HomeTeam"] == sel) | (df["AwayTeam"] == sel)].copy()

    st.markdown(f"""
    <div class="team-card">
        <div>
            <div class="team-name">{sel}</div>
            <div class="team-sub">Ranked &nbsp;<b>#{row['Pos']}</b>&nbsp; · &nbsp;{row['Zone']}&nbsp; · &nbsp;{row['P']} matches played</div>
            <div class="team-form" style="margin-top:0.5rem;">{row['Form']}</div>
        </div>
        <div style="text-align:right;">
            <div style="font-size:3rem;font-weight:900;color:#5de890;line-height:1;">{row['Pts']}</div>
            <div style="color:rgba(255,255,255,0.4);font-size:0.82rem;letter-spacing:0.08em;text-transform:uppercase;">Points</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    win_rate = row["W"] / row["P"] * 100
    m1,m2,m3,m4,m5,m6 = st.columns(6)
    m1.metric("Wins",         f"{row['W']}")
    m2.metric("Draws",        f"{row['D']}")
    m3.metric("Losses",       f"{row['L']}")
    m4.metric("Win Rate",     f"{win_rate:.0f}%")
    m5.metric("Goals Scored", f"{row['GF']}")
    m6.metric("Clean Sheets", f"{row['CS']}")

    st.markdown("<br>", unsafe_allow_html=True)

    tm["Venue"]   = tm["HomeTeam"].eq(sel).map({True:"Home", False:"Away"})
    tm["Opponent"]= tm.apply(lambda r: r["AwayTeam"] if r["HomeTeam"]==sel else r["HomeTeam"], axis=1)
    tm["TG"]      = tm.apply(lambda r: r["FTHG"]     if r["HomeTeam"]==sel else r["FTAG"],     axis=1)
    tm["OG"]      = tm.apply(lambda r: r["FTAG"]     if r["HomeTeam"]==sel else r["FTHG"],     axis=1)
    tm["Outcome"] = tm.apply(lambda r: "Win" if r["TG"]>r["OG"] else ("Loss" if r["TG"]<r["OG"] else "Draw"), axis=1)

    lc, rc = st.columns([1.6, 1])
    with lc:
        fig_line = px.line(
            tm, x="Date", y="TG", markers=True,
            title=f"{sel} — Goals Scored vs Conceded",
            color="Venue", color_discrete_map={"Home":"#5de890","Away":"#5aaeff"},
            hover_data=["Opponent","OG","Outcome"]
        )
        fig_line.add_scatter(
            x=tm["Date"], y=tm["OG"], mode="lines+markers", name="Goals Conceded",
            line=dict(color="#f85149", dash="dot"), marker=dict(size=6),
            customdata=tm[["Opponent","Outcome"]].to_numpy(),
            hovertemplate="Date: %{x|%d %b %Y}<br>Conceded: %{y}<br>vs %{customdata[0]}<br>%{customdata[1]}<extra></extra>"
        )
        fig_line.update_layout(yaxis_title="Goals", xaxis_title="")
        st.plotly_chart(_fig_style(fig_line, 370), use_container_width=True, config={"displayModeBar": False})

    with rc:
        outs = tm["Outcome"].value_counts().reindex(["Win","Draw","Loss"], fill_value=0).reset_index()
        outs.columns = ["Outcome","Count"]
        fig_res = go.Figure(go.Pie(
            labels=outs["Outcome"], values=outs["Count"], hole=0.66,
            marker=dict(colors=["#5de890","#f5c842","#f85149"], line=dict(color="rgba(0,0,0,0)", width=0)),
            textinfo="label+value", showlegend=False
        ))
        fig_res.update_layout(
            title="Results Breakdown",
            annotations=[dict(text=f"<b>{row['P']}</b><br><span style='font-size:11px'>Games</span>",
                              x=0.5, y=0.5, font_size=18, font_color="#ffffff", showarrow=False)],
            paper_bgcolor="rgba(0,0,0,0)", font=dict(color="rgba(255,255,255,0.75)"),
            margin=dict(t=48, b=10, l=10, r=10), height=370
        )
        st.plotly_chart(fig_res, use_container_width=True, config={"displayModeBar": False})

    st.markdown("#### 🏟️ Home vs Away Breakdown")
    vdf = pd.DataFrame({
        "Venue":          ["Home","Away"],
        "Points":         [row["Home Pts"], row["Away Pts"]],
        "Goals Scored":   [tm[tm["Venue"]=="Home"]["TG"].sum(), tm[tm["Venue"]=="Away"]["TG"].sum()],
        "Goals Conceded": [tm[tm["Venue"]=="Home"]["OG"].sum(), tm[tm["Venue"]=="Away"]["OG"].sum()]
    })
    vc1, vc2 = st.columns(2)
    with vc1:
        fv1 = px.bar(vdf, x="Venue", y="Points", color="Venue", title="Points by Venue",
                     color_discrete_map={"Home":"#5de890","Away":"#5aaeff"}, text_auto=True)
        fv1.update_layout(showlegend=False, yaxis_title="Points")
        st.plotly_chart(_fig_style(fv1, 300), use_container_width=True, config={"displayModeBar": False})
    with vc2:
        fv2 = px.bar(
            vdf.melt(id_vars="Venue", value_vars=["Goals Scored","Goals Conceded"], var_name="Type", value_name="Total"),
            x="Venue", y="Total", color="Type", barmode="group", title="Goals by Venue",
            color_discrete_sequence=["#5de890","#f85149"], text_auto=True
        )
        fv2.update_layout(legend_title="")
        st.plotly_chart(_fig_style(fv2, 300), use_container_width=True, config={"displayModeBar": False})


# ══════════════════════════════════════════
# TAB 3 — Head-to-Head
# ══════════════════════════════════════════

with tab3:
    st.markdown("""
    <div class="s-label">Tale of the Tape</div>
    <div class="s-head">Head-to-Head Matchup</div>
    <div class="s-copy">Pick two clubs and compare their full-season statistics side by side.</div>
    """, unsafe_allow_html=True)

    cs1, cs2 = st.columns(2)
    with cs1:
        team_a = st.selectbox("Club A", teams_list, index=0)
    with cs2:
        team_b = st.selectbox("Club B", teams_list, index=min(1, len(teams_list)-1))

    if team_a == team_b:
        st.warning("⚠️ Please choose two different clubs.")
    else:
        ra = standings[standings["Team"] == team_a].iloc[0]
        rb = standings[standings["Team"] == team_b].iloc[0]

        st.markdown(f"""
        <div class="tape-wrap">
            <div class="tape-box" style="border-left:3px solid #5de890;">
                <div style="font-size:0.7rem;font-weight:700;color:#5de890;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:6px;">Club A</div>
                <div class="tape-club">{team_a}</div>
                <div class="tape-pts" style="color:#5de890;">Rank #{ra['Pos']} &nbsp;·&nbsp; {ra['Pts']} pts</div>
                <div class="tape-form">{ra['Form']}</div>
            </div>
            <div class="tape-vs">VS</div>
            <div class="tape-box" style="border-right:3px solid #5aaeff;">
                <div style="font-size:0.7rem;font-weight:700;color:#5aaeff;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:6px;">Club B</div>
                <div class="tape-club">{team_b}</div>
                <div class="tape-pts" style="color:#5aaeff;">Rank #{rb['Pos']} &nbsp;·&nbsp; {rb['Pts']} pts</div>
                <div class="tape-form">{rb['Form']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        metrics = [
            ("Points",         int(ra["Pts"]),       int(rb["Pts"])),
            ("Wins",           int(ra["W"]),          int(rb["W"])),
            ("Draws",          int(ra["D"]),          int(rb["D"])),
            ("Losses",         int(ra["L"]),          int(rb["L"])),
            ("Goals Scored",   int(ra["GF"]),         int(rb["GF"])),
            ("Goals Conceded", int(ra["GA"]),         int(rb["GA"])),
            ("Goal Diff.",     int(ra["GD"]),         int(rb["GD"])),
            ("Clean Sheets",   int(ra["CS"]),         int(rb["CS"])),
            ("Home Points",    int(ra["Home Pts"]),   int(rb["Home Pts"])),
            ("Away Points",    int(ra["Away Pts"]),   int(rb["Away Pts"])),
        ]
        mdf = pd.DataFrame(metrics, columns=["Metric", team_a, team_b])
        fig_tape = go.Figure()
        fig_tape.add_trace(go.Bar(y=mdf["Metric"], x=mdf[team_a], name=team_a,
                                  orientation="h", marker_color="#5de890",
                                  text=mdf[team_a], textposition="auto"))
        fig_tape.add_trace(go.Bar(y=mdf["Metric"], x=mdf[team_b], name=team_b,
                                  orientation="h", marker_color="#5aaeff",
                                  text=mdf[team_b], textposition="auto"))
        fig_tape.update_layout(
            barmode="group", yaxis=dict(autorange="reversed"),
            title=f"Statistical Comparison: {team_a} vs {team_b}",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(_fig_style(fig_tape, 480), use_container_width=True, config={"displayModeBar": False})

        st.markdown("#### 📅 This Season's Encounters")
        h2h = df[
            ((df["HomeTeam"]==team_a) & (df["AwayTeam"]==team_b)) |
            ((df["HomeTeam"]==team_b) & (df["AwayTeam"]==team_a))
        ]
        if h2h.empty:
            st.info("No head-to-head fixture between these two clubs in the current dataset.")
        else:
            for _, m in h2h.iterrows():
                wn = (f"🏆 {m['HomeTeam']} Win" if m["FTR"]=="H"
                      else (f"🏆 {m['AwayTeam']} Win" if m["FTR"]=="A" else "🤝 Draw"))
                st.markdown(f"""
                <div class="match-card">
                    <div>
                        <div class="match-date">{m['Date']:%d %b %Y} &nbsp;·&nbsp; {m['HomeTeam']} (Home)</div>
                        <div class="match-score">{m['HomeTeam']} <span>{m['FTHG']} – {m['FTAG']}</span> {m['AwayTeam']}</div>
                    </div>
                    <div class="match-winner">{wn}</div>
                </div>
                """, unsafe_allow_html=True)


# ══════════════════════════════════════════
# TAB 4 — Season Records
# ══════════════════════════════════════════

with tab4:
    st.markdown("""
    <div class="s-label">Season Accolades</div>
    <div class="s-head">Records & Highlights</div>
    <div class="s-copy">Outstanding team achievements across the 2024/25 Premier League season.</div>
    """, unsafe_allow_html=True)

    top_att  = standings.loc[standings["GF"].idxmax()]
    top_def  = standings.loc[standings["GA"].idxmin()]
    top_home = standings.loc[standings["Home Pts"].idxmax()]
    top_away = standings.loc[standings["Away Pts"].idxmax()]
    top_cs   = standings.loc[standings["CS"].idxmax()]
    df["Margin"] = (df["FTHG"] - df["FTAG"]).abs()
    thriller    = df.loc[df["TotalGoals"].idxmax()]
    biggest_win = df.loc[df["Margin"].idxmax()]

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="g-card">
            <div class="g-label">⚡ Best Attack</div>
            <div class="g-value">{top_att['Team']}</div>
            <div class="g-desc"><b>{int(top_att['GF'])} goals</b> in {int(top_att['P'])} games &nbsp;({top_att['GF']/top_att['P']:.2f}/match)</div>
        </div>
        <div class="g-card">
            <div class="g-label">🏰 Home Fortress</div>
            <div class="g-value">{top_home['Team']}</div>
            <div class="g-desc"><b>{int(top_home['Home Pts'])} home points</b> earned at home</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="g-card">
            <div class="g-label">🛡️ Iron Defence</div>
            <div class="g-value">{top_def['Team']}</div>
            <div class="g-desc">Conceded only <b>{int(top_def['GA'])} goals</b> ({top_def['GA']/top_def['P']:.2f}/match)</div>
        </div>
        <div class="g-card">
            <div class="g-label">✈️ Road Warriors</div>
            <div class="g-value">{top_away['Team']}</div>
            <div class="g-desc"><b>{int(top_away['Away Pts'])} away points</b> on the road</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="g-card">
            <div class="g-label">🧤 Clean Sheet Kings</div>
            <div class="g-value">{top_cs['Team']}</div>
            <div class="g-desc"><b>{int(top_cs['CS'])} clean sheets</b> &nbsp;({top_cs['CS']/top_cs['P']:.0%} shut-out rate)</div>
        </div>
        <div class="g-card">
            <div class="g-label">⚽ Goal Thriller</div>
            <div class="g-value">{int(thriller['TotalGoals'])} Goals</div>
            <div class="g-desc"><b>{thriller['HomeTeam']} {thriller['FTHG']}–{thriller['FTAG']} {thriller['AwayTeam']}</b> &nbsp;· {thriller['Date']:%d %b %Y}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="record-card">
        <div class="g-label">💥 Biggest Margin Victory of the Season</div>
        <div style="font-size:1.6rem;font-weight:900;color:#ffffff;margin:4px 0;">
            {biggest_win['HomeTeam']} &nbsp;
            <span style="color:#5de890;">{biggest_win['FTHG']} – {biggest_win['FTAG']}</span>
            &nbsp; {biggest_win['AwayTeam']}
            &nbsp;&nbsp;
            <span style="font-size:1rem;font-weight:600;color:#f85149;">({biggest_win['Margin']:.0f}-goal margin)</span>
        </div>
        <div class="g-desc">Played on {biggest_win['Date']:%d %b %Y}</div>
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# FOOTER
# ==========================================

st.divider()
st.markdown("""
<div class="ft">
    Footylytics &nbsp;·&nbsp; AQX Sports Analytics Data Bowl 4.0
    &nbsp;·&nbsp; Data: Football-Data.co.uk
</div>
""", unsafe_allow_html=True)