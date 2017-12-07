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

    if request.method=='POST':
        TEAM1_ID = request.form.get('team1_vs')
        TEAM2_ID = request.form.get('team2_vs')
        team1_data,team2_data,compare,winner,adv,loser = RunScript(TEAM1_ID,TEAM2_ID)
        print(winner)

    return render_template('nba-adv-predictor.html',t1_data=team1_data,t2_data=team2_data,team_comparison=compare,win_team=winner,pct_adv=adv,lose_team=loser)

if __name__ == "__main__":
    
    app.run(debug = True)
