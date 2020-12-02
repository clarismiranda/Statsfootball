#!/bin/bash
echo "Season: $1"
echo "Window: $2"

python maps_teams_stats.py GB 39 $1 10 $2
python maps_teams_stats.py ES 140 $1 11 $2
python maps_teams_stats.py DE 78 $1 9 $2
python maps_teams_stats.py IT 135 $1 9 $2
python maps_teams_stats.py FR 61 $1 12 $2
python maps_teams_stats.py NL 88 $1 10 $2
python maps_teams_stats.py PT 94 $1 9 $2
python maps_teams_stats.py BE 144 $1 14 $2

python maps_fixtures_stats.py GB 39 $1 10 $2
python maps_fixtures_stats.py ES 140 $1 11 $2
python maps_fixtures_stats.py DE 78 $1 9 $2
python maps_fixtures_stats.py IT 135 $1 9 $2
python maps_fixtures_stats.py FR 61 $1 12 $2
python maps_fixtures_stats.py NL 88 $1 10 $2
python maps_fixtures_stats.py PT 94 $1 9 $2
python maps_fixtures_stats.py BE 144 $1 14 $2