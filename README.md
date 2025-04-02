# ⚾ Pitcher vs Batter Matchup Analyzer

This internal scouting tool compares MLB pitchers and batters based on real-time Statcast data pulled from Baseball Savant using the `pybaseball` API.

## Features
- Pulls pitcher + batter data live using names
- Calculates K%, PutAway%, Whiff%, SLG, OBA, and BA
- Computes per-pitch delta metrics and highlights edge matchups
- Downloads tables as CSV or Excel
- Defaults to current date (NY Eastern) for easy daily usage

## Deployment
This app is deployed privately via [Render](https://render.com) using `render.yaml`. It supports caching and multi-season input.

## Requirements
See `requirements.txt`
