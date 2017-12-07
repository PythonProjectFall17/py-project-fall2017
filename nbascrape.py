# python project fall 2017
# scrape/parsing
# initial

from lxml import html
from random import randint
import time
import urllib.request
import requests
import datetime

def fileTeams():
    teams = []
    print("Teams to choose from:\n")
    f = open("teams.txt", 'r')
    for team in f:
        team = team.strip("\n")
        teams.append(team)
    return teams

# scrapes and parses team data
def getTeams(team1, team2):
    url = "https://basketball.realgm.com/nba/teams/"
    end_url = "/Stats/2018/Averages"

    list = []
    f = open("urls.txt", 'r')

    # load teams into list
    for urls in f:
        urls = urls.strip("\n")
        list.append(url + urls + end_url)

    print("Selected Teams (by index): \n")
    print("Comparing: " + str(team1) + " vs. " + str(team2))
    print(list[team1])
    print(list[team2])

    # both lists are parsed with values
    t1 = scrapeUrl(list[team1])
    t2 = scrapeUrl(list[team2])

    print("\nList Data Team 1:")
    print("Player Stats: " + str(t1[0]))
    print("Team Stats: " + str(t1[1]))
    print("Previous Games (Splits): " + str(t1[2]))

    print("\nList Data Team 2:")
    print("Player Stats: " + str(t2[0]))
    print("Team Stats: " + str(t2[1]))
    print("Previous Games (Splits): " + str(t2[2]))

    # calling compareTeams to compare team data and determine winner
    winner = compareTeams(team1, t1, team2, t2)

def parseTeamData(data, iter, max, index):
    team_stats = []
    # stats: each player needs to be in their own list
    for j in range(1, iter+1):
        stat_list = []
        for i in range(1, max):
            test_entry = data.xpath("//*/tbody/tr[" + str(j) + "]/td[" + str(i) + "]/text()")
            # test to make sure the HTML does not have a broken value
            #print("test entry" + str(test_entry))

            if test_entry:
                # for team stats
                # adjustment
                size = len(test_entry)
                # if length is 2, we want index

                if index is 1 and i is 2:
                    pstat = test_entry[0]
                elif index is 2 and size is not 3:
                    #print("test entry" + str(test_entry))
                    pstat = test_entry[size-1]
                    #print("Select = " + pstat)
                else:
                    #print("else test entry" + str(test_entry))
                    pstat = test_entry[index]

            else:
                """ pad with NULL to indicate broken HTML value
                    we can change this to a different value if needed
                """
                pstat = 'NULL'

            stat_list.append(pstat)

        team_stats.append(stat_list)

    return team_stats

# scrapes urls for each team and parses them into respective lists
# lists are then passed into compareTeams() in order to apply comparison algorithm
def scrapeUrl(url):
    try:
        # NOTE: Returning 0 for success, 1 for failure
        session_requests = requests.session()
        r = session_requests.get(url, headers=dict(referer=url))

        # status code 200 indicates html page access = successful
        if r.status_code == 200:
            print("Web page scraped successfully!")

            # tree is the HTML content we are parsing
            tree = html.fromstring(r.content)
            # HTML content (commented out because we do not need to see this)
            #print(str(r.content))

            # HTML target (commented out because we do not need to see this)
            #print("Our HTML Target: ", tree)

            roster_spots = 0
            team_stat_fields = 0
            team_splits = 0

            full_body = tree.xpath("//*/tbody")
            for tbody in full_body:

                # get number of team splits fields for parsing
                if team_stat_fields > 1:
                    for tr in tbody:
                        team_splits = team_splits + 1

                # get number of team stat fields for parsing
                if roster_spots > 1 and team_stat_fields is 0:
                    for tr in tbody:
                        team_stat_fields = team_stat_fields + 1

                # get number of roster spots for individual player parsing
                if roster_spots is 0:
                    for tr in tbody:
                        roster_spots = roster_spots + 1

            print("# of roster spots: " + str(roster_spots))
            print("# of team stat fields: " + str(team_stat_fields))
            print("# of team splits (games played): " + str(team_splits))

            parsed_team_stats = parseTeamData(tree, team_stat_fields, 22, 1)
            parsed_team_splits = parseTeamData(tree, team_splits, 22, 2)

            # Parse roster data (separate from team data)
            team_stats = []
            # stats: each player needs to be in their own list
            for j in range(1, roster_spots+1):
                stat_list = []

                for i in range(1, 24):
                    test_entry = tree.xpath("//*/tbody/tr[" + str(j) + "]/td[" + str(i) + "]/text()")

                    # test to make sure the HTML does not have a broken value
                    if test_entry:
                        # for player stats
                        pstat = test_entry[0]

                    else:
                        """ pad with NULL to indicate broken HTML value
                            we can change this to a different value if needed
                        """
                        pstat = 'NULL'

                    if i == 1:
                        stat_list.append("Player #" + pstat)
                    elif i == 2:
                        test_entry = tree.xpath("//*/tbody/tr[" + str(j) + "]/td[" + str(i) + "]/a/text()")
                        stat_list.append(test_entry[0])
                    else:
                        stat_list.append(pstat)

                team_stats.append(stat_list)

    except Exception as e:
        print("Error: ", e)
        return 1

    # make final list of lists
    data_pack = []
    data_pack.append(team_stats)
    data_pack.append(parsed_team_stats)
    data_pack.append(parsed_team_splits)

    return data_pack


# This is where we will implement algorithm to compare the team's player stats/other stats
def compareTeams(team1id, data1, team2id, data2):
    """
    REGULAR SEASON INDIVIDUAL PLAYER STATS:
        Location: data[0][index]
        Entry Format:
            Player#, Player Name, Team, GP, MPG, FGM, FGA, FG%, 3PM, 3PA, 3P%, FTM, FTA, FT%, TOV, PF, ORB, DRB, RPG, APG, SPG, BPG, PPG

    REGULAR SEASON TEAM STATS:
        Location: data[1][index]
        Entry Format:
            Totals, GP, MPG, FGM, FGA, FG%, 3PM 3PA, 3P%, FTM, FTA, FT%, TOV, PF, ORB, DRB, TRB, APG, SPG, BPG, PPG

    REGULAR SEASON TEAM SPLITS:
        Location: data[2][index]
        Entry Format:
            v. Team, GP, MPG, FGM, FGA, FG%, 3PM, 3PA, 3P%, FTM, FTA, FT%, TOV, PF, ORB, DRB, TRB, APG, SPG, BPG, PPG

    """
    print("\nTeam 1: " + str(team1id) + ", Team 2: " + str(team2id))
    # use team1id and team2id to get teams from depth charts
    depth_charts = findDepths()
    team1_rotations = ""
    team2_rotations = ""

    for team_entry in depth_charts:
        if team_entry[0] is team1id:
            team1_rotations = team_entry
        if team_entry[0] is team2id:
            team2_rotations = team_entry

    print("Team 1 Starters: " + str(team1_rotations[1]))
    print("Team 1 Bench/Rotation: " + str(team1_rotations[2]))
    print("\nTeam 2 Starters: " + str(team2_rotations[1]))
    print("Team 2 Bench/Rotation: " + str(team2_rotations[2]))
    """
        DO WINNER CALCULATIONS HERE
        USING   team1_rotations, data1
                team2_rotations, data2

        RETURN WINNER
    """

    # TEAM 1 STATS

    # STARTERS
    T1_S_PPG = data1[1][1][20]
    T1_S_FG = data1[1][1][5]
    T1_S_FT = data1[1][1][11]
    T1_S_3PM = data1[1][1][6]
    T1_S_AST = data1[1][1][17]
    T1_S_DRB = data1[1][1][15]
    T1_S_ORB = data1[1][1][14]
    T1_S_STL = data1[1][1][18]
    T1_S_BLK = data1[1][1][19]
    T1_S_TOV = data1[1][1][12]

    # BENCH
    T1_B_PPG = data1[1][2][20]
    T1_B_FG = data1[1][2][5]
    T1_B_FT = data1[1][2][11]
    T1_B_3PM = data1[1][2][6]
    T1_B_AST = data1[1][2][17]
    T1_B_DRB = data1[1][2][15]
    T1_B_ORB = data1[1][2][14]
    T1_B_STL = data1[1][2][18]
    T1_B_BLK = data1[1][2][19]
    T1_B_TOV = data1[1][2][12]

    # TEAM 2 STATS

    # STARTERS
    T2_S_PPG = data2[1][1][20]
    T2_S_FG = data2[1][1][5]
    T2_S_FT = data2[1][1][11]
    T2_S_3PM = data2[1][1][6]
    T2_S_AST = data2[1][1][17]
    T2_S_DRB = data2[1][1][15]
    T2_S_ORB = data2[1][1][14]
    T2_S_STL = data2[1][1][18]
    T2_S_BLK = data2[1][1][19]
    T2_S_TOV = data2[1][1][12]

    # BENCH
    T2_B_PPG = data2[1][2][20]
    T2_B_FG = data2[1][2][5]
    T2_B_FT = data2[1][2][11]
    T2_B_3PM = data2[1][2][6]
    T2_B_AST = data2[1][2][17]
    T2_B_DRB = data2[1][2][15]
    T2_B_ORB = data2[1][2][14]
    T2_B_STL = data2[1][2][18]
    T2_B_BLK = data2[1][2][19]
    T2_B_TOV = data2[1][2][12]

    # calculate winner via a 'points' system,
    # whoever leads in each attribute gets a point

    # BEGIN TEAM COMPARISON

    # STARTERS

    t1_s_points = 0  # starters points
    t2_s_points = 0

    if T1_S_PPG > T2_S_PPG:  # points per game
        t1_s_points += 1
    elif T2_S_PPG > T1_S_PPG:
        t2_s_points += 1
    if T1_S_FG > T2_S_FG:  # field goal percentage
        t1_s_points += 1
    elif T2_S_FG > T1_S_FG:
        t2_s_points += 1
    if T1_S_FT > T2_S_FT:  # free throw percentage
        t1_s_points += 1
    elif T2_S_FT > T1_S_FT:
        t2_s_points += 1
    if T1_S_3PM > T2_S_3PM:  # 3 pointers made
        t1_s_points += 1
    elif T2_S_3PM > T1_S_3PM:
        t2_s_points += 1
    if T1_S_AST > T2_S_AST:  # assists per game
        t1_s_points += 1
    elif T2_S_AST > T1_S_AST:
        t2_s_points += 1
    if T1_S_DRB > T2_S_DRB:  # defensive rebounds
        t1_s_points += 1
    elif T2_S_DRB > T1_S_DRB:
        t2_s_points += 1
    if T1_S_ORB > T2_S_ORB:  # offensive rebounds
        t1_s_points += 1
    elif T2_S_ORB > T1_S_ORB:
        t2_s_points += 1
    if T1_S_STL > T2_S_STL:  # steals per game
        t1_s_points += 1
    elif T2_S_STL > T1_S_STL:
        t2_s_points += 1
    if T1_S_BLK > T2_S_BLK:  # blocks per game
        t1_s_points += 1
    elif T2_S_BLK > T1_S_BLK:
        t2_s_points += 1
    if T1_S_TOV > T2_S_TOV:  # turnovers per game
        t2_s_points += 1  # team gets a point if they have LESS turnovers
    elif T2_S_TOV > T1_S_TOV:
        t1_s_points += 1

    # BENCH

    t1_b_points = 0  # bench points
    t2_b_points = 0

    if T1_B_PPG > T2_B_PPG:  # points per game
        t1_b_points += 1
    elif T2_B_PPG > T1_B_PPG:
        t2_b_points += 1
    if T1_B_FG > T2_B_FG:  # field goal percentage
        t1_b_points += 1
    elif T2_B_FG > T1_B_FG:
        t2_b_points += 1
    if T1_B_FT > T2_B_FT:  # free throw percentage
        t1_b_points += 1
    elif T2_B_FT > T1_B_FT:
        t2_b_points += 1
    if T1_B_3PM > T2_B_3PM:  # 3 pointers made
        t1_b_points += 1
    elif T2_B_3PM > T1_B_3PM:
        t2_b_points += 1
    if T1_B_AST > T2_B_AST:  # assists per game
        t1_b_points += 1
    elif T2_B_AST > T1_B_AST:
        t2_b_points += 1
    if T1_B_DRB > T2_B_DRB:  # defensive rebounds
        t1_b_points += 1
    elif T2_B_DRB > T1_B_DRB:
        t2_b_points += 1
    if T1_B_ORB > T2_B_ORB:  # offensive rebounds
        t1_b_points += 1
    elif T2_B_ORB > T1_B_ORB:
        t2_b_points += 1
    if T1_B_STL > T2_B_STL:  # steals per game
        t1_b_points += 1
    elif T2_B_STL > T1_B_STL:
        t2_b_points += 1
    if T1_B_BLK > T2_B_BLK:  # blocks per game
        t1_b_points += 1
    elif T2_B_BLK > T1_B_BLK:
        t2_b_points += 1
    if T1_B_TOV > T2_B_TOV:  # turnovers per game
        t2_b_points += 1  # team gets a point if they have LESS turnovers
    elif T2_B_TOV > T1_B_TOV:
        t1_b_points += 1

    # BEGIN INDIVIDUAL MATCHUPS COMPARISON

    """
     Note:
     Some players will get 3 points if they lead the other player in their primary stat.
     For example, the leading point guard will get 3 points for having more assists.
     Centers will get 3 points for having more rebounds, etc.
     Some players will get 2 points for various stats that are deemed important for the position (PPG for SG, etc).
     And finally, for all other stats that hold less value, 1 point.
      """

    t1_playerpoints = 0
    t2_playerpoints = 0

    S_PG_T1 = ""
    S_PG_T1_stats = []
    S_PG_T2 = ""
    S_PG_T2_stats = []
    S_SG_T1 = ""
    S_SG_T1_stats = []
    S_SG_T2 = ""
    S_SG_T2_stats = []
    S_SF_T1 = ""
    S_SF_T1_stats = []
    S_SF_T2 = ""
    S_SF_T2_stats = []
    S_PF_T1 = ""
    S_PF_T1_stats = []
    S_PF_T2 = ""
    S_PF_T2_stats = []
    S_C_T1 = ""
    S_C_T1_stats = []
    S_C_T2 = ""
    S_C_T2_stats = []

    print("GATHERING STARTER PLAYERS DATA FOR BOTH TEAMS...")
    print(team1_rotations)
    for player in team1_rotations[1]:
        if "PG" in player:
            parse = player.split(" ")
            S_PG_T1 = parse[1]
            print(S_PG_T1)
        if "SG" in player:
            parse = player.split(" ")
            S_SG_T1 = parse[1]
            print(S_SG_T1)
        if "SF" in player:
            parse = player.split(" ")
            S_SF_T1 = parse[1]
            print(S_SF_T1)
        if "PF" in player:
            parse = player.split(" ")
            S_PF_T1 = parse[1]
            print(S_PF_T1)
        if "C" in player:
            parse = player.split(" ")
            S_C_T1 = parse[1]
            print(S_C_T1)

    for index, player in enumerate(data1[0]):
        if S_PG_T1 in player[1]:
            S_PG_T1_stats = data1[0][index]
        if S_SG_T1 in player[1]:
            S_SG_T1_stats = data1[0][index]
        if S_SF_T1 in player[1]:
            S_SF_T1_stats = data1[0][index]
        if S_PF_T1 in player[1]:
            S_PF_T1_stats = data1[0][index]
        if S_C_T1 in player[1]:
            S_C_T1_stats = data1[0][index]

    print(str(S_PG_T1_stats))
    print(str(S_SG_T1_stats))
    print(str(S_SF_T1_stats))
    print(str(S_PF_T1_stats))
    print(str(S_C_T1_stats))

    for player in team2_rotations[1]:
        if "PG" in player:
            parse = player.split(" ")
            S_PG_T2 = parse[1]
            print(S_PG_T2)
        if "SG" in player:
            parse = player.split(" ")
            S_SG_T2 = parse[1]
            print(S_SG_T2)
        if "SF" in player:
            parse = player.split(" ")
            S_SF_T2 = parse[1]
            print(S_SF_T2)
        if "PF" in player:
            parse = player.split(" ")
            S_PF_T2 = parse[1]
            print(S_PF_T2)
        if "C" in player:
            parse = player.split(" ")
            S_C_T2 = parse[1]
            print(S_C_T2)

    for index, player in enumerate(data2[0]):
        if S_PG_T2 in player[1]:
            S_PG_T2_stats = data2[0][index]
        if S_SG_T2 in player[1]:
            S_SG_T2_stats = data2[0][index]
        if S_SF_T2 in player[1]:
            S_SF_T2_stats = data2[0][index]
        if S_PF_T2 in player[1]:
            S_PF_T2_stats = data2[0][index]
        if S_C_T2 in player[1]:
            S_C_T2_stats = data2[0][index]

    """
        COMPARE STARTING POINT GUARDS FOR BOTH TEAMS HERE
    """
    print("\nComparing Starting Point Guards: " + S_PG_T1_stats[2] + ": " + S_PG_T1_stats[1] + " vs. " + S_PG_T2_stats[
        2] + ": " + S_PG_T2_stats[1])

    print()

    # Team 1 starting PG stats
    PPG_S_PG_T1 = S_PG_T1_stats[22]
    FG_S_PG_T1 = S_PG_T1_stats[7]
    FT_S_PG_T1 = S_PG_T1_stats[13]
    PM3_S_PG_T1 = S_PG_T1_stats[8]  # PM3 means 3PM cuz python doesn't like when you start a variable name with int :-)
    AST_S_PG_T1 = S_PG_T1_stats[19]
    REB_S_PG_T1 = S_PG_T1_stats[18]
    STL_S_PG_T1 = S_PG_T1_stats[20]
    BLK_S_PG_T1 = S_PG_T1_stats[21]

    # Team 2 starting PG stats
    PPG_S_PG_T2 = S_PG_T2_stats[22]
    FG_S_PG_T2 = S_PG_T2_stats[7]
    FT_S_PG_T2 = S_PG_T2_stats[13]
    PM3_S_PG_T2 = S_PG_T2_stats[8]  # PM3 means 3PM cuz python doesn't like when you start a variable name with int :-)
    AST_S_PG_T2 = S_PG_T2_stats[19]
    REB_S_PG_T2 = S_PG_T2_stats[18]
    STL_S_PG_T2 = S_PG_T2_stats[20]
    BLK_S_PG_T2 = S_PG_T2_stats[21]

    if PPG_S_PG_T1 > PPG_S_PG_T2:
        t1_playerpoints += 2
    elif PPG_S_PG_T2 > PPG_S_PG_T1:
        t2_playerpoints += 2
    if FG_S_PG_T1 > FG_S_PG_T2:
        t1_playerpoints += 1
    elif FG_S_PG_T2 > FG_S_PG_T1:
        t2_playerpoints += 1
    if FT_S_PG_T1 > FT_S_PG_T2:
        t1_playerpoints += 2
    elif FT_S_PG_T2 > FT_S_PG_T1:
        t2_playerpoints += 2
    if PM3_S_PG_T1 > PM3_S_PG_T2:
        t1_playerpoints += 2
    elif PM3_S_PG_T2 > PM3_S_PG_T1:
        t2_playerpoints += 2
    if AST_S_PG_T1 > AST_S_PG_T2:
        t1_playerpoints += 2    # 3
    elif AST_S_PG_T2 > AST_S_PG_T1:
        t2_playerpoints += 2    # 3
    if REB_S_PG_T1 > REB_S_PG_T2:
        t1_playerpoints += 1
    elif REB_S_PG_T2 > REB_S_PG_T1:
        t2_playerpoints += 1
    if STL_S_PG_T1 > STL_S_PG_T2:
        t1_playerpoints += 1
    elif STL_S_PG_T2 > STL_S_PG_T1:
        t2_playerpoints += 1
    if BLK_S_PG_T1 > BLK_S_PG_T2:
        t1_playerpoints += 1
    elif BLK_S_PG_T2 > BLK_S_PG_T1:
        t2_playerpoints += 1

    print("PG")
    print(t1_playerpoints)
    print(t2_playerpoints)

    """
        COMPARE STARTING SHOOTING GUARDS FOR BOTH TEAMS HERE
    """
    print(
        "\nComparing Starting Shooting Guards: " + S_SG_T1_stats[2] + ": " + S_SG_T1_stats[1] + " vs. " + S_SG_T2_stats[
            2] + ": " + S_SG_T2_stats[1])

    # Team 1 starting SG stats
    PPG_S_SG_T1 = S_SG_T1_stats[22]
    FG_S_SG_T1 = S_SG_T1_stats[7]
    FT_S_SG_T1 = S_SG_T1_stats[13]
    PM3_S_SG_T1 = S_SG_T1_stats[8]  # PM3 means 3PM cuz python doesn't like when you start a variable name with int :-)
    AST_S_SG_T1 = S_SG_T1_stats[19]
    REB_S_SG_T1 = S_SG_T1_stats[18]
    STL_S_SG_T1 = S_SG_T1_stats[20]
    BLK_S_SG_T1 = S_SG_T1_stats[21]

    # Team 2 starting SG stats
    PPG_S_SG_T2 = S_SG_T2_stats[22]
    FG_S_SG_T2 = S_SG_T2_stats[7]
    FT_S_SG_T2 = S_SG_T2_stats[13]
    PM3_S_SG_T2 = S_SG_T2_stats[8]  # PM3 means 3PM cuz python doesn't like when you start a variable name with int :-)
    AST_S_SG_T2 = S_SG_T2_stats[19]
    REB_S_SG_T2 = S_SG_T2_stats[18]
    STL_S_SG_T2 = S_SG_T2_stats[20]
    BLK_S_SG_T2 = S_SG_T2_stats[21]

    if PPG_S_SG_T1 > PPG_S_SG_T2:
        t1_playerpoints += 2    # 3
    elif PPG_S_SG_T2 > PPG_S_SG_T1:
        t2_playerpoints += 2    # 3
    if FG_S_SG_T1 > FG_S_SG_T2:
        t1_playerpoints += 1
    elif FG_S_SG_T2 > FG_S_SG_T1:
        t2_playerpoints += 1
    if FT_S_SG_T1 > FT_S_SG_T2:
        t1_playerpoints += 1
    elif FT_S_SG_T2 > FT_S_SG_T1:
        t2_playerpoints += 1
    if PM3_S_SG_T1 > PM3_S_SG_T2:
        t1_playerpoints += 2
    elif PM3_S_SG_T2 > PM3_S_SG_T1:
        t2_playerpoints += 2
    if AST_S_SG_T1 > AST_S_SG_T2:
        t1_playerpoints += 1
    elif AST_S_SG_T2 > AST_S_SG_T1:
        t2_playerpoints += 1
    if REB_S_SG_T1 > REB_S_SG_T2:
        t1_playerpoints += 1
    elif REB_S_SG_T2 > REB_S_SG_T1:
        t2_playerpoints += 1
    if STL_S_SG_T1 > STL_S_SG_T2:
        t1_playerpoints += 1
    elif STL_S_SG_T2 > STL_S_SG_T1:
        t2_playerpoints += 1
    if BLK_S_SG_T1 > BLK_S_SG_T2:
        t1_playerpoints += 1
    elif BLK_S_SG_T2 > BLK_S_SG_T1:
        t2_playerpoints += 1

    print("SG")
    print(t1_playerpoints)
    print(t2_playerpoints)

    """
        COMPARE STARTING SMALL FORWARDS FOR BOTH TEAMS HERE
    """
    print(
        "\nComparing Starting Small Forwards: " + S_SF_T1_stats[2] + ": " + S_SF_T1_stats[1] + " vs. " + S_SF_T2_stats[
            2] + ": " + S_SF_T2_stats[1])

    # Team 1 starting SF stats
    PPG_S_SF_T1 = S_SF_T1_stats[22]
    FG_S_SF_T1 = S_SF_T1_stats[7]
    FT_S_SF_T1 = S_SF_T1_stats[13]
    PM3_S_SF_T1 = S_SF_T1_stats[8]  # PM3 means 3PM cuz python doesn't like when you start a variable name with int :-)
    AST_S_SF_T1 = S_SF_T1_stats[19]
    REB_S_SF_T1 = S_SF_T1_stats[18]
    STL_S_SF_T1 = S_SF_T1_stats[20]
    BLK_S_SF_T1 = S_SF_T1_stats[21]

    # Team 2 starting SF stats
    PPG_S_SF_T2 = S_SF_T2_stats[22]
    FG_S_SF_T2 = S_SF_T2_stats[7]
    FT_S_SF_T2 = S_SF_T2_stats[13]
    PM3_S_SF_T2 = S_SF_T2_stats[8]  # PM3 means 3PM cuz python doesn't like when you start a variable name with int :-)
    AST_S_SF_T2 = S_SF_T2_stats[19]
    REB_S_SF_T2 = S_SF_T2_stats[18]
    STL_S_SF_T2 = S_SF_T2_stats[20]
    BLK_S_SF_T2 = S_SF_T2_stats[21]

    if PPG_S_SF_T1 > PPG_S_SF_T2:
        t1_playerpoints += 2    # changed 2
    elif PPG_S_SF_T2 > PPG_S_SF_T1:
        t2_playerpoints += 2    # changed 2
    if FG_S_SF_T1 > FG_S_SF_T2:
        t1_playerpoints += 1
    elif FG_S_SF_T2 > FG_S_SF_T1:
        t2_playerpoints += 1
    if FT_S_SF_T1 > FT_S_SF_T2:
        t1_playerpoints += 1
    elif FT_S_SF_T2 > FT_S_SF_T1:
        t2_playerpoints += 1
    if PM3_S_SF_T1 > PM3_S_SF_T2:
        t1_playerpoints += 1
    elif PM3_S_SF_T2 > PM3_S_SF_T1:
        t2_playerpoints += 1
    if AST_S_SF_T1 > AST_S_SF_T2:
        t1_playerpoints += 1
    elif AST_S_SF_T2 > AST_S_SF_T1:
        t2_playerpoints += 1
    if REB_S_SF_T1 > REB_S_SF_T2:
        t1_playerpoints += 1
    elif REB_S_SF_T2 > REB_S_SF_T1:
        t2_playerpoints += 1
    if STL_S_SF_T1 > STL_S_SF_T2:
        t1_playerpoints += 2
    elif STL_S_SF_T2 > STL_S_SF_T1:
        t2_playerpoints += 2
    if BLK_S_SF_T1 > BLK_S_SF_T2:
        t1_playerpoints += 1
    elif BLK_S_SF_T2 > BLK_S_SF_T1:
        t2_playerpoints += 1

    print("SF")
    print(t1_playerpoints)
    print(t2_playerpoints)

    """
        COMPARE STARTING POWER FORWARDS FOR BOTH TEAMS HERE
    """
    print(
        "\nComparing Starting Power Forwards: " + S_PF_T1_stats[2] + ": " + S_PF_T1_stats[1] + " vs. " + S_PF_T2_stats[
            2] + ": " + S_PF_T2_stats[1])

    # Team 1 starting PF stats
    PPG_S_PF_T1 = S_PF_T1_stats[22]
    FG_S_PF_T1 = S_PF_T1_stats[7]
    FT_S_PF_T1 = S_PF_T1_stats[13]
    PM3_S_PF_T1 = S_PF_T1_stats[8]  # PM3 means 3PM cuz python doesn't like when you start a variable name with int :-)
    AST_S_PF_T1 = S_PF_T1_stats[19]
    REB_S_PF_T1 = S_PF_T1_stats[18]
    STL_S_PF_T1 = S_PF_T1_stats[20]
    BLK_S_PF_T1 = S_PF_T1_stats[21]

    # Team 2 starting PF stats
    PPG_S_PF_T2 = S_PF_T2_stats[22]
    FG_S_PF_T2 = S_PF_T2_stats[7]
    FT_S_PF_T2 = S_PF_T2_stats[13]
    PM3_S_PF_T2 = S_PF_T2_stats[8]  # PM3 means 3PM cuz python doesn't like when you start a variable name with int :-)
    AST_S_PF_T2 = S_PF_T2_stats[19]
    REB_S_PF_T2 = S_PF_T2_stats[18]
    STL_S_PF_T2 = S_PF_T2_stats[20]
    BLK_S_PF_T2 = S_PF_T2_stats[21]

    if PPG_S_PF_T1 > PPG_S_PF_T2:
        t1_playerpoints += 2
    elif PPG_S_PF_T2 > PPG_S_PF_T1:
        t2_playerpoints += 2
    if FG_S_PF_T1 > FG_S_PF_T2:
        t1_playerpoints += 1
    elif FG_S_PF_T2 > FG_S_PF_T1:
        t2_playerpoints += 1
    if FT_S_PF_T1 > FT_S_PF_T2:
        t1_playerpoints += 1
    elif FT_S_PF_T2 > FT_S_PF_T1:
        t2_playerpoints += 1
    if PM3_S_PF_T1 > PM3_S_PF_T2:
        t1_playerpoints += 1
    elif PM3_S_PF_T2 > PM3_S_PF_T1:
        t2_playerpoints += 1
    if AST_S_PF_T1 > AST_S_PF_T2:
        t1_playerpoints += 1
    elif AST_S_PF_T2 > AST_S_PF_T1:
        t2_playerpoints += 1
    if REB_S_PF_T1 > REB_S_PF_T2:
        t1_playerpoints += 2
    elif REB_S_PF_T2 > REB_S_PF_T1:
        t2_playerpoints += 2
    if STL_S_PF_T1 > STL_S_PF_T2:
        t1_playerpoints += 1
    elif STL_S_PF_T2 > STL_S_PF_T1:
        t2_playerpoints += 1
    if BLK_S_PF_T1 > BLK_S_PF_T2:
        t1_playerpoints += 2
    elif BLK_S_PF_T2 > BLK_S_PF_T1:
        t2_playerpoints += 2

    print("PF")
    print(t1_playerpoints)
    print(t2_playerpoints)

    """
        COMPARE STARTING CENTERS FOR BOTH TEAMS HERE
    """
    print(
        "\nComparing Starting Centers: " + S_C_T1_stats[2] + ": " + S_C_T1_stats[1] + " vs. " + S_C_T2_stats[2] + ": " +
        S_C_T2_stats[1])

    # Team 1 starting C stats
    PPG_S_C_T1 = S_C_T1_stats[22]
    FG_S_C_T1 = S_C_T1_stats[7]
    FT_S_C_T1 = S_C_T1_stats[13]
    PM3_S_C_T1 = S_C_T1_stats[8]  # PM3 means 3PM cuz python doesn't like when you start a variable name with int :-)
    AST_S_C_T1 = S_C_T1_stats[19]
    REB_S_C_T1 = S_C_T1_stats[18]
    STL_S_C_T1 = S_C_T1_stats[20]
    BLK_S_C_T1 = S_C_T1_stats[21]

    # Team 2 starting C stats
    PPG_S_C_T2 = S_C_T2_stats[22]
    FG_S_C_T2 = S_C_T2_stats[7]
    FT_S_C_T2 = S_C_T2_stats[13]
    PM3_S_C_T2 = S_C_T2_stats[8]  # PM3 means 3PM cuz python doesn't like when you start a variable name with int :-)
    AST_S_C_T2 = S_C_T2_stats[19]
    REB_S_C_T2 = S_C_T2_stats[18]
    STL_S_C_T2 = S_C_T2_stats[20]
    BLK_S_C_T2 = S_C_T2_stats[21]

    if PPG_S_C_T1 > PPG_S_C_T2:
        t1_playerpoints += 1
    elif PPG_S_C_T2 > PPG_S_C_T1:
        t2_playerpoints += 1
    if FG_S_C_T1 > FG_S_C_T2:
        t1_playerpoints += 1
    elif FG_S_C_T2 > FG_S_C_T1:
        t2_playerpoints += 1
    if FT_S_C_T1 > FT_S_C_T2:
        t1_playerpoints += 1
    elif FT_S_C_T2 > FT_S_C_T1:
        t2_playerpoints += 1
    if PM3_S_C_T1 > PM3_S_C_T2:
        t1_playerpoints += 1
    elif PM3_S_C_T2 > PM3_S_C_T1:
        t2_playerpoints += 1
    if AST_S_C_T1 > AST_S_C_T2:
        t1_playerpoints += 1
    elif AST_S_C_T2 > AST_S_C_T1:
        t2_playerpoints += 1
    if REB_S_C_T1 > REB_S_C_T2:
        t1_playerpoints += 2    # 2
    elif REB_S_C_T2 > REB_S_C_T1:
        t2_playerpoints += 2    # 2
    if STL_S_C_T1 > STL_S_C_T2:
        t1_playerpoints += 1
    elif STL_S_C_T2 > STL_S_C_T1:
        t2_playerpoints += 1
    if BLK_S_C_T1 > BLK_S_C_T2:
        t1_playerpoints += 2
    elif BLK_S_C_T2 > BLK_S_C_T1:
        t2_playerpoints += 2

    print("C")
    print(t1_playerpoints)
    print(t2_playerpoints)

    """
        If we want to compare one thing from bench we could average points off bench and apply that

    """

    # BEGIN MATCHUP POINTS CALCULATION

    # weighted 50% for team stats (20% bench, 30% starters)
    # weighted 50% for individual player matchups

    print(": " + str(t1_b_points) + ", " + str(t1_playerpoints) + ", " + str(t1_s_points))
    print(": " + str(t2_b_points) + ", " + str(t2_playerpoints) + ", " + str(t2_s_points))

    t1_totalpoints = (((t1_b_points) + (t1_s_points)) * 0.6) + (t1_playerpoints * 0.4)  # removed adjustment for bench
    t2_totalpoints = (((t2_b_points) + (t2_s_points)) * 0.6) + (t2_playerpoints * 0.4)  # removed adjustment for bench

    # output/return results with team names and rounded percentage
    # ( not like this lol but its a start )

    if t1_totalpoints > t2_totalpoints:
        advantage = round((((t1_totalpoints - t2_totalpoints) / 10) * 100), 2)
        # calculate percentage advantage to beat other team
        print("\n", S_C_T1_stats[2], " has a ", advantage, "% advantage over ", S_C_T2_stats[2], "!")
    elif t2_totalpoints > t1_totalpoints:
        advantage = round((((t2_totalpoints - t1_totalpoints) / 10) * 100), 2)
        print("\n", S_C_T2_stats[2], " has a ", advantage, "% advantage over ", S_C_T1_stats[2], "!")
    elif t1_totalpoints == t2_totalpoints:
        print("\nNeither team has a distinct advantage. What a perfect matchup!")

    return True

def findDepths():
    """
        Function gets list of all starters and bench/rotation players for each team
        Returned List Format: List[Team Number (Corresponds with Indexes in teams.txt), List of Starters, List of Bench]
    """
    url = "https://basketball.realgm.com/nba/depth-charts"
    f = open("teams.txt", 'r')

    try:
        # NOTE: Returning 0 for success, 1 for failure
        session_requests = requests.session()
        r = session_requests.get(url, headers=dict(referer=url))

        # status code 200 indicates html page access = successful
        if r.status_code == 200:
            # tree is the HTML content we are parsing
            tree = html.fromstring(r.content)

            # get depth chart tables: 2 to 92 (separated by 3 each time)
            depth_charts = []
            count = 2
            i = 2
            while i < 92:
                starters = []
                bench = []
                players = []
                # get team name
                team_name = tree.xpath("//*[@id='site-takeover']/div[3]/div/h2[" + str(count) + "]/text()")
                f.seek(0)
                for num, line in enumerate(f):
                    line = line.strip("\n")
                    if line in str(team_name[1]):
                        players.append(num)

                for j in range(2, 7):
                    try:
                        row1 = tree.xpath("//*[@id='site-takeover']/div[3]/div/div[" + str(i) + "]/table/tbody/tr[1]/td[" + str(j) + "]/a/text()")
                        if j is 2:
                            addpos1 = "PG," + row1[0]
                        elif j is 3:
                            addpos1 = "SG," + row1[0]
                        elif j is 4:
                            addpos1 = "SF," + row1[0]
                        elif j is 5:
                            addpos1 = "PF," + row1[0]
                        elif j is 6:
                            addpos1 = "C," + row1[0]

                        starters.append(addpos1)
                    except Exception as e:
                        # catch a blank html entry
                        pass
                for j in range(2, 7):
                    try:
                        row2 = tree.xpath("//*[@id='site-takeover']/div[3]/div/div[" + str(i) + "]/table/tbody/tr[2]/td[" + str(j) + "]/a/text()")
                        if j is 2:
                            addpos2 = "PG," + row2[0]
                        elif j is 3:
                            addpos2 = "SG," + row2[0]
                        elif j is 4:
                            addpos2 = "SF," + row2[0]
                        elif j is 5:
                            addpos2 = "PF," + row2[0]
                        elif j is 6:
                            addpos2 = "C," + row2[0]

                        bench.append(addpos2)
                    except Exception as e:
                        # catch a blank html entry
                        pass

                players.append(starters)
                players.append(bench)
                #  actual team name
                #depth_charts.append(team_name[1])
                depth_charts.append(players)
                i = i + 3
                count = count + 1

    except Exception as e:
        print("Error: ", e)
        return 1

    # returns
    return depth_charts

if __name__ == "__main__":

    # all valid teams located in teams.txt
    # call prints all to screen for testing purposes
    teams = fileTeams()

    for index, team in enumerate(teams):
        print(str(index) + ". " + str(team))

    print("\nPlease enter two teams #s to determine a winner: (testing)")
    print("\n")

    # ideally this would be done via a drop down/method on gui
    # select via indexed teams
    team1 = int(input("Team 1: "))
    team2 = int(input("Team 2: "))

    # team1 & team2 are indexed in urls with corresponding team in urls.txt
    getTeams(team1, team2)
