# FootballMLP

FootballMLP is a framework which stands for Football Machine Learning Pipeline. By testing different Machine Learning Algorithms as well careffully studying football statistics, FootballMLP is able to predict football games and perform some extra tasks as described above.

## What I need to have?
Before using FootballMLP it is important to have the fixtures needed for the discriminating football results. Here is everything you need to install or perform previous executing the predictions.

### Python packages
FootballMLP needs the next libraries to work:
- [Matplotlib] - 2D graphics library
- [Numpy] - Scientific computation package
- [Scipy] - Mathematics and science environment
- [Sklearn] - Machine learning library
- [Seaborn] - Data visualization library

[Matplotlib]: <https://matplotlib.org/>
[Numpy]: <https://numpy.org/>
[Scipy]: <https://www.scipy.org/>
[Sklearn]: <https://scikit-learn.org/stable/>
[Seaborn]: <https://seaborn.pydata.org/>

### Where is the data?
Everything you want to retrieve can be find by using [API-Football](https://www.api-football.com/). But FootballMLP has released a library for it [apifootballpy](https://github.com/clarismiranda/apifootball/tree/lastFixtures)

### Dataset for Standings
This creates a whole dataset of teams' standings up to a season and a week (the last week played), the window parameter controls how many season before the current season wants to be save.\
python maps_teams_stats.py --country --league --season --week --window
```bash
python maps_teams_stats.py DE 78 2020 4 5
```
> Note: by using a window of 5, it is expected to save the standings from 2016 to 2020.

### Dataset for Fixtures
This creates a whole dataset of league's fixtures up to a season and a week (the last week played) mapped with the team's last standings, the window parameter controls how many season before the current season wants to be save.\
python maps_fixtures_stats.py --country --league --season --week --window
```bash
python maps_fixtures_stats.py DE 78 2020 4 5
```
> Note: by using a window of 5, it is expected to save the standings from 2016 to 2020.

## Testing FootballMLP

## Predicting with FootballMLP
