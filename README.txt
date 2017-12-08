Python web scraper/crawler that pulls both player and team statistical data in real-time from RealGM (basketball statsitics website), for the purpose of analyzing and ultimately predicting the advantageous team in the selected matchup.

Libaries Used:
flask, lxml, requests, html

Resources:
https://basketball.realgm.com/nba/depth-charts
-- scraping team lineups and positions for individual comparisons
https://basketball.realgm.com/nba/teams/
-- scraping statistical averages for each team

Features:
- Weighted points system to determine which team has the advantage in the selected matchup
-- Weighted comparison of team starters, bench, and collective statistical averages
-- Weighted comparison of individual player vs. player matchups in their respective position (PG, SF, PF, C, SG). Higher point rewards for specific statistical categories that are deemed more important for the specific position (i.e. PG is rewarded +3 for higher assists, C is rewarded +3 for higher rebounds; as opposed to the standard +1.

Work Seperation:
Victor & Mike -- Back-end (Scraping/Parsing/Algorithm)
Doug & David -- Front-end (Flask/HTML/Javascript)


HOW-TO Run Program:
- install flask if not already installed: pip3 install flask

- run the following on command line to connect the application

-- export FLASK_APP=app.py

-- flask run



The program should now be active on local host:
http://127.0.0.1:5000/nba-adv-predictor
