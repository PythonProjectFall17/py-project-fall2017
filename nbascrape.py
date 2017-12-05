# python project fall 2017
# scrape/parsing
# initial

from lxml import html
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
    # All Player Stats
    # Tests
    print("\n")
    print("Roster Player (1): " + str(data1[0][0][1]) + ", Team: " + str(data1[0][0][2]))
    print("Team Stats for " + str(data1[0][0][2]) + ": " + str(data1[1][0]))
    print("Team Splits (one game) for " + str(data1[0][0][2]) + " " + str(data1[2][0]))

    print("\n")
    print("Roster Player(1): " + str(data2[0][0][1]) + ", Team: " + str(data2[0][0][2]))
    print("Team Stats for " + str(data2[0][0][2]) + ": " + str(data2[1][0]))
    print("Team Splits (one game) for " + str(data2[0][0][2]) + " " + str(data2[2][0]))


    print("\nTeam 1: " + str(team1id) + ", Team 2: " + str(team2id))
    # use team1id and team2id to get teams from depth charts
    depth_charts = findDepths()

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





