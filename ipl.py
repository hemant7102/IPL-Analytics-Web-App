import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

matches = pd.read_csv(os.path.join(DATA_DIR, "ipl_matches.csv"))



def teamsAPI():
    teams = sorted(set(matches.Team1).union(set(matches.Team2)))
    return {"teams": teams}


def teamVteamAPI(team1, team2, season="all"):
    df = matches.copy()

    if season != "all":
        df = df[df.Season == int(season)]

    valid_teams = set(df.Team1).union(set(df.Team2))
    if team1 not in valid_teams or team2 not in valid_teams:
        return {"error": "Invalid team name"}

    h2h = df[
        ((df.Team1 == team1) & (df.Team2 == team2)) |
        ((df.Team1 == team2) & (df.Team2 == team1))
    ]

    total = h2h.shape[0]
    wins = h2h.WinningTeam.value_counts()

    return {
        "total_matches": int(total),
        team1: int(wins.get(team1, 0)),
        team2: int(wins.get(team2, 0)),
        "draws": int(total - wins.get(team1, 0) - wins.get(team2, 0))
    }
