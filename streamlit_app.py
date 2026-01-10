import streamlit as st
import pandas as pd

import analytics
import ipl


st.set_page_config(page_title="IPL Analytics", layout="wide")
st.title("IPL Analytics Dashboard")


# Load basic data only once
@st.cache_data
def load_data():
    teams = ipl.teamsAPI()["teams"]
    players = analytics.getPlayers()
    seasons = ["all"] + analytics.getSeasons()["seasons"]
    return teams, players, seasons


teams, players, seasons = load_data()


feature = st.sidebar.selectbox(
    "Select Feature",
    ["Team Record", "Team vs Team", "Batting Record", "Bowling Record"]
)

season = st.sidebar.selectbox("Season", seasons)


# Team Record
if feature == "Team Record":
    team = st.selectbox("Select Team", teams)

    data = analytics.teamAPI(team, season)
    team_data = data[team]

    st.subheader("Overall Record")
    st.write(team_data["overall"])

    st.subheader("Record Against Teams")
    df = pd.DataFrame.from_dict(team_data["against"], orient="index")
    st.dataframe(df)


# Team vs Team
elif feature == "Team vs Team":
    team1 = st.selectbox("Team 1", teams)
    team2 = st.selectbox("Team 2", teams)

    if team1 != team2:
        data = ipl.teamVteamAPI(team1, team2, season)

        st.subheader("Head to Head Summary")
        st.write(data)


# Batting Record
elif feature == "Batting Record":
    batsman = st.selectbox("Select Batsman", players["batters"])

    data = analytics.batsmanAPI(batsman, season)
    batsman_data = data[batsman]

    st.subheader("Overall Batting Stats")
    st.write(batsman_data["all"])

    st.subheader("Batting Against Teams")
    df = pd.DataFrame.from_dict(batsman_data["against"], orient="index")
    st.dataframe(df)


# Bowling Record
elif feature == "Bowling Record":
    bowler = st.selectbox("Select Bowler", players["bowlers"])

    data = analytics.bowlerAPI(bowler, season)
    bowler_data = data[bowler]

    st.subheader("Overall Bowling Stats")
    st.write(bowler_data["all"])

    st.subheader("Bowling Against Teams")
    df = pd.DataFrame.from_dict(bowler_data["against"], orient="index")
    st.dataframe(df)


# Player VS Player
elif feature == "Player vs Player":

    compare_type = st.radio(
        "Comparison Type",
        ["Batting", "Bowling"]
    )

    col1, col2 = st.columns(2)

    if compare_type == "Batting":
        player1 = col1.selectbox("Player 1", players["batters"])
        player2 = col2.selectbox("Player 2", players["batters"])

        data1 = analytics.batsmanAPI(player1, season)[player1]["all"]
        data2 = analytics.batsmanAPI(player2, season)[player2]["all"]

        df = pd.DataFrame({
            player1: data1,
            player2: data2
        })

        st.subheader("Batting Comparison")
        st.dataframe(df)

        st.subheader("Runs Comparison")
        st.bar_chart(df.loc[["runs"]].T)

        st.subheader("Average Comparison")
        st.bar_chart(df.loc[["avg"]].T)

    else:
        player1 = col1.selectbox("Bowler 1", players["bowlers"])
        player2 = col2.selectbox("Bowler 2", players["bowlers"])

        data1 = analytics.bowlerAPI(player1, season)[player1]["all"]
        data2 = analytics.bowlerAPI(player2, season)[player2]["all"]

        df = pd.DataFrame({
            player1: data1,
            player2: data2
        })

        st.subheader("Bowling Comparison")
        st.dataframe(df)

        st.subheader("Wickets Comparison")
        st.bar_chart(df.loc[["wickets"]].T)

        st.subheader("Economy Comparison")
        st.bar_chart(df.loc[["economy"]].T)
