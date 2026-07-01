import streamlit as st
import requests
import json
import os
import plotly.graph_objects as go

API_BASE = os.environ.get("MOMENTUMLENS_API_URL", "http://localhost:8000")
SAMPLE_MATCH_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample", "sample_match.json")

st.set_page_config(page_title="Dashboard — MomentumLens", layout="wide")
st.title("📊 Match Dashboard")

with st.sidebar:
    st.header("Load Match")

    load_method = st.radio("Data Source", ["Sample Match", "Upload JSON", "Manual Entry"], index=0)

    if load_method == "Sample Match":
        st.caption("Load the bundled sample match (FC Momentum vs United FC) with all events.")
        if st.button("🚀 Load Sample Match", use_container_width=True):
            try:
                with open(SAMPLE_MATCH_PATH) as f:
                    sample_data = json.load(f)

                with st.spinner("Loading match with events..."):
                    r = requests.post(f"{API_BASE}/matches/load", json=sample_data)
                    if r.status_code == 200:
                        match_data = r.json()
                        st.session_state["match_id"] = sample_data["match_id"]
                        st.session_state["home_team"] = sample_data["home_team"]
                        st.session_state["away_team"] = sample_data["away_team"]
                        st.success(f"Match loaded: {sample_data['home_team']} vs {sample_data['away_team']}")
                    else:
                        st.error(f"Load failed: {r.text}")
                        st.stop()

                with st.spinner("Analyzing momentum..."):
                    r = requests.post(f"{API_BASE}/matches/{sample_data['match_id']}/analyze")
                    if r.status_code == 200:
                        data = r.json()
                        st.session_state["analysis"] = data
                        st.success(f"Found {len(data['turning_points'])} turning points.")
                    else:
                        st.error(f"Analysis failed: {r.text}")
            except FileNotFoundError:
                st.error(f"Sample file not found at: {SAMPLE_MATCH_PATH}")

    elif load_method == "Upload JSON":
        st.caption("Upload a match JSON file with events.")
        uploaded = st.file_uploader("Choose a match JSON file", type=["json"])
        if uploaded and st.button("📤 Load & Analyze", use_container_width=True):
            try:
                match_data = json.loads(uploaded.read())
            except json.JSONDecodeError:
                st.error("Invalid JSON file.")
                st.stop()

            with st.spinner("Loading match with events..."):
                r = requests.post(f"{API_BASE}/matches/load", json=match_data)
                if r.status_code == 200:
                    st.session_state["match_id"] = match_data["match_id"]
                    st.session_state["home_team"] = match_data["home_team"]
                    st.session_state["away_team"] = match_data["away_team"]
                    st.success(f"Match loaded: {match_data['home_team']} vs {match_data['away_team']}")
                else:
                    st.error(f"Load failed: {r.text}")
                    st.stop()

            with st.spinner("Analyzing momentum..."):
                r = requests.post(f"{API_BASE}/matches/{match_data['match_id']}/analyze")
                if r.status_code == 200:
                    data = r.json()
                    st.session_state["analysis"] = data
                    st.success(f"Found {len(data['turning_points'])} turning points.")
                else:
                    st.error(f"Analysis failed: {r.text}")

    else:  # Manual Entry
        st.caption("Manually enter match details (no events — for testing only).")
        match_id = st.text_input("Match ID", value="match_001")
        home_team = st.text_input("Home Team", value="Team A")
        away_team = st.text_input("Away Team", value="Team B")
        date = st.text_input("Date (optional)")

        if st.button("Load & Analyze"):
            with st.spinner("Loading match..."):
                r = requests.post(f"{API_BASE}/matches/load", json={
                    "match_id": match_id,
                    "home_team": home_team,
                    "away_team": away_team,
                    "date": date or None,
                })
                if r.status_code == 200:
                    st.session_state["match_id"] = match_id
                    st.session_state["home_team"] = home_team
                    st.session_state["away_team"] = away_team
                    st.success("Match loaded.")
                else:
                    st.error(f"Load failed: {r.text}")

            with st.spinner("Analyzing momentum..."):
                r = requests.post(f"{API_BASE}/matches/{match_id}/analyze")
                if r.status_code == 200:
                    data = r.json()
                    st.session_state["analysis"] = data
                    st.success(f"Found {len(data['turning_points'])} turning points.")
                else:
                    st.error(f"Analysis failed: {r.text}")

# --- Main Dashboard Area ---

analysis = st.session_state.get("analysis")
if not analysis:
    st.info("👈 Load and analyze a match using the sidebar to see the dashboard.")
    st.stop()

tps = analysis["turning_points"]
home = st.session_state.get("home_team", "Home")
away = st.session_state.get("away_team", "Away")
match_id = st.session_state.get("match_id", "")

# Match header
st.markdown(f"### ⚽ {home} vs {away}")
if match_id:
    st.caption(f"Match ID: {match_id}")

# Momentum timeline chart
minutes = [tp["minute"] for tp in tps]
deltas = [tp["momentum_delta"] for tp in tps]
colors = ["#2196F3" if tp["direction"] == "home" else "#F44336" for tp in tps]

fig = go.Figure()
fig.add_trace(go.Bar(
    x=minutes, y=deltas, marker_color=colors,
    name="Momentum Delta",
    hovertemplate="Minute %{x}<br>Delta: %{y:.3f}<extra></extra>",
))
fig.add_hline(y=0, line_dash="dash", line_color="gray")
fig.update_layout(
    title=f"Momentum Shifts: {home} (blue ▲) vs {away} (red ▼)",
    xaxis_title="Minute",
    yaxis_title="Momentum Delta",
    height=400,
)
st.plotly_chart(fig, use_container_width=True)

# Turning point details + explanation
st.subheader("Turning Points")
for i, tp in enumerate(tps):
    direction_team = home if tp["direction"] == "home" else away
    with st.expander(f"⏱️ Minute {tp['minute']} — shift toward {direction_team} (confidence: {tp['confidence']:.0%})"):
        causes = analysis["cause_rankings"][i]
        if causes:
            st.markdown("**Top Causes:**")
            for c in causes[:3]:
                st.markdown(f"- **{c['cause'].replace('_', ' ').title()}** (score: {c['score']:.2f})")
                for ev in c["evidence"][:2]:
                    st.caption(ev)

        if st.button(f"🤖 Generate AI Explanation", key=f"exp_{i}"):
            with st.spinner("Asking IBM Granite..."):
                r = requests.post(f"{API_BASE}/matches/{match_id}/explain/{i}")
                if r.status_code == 200:
                    st.markdown(r.json()["explanation"])
                elif r.status_code == 503:
                    st.warning("⚠️ IBM Granite is not configured. Set WatsonX credentials in .env to enable AI explanations.")
                else:
                    st.error(r.text)
