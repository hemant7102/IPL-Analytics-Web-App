import os
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

matches = pd.read_csv(os.path.join(DATA_DIR, "ipl_matches.csv"))
balls = pd.read_csv(os.path.join(DATA_DIR, "ipl_ball.csv"))


ball_match = balls.merge(matches, on="ID", how="inner")

ball_match["BowlingTeam"] = ball_match.Team1 + ball_match.Team2
ball_match["BowlingTeam"] = ball_match[["BowlingTeam", "BattingTeam"]].apply(
    lambda x: x.iloc[0].replace(x.iloc[1], ""), axis=1
)

ball_match = ball_match[ball_match.innings.isin([1, 2])]


def filter_season(df, season):
    if season == "all":
        return df
    return df[df.Season.astype(str) == str(season)]



def getPlayers():
    return {
        "batters": sorted(ball_match.batter.dropna().unique().tolist()),
        "bowlers": sorted(ball_match.bowler.dropna().unique().tolist())
    }


def getSeasons():
    seasons = matches.Season.dropna().unique().tolist()

    cleaned_seasons = []
    for s in seasons:
        # Handle cases like "2020/21"
        if isinstance(s, str) and "/" in s:
            cleaned_seasons.append(s)   # keep as string
        else:
            cleaned_seasons.append(int(s))

    return {"seasons": sorted(cleaned_seasons, key=str)}



# Team Record
def teamAPI(team, season="all"):
    df = filter_season(matches, season)

    if team not in set(df.Team1).union(set(df.Team2)):
        return {"error": "Invalid team name"}

    team_df = df[(df.Team1 == team) | (df.Team2 == team)]

    overall = {
        "matchesplayed": int(team_df.shape[0]),
        "won": int(team_df[team_df.WinningTeam == team].shape[0]),
        "loss": int(team_df.shape[0] - team_df[team_df.WinningTeam == team].shape[0] - team_df[team_df.WinningTeam.isna()].shape[0]),
        "noResult": int(team_df[team_df.WinningTeam.isna()].shape[0]),
        "title": int(team_df[(team_df.MatchNumber == "Final") & (team_df.WinningTeam == team)].shape[0])
    }

    against = {}
    for opp in set(df.Team1).union(set(df.Team2)):
        if opp == team:
            continue
        d = team_df[(team_df.Team1 == opp) | (team_df.Team2 == opp)]
        against[opp] = {
            "matchesplayed": int(d.shape[0]),
            "won": int(d[d.WinningTeam == team].shape[0]),
            "loss": int(d.shape[0] - d[d.WinningTeam == team].shape[0] - d[d.WinningTeam.isna()].shape[0]),
            "noResult": int(d[d.WinningTeam.isna()].shape[0])
        }

    return {team: {"overall": overall, "against": against}}


# Batting Record
def batsmanAPI(batsman, season="all"):
    df = filter_season(ball_match, season)
    df = df[df.batter == batsman]

    if df.empty:
        return {"error": "Batsman not found"}

    outs = df[df.player_out == batsman].shape[0]
    balls_faced = df[~(df.extra_type == "wides")].shape[0]

    overall = {
        "innings": int(df.ID.nunique()),
        "runs": int(df.batsman_run.sum()),
        "fours": int(df[(df.batsman_run == 4) & (df.non_boundary == 0)].shape[0]),
        "sixes": int(df[(df.batsman_run == 6) & (df.non_boundary == 0)].shape[0]),
        "avg": round(df.batsman_run.sum() / outs, 2) if outs else None,
        "strikeRate": round((df.batsman_run.sum() / balls_faced) * 100, 2) if balls_faced else 0,
        "notOut": int(df.ID.nunique() - outs),
        "mom": int(df[df.Player_of_Match == batsman].ID.nunique())
    }

    against = {}
    for team in df.BowlingTeam.unique():
        tdf = df[df.BowlingTeam == team]
        outs = tdf[tdf.player_out == batsman].shape[0]
        balls = tdf[~(tdf.extra_type == "wides")].shape[0]

        against[team] = {
            "innings": int(tdf.ID.nunique()),
            "runs": int(tdf.batsman_run.sum()),
            "avg": round(tdf.batsman_run.sum() / outs, 2) if outs else None,
            "strikeRate": round((df.batsman_run.sum() / balls_faced) * 100, 2) if balls_faced else 0

        }

    return {batsman: {"all": overall, "against": against}}


# Bowling Record
def bowlerAPI(bowler, season="all"):
    df = filter_season(ball_match, season)
    df = df[df.bowler == bowler]

    if df.empty:
        return {"error": "Bowler not found"}

    legal = df[~df.extra_type.isin(["wides", "noballs"])]
    wickets = df[df.isWicketDelivery == 1].shape[0]

    overall = {
        "innings": int(df.ID.nunique()),
        "wickets": int(wickets),
        "economy": round((df.total_run.sum() / legal.shape[0]) * 6, 2) if legal.shape[0] else 0,
        "avg": round(df.total_run.sum() / wickets, 2) if wickets else None,
        "strikeRate": round(legal.shape[0] / wickets, 2) if wickets else None,
        "mom": int(df[df.Player_of_Match == bowler].ID.nunique())
    }

    against = {}
    for team in df.BattingTeam.unique():
        tdf = df[df.BattingTeam == team]
        legal = tdf[~tdf.extra_type.isin(["wides", "noballs"])]
        wickets = tdf[tdf.isWicketDelivery == 1].shape[0]

        against[team] = {
            "innings": int(tdf.ID.nunique()),
            "wickets": int(wickets),
            "economy": round((tdf.total_run.sum() / legal.shape[0]) * 6, 2) if legal.shape[0] else 0,
            "avg": round(tdf.total_run.sum() / wickets, 2) if wickets else None
        }

    return {bowler: {"all": overall, "against": against}}
