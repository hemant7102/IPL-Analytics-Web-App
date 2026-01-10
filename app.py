from flask import Flask, jsonify, request
import ipl
import analytics

app = Flask(__name__)


@app.route('/')
def home():
    return jsonify({"message": "IPL Analytics API is running"})

# Teams
@app.route('/api/teams')
def teams():
    return jsonify(ipl.teamsAPI())

# Team VS Team
@app.route('/api/teamvteam')
def teamvteam():
    team1 = request.args.get('team1')
    team2 = request.args.get('team2')
    season = request.args.get('season', 'all')

    if not team1 or not team2:
        return jsonify({"error": "team1 and team2 required"}), 400

    return jsonify(ipl.teamVteamAPI(team1, team2, season))

# Team Record
@app.route('/api/team-record')
def team_record():
    team = request.args.get('team')
    season = request.args.get('season', 'all')

    if not team:
        return jsonify({"error": "team required"}), 400

    return jsonify(analytics.teamAPI(team, season))


# Batting Record
@app.route('/api/batting-record')
def batting_record():
    batsman = request.args.get('batsman')
    season = request.args.get('season', 'all')

    if not batsman:
        return jsonify({"error": "batsman required"}), 400

    return jsonify(analytics.batsmanAPI(batsman, season))


# Bowling Record
@app.route('/api/bowling-record')
def bowling_record():
    bowler = request.args.get('bowler')
    season = request.args.get('season', 'all')

    if not bowler:
        return jsonify({"error": "bowler required"}), 400

    return jsonify(analytics.bowlerAPI(bowler, season))

# Players Record
@app.route('/api/players')
def players():
    return jsonify(analytics.getPlayers())


# IPL Seasons
@app.route('/api/seasons')
def seasons():
    return jsonify(analytics.getSeasons())


if __name__ == "__main__":
    app.run(debug=True)
