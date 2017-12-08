from flask import Flask, render_template, redirect, \
    url_for, request, session, flash, g
from functools import wraps
from nbascrape import *
from random import randint

app = Flask(__name__)

app.secret_key = 'my precious'

@app.route('/nba-adv-predictor', methods=['GET', 'POST'])
def predict():
    winner = []
    adv = []
    loser = []
    newList = []
    BattleTxt = []
    newCurrentPokes = []
    team1_data = []
    team2_data = []
    compare = []
    teams = ['Boston Celtics',
             'Brooklyn Nets',
             'New York Knicks',
             'Philadelphia Sixers',
             'Toronto Raptors',
             'Chicago Bulls',
             'Cleveland Cavaliers',
             'Detroit Pistons',
             'Indiana Pacers',
             'Milwaukee Bucks',
             'Atlanata Hawks',
             'Charlotte Hornets',
             'Miami Heat',
             'Orlando Magic',
             'Washington Wizards',
             'Denver Nuggets',
             'Minnesota Timberwolves',
             'Oklahoma City Thunder',
             'Portland Trailblazers',
             'Utah Jazz',
             'Golden State Warriors',
             'Los Angeles Clippers',
             'Los Angelese Lakers',
             'Phoenix Suns',
             'Sacramento Kings',
             'Dallas Mavericks',
             'Houston Rockets',
             'Memphis Grizzlies',
             'New Orleans Pelicans',
             'San Antonio Spurs']

    if request.method=='POST':
        TEAM1_ID = request.form.get('team1_vs')
        TEAM2_ID = request.form.get('team2_vs')
        print('team 1 id: ' + TEAM1_ID)
        print('team 2 id: ' + TEAM2_ID)
        team1_data,team2_data,compare,winner,adv,loser = RunScript(TEAM1_ID,TEAM2_ID)
        print(winner)
        print('team 1 data: ' + str(team1_data))
        print('team 2 data: ' + str(team2_data))
        print('compare val: ' + str(compare))
        print('winner: ' + str(winner))
        print('advanage: ' + str(adv))
        print('loser: ' + str(loser))

    return render_template('nba-adv-predictor.html',t1_data=team1_data,t2_data=team2_data,team_comparison=compare,win_team=winner,pct_adv=adv,lose_team=loser,teams=teams)

if __name__ == "__main__":

    app.run(debug = True)
