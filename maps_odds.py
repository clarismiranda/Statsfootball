"""
	This script generates a CSV up to a given week and season
	from teams' standings retrieved on APIFootball
"""

import json
import os
import sys
import pandas as pd
from pandas import json_normalize

if len(sys.argv) > 2:
    # Which season to include
    season = sys.argv[1]
    # This is how many years from the starting season to retrieve
    window = sys.argv[2]
else:
    print("Wrong arguments were given, expected: --season --window")

# Dealing with historicity
start_season = int(season)
year_window = int(window)
seasons = list(range(start_season, start_season - year_window, -1))

# League directory
dirCountry = '../' + 'Odds' + '/'

df = pd.DataFrame()
curr_odds = None

# Principal leagues are sorted ascendent
dirLeague = sorted(os.listdir(dirCountry))

for league in dirLeague:
    if league == ".DS_Store":
        continue
    if "csv" in league:
        continue
    for season in seasons:
        dirName = dirCountry + league + '/' + str(season) + '/' 
        for odd in os.listdir(dirName):
            if odd == ".DS_Store":
                continue
            if ".csv" in odd:
                continue
            try:
                file_name = dirName + odd
                with open(file_name) as f:
                    curr_odds = json.load(f)
            except:
                print("id= %s, w=%s" % (odd))
            # Adds current odds to dataframe
            df = df.append(json_normalize(curr_odds))
            curr_odds = None
        
# csv to save
file_title = str(season) + '_odds'+ '.csv'
csv_file = dirCountry + file_title
print(csv_file)
df.to_csv(csv_file, index=False)
df = pd.DataFrame()