# =========================================================================== #

#%% ========================================================================= #

import pandas as pd
import numpy as np


#%% ========================================================================= #
# functions

def get_csv(filename):
    p = 'data/' + filename + '.csv'
    f_df = pd.read_csv(p)
    print(p, ' --> ', f_df.shape, '\n', f_df.dtypes, '\n', sep='')
    return f_df


def tally(f_df, f_col, export=False):
    doot = f_df.groupby(f_col).size().sort_values(ascending=False)\
        .reset_index(name='count')

    if export:
        doot.to_csv('tally.csv', index=False)
    else:
        print(doot, '\n')


def df_info(name, df):
    print('\n', name, ' --> ', df.shape, df.dtypes, '\n', sep='')


def add_id_yr(df):
    df['id_yr'] = (df['player_id'] + '-'
                   + df['year'].apply(str))


def add_player_metrics(df, prefix):
    prefix_col = prefix + 'id_yr'
    add_id_yr(df)
    metrics = df.groupby(['id_yr'], as_index=False).sum()
    metrics = metrics.add_prefix(prefix)
    metrics.rename(columns={prefix_col: 'id_yr'}, inplace=True)
    doot = players.merge(metrics, on='id_yr', how='left')
    return doot


#%% ========================================================================= #
# import csv files

appearances = get_csv('appearances')
batting = get_csv('batting')
fielding = get_csv('fielding')
og_people = get_csv('og_people')
pitching = get_csv('pitching')
salaries = get_csv('salaries')
teams = get_csv('og_teams')


#%% ========================================================================= #
# create field name dictionaries

appearances_dict = {
    'yearID': 'year',
    'teamID': 'team_id',
    'lgID': 'x1',
    'playerID': 'player_id',
    'G_all': 'total_games',
    'GS': 'x2',
    'G_batting': 'x3',
    'G_defense': 'x4',
    'G_p': 'g_pos_pitcher',
    'G_c': 'g_pos_catcher',
    'G_1b': 'g_pos_first_base',
    'G_2b': 'g_pos_second_base',
    'G_3b': 'g_pos_third_base',
    'G_ss': 'g_pos_shortstop',
    'G_lf': 'g_pos_left_field',
    'G_cf': 'g_pos_center_field',
    'G_rf': 'g_pos_right_field',
    'G_of': 'x5',
    'G_dh': 'x6',
    'G_ph': 'x7',
    'G_pr': 'x8'
}

batting_dict = {
    'playerID': 'player_id',
    'yearID': 'year',
    'stint': 'x1',
    'teamID': 'team_id',
    'lgID': 'x2',
    'G': 'games_played',
    'AB': 'at_bats',
    'R': 'runs_scored',
    'H': 'hits',
    '2B': 'doubles',
    '3B': 'triples',
    'HR': 'homeruns',
    'RBI': 'runs_batted_in',
    'SB': 'stolen_bases',
    'CS': 'caught_stealing',
    'BB': 'x3',
    'SO': 'strikeouts',
    'IBB': 'intentional_walks',
    'HBP': 'hit_by_pitch',
    'SH': 'sacrifice_hits',
    'SF': 'sacrifice_flies',
    'GIDP': 'x4'
}

fielding_dict = {
    'playerID': 'player_id',
    'yearID': 'year',
    'stint': 'stint',
    'teamID': 'team_id',
    'lgID': 'x1',
    'POS': 'position',
    'G': 'games_played',
    'GS': 'games_started',
    'InnOuts': 'outs_played',
    'PO': 'x2',
    'A': 'assists',
    'E': 'errors',
    'DP': 'double_plays',
    'PB': 'x4',
    'WP': 'x5',
    'SB': 'opp_stolen_bases_bc',
    'CS': 'opp_caught_stealing_bc',
    'ZR': 'x3'
}

people_dict = {
    'playerID': 'player_id',
    'birthYear': 'birth_year',
    'birthMonth': 'birth_month',
    'birthDay': 'birth_day',
    'birthCountry': 'birth_country',
    'birthState': 'birth_state',
    'birthCity': 'birth_city',
    'deathYear': 'x1',
    'deathMonth': 'x2',
    'deathDay': 'x3',
    'deathCountry': 'x4',
    'deathState': 'x5',
    'deathCity': 'x6',
    'nameFirst': 'first_name',
    'nameLast': 'last_name',
    'nameGiven': 'x7',
    'weight': 'weight',
    'height': 'height',
    'bats': 'batting_hand',
    'throws': 'throwing_hand',
    'debut': 'career_first_game',
    'finalGame': 'career_last_game',
    'retroID': 'x8',
    'bbrefID': 'x9'
}

pitching_dict = {
    'playerID': 'player_id',
    'yearID': 'year',
    'stint': 'stint',
    'teamID': 'team_id',
    'lgID': 'x1',
    'W': 'wins',
    'L': 'loses',
    'G': 'games_played',
    'GS': 'x2',
    'CG': 'x3',
    'SHO': 'shutouts',
    'SV': 'saves',
    'IPouts': 'outs_pitched',
    'H': 'hits',
    'ER': 'earned_runs',
    'HR': 'homeruns',
    'BB': 'walks',
    'SO': 'strikeouts',
    'BAOpp': 'opponent_batting_avg',
    'ERA': 'earned_run_avg',
    'IBB': 'intentional_walks',
    'WP': 'wild_pitches',
    'HBP': 'hit_by_pitch',
    'BK': 'balks',
    'BFP': 'batters_faced',
    'GF': 'x4',
    'R': 'x5',
    'SH': 'x6',
    'SF': 'x7',
    'GIDP': 'x8'
}

salaries_dict = {
    'yearID': 'year',
    'teamID': 'team_id',
    'lgID': 'league_id',
    'playerID': 'player_id',
    'salary': 'salary'
}

teams_dict = {
    'yearID': 'year',
    'lgID': 'league_id',
    'teamID': 'team_id',
    'franchID': 'x1',
    'divID': 'x2',
    'Rank': 'season_rank',
    'G': 'games_played',
    'Ghome': 'x3',
    'W': 'wins',
    'L': 'loses',
    'DivWin': 'division_win',
    'WCWin': 'wild_card_win',
    'LgWin': 'league_win',
    'WSWin': 'world_series_win',
    'R': 'runs_scored',
    'AB': 'total_at_bats',
    'H': 'total_hits',
    '2B': 'doubles',
    '3B': 'triples',
    'HR': 'homeruns',
    'BB': 'walks_by_batters',
    'SO': 'strikeouts_by_batters',
    'SB': 'stolen_bases',
    'CS': 'caught_stealing',
    'HBP': 'batters_hit_by_pitch',
    'SF': 'sacrifice_flies',
    'RA': 'opponents_runs_scored',
    'ER': 'earned_runs_allowed',
    'ERA': 'earned_run_avg',
    'CG': 'completed_games',
    'SHO': 'shutouts',
    'SV': 'saves',
    'IPouts': 'outs_pitched',
    'HA': 'hits_allowed',
    'HRA': 'homeruns_allowed',
    'BBA': 'walks_allowed',
    'SOA': 'strikeouts_by_pitchers',
    'E': 'errors',
    'DP': 'double_plays',
    'FP': 'fielding_percentage',
    'name': 'team_name',
    'park': 'park_name',
    'attendance': 'x4',
    'BPF': 'x5',
    'PPF': 'x6',
    'teamIDBR': 'x7',
    'teamIDlahman45': 'x8',
    'teamIDretro': 'x9'
}


#%% ========================================================================= #
# rename columns

appearances.rename(columns=appearances_dict, inplace=True)
batting.rename(columns=batting_dict, inplace=True)
fielding.rename(columns=fielding_dict, inplace=True)
og_people.rename(columns=people_dict, inplace=True)
pitching.rename(columns=pitching_dict, inplace=True)
salaries.rename(columns=salaries_dict, inplace=True)
teams.rename(columns=teams_dict, inplace=True)

df_info('appearances', appearances)
df_info('batting', batting)
df_info('fielding', fielding)
df_info('og_people', og_people)
df_info('pitching', pitching)
df_info('salaries', salaries)
df_info('teams', teams)

del appearances_dict, batting_dict, fielding_dict, people_dict, pitching_dict
del salaries_dict, teams_dict


#%% ========================================================================= #
# drop unwanted columns

for x in ['x1', 'x2', 'x3', 'x4', 'x5', 'x6', 'x7', 'x8', 'x9']:
    if x in appearances.columns:
        appearances.drop(columns=[x], inplace=True)
    if x in batting.columns:
        batting.drop(columns=[x], inplace=True)
    if x in fielding.columns:
        fielding.drop(columns=[x], inplace=True)
    if x in og_people.columns:
        og_people.drop(columns=[x], inplace=True)
    if x in pitching.columns:
        pitching.drop(columns=[x], inplace=True)
    if x in salaries.columns:
        salaries.drop(columns=[x], inplace=True)
    if x in teams.columns:
        teams.drop(columns=[x], inplace=True)

print('\nappearances: \n', appearances.columns, '\n')
print('\nbatting: \n', batting.columns, '\n')
print('\nfielding: \n', fielding.columns, '\n')
print('\nog_people: \n', og_people.columns, '\n')
print('\npitching: \n', pitching.columns, '\n')
print('\nsalaries: \n', salaries.columns, '\n')
print('\nteams: \n', teams.columns, '\n')

del x


#%% ========================================================================= #
# create new people df

people_cols = [
    'player_id', 'birth_year', 'birth_month', 'birth_day', 'birth_country',
    'birth_state', 'birth_city', 'first_name', 'last_name', 'weight', 'height',
    'batting_hand', 'throwing_hand', 'career_first_game', 'career_last_game'
]

people = og_people[people_cols].copy()
df_info('people', people)

del people_cols, og_people


#%% ========================================================================= #
# correct birth fields in people df

for col in ['birth_year', 'birth_month', 'birth_day']:
    people[col] = people[col].apply(str)
    people[col] = people[col].str.replace('.0', '', regex=False)
    people[col] = people[col].str.pad(2, side='left', fillchar='0')

people['birth_date'] = (people['birth_year']
                        + people['birth_month']
                        + people['birth_day'])

del col


#%% ========================================================================= #
# combine player name fields in people df

people['player_name'] = (people['first_name'] + " " + people['last_name'])


#%% ========================================================================= #
# add year and id_yr to people df

yrs = {
    'year': batting['year'].unique(),
    'key': 0
}

years = pd.DataFrame(data=yrs)
people['key'] = 0
people = people.merge(years, on='key', how='outer')
add_id_yr(people)

del yrs, years


#%% ========================================================================= #
# convert fields to datetimes

for col in ['career_first_game', 'career_last_game', 'birth_date']:
    people[col] = pd.to_datetime(people[col], errors='coerce')

del col


#%% ========================================================================= #
# create player df

player_cols = [
    'id_yr', 'player_id', 'year', 'birth_date', 'birth_country',
    'birth_state', 'birth_city', 'player_name', 'weight', 'height',
    'batting_hand', 'throwing_hand', 'career_first_game', 'career_last_game'
]

players = people[player_cols].copy()
df_info('players', players)

del player_cols, people


#%% ========================================================================= #
# add metrics from other dataframes to player df

# players + appearances
players = add_player_metrics(appearances, 'app_')
df_info('players + appearances', players)

# players + batting
players = add_player_metrics(batting, 'bat_')
df_info('players + batting', players)

# players + fielding
players = add_player_metrics(fielding, 'fld_')
df_info('players + fielding', players)

# players + pitching
players = add_player_metrics(pitching, 'pch_')
df_info('players + pitching', players)

# players + salaries
players = add_player_metrics(salaries, 'sal_')
df_info('players + salaries', players)


#%% ========================================================================= #
# create singles (batting) metric

singles = (players['bat_hits']
           - players['bat_homeruns']
           - players['bat_triples']
           - players['bat_doubles'])

add_singles = players.columns.get_loc('bat_hits') + 1
players.insert(loc=add_singles, column='bat_singles', value=singles)

del singles, add_singles


#%% ========================================================================= #
# add team_id to players df

m1 = appearances[['id_yr', 'team_id']].copy()
m2 = batting[['id_yr', 'team_id']].copy()
m3 = fielding[['id_yr', 'team_id']].copy()
m4 = pitching[['id_yr', 'team_id']].copy()
m5 = salaries[['id_yr', 'team_id']].copy()

id_yr_team = pd.concat([m1, m2, m3, m4, m5], ignore_index=True)
id_yr_team.drop_duplicates(inplace=True)

players = players.join(id_yr_team.set_index('id_yr'), on='id_yr', how='left')

del m1, m2, m3, m4, m5, id_yr_team
del appearances, batting, fielding, pitching, salaries


#%% ========================================================================= #
# add team_name to players df

team_key = teams[['year', 'team_id', 'team_name']].copy()
team_key.drop_duplicates(inplace=True)

for df in [team_key, players]:
    df['key'] = (df['team_id'] + '-' + df['year'].apply(str))
    df['key'] = (df['team_id'] + '-' + df['year'].apply(str))

team_key.drop(columns=['team_id', 'year'], inplace=True)
players = players.join(team_key.set_index('key'), on='key', how='left')
players.drop(columns='key', inplace=True)

del df, team_key, teams


#%% ========================================================================= #
# remove records where most metrics are null

players['null_count'] = players.isnull().sum(axis=1)
mask = players['null_count'] < 50
players = players.loc[mask].reset_index(drop=True)
print(players.shape)

del mask


#%% ========================================================================= #
# remove any duplicate or unnecessary columns

drop_cols = [
    'app_year', 'bat_year', 'bat_games_played', 'fld_year', 'fld_stint', 
    'fld_games_played', 'fld_games_started', 'pch_year', 'pch_stint', 
    'pch_wins', 'pch_loses', 'pch_games_played', 'sal_year', 'null_count'
]

players.drop(columns=drop_cols, inplace=True)
print(players.columns)

del drop_cols


#%% ========================================================================= #
# create position column

pos_cols = [
    'app_g_pos_pitcher', 'app_g_pos_catcher', 'app_g_pos_first_base', 
    'app_g_pos_second_base', 'app_g_pos_third_base', 'app_g_pos_shortstop', 
    'app_g_pos_left_field', 'app_g_pos_center_field', 'app_g_pos_right_field'
]

players['max'] = players[pos_cols].max(axis=1)

conditions = [
    players['app_g_pos_pitcher'] == players['max'],
    players['app_g_pos_catcher'] == players['max'],
    players['app_g_pos_first_base'] == players['max'],
    players['app_g_pos_second_base'] == players['max'],
    players['app_g_pos_third_base'] == players['max'],
    players['app_g_pos_shortstop'] == players['max'],
    players['app_g_pos_left_field'] == players['max'],
    players['app_g_pos_center_field'] == players['max'],
    players['app_g_pos_right_field'] == players['max']
]
results = [
    'Pitcher',
    'Catcher',
    'First Base',
    'Second Base',
    'Third Base',
    'Shortstop',
    'Left Field',
    'Center Field',
    'Right Field'
]

players['primary_position'] = np.select(conditions, results, default=np.nan)

players.drop(columns=pos_cols, inplace=True)
players.drop(columns=['max'], inplace=True)

del conditions, results, pos_cols

print(players.columns)


#%% ========================================================================= #
# create year (date)

players['year_date'] = (players['year'].apply(str) + '-01-01')
players['year_date'] = pd.to_datetime(players['year_date'], errors='coerce')

print(players.dtypes)


#%% ========================================================================= #
# rearrange columns

cols_to_move = [
    'id_yr', 'player_id', 'player_name', 'year', 'year_date', 'birth_date',
    'career_first_game', 'career_last_game', 'team_id', 'team_name',
    'primary_position', 'birth_country', 'birth_state', 'birth_city',
    'batting_hand', 'throwing_hand'
]

players = players[cols_to_move
                  + [col for col in players.columns if col not in cols_to_move]]

print(players.dtypes)

del cols_to_move


#%% ========================================================================= #
# remove records with no salary info

mask = players['sal_salary'] >= 0
players = players.loc[mask].reset_index(drop=True)

del mask


#%% ========================================================================= #
# clean up column names

final_col_dict = {
    'id_yr': 'PlayerID-Year',
    'player_id': 'PlayerID',
    'player_name': 'Player Name',
    'year': 'Year',
    'year_date': 'Year (Date)',
    'birth_date': 'Birth Date',
    'career_first_game': 'Career First Game',
    'career_last_game': 'Career Last Game',
    'team_id': 'TeamID',
    'team_name': 'Team Name',
    'primary_position': 'Primary Position',
    'birth_country': 'Birth Country',
    'birth_state': 'Birth State',
    'birth_city': 'Birth City',
    'batting_hand': 'Batting Hand',
    'throwing_hand': 'Throwing Hand',
    'weight': 'Weight',
    'height': 'Height',
    'app_total_games': 'Total Appearances',
    'bat_at_bats': 'Total At-Bats (batting)',
    'bat_runs_scored': 'Runs Scored (batting)',
    'bat_hits': 'Hits-Total (batting)',
    'bat_singles': 'Hits-Singles (batting)',
    'bat_doubles': 'Hits-Doubles (batting)',
    'bat_triples': 'Hits-Triples (batting)',
    'bat_homeruns': 'Hits-Homeruns (batting)',
    'bat_runs_batted_in': 'Runs Batted In (batting)',
    'bat_stolen_bases': 'Stolen Bases (batting)',
    'bat_caught_stealing': 'Caught Stealing (batting)',
    'bat_strikeouts': 'Strikeouts (batting)',
    'bat_intentional_walks': 'Intentional Walks (batting)',
    'bat_hit_by_pitch': 'Hit by Pitch (batting)',
    'bat_sacrifice_hits': 'Sacrifice Hits (batting)',
    'bat_sacrifice_flies': 'Sacrifice Flies (batting)',
    'fld_outs_played': 'Outs Played (fielding)',
    'fld_assists': 'Assists (fielding)',
    'fld_errors': 'Errors (fielding)',
    'fld_double_plays': 'Double Plays (fielding)',
    'fld_opp_stolen_bases_bc': 'Opponent Stolen Bases (fielding)',
    'fld_opp_caught_stealing_bc': 'Opponent Caught Stealing (fielding)',
    'pch_shutouts': 'Shutouts (pitching)',
    'pch_saves': 'Saves (pitching)',
    'pch_outs_pitched': 'Outs Played (pitching)',
    'pch_hits': 'Opponent Hits (pitching)',
    'pch_earned_runs': 'Opponent Earned Runs (pitching)',
    'pch_homeruns': 'Opponent Homeruns (pitching)',
    'pch_walks': 'Walks (pitching)',
    'pch_strikeouts': 'Strikeouts (pitching)',
    'pch_opponent_batting_avg': 'Opponent Batting Avg (pitching)',
    'pch_earned_run_avg': 'Opponent Earned Run Avg (pitching)',
    'pch_intentional_walks': 'Intentional Walks (pitching)',
    'pch_wild_pitches': 'Wild Pitches (pitching)',
    'pch_hit_by_pitch': 'Hit by Pitch (pitching)',
    'pch_balks': 'Balks (pitching)',
    'pch_batters_faced': 'Batters Faced (pitching)',
    'sal_salary': 'Salary'
}

players.rename(columns=final_col_dict, inplace=True)
print(players.columns)

del final_col_dict


#%% ========================================================================= #
# export dataframes

players.to_csv('data/clean/players-v2.csv', index=False)





''' ____                           ______                __
   / __ )_________  ____  ____ ___/_  __/___  ____ _____/ /
  / __  / ___/ __ \/ __ \/_  // _ \/ / / __ \/ __ `/ __  / 
 / /_/ / /  / /_/ / / / / / //  __/ / / /_/ / /_/ / /_/ /  
/_____/_/   \____/_/ /_/ /___|___/_/  \____/\__,_/\__,_/ '''