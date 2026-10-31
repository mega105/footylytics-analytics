
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

px.defaults.template = "plotly_dark"


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Footylytics",
    page_icon="⚽",
    layout="wide"
)

DATA_PATH = Path(__file__).parent / "data" / "E0.csv"


# ==========================================
# CUSTOM aSTYLE
# ==========================================

st.markdown("""
<style>
    :root {
        --ink: #e8f1ec;
        --muted: #91a59a;
        --line: rgba(165, 205, 179, 0.13);
    }

    .stApp {
        background:
            radial-gradient(ellipse at 12% 0%, rgba(32, 99, 67, 0.19), transparent 34%),
            #0b1411;
        color: var(--ink);
    }

    .block-container {
        max-width: 1500px;
        padding-top: 1.8rem;
        padding-bottom: 3rem;
    }

    [data-testid="stSidebar"] {
        background: #101b17;
        border-right: 1px solid var(--line);
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stCaptionContainer"] {
        color: var(--muted);
    }

    h1, h2, h3 {
        letter-spacing: -0.035em;
    }

    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #182a22, #111d19);
        border: 1px solid var(--line);
        padding: 18px 20px;
        border-radius: 16px;
        box-shadow: 0 8px 26px rgba(0, 0, 0, 0.14);
        min-height: 112px;
    }

    [data-testid="stMetricLabel"] {
        color: #a4b8ac;
    }

    [data-testid="stMetricValue"] {
        color: #f3fff7;
        font-weight: 700;
    }

    div[data-testid="stPlotlyChart"] {
        background: linear-gradient(145deg, rgba(23, 39, 33, 0.86), rgba(17, 29, 25, 0.86));
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 8px;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid var(--line);
        border-radius: 14px;
        overflow: hidden;
    }

    .hero {
        position: relative;
        overflow: hidden;
        padding: 2rem 2.2rem;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(118, 224, 159, 0.22);
        border-radius: 22px;
        background:
            radial-gradient(circle at 88% 40%, rgba(86, 218, 139, 0.2), transparent 22%),
            linear-gradient(115deg, #18372a 0%, #14251e 58%, #101b17 100%);
    }

    .hero-kicker {
        color: #87e9aa;
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.16em;
        text-transform: uppercase;
    }

    .hero-title {
        margin: 0.5rem 0 0.25rem;
        color: #f3fff7;
        font-size: clamp(2.1rem, 5vw, 3.2rem);
        font-weight: 800;
        letter-spacing: -0.06em;
        line-height: 1;
    }

    .hero-copy {
        margin: 0.7rem 0 0;
        color: #b6c9bd;
        font-size: 1rem;
    }

    .section-note {
        margin-top: -0.55rem;
        margin-bottom: 1.1rem;
        color: var(--muted);
        font-size: 0.92rem;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# LOAD DATA
# ==========================================

@st.cache_data
def load_data():

    df = pd.read_csv(DATA_PATH)

    required_columns = [
        "Date", "HomeTeam", "AwayTeam",
        "FTHG", "FTAG"
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing columns: {missing}"
        )

    df = df.dropna(
        subset=["HomeTeam", "AwayTeam", "FTHG", "FTAG"]
    ).copy()

    df["Date"] = pd.to_datetime(
        df["Date"],
        dayfirst=True,
        errors="coerce"
    )

    df["FTHG"] = pd.to_numeric(
        df["FTHG"], errors="coerce"
    )

    df["FTAG"] = pd.to_numeric(
        df["FTAG"], errors="coerce"
    )

    df = df.dropna(
        subset=["FTHG", "FTAG"]
    )

    df["FTHG"] = df["FTHG"].astype(int)
    df["FTAG"] = df["FTAG"].astype(int)

    # Calculate match results
    df["FTR"] = df.apply(
        lambda x:
        "H" if x["FTHG"] > x["FTAG"]
        else "A" if x["FTHG"] < x["FTAG"]
        else "D",
        axis=1
    )

    return df.sort_values("Date")


# ==========================================
# LEAGUE TABLE CALCULATION
# ==========================================

def calculate_standings(df):

    teams = sorted(
        set(df["HomeTeam"]) |
        set(df["AwayTeam"])
    )

    standings = []

    for team in teams:

        home = df[df["HomeTeam"] == team]
        away = df[df["AwayTeam"] == team]

        played = len(home) + len(away)

        wins = (
            (home["FTR"] == "H").sum() +
            (away["FTR"] == "A").sum()
        )

        draws = (
            (home["FTR"] == "D").sum() +
            (away["FTR"] == "D").sum()
        )

        losses = played - wins - draws

        goals_for = (
            home["FTHG"].sum() +
            away["FTAG"].sum()
        )

        goals_against = (
            home["FTAG"].sum() +
            away["FTHG"].sum()
        )

        standings.append({

            "Team": team,
            "P": played,
            "W": int(wins),
            "D": int(draws),
            "L": int(losses),

            "GF": int(goals_for),
            "GA": int(goals_against),

            "GD": int(goals_for - goals_against),

            "Pts": int(wins * 3 + draws),

            "Home Pts": int(
                (home["FTR"] == "H").sum() * 3 +
                (home["FTR"] == "D").sum()
            ),

            "Away Pts": int(
                (away["FTR"] == "A").sum() * 3 +
                (away["FTR"] == "D").sum()
            )

        })

    result = pd.DataFrame(standings)

    return result.sort_values(
        ["Pts", "GD", "GF"],
        ascending=False
    ).reset_index(drop=True)


# ==========================================
# APPLICATION HEADER
# ==========================================

st.markdown("""
<div class="hero">
    <div class="hero-kicker">English Premier League &nbsp;·&nbsp; 2024/25</div>
    <div class="hero-title">Footylytics <span aria-hidden="true">⚽</span></div>
    <p class="hero-copy">The story behind every goal, point, and team performance throughout the season.</p>
</div>
""", unsafe_allow_html=True)

st.divider()


# ==========================================
# CHECK DATASET
# ==========================================

if not DATA_PATH.exists():

    st.error(
        "Dataset not found. Please place E0.csv "
        "inside the data folder."
    )

    st.stop()


try:

    df = load_data()
    standings = calculate_standings(df)

except Exception as error:

    st.error(f"Unable to load dataset: {error}")
    st.stop()


if df.empty:

    st.error("No valid match records found.")
    st.stop()


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.markdown("## ⚽ Footylytics")
    st.caption("Premier League analytics hub")
    st.divider()

    selected_team = st.selectbox(
        "Explore team performance",
        ["All Teams"] + standings["Team"].tolist()
    )

    st.divider()

    st.caption("DATA SUMMARY")

    st.write(f"⚽ {len(df)} matches")

    st.write(f"🏟️ {len(standings)} teams")

    st.caption(
        f"Period: {df['Date'].min():%d %b %Y} – "
        f"{df['Date'].max():%d %b %Y}"
    )


# ==========================================
# LEAGUE OVERVIEW
# ==========================================

st.header("Season Overview")
st.markdown(
    '<p class="section-note">A snapshot of the key numbers from every match.</p>',
    unsafe_allow_html=True
)

total_matches = len(df)

total_goals = int(
    df["FTHG"].sum() + df["FTAG"].sum()
)

home_wins = int(
    (df["FTR"] == "H").sum()
)

draws = int(
    (df["FTR"] == "D").sum()
)

away_wins = int(
    (df["FTR"] == "A").sum()
)

goals_per_match = total_goals / total_matches

col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric("Matches", f"{total_matches:,}")
col2.metric("Total goals", f"{total_goals:,}")
col3.metric("Goals / match", f"{goals_per_match:.2f}")
col4.metric("Home wins", f"{home_wins}", f"{home_wins / total_matches:.0%}")
col5.metric("Draws", f"{draws}", f"{draws / total_matches:.0%}")
col6.metric("Away wins", f"{away_wins}", f"{away_wins / total_matches:.0%}")

st.subheader("The season at a glance")
trend_col, result_col = st.columns([1.55, 1])

monthly = (
    df.assign(Month=df["Date"].dt.to_period("M").dt.to_timestamp())
    .groupby("Month", as_index=False)
    .agg(Goals=("FTHG", "sum"), Matches=("FTHG", "size"))
)
monthly["Goals per match"] = monthly["Goals"] / monthly["Matches"]

with trend_col:
    trend_fig = px.area(
        monthly,
        x="Month",
        y="Goals",
        markers=True,
        title="Goals scored by month",
        color_discrete_sequence=["#61e294"],
        hover_data={"Matches": True, "Goals per match": ":.2f"}
    )
    trend_fig.update_traces(
        fillcolor="rgba(97, 226, 148, 0.12)",
        line={"width": 3}
    )
    trend_fig.update_layout(height=340, yaxis_title="Goals", xaxis_title="")
    st.plotly_chart(
        trend_fig,
        use_container_width=True,
        config={"displayModeBar": False}
    )

with result_col:
    result_data = pd.DataFrame({
        "Result": ["Home win", "Draw", "Away win"],
        "Matches": [home_wins, draws, away_wins]
    })
    result_fig = px.pie(
        result_data,
        names="Result",
        values="Matches",
        hole=0.68,
        title="Match result distribution",
        color="Result",
        color_discrete_map={
            "Home win": "#61e294",
            "Draw": "#e9bd67",
            "Away win": "#6eb8ee"
        }
    )
    result_fig.update_traces(
        textposition="inside",
        textinfo="percent",
        marker={"line": {"color": "#111d19", "width": 3}}
    )
    result_fig.update_layout(
        height=340,
        legend_title="",
        margin={"t": 55, "b": 10, "l": 10, "r": 10}
    )
    st.plotly_chart(
        result_fig,
        use_container_width=True,
        config={"displayModeBar": False}
    )


# ==========================================
# LEAGUE STANDINGS
# ==========================================

st.divider()

st.header("League Standings")
st.markdown(
    '<p class="section-note">Ranked by points, goal difference, and then goals scored.</p>',
    unsafe_allow_html=True
)

table = standings[
    ["Team", "P", "W", "D", "L",
     "GF", "GA", "GD", "Pts"]
].copy()

table.insert(
    0,
    "Position",
    range(1, len(table) + 1)
)
table = table.rename(columns={
    "P": "Played",
    "W": "Won",
    "D": "Drawn",
    "L": "Lost",
    "GF": "Goals For",
    "GA": "Goals Against",
    "GD": "Goal Difference",
    "Pts": "Points"
})

st.dataframe(
    table,
    hide_index=True,
    use_container_width=True,
    height=590
)


# ==========================================
# GOALS ANALYSIS
# ==========================================

st.divider()

st.header("Goal Analysis")
st.markdown(
    '<p class="section-note">Compare each team’s attacking output and defensive strength.</p>',
    unsafe_allow_html=True
)

goal_data = standings[
    ["Team", "GF", "GA"]
].rename(columns={
    "GF": "Goals For",
    "GA": "Goals Against"
}).melt(
    id_vars="Team",
    var_name="Metric",
    value_name="Goals"
)

fig = px.bar(
    goal_data,
    x="Goals",
    y="Team",
    color="Metric",
    orientation="h",
    barmode="group",
    title="Goals scored vs. goals conceded",
    color_discrete_sequence=["#61e294", "#f08372"]
)

fig.update_layout(
    height=650,
    yaxis_title="",
    legend_title="",
    xaxis_title="Goals"
)
fig.update_yaxes(categoryorder="total ascending")

st.plotly_chart(
    fig,
    use_container_width=True,
    config={"displayModeBar": False}
)

st.subheader("Points and goal difference")
scatter_fig = px.scatter(
    standings,
    x="GD",
    y="Pts",
    size="GF",
    color="Pts",
    hover_name="Team",
    hover_data={"GF": True, "GA": True, "W": True, "GD": True, "Pts": False},
    color_continuous_scale=["#315844", "#61e294"],
    title="Team performance map"
)
scatter_fig.update_traces(
    marker={"line": {"color": "#d9f7e3", "width": 1}, "opacity": 0.88}
)
scatter_fig.update_layout(
    height=480,
    xaxis_title="Goal difference",
    yaxis_title="Points",
    coloraxis_showscale=False
)
st.plotly_chart(
    scatter_fig,
    use_container_width=True,
    config={"displayModeBar": False}
)


# ==========================================
# TEAM PERFORMANCE
# ==========================================

st.divider()

st.header("Explore a Team")
st.markdown(
    '<p class="section-note">Review match results, goal trends, and consistency for your selected team.</p>',
    unsafe_allow_html=True
)

if selected_team == "All Teams":

    st.info(
        "Select a team in the sidebar to explore its performance."
    )

else:

    team_data = standings[
        standings["Team"] == selected_team
    ].iloc[0]

    team_matches = df[
        (df["HomeTeam"] == selected_team) |
        (df["AwayTeam"] == selected_team)
    ].copy()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Points", int(team_data["Pts"]))

    c2.metric(
        "Wins",
        int(team_data["W"])
    )

    c3.metric(
        "Goals scored",
        int(team_data["GF"])
    )

    c4.metric(
        "Goals conceded",
        int(team_data["GA"])
    )

    # Home and away analysis

    home = team_matches[
        team_matches["HomeTeam"] == selected_team
    ]

    away = team_matches[
        team_matches["AwayTeam"] == selected_team
    ]

    team_matches["Venue"] = team_matches["HomeTeam"].eq(selected_team).map(
        {True: "Home", False: "Away"}
    )
    team_matches["Opponent"] = team_matches.apply(
        lambda match: (
            match["AwayTeam"]
            if match["HomeTeam"] == selected_team
            else match["HomeTeam"]
        ),
        axis=1
    )
    team_matches["Team goals"] = team_matches.apply(
        lambda match: (
            match["FTHG"]
            if match["HomeTeam"] == selected_team
            else match["FTAG"]
        ),
        axis=1
    )
    team_matches["Opponent goals"] = team_matches.apply(
        lambda match: (
            match["FTAG"]
            if match["HomeTeam"] == selected_team
            else match["FTHG"]
        ),
        axis=1
    )
    team_matches["Result"] = team_matches.apply(
        lambda match: (
            "Win"
            if match["Team goals"] > match["Opponent goals"]
            else "Loss"
            if match["Team goals"] < match["Opponent goals"]
            else "Draw"
        ),
        axis=1
    )

    form_col, venue_col = st.columns([1.5, 1])
    with form_col:
        form_fig = px.line(
            team_matches,
            x="Date",
            y="Team goals",
            markers=True,
            color="Venue",
            color_discrete_map={"Home": "#61e294", "Away": "#6eb8ee"},
            hover_data=["Opponent", "Opponent goals", "Result"],
            title=f"{selected_team} goal trend"
        )
        form_fig.add_scatter(
            x=team_matches["Date"],
            y=team_matches["Opponent goals"],
            mode="lines+markers",
            name="Opponent goals",
            line={"color": "#f08372", "dash": "dot"},
            marker={"size": 6},
            customdata=team_matches[["Opponent", "Result"]].to_numpy(),
            hovertemplate=(
                "Date: %{x|%d %b %Y}<br>Opponent goals: %{y}"
                "<br>Opponent: %{customdata[0]}<br>Result: %{customdata[1]}"
                "<extra></extra>"
            )
        )
        form_fig.update_layout(height=390, xaxis_title="", yaxis_title="Goals")
        st.plotly_chart(
            form_fig,
            use_container_width=True,
            config={"displayModeBar": False}
        )

    with venue_col:
        result_counts = (
            team_matches["Result"]
            .value_counts()
            .reindex(["Win", "Draw", "Loss"], fill_value=0)
            .rename_axis("Result")
            .reset_index(name="Matches")
        )
        team_result_fig = px.pie(
            result_counts,
            names="Result",
            values="Matches",
            hole=0.66,
            title="Results breakdown"
        )
        team_result_fig.update_traces(
            textposition="inside",
            textinfo="label+value",
            marker={
                "colors": ["#61e294", "#e9bd67", "#f08372"],
                "line": {"color": "#111d19", "width": 3}
            }
        )
        team_result_fig.update_layout(
            height=390,
            showlegend=False,
            margin={"t": 55, "b": 10, "l": 10, "r": 10}
        )
        st.plotly_chart(
            team_result_fig,
            use_container_width=True,
            config={"displayModeBar": False}
        )

    home_points = (
        (home["FTR"] == "H").sum() * 3 +
        (home["FTR"] == "D").sum()
    )

    away_points = (
        (away["FTR"] == "A").sum() * 3 +
        (away["FTR"] == "D").sum()
    )

    venue_data = pd.DataFrame({

        "Venue": ["Home", "Away"],

        "Points": [
            int(home_points),
            int(away_points)
        ]

    })

    fig2 = px.bar(
        venue_data,
        x="Venue",
        y="Points",
        color="Venue",
        title="Home vs. away points",
        color_discrete_map={"Home": "#61e294", "Away": "#6eb8ee"}
    )

    fig2.update_layout(
        height=340,
        xaxis_title="",
        yaxis_title="Points",
        showlegend=False
    )
    st.plotly_chart(
        fig2,
        use_container_width=True,
        config={"displayModeBar": False}
    )


# ==========================================
# TEAM COMPARISON
# ==========================================

st.divider()

st.header("Compare Teams")
st.markdown(
    '<p class="section-note">Choose two teams to compare their results and key statistics.</p>',
    unsafe_allow_html=True
)

teams = standings["Team"].tolist()

col1, col2 = st.columns(2)

with col1:

    team_a = st.selectbox(
        "Team A",
        teams,
        index=0
    )

with col2:

    team_b = st.selectbox(
        "Team B",
        teams,
        index=min(1, len(teams) - 1)
    )

comparison = standings[
    standings["Team"].isin([team_a, team_b])
][
    ["Team", "W", "D", "L", "GF", "GA", "GD", "Pts"]
].rename(columns={
    "W": "Wins",
    "D": "Draws",
    "L": "Losses",
    "GF": "Goals For",
    "GA": "Goals Against",
    "GD": "Goal Difference",
    "Pts": "Points"
})

st.dataframe(
    comparison,
    hide_index=True,
    use_container_width=True
)

comparison_metrics = standings[
    standings["Team"].isin([team_a, team_b])
][["Team", "W", "D", "L", "GF", "GA", "Pts"]].rename(columns={
    "W": "Wins",
    "D": "Draws",
    "L": "Losses",
    "GF": "Goals For",
    "GA": "Goals Against",
    "Pts": "Points"
}).melt(
    id_vars="Team",
    var_name="Statistic",
    value_name="Total"
)
comparison_fig = px.bar(
    comparison_metrics,
    x="Statistic",
    y="Total",
    color="Team",
    barmode="group",
    title="Statistics comparison",
    color_discrete_sequence=["#61e294", "#6eb8ee"],
    text_auto=True
)
comparison_fig.update_layout(
    height=390,
    xaxis_title="",
    yaxis_title="Total",
    legend_title=""
)
st.plotly_chart(
    comparison_fig,
    use_container_width=True,
    config={"displayModeBar": False}
)


# ==========================================
# AUTOMATED INSIGHTS
# ==========================================

st.divider()

st.header("Season Highlights")

top_attack = standings.loc[
    standings["GF"].idxmax()
]

best_defence = standings.loc[
    standings["GA"].idxmin()
]

best_home = standings.loc[
    standings["Home Pts"].idxmax()
]

best_away = standings.loc[
    standings["Away Pts"].idxmax()
]

col1, col2 = st.columns(2)

with col1:

    st.success(
        f"**Best attack**\n\n"
        f"{top_attack['Team']} scored "
        f"{int(top_attack['GF'])} goals."
    )

    st.info(
        f"**Best at home**\n\n"
        f"{best_home['Team']} earned "
        f"{int(best_home['Home Pts'])} home points."
    )

with col2:

    st.success(
        f"**Best defence**\n\n"
        f"{best_defence['Team']} conceded "
        f"{int(best_defence['GA'])} goals."
    )

    st.info(
        f"**Best away performance**\n\n"
        f"{best_away['Team']} earned "
        f"{int(best_away['Away Pts'])} away points."
    )


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "Footylytics | Football Analytics Project | "
    "Data source: Football-Data.co.uk"
)
