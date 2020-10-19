import numpy as np
import pandas as pd

# Set win as 1, draw as 0 and lose as -1
def get_status(r):
    goals_home = r["goals_home"]
    goals_away = r["goals_away"]
    if goals_home > goals_away:
        return 1
    elif goals_home == goals_away:
        return 0
    else:
        return -1

def get_target(df):
    # status_home: either win, draw or lose for home team, predicted label
    target = []
    for index, row in df.iterrows():
        target.append(get_status(row))
    return target

def clean_data(df):
    df = df.drop(df.columns[0], axis=1)
    df = df.drop(columns=["league","id"], axis=1)
    df["home_team.id"] = df["team_home.team.id"]
    df["away_team.id"] = df["team_away.team.id"]
    df["home_team.name"] = df["team_home.team.name"]
    df["away_team.name"] = df["team_away.team.name"]
    # Just fixtures statistics
    df = df.drop(df.filter(regex='team_away').columns, axis=1)
    df = df.drop(df.filter(regex='team_home.').columns, axis=1)
    df["stats_away.p_percentage"] = df["stats_away.p_accurate"]/df["stats_away.p_total"]
    df["stats_home.p_percentage"] = df["stats_home.p_accurate"]/df["stats_home.p_total"]
    # None values set to 0
    df.fillna(value=0, inplace=True)
    # Posession % to decimal
    df["stats_away.possession"] = df["stats_away.possession"].apply(lambda x: (int(str(x).strip('%'))/100))
    df["stats_home.possession"] = df["stats_home.possession"].apply(lambda x: (int(str(x).strip('%'))/100))
    return df

def df_season(country, league, season, week, drop_goals=True):
    dirCountry = '../' + country + '/'
    dirName = dirCountry + league + '/' + str(season) + '/'
    file_title = str(season) + '_' + str(week) + '.csv'
    csv_file = dirName + file_title
    df = pd.read_csv(csv_file)
    df = clean_data(df)
    target = get_target(df)
    if drop_goals:
        df = df.drop(columns=["goals_away","goals_home"], axis=1) 
    return df, target

def get_all(data):
    all_data = pd.DataFrame()
    all_target = []
    for d in data:
        all_data = all_data.append(d[1])
        all_target = all_target + d[2]
    return all_data, all_target

#pezzali score goals(team)/attempts(team) x attempts(opponent)/goals(opponent)
def pezzali_data(data, is_train=True, both=False):
	new_data = pd.DataFrame()
	values = {'goal_home': 0, 'goals_away': 0}
	data.fillna(value=values)
	data.reset_index(inplace=True)
	pezzali_diff = []
	shots_fraction = []
	for index, row in data.iterrows():
		att_home = row["stats_home.s_off_g"] + row["stats_home.s_on_g"] + 1
		h_home = (row["goals_home"] + 1)/att_home
		att_away = row["stats_away.s_off_g"] + row["stats_away.s_on_g"] + 1
		h_away = att_away/(row["goals_away"] + 1)
		p_home = h_home * h_away
		a_away = (row["goals_away"] + 1)/att_away
		a_home = att_home/(row["goals_home"] + 1)
		p_away = a_away * a_home
		diff_p = p_home - p_away
		sf_home = (row["stats_home.s_in"]+1)/(row["stats_home.s_in"]+row["stats_home.s_out"]+1)
		sf_away = (row["stats_away.s_in"]+1)/(row["stats_away.s_in"]+row["stats_away.s_out"]+1)
		diff_sf = sf_home - sf_away
		pezzali_diff.append(diff_p)
		shots_fraction.append(diff_sf)
	new_data["home_team.id"] = data["home_team.id"]
	new_data["away_team.id"] = data["away_team.id"]
	new_data["diff_pezzali"] = pezzali_diff
	new_data["diff_s_fraction"] = shots_fraction
	new_data["diff_defensive"] = ((data["stats_home.s_blocked"]+.01)/(data["stats_away.s_total"]+.01)) - ((data["stats_away.s_blocked"]+.01)/(data["stats_home.s_total"]+.01))
	new_data["stats_home.c_red"] = data["stats_home.c_red"]
	new_data["diff_s_off_g"] = data["stats_home.s_off_g"]-data["stats_away.s_off_g"]
	new_data["diff_s_total"] = data["stats_home.s_total"]-data["stats_away.s_total"]
	new_data["diff_s_out"] = data["stats_home.s_out"]-data["stats_away.s_out"]
	new_data["diff_saves"] = data["stats_home.saves"]-data["stats_away.saves"]
	new_data["stats_home.s_blocked"] = data["stats_home.s_blocked"]
	new_data["stats_away.s_blocked"] = data["stats_away.s_blocked"]
	new_data["season"] = data["season"]
	new_data["week"] = data["week"]
	if both == True:
		data["diff_pezzali"] = pezzali_diff
		data["diff_s_fraction"] = shots_fraction
		data["diff_defensive"] = ((data["stats_home.s_blocked"]+.01)/(data["stats_away.s_total"]+.01)) - ((data["stats_away.s_blocked"]+.01)/(data["stats_home.s_total"]+.01))
		data["diff_s_off_g"] = data["stats_home.s_off_g"]-data["stats_away.s_off_g"]
		data["diff_s_total"] = data["stats_home.s_total"]-data["stats_away.s_total"]
		data["diff_s_out"] = data["stats_home.s_out"]-data["stats_away.s_out"]
		data["diff_saves"] = data["stats_home.saves"]-data["stats_away.saves"]
		return data
	if is_train:
		new_data["home_team.name"] = data["home_team.name"]
		new_data["away_team.name"] = data["away_team.name"]
	return new_data