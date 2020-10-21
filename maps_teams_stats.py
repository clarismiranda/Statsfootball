"""
	This script generates a CSV up to a given week and season
	from teams' standings retrieved on APIFootball
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
curr_standings = None

# Principal leagues are sorted ascendent
dirLeague = sorted(os.listdir(dirCountry))

for league in dirLeague:
    if league == ".DS_Store":
        continue
    if "csv" in league:
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
            if season == start_season:
            	curr_week = int(week)
            else:
            	curr_week = 38
            c_w = list(range(curr_week, -1, -1))
            i_w = 0
            while curr_standings == None:
                we = c_w[i_w]
                json_standings = dirTeam + team_id + '_' + str(we) + '.json'
                try:
                    with open(json_standings) as f:
                        curr_standings = json.load(f)
                except:
                    print("id= %s, w=%s" % (team_id, str(we)))
                i_w = i_w + 1
            # Adding league
            curr_standings.update({"league": int(league)})
            # Adding season
            curr_standings.update({"season": season})
            # Adds current standing to dataframe
            df = df.append(json_normalize(curr_standings))
            curr_standings = None
        
        # csv to save
        file_title = str(season) + '.csv'
        csv_file = dirName + file_title
        print(csv_file)
        df.to_csv(csv_file)
        df = pd.DataFrame()