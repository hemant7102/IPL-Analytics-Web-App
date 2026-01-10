import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

API = "http://127.0.0.1:5000"

st.set_page_config(
    page_title="IPL Analytics Dashboard",
    layout="wide"
)

st.title("IPL Analytics Dashboard")

@st.cache_data
def load_data():
    teams = requests.get(f"{API}/api/teams").json()["teams"]
    players = requests.get(f"{API}/api/players").json()
    seasons = ["all"] + requests.get(f"{API}/api/seasons").json()["seasons"]
    return teams, players, seasons


def download_csv(df, filename):
    csv = df.to_csv().encode("utf-8")
    st.download_button(
        "Download CSV",
        csv,
        filename,
        "text/csv"
    )


teams, players, seasons = load_data()

feature = st.sidebar.selectbox(
    "Select Analysis",
    [
        "Team Record",
        "Team vs Team",
        "Batting Record",
        "Bowling Record",
        "Player vs Player"
    ]
)

season = st.sidebar.selectbox("Season", seasons)


# Team Record
if feature == "Team Record":
    team = st.selectbox("Select Team", teams)

    data = requests.get(
        f"{API}/api/team-record",
        params={"team": team, "season": season}
    ).json()

    t = data[team]
    o = t["overall"]
    vs = pd.DataFrame.from_dict(t["against"], orient="index")

    tab1, tab2, tab3 = st.tabs(["Overview", "Charts", "Table"])

    with tab1:
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Matches", o["matchesplayed"])
        c2.metric("Wins", o["won"])
        c3.metric("Losses", o["loss"])
        c4.metric("No Result", o["noResult"])
        c5.metric("Titles", o["title"])

    with tab2:
        st.subheader("Match Outcome Distribution")
        outcome_df = pd.DataFrame({
            "Result": ["Wins", "Losses", "No Result"],
            "Count": [o["won"], o["loss"], o["noResult"]]
        }).set_index("Result")
        st.bar_chart(outcome_df)

        st.subheader("Wins vs Opponents")
        st.bar_chart(vs["won"])

    with tab3:
        st.dataframe(vs, use_container_width=True)
        download_csv(vs, f"{team}_team_record_{season}.csv")


# Team VS Team
elif feature == "Team vs Team":
    c1, c2 = st.columns(2)
    team1 = c1.selectbox("Team 1", teams)
    team2 = c2.selectbox("Team 2", teams)

    if team1 != team2:
        data = requests.get(
            f"{API}/api/teamvteam",
            params={"team1": team1, "team2": team2, "season": season}
        ).json()

        tab1, tab2 = st.tabs(["Overview", "Charts"])

        with tab1:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Matches", data["total_matches"])
            m2.metric(team1, data[team1])
            m3.metric(team2, data[team2])
            m4.metric("Draw / NR", data["draws"])

        with tab2:
            st.subheader("Head-to-Head Wins")
            st.bar_chart(
                pd.DataFrame(
                    {"Wins": [data[team1], data[team2]]},
                    index=[team1, team2]
                )
            )

            fig, ax = plt.subplots()
            ax.pie(
                [data[team1], data[team2]],
                labels=[team1, team2],
                autopct="%1.1f%%",
                startangle=90
            )
            ax.axis("equal")
            st.pyplot(fig)


# Batting Record
elif feature == "Batting Record":
    batsman = st.selectbox("Select Batsman", players["batters"])

    data = requests.get(
        f"{API}/api/batting-record",
        params={"batsman": batsman, "season": season}
    ).json()

    p = data[batsman]
    o = p["all"]
    vs = pd.DataFrame.from_dict(p["against"], orient="index")

    tab1, tab2, tab3 = st.tabs(["Overview", "Charts", "Table"])

    with tab1:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Runs", o["runs"])
        c2.metric("Average", o["avg"])
        c3.metric("Strike Rate", o["strikeRate"])
        c4.metric("Innings", o["innings"])

    with tab2:
        st.subheader("Runs vs Teams")
        st.bar_chart(vs["runs"])

        st.subheader("Average vs Teams")
        st.line_chart(vs["avg"])

        st.subheader("Strike Rate vs Teams")
        st.line_chart(vs["strikeRate"])

    with tab3:
        st.dataframe(vs, use_container_width=True)
        download_csv(vs, f"{batsman}_batting_vs_teams_{season}.csv")


# Bowling Record
elif feature == "Bowling Record":
    bowler = st.selectbox("Select Bowler", players["bowlers"])

    data = requests.get(
        f"{API}/api/bowling-record",
        params={"bowler": bowler, "season": season}
    ).json()

    p = data[bowler]
    o = p["all"]
    vs = pd.DataFrame.from_dict(p["against"], orient="index")

    tab1, tab2, tab3 = st.tabs(["Overview", "Charts", "Table"])

    with tab1:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Wickets", o["wickets"])
        c2.metric("Economy", o["economy"])
        c3.metric("Average", o["avg"])
        c4.metric("Strike Rate", o["strikeRate"])

    with tab2:
        st.subheader("Wickets vs Teams")
        st.bar_chart(vs["wickets"])

        st.subheader("Economy vs Teams")
        st.line_chart(vs["economy"])

        fig, ax = plt.subplots()
        ax.scatter(vs["economy"], vs["wickets"])
        ax.set_xlabel("Economy")
        ax.set_ylabel("Wickets")
        ax.set_title("Economy vs Wickets")
        st.pyplot(fig)
        
    with tab3:
        st.dataframe(vs, use_container_width=True)
        download_csv(vs, f"{bowler}_bowling_vs_teams_{season}.csv")


# Player VS Player Comparison
elif feature == "Player vs Player":

    compare_type = st.radio(
        "Comparison Type",
        ["Batting", "Bowling"],
        horizontal=True
    )

    c1, c2 = st.columns(2)

    if compare_type == "Batting":
        p1 = c1.selectbox("Player 1", players["batters"])
        p2 = c2.selectbox("Player 2", players["batters"])

        d1 = requests.get(
            f"{API}/api/batting-record",
            params={"batsman": p1, "season": season}
        ).json()[p1]["all"]

        d2 = requests.get(
            f"{API}/api/batting-record",
            params={"batsman": p2, "season": season}
        ).json()[p2]["all"]

        df = pd.DataFrame({p1: d1, p2: d2})

        st.subheader("Batting Comparison")
        st.dataframe(df, use_container_width=True)

        st.subheader("Runs Comparison")
        st.bar_chart(df.loc[["runs"]].T)

        st.subheader("Average Comparison")
        st.bar_chart(df.loc[["avg"]].T)

    else:
        p1 = c1.selectbox("Bowler 1", players["bowlers"])
        p2 = c2.selectbox("Bowler 2", players["bowlers"])

        d1 = requests.get(
            f"{API}/api/bowling-record",
            params={"bowler": p1, "season": season}
        ).json()[p1]["all"]

        d2 = requests.get(
            f"{API}/api/bowling-record",
            params={"bowler": p2, "season": season}
        ).json()[p2]["all"]

        df = pd.DataFrame({p1: d1, p2: d2})

        st.subheader("Bowling Comparison")
        st.dataframe(df, use_container_width=True)

        st.subheader("Wickets Comparison")
        st.bar_chart(df.loc[["wickets"]].T)

        st.subheader("Economy Comparison")
        st.bar_chart(df.loc[["economy"]].T)
