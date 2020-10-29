"""
	This script generates a CSV up to a given week and season
	from fixture's statistics mapped to team's standings retrieved from APIFootball
"""

import json
import os
import sys
import pandas as pd
from pandas import json_normalize

if len(sys.argv) > 5:
	# Setting country and season from system arguments
    country = sys.argv[1]
    league = sys.argv[2]
    season = sys.argv[3]
    # This is the last week played on the league
    week = sys.argv[4]
    # This is how many years from the starting season to retrieve
    window = sys.argv[5]
else:
    print("Wrong arguments were given, expected: --country --league --season --week --window")

# Dealing with historicity
curr_week = int(week)
year_window = int(window)
start_season = int(season)
seasons = list(range(start_season, start_season - year_window, -1))

# League directory
dirCountry = '../' + country + '/'
dirName = dirCountry + league + '/'

df = pd.DataFrame()
standings = None
curr_standings = None
away_team_stands = None
fixture = None
# This will prevent duplicated fixtures
visited_fixtures = []
# This will help to map to standings to week: team : stands
visited_standings = {}
# Easy access to last standings
current_standings = {}

# Principal leagues are sorted ascendent
dirLeague = sorted(os.listdir(dirCountry))

for league in dirLeague:
    if league == ".DS_Store":
        continue
    if "csv" in league:
        continue
    if ".json" in league:
        continue
    for season in seasons:
        dirName = dirCountry + league + '/' + str(season) + '/' 
        for subdir in os.listdir(dirName):
            if subdir == ".DS_Store":
                continue
            if subdir == "teams.json":
                continue
            if ".csv" in subdir:
                continue
            team_id = subdir
            # Entering directory of a team
            dirTeam = dirName + team_id + '/'
            
            # Initializes all current standings
            c_w = list(range(curr_week, -1, -1))
            i_w = 0
            while team_id not in current_standings:
                we = c_w[i_w]
                json_standings = dirTeam + team_id + '_' + str(we) + '.json'
                try:
                    with open(json_standings) as f:
                        curr_standings = json.load(f)
                        current_standings[team_id] = curr_standings
                except:
                    print("id= %s, w=%s" % (team_id, str(we)))
                i_w = i_w + 1
            curr_standings = current_standings[team_id]
            
            # Gets standings from a team if they have not being added
            for week in list(range(0, 38, 1)):
                week = str(week)
                if week not in visited_standings:
                    visited_standings[week] = {}
                    if team_id not in visited_standings[week]:
                        try:
                            json_standings = dirTeam + team_id + '_' + week + '.json'
                            with open(json_standings) as f:
                                standings = json.load(f)
                                visited_standings[week][team_id] = standings
                        except:
                            visited_standings[week][team_id] = curr_standings
                            standings = curr_standings

            # Directory of team in home
            dirHome = dirTeam + 'home/'
            for file in os.listdir(dirHome):
                # Check if fixture hasn't being added to dataframe
                if file not in visited_fixtures:
                    path = dirHome + file
                    with open(path) as f:
                        fixture = json.load(f)
                        # Adds id of fixture as "id_fixture.json"
                        visited_fixtures.append(file)
                        # Next, get away team's external info
                        away_team = str(fixture["team_away"]["id"])
                        w = fixture["week"]
                        w = ''.join(filter(str.isdigit, w))
                        # Case when is europa classifiers
                        if w == '':
                            continue
                        # Gets standings from away_team
                        if away_team in visited_standings[w]:
                            away_team_stands = visited_standings[w][away_team]
                        else:
                            try:
                                fileAwayTeam = dirName + away_team + '/' + away_team + '_' + week + '.json'
                                with open(fileAwayTeam) as f:
                                    away_team_stands = json.load(f)
                                    visited_standings[w][away_team] = away_team_stands
                            except:
                                i_w = 0
                                while away_team not in current_standings:
                                    we = c_w[i_w]
                                    fileAwayTeam = dirName + away_team + '/' + away_team + '_' + str(we) + '.json'
                                    try:
                                        with open(fileAwayTeam) as f:
                                            away_team_stands = json.load(f)
                                            visited_standings[w][away_team] = away_team_stands
                                            current_standings[away_team] = away_team_stands
                                    except:
                                        print("id= %s, w=%s" % (away_team, str(we)))
                                    i_w = i_w + 1
                        # Home team standings
                        if team_id in visited_standings[w]:
                            standings = visited_standings[w][team_id]
                        else:
                            standings = current_standings[team_id]
                        # Gets away current standings if fixtures is set to null
                        if fixture["goals_away"] is None:
                            away_team_stands = current_standings[away_team]
                            # Changes if game to be played
                            standings = current_standings[team_id]
                        else:
                            if away_team in visited_standings[w]:
                                away_team_stands = visited_standings[w][away_team]
                            else:
                                away_team_stands = current_standings[away_team]
                    # Three main jsons to a dataframe
                    # standings "this is the home team"
                    # away_team_stands
                    # the fixture itself
                    # The premise that away standings from home team aren't relevant
                    try:
                        #del standings['stats_away']
                        fixture.update({"team_home": standings})
                    except:
                        print("Couldn't delete stats away")
                    # The premise that home standings from away team aren't relevant
                    try:
                        #del away_team_stands['stats_home']
                        fixture.update({"team_away": away_team_stands})
                    except:
                        print("Couldn't delete stats home")
                    # Adding league
                    fixture.update({"league": int(league)})
                    # Adding season
                    fixture.update({"season": season})
                    df = df.append(json_normalize(fixture))
                else:
                    continue
        # Initializes all current standings
        if season == int(start_season):
            curr_week = int(week)
        else:
            curr_week = 38
        # csv to save
        file_title = str(season) + '_' + str(curr_week) + '.csv'
        csv_file = dirName + file_title
        print(csv_file)
        df.to_csv(csv_file)
        df = pd.DataFrame()
        standings = None
        curr_standings = None
        away_team_stands = None
        fixture = None
        visited_fixtures = []
        visited_standings = {}
        current_standings = {}