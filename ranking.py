from sklearn import preprocessing
from scipy.cluster.hierarchy import linkage, cophenet, dendrogram
from scipy.spatial.distance import pdist
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

class Attr:
    def __init__(self, name, value, value2=None, value3=None):
        #This is the name of the team
        self.name = self.new_name(name)
        # This is the cluster value
        self.value = value
        # This is the id of the team
        self.value2 = self.val2(name)
        # This is the season
        self.value3 = self.val3(name)
    def __str__(self):
        st = "name: " + self.name + ", value: " + str(self.value)
        if self.value2 != None:
            st = st + ", value2: " + str(self.value2)
        if self.value3 != None:
            st = st + ", value3: " + str(self.value3)
        return st
    def new_name(self, name):
        return name[3:]
    def val2(self, name):
        return name[0:3]
    def val3(self, name):
        return name[-4:]

def get_value(attr):
    """
        Returns: the attribute value of the class Attr
        which is the cluster
    """
    return attr.value

def sorted_class(names, values, color=None):
    """
        Returns: a list of names and values sorted (the cluster)
    """
    attrs = []
    for i in range(0, len(names)):
        attrs.append(Attr(names[i], values[i]))
    # Sorts by attribute value
    attrs.sort(key=get_value)
    new_names = []
    new_values = []
    # Divides the names from the values
    for i in range(0, len(names)):
        new_names.append(attrs[i].name)
        new_values.append(attrs[i].value)
    return new_names, new_values

def encode_data(df, df_column):
    """
        Returns: a numerical encoded column from its categorical value
                df_column is the column to encode
    """
    elements = np.unique(df[df_column].astype(str))
    print(len(elements))
    print(elements)
    enc = preprocessing.LabelEncoder()
    enc.fit(elements)
    return enc.transform(df[df_column].astype(str))

def encode_description(row):
    """
        Returns: the numerical value of a description
    """
    label = {'Promotion - Champions League (Group Stage)': 1, 
             'UEFA Champions League': 1,
             'UEFA Champions League Qualifiers': 2,
             'Promotion - Europa League (Group Stage)': 3,
             'UEFA Europa League': 3,
             'Promotion - Europa League (Qualification)': 4,
             'nan': 5,
             'Relegation - LaLiga2': 6,
             'Relegation': 6
            }
    # If it doesn't have a promotion return regular team 5
    if row in label:
        return label[row]
    else:
        return 5

def decode_description(row):
    """
        Returns: the categorical value of a description
    """
    label = {1: 'Promotion - Champions League (Group Stage)', 
             1: 'UEFA Champions League',
             2: 'UEFA Champions League Qualifiers',
             3: 'Promotion - Europa League (Group Stage)',
             3: 'UEFA Europa League',
             4: 'Promotion - Europa League (Qualification)',
             5: 'None',
             6: 'Relegation - LaLiga2',
             6: 'Relegation',
            }
    # If it is a regular team returns 5
    if row in label:
        return label[row]
    else:
        return 'None'

def score_home(best):
    """
        Returns: the value of the best streaks for home team on scores
    """
    if best != 0:
        return int(best[0]) - int(best[2])
    return best

def score_away(best):
    """
        Returns: the value of the best streaks for away team on scores
    """
    if best != 0:
        return int(best[2]) - int(best[0])
    return best

def clean_data(df, clean_type=None):
    """
        Returns: a clean dataframe with numerical values
    """
    df = df.drop(df.columns[0], axis=1)
    # Ratio of games lose/played, draws/played
    df["stats_away.lose"] = df["stats_away.lose"]/df["stats_away.played"]
    df["stats_away.draws"] = df["stats_away.draws"]/df["stats_away.played"]
    df["stats_home.lose"] = df["stats_home.lose"]/df["stats_home.played"]
    df["stats_home.draws"] = df["stats_home.draws"]/df["stats_home.played"]
    df = df.drop(columns=["team.id", "team.name","season","league","goals_diff","form","group","stats_home.played","stats_away.played",
                          "stats_home.wins", "stats_away.wins", "stats_home.goals_for", "stats_home.goals_against",
                         "stats_away.goals_for", "stats_away.goals_against"], axis=1)
    # Encode description (Promotion: either Champions, UEFA Europe, Second division)
    df["description"] = df["description"].apply(encode_description)
    # None values set to 0
    df.fillna(value=0, inplace=True)
    if clean_type == 'home':
        # Delete stats from away matches
        df = df.drop(df.filter(regex='stats_away').columns, axis=1)
        # For best_lose
        df["stats_home.streaks.best_lose"] = df["stats_home.streaks.best_lose"].apply(score_home)
        # For best_win
        df["stats_home.streaks.best_win"] = df["stats_home.streaks.best_win"].apply(score_home)
    elif clean_type == 'away':
        # Delete stats from away matches
        df = df.drop(df.filter(regex='stats_home').columns, axis=1)
        # For best_lose
        df["stats_away.streaks.best_lose"] = df["stats_away.streaks.best_lose"].apply(score_home)
        # For best_win
        df["stats_away.streaks.best_win"] = df["stats_away.streaks.best_win"].apply(score_home)
    else:
        # For best_lose
        df["stats_home.streaks.best_lose"] = df["stats_home.streaks.best_lose"].apply(score_home)
        df["stats_away.streaks.best_lose"] = df["stats_away.streaks.best_lose"].apply(score_away)
        # For best_win
        df["stats_home.streaks.best_win"] = df["stats_home.streaks.best_win"].apply(score_home)
        df["stats_away.streaks.best_win"] = df["stats_away.streaks.best_win"].apply(score_away)
    return df

def get_target(df, label):
    """
        Returns: a column from the specific label of the dataframe
    """
    target = []
    for index, row in df.iterrows():
        target.append(row[label])
    return target

def df_season(country, league, season, label, drop_others=None, clean_type=None):
    """
        Returns: the data of a given season and the names of the teams
                label is the list columns to keep as target
                drop_others a list of columns if neccesary to be removed
                clean_type is either Home/Away/None
    """
    dirCountry = '../' + country + '/'
    dirName = dirCountry + league + '/' + str(season) + '/'
    file_title = str(season) + '.csv'
    csv_file = dirName + file_title
    df = pd.read_csv(csv_file)
    df_names = df['team.id'].astype(str) + df['team.name']
    df_names = df_names.tolist()
    # Retrieve only the standings of the data of study (Home/Away)
    df = clean_data(df, clean_type)
    target = []
    # Saves the target
    for l in label:
        target = target + [get_target(df, l)]
    # Removes the target
    df = df.drop(columns=label, axis=1)
    # Extra columns to be remove
    if drop_others != None:
        df = df.drop(columns=drop_others, axis=1)
    return df, target, df_names

def concat_data(country, league, seasons, target_col, clean_type):
    """
        Returns: a list of data tuples in a year window
    """
    data = []
    # Creates a row for each season with the form of tuple (season, data, target, name)
    for season in seasons:
        df, target, name = df_season(country, league, season, target_col, clean_type=clean_type)
        tup = (season, df, target, name)
        data.append(tup)
    return data, df.columns

def get_all_data(data, target_n):
    """
    Returns: the list of data, seasons, team's name and the target in a year window
    """
    all_data = pd.DataFrame()
    all_season = []
    all_names = []
    all_target = [ [] for _ in range(target_n) ]
    for d in data:
        # The data frame of the season
        all_data = all_data.append(d[1])
        # Populates the season array with the actual season d[0]
        all_season = all_season + [d[0] for _ in range(len(d[1]))]
        # The names of the teams in d[3]
        all_names = all_names + d[3]
        i = 0
        # This is a 2D array of the given targets: ranking, points and promotion
        for target in d[2]:
            all_target[i] = all_target[i] + target
            i = i + 1
    return all_data, all_season, all_names, all_target

def label_team_season(all_names, all_season):
    """
    Returns: list of teams names with its season
    """
    dendo_label = []
    for i in range(len(all_season)):
        d_l = all_names[i] + " - " + str(all_season[i])
        dendo_label.append(d_l)
    return dendo_label

def dendogram_graph(data, best_method, label):
    """
    Plots the dendogram from Z linkage matrix
    """
    label = [l[3:] for l in label]
    # The resulting linkage of the best cophenetic distance
    Z = linkage(data, best_method)
    coph_matrix = cophenet(Z)
    fig = plt.figure(figsize=(25, 10))
    # Creates dendrogram
    dendo = dendrogram(Z, leaf_rotation=90, labels=label)
    plt.title(best_method)
    plt.show()
    return (Z, coph_matrix)

def HierarchicalClustering(data, label):
    """
    Finds the best linkage method and plots its dendogram
    Returns: Z linkage matrix, cophenet matrix and best cophenetic distance
    """
    methods = ["single","complete","average","centroid","ward"]
    # Pass the dataset into pdist to get your proximity matrix for calculating CPCC
    proximity_matrix = pdist(data)
    best_coph = -1
    best_method = None
    # For each linkage method finds its cophenetic distance
    for method in methods:
        Z = linkage(data, method)
        coph, coph_matrix = cophenet(Z, proximity_matrix)
        # Finds the minimum distance between clusters
        if coph > best_coph:
            best_coph = coph
            best_method = method
            best_matrix = coph_matrix
    final = dendogram_graph(data, best_method, label)
    return final[0], final[1], best_coph