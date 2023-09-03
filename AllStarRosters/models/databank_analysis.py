import pandas as pd

import helpers.dataframe_utils as dfUtils
from helpers.enum_factory import DatabankDataType
from models.baseball_databank import BaseballDatabank

databankModel = BaseballDatabank()

pd.options.mode.chained_assignment = None
# =================================================================================================================== #

def add_key(dataframe: pd.DataFrame, key_name: str, key_cols: list) -> pd.DataFrame:
    df = dfUtils.copy(dataframe)
    missing_cols = []

    for key in key_cols:
        if key not in df.columns:
            missing_cols.append(key)

    if len(missing_cols) > 0:
        print(f'dataframe missing columns needed to create {key_name}: {missing_cols}')
        return dataframe
    else:
        df.insert(0, key_name, pd.NA)
        df[key_name] = df[key_cols].apply(lambda x: '-'.join(x.astype(str)), axis=1)
        return df


def add_player_key(dataframe: pd.DataFrame) -> pd.DataFrame:
    return add_key(dataframe, 'player_key', ['player_id', 'year_id'])


def add_team_key(dataframe: pd.DataFrame) -> pd.DataFrame:
    return add_key(dataframe, 'team_key', ['team_id', 'year_id'])


# =================================================================================================================== #

def to_Int64(dataframe, columns):
    df = dfUtils.copy(dataframe)
    cols = columns if isinstance(columns, list) else [columns]
    for col in cols:
        if col in df.columns:
            df[col] = df[col].round().astype('Int64')
    return df


def to_Float64(dataframe, columns):
    df = dfUtils.copy(dataframe)
    cols = columns if isinstance(columns, list) else [columns]
    for col in cols:
        if col in df.columns:
            df[col] = df[col].astype('Float64')
    return df


def to_datetime64(dataframe, columns):
    df = dfUtils.copy(dataframe)
    cols = columns if isinstance(columns, list) else [columns]
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    return df


def na_to_false(dataframe, columns):
    df = dfUtils.copy(dataframe)
    cols = columns if isinstance(columns, list) else [columns]
    for col in cols:
        if col in df.columns:
            df[col] = df[col].fillna(False).astype(bool)
    return df


def get_stats_agg_dict(agg_cols: list) -> dict:
    return {col: 'sum' for col in agg_cols}


def add_primary_position(dataframe: pd.DataFrame) -> pd.DataFrame:
    df = dfUtils.copy(dataframe)

    pos_col_map = {
        'games_pitcher'          : 'Pitcher',
        'games_catcher'          : 'Catcher',
        'games_first_base'       : 'First Base',
        'games_second_base'      : 'Second Base',
        'games_third_base'       : 'Third Base',
        'games_shortstop'        : 'Shortstop',
        'games_left_field'       : 'Left Field',
        'games_center_field'     : 'Center Field',
        'games_right_field'      : 'Right Field',
        'games_designated_hitter': 'Designated Hitter',
        'games_pinch_hitter'     : 'Pinch Hitter',
        'games_pinch_runner'     : 'Pinch Runner'
    }

    pos_cols = list(pos_col_map.keys())
    df[pos_cols] = df[pos_cols].fillna(0)

    for col in pos_cols:
        if col not in df.columns:
            return dataframe

    df['max'] = df[pos_cols].max(axis=1)
    df = to_Int64(df, 'max')

    for idx, row in df.iterrows():
        matches = []
        for col, val in row.items():
            if col in list(pos_cols):
                if val == df.at[idx, 'max']:
                    matches.append(col)

        df.at[idx, 'primary_position'] = pos_col_map.get(matches[0])

    df.drop(columns='max', inplace=True)

    return df


def add_prefix(dataframe, prefix, columns=None):
    df = dfUtils.copy(dataframe)

    if prefix is None:
        return df

    if columns is not None:
        columns = columns if isinstance(columns, list) else [columns]
    else:
        columns = df.columns

    exclude = [
        'player_key',
        'team_key',
        'player_id',
        'team_id',
        'year_id',
        'school_id',
        'franchise_id',
        'division_id'
    ]

    final_cols = []
    for c in columns:
        if c not in exclude:
            final_cols.append(c)

    for col in final_cols:
        if col in df.columns:
            df = df.rename(columns={
                col: prefix + col})

    return df


def dataframe_processor(dataframe: pd.DataFrame,
                        data_type: DatabankDataType) -> pd.DataFrame:
    df = dfUtils.copy(dataframe)
    df = dfUtils.update_headers(df, databankModel.get_headers(data_type.value))
    key_col = get_key_col(data_type)
    df = add_prefix(df, get_prefix(data_type))
    df = add_player_key(df) if key_col == 'player_key' else df
    df = add_team_key(df) if key_col == 'team_key' else df
    df = process_data(df, data_type)
    df = df[get_final_cols(data_type)]
    df = to_Int64(df, get_int_cols(data_type)) if get_int_cols(data_type) is not None else df
    df = to_Float64(df, get_float_cols(data_type)) if get_float_cols(data_type) is not None else df
    df = df.sort_values(key_col).drop_duplicates().reset_index(drop=True)
    return df


# =================================================================================================================== #

def get_final_cols(data_type: DatabankDataType) -> list:
    match data_type:
        case DatabankDataType.ALLSTAR:
            return [
                'player_key',
                'allstar_flag',
            ]
        case DatabankDataType.APPEARANCES:
            return [
                'player_id',
                'year_id',
                'team_id',
                'league_id',
                'primary_position',
                'total_games',
                'games_started',
                'games_batting',
                'games_defense',
                'games_pitcher',
                'games_catcher',
                'games_first_base',
                'games_second_base',
                'games_third_base',
                'games_shortstop',
                'games_left_field',
                'games_center_field',
                'games_right_field',
                'games_outfield',
                'games_designated_hitter',
                'games_pinch_hitter',
                'games_pinch_runner'
            ]
        case DatabankDataType.AWARDS:
            return [
                'player_key',
                'mvp_award',
                'rookie_oty_award'
            ]
        case DatabankDataType.COLLEGE:
            return [
                'player_id',
                'college_play_flag',
                'college_years_played',
                'college_name',
                'college_multiple'
            ]
        case DatabankDataType.HOF:
            return [
                'player_id',
                'hall_of_fame'
            ]
        case DatabankDataType.MANAGERS:
            return [
                'team_key',
                'manager_name',
                'manager_multiple'
            ]
        case DatabankDataType.PEOPLE:
            return [
                'player_id',
                'full_name',
                'first_name',
                'last_name',
                'weight',
                'height',
                'batting_hand',
                'throwing_hand',
                'debut_date',
                'final_game',
                'birth_country',
                'birth_state',
                'birth_city',
                'birth_date'
            ]
        case DatabankDataType.SALARIES:
            return [
                'player_key',
                'salary',
            ]
        case DatabankDataType.TEAMS:
            return [
                'team_key',
                'franchise_id',
                'division_id',
                'team_name',
                'franchise_name',
                'franchise_active',
                'team_home_park_name',
                'team_home_park_attendance',
                'team_home_park_factor_batter',
                'team_rank',
                'team_division_series',
                'team_wild_card_series',
                'team_league_series',
                'team_world_series'
            ]
        case DatabankDataType.REG_BATTING:
            return [
                'player_key',
                'batting_games_played',
                'batting_at_bats',
                'batting_runs',
                'batting_hits',
                'batting_doubles',
                'batting_triples',
                'batting_home_runs',
                'batting_runs_batted_in',
                'batting_stolen_bases',
                'batting_caught_stealing',
                'batting_base_on_balls',
                'batting_strikeouts',
                'batting_intentional_walks',
                'batting_hit_by_pitch',
                'batting_sacrifice_hits',
                'batting_sacrifice_flies',
                'batting_grounded_into_double_plays'
            ]
        case DatabankDataType.REG_FIELDING:
            return [
                'player_key',
                'fielding_games_played',
                'fielding_outs_played',
                'fielding_putouts',
                'fielding_assists',
                'fielding_errors',
                'fielding_double_plays',
                'fielding_passed_balls',
                'fielding_wild_pitches',
                'fielding_opp_stolen_bases',
                'fielding_opp_caught_stealing',
                'fielding_zone_rating'
            ]
        case DatabankDataType.POST_BATTING:
            return [
                'player_key',
                'batting_post_games_played',
                'batting_post_at_bats',
                'batting_post_runs',
                'batting_post_hits',
                'batting_post_doubles',
                'batting_post_triples',
                'batting_post_home_runs',
                'batting_post_runs_batted_in',
                'batting_post_stolen_bases',
                'batting_post_caught_stealing',
                'batting_post_base_on_balls',
                'batting_post_strikeouts',
                'batting_post_intentional_walks',
                'batting_post_hit_by_pitch',
                'batting_post_sacrifice_hits',
                'batting_post_sacrifice_flies',
                'batting_post_grounded_into_double_plays'
            ]
        case DatabankDataType.POST_FIELDING:
            return [
                'player_key',
                'fielding_post_games_played',
                'fielding_post_games_started',
                'fielding_post_outs_played',
                'fielding_post_putouts',
                'fielding_post_assists',
                'fielding_post_errors',
                'fielding_post_double_plays',
                'fielding_post_triple_plays',
                'fielding_post_passed_balls',
                'fielding_post_opp_stolen_bases',
                'fielding_post_opp_caught_stealing'
            ]
        case _:
            return None


def get_int_cols(data_type: DatabankDataType) -> list:
    match data_type:
        case DatabankDataType.APPEARANCES:
            return [
                'total_games',
                'games_started',
                'games_batting',
                'games_defense',
                'games_pitcher',
                'games_catcher',
                'games_first_base',
                'games_second_base',
                'games_third_base',
                'games_shortstop',
                'games_left_field',
                'games_center_field',
                'games_right_field',
                'games_outfield',
                'games_designated_hitter',
                'games_pinch_hitter',
                'games_pinch_runner'
            ]
        case DatabankDataType.COLLEGE:
            return [
                'college_years_played'
            ]
        case DatabankDataType.SALARIES:
            return [
                'salary'
            ]
        case DatabankDataType.TEAMS:
            return [
                'team_home_park_attendance',
                'team_home_park_factor_batter',
                'team_rank'
            ]
        case DatabankDataType.REG_BATTING:
            return [
                'batting_games_played',
                'batting_at_bats',
                'batting_runs',
                'batting_hits',
                'batting_doubles',
                'batting_triples',
                'batting_home_runs',
                'batting_runs_batted_in',
                'batting_stolen_bases',
                'batting_caught_stealing',
                'batting_base_on_balls',
                'batting_strikeouts',
                'batting_intentional_walks',
                'batting_hit_by_pitch',
                'batting_sacrifice_hits',
                'batting_sacrifice_flies',
                'batting_grounded_into_double_plays'
            ]
        case DatabankDataType.REG_FIELDING:
            return [
                'fielding_games_played',
                'fielding_outs_played',
                'fielding_putouts',
                'fielding_assists',
                'fielding_errors',
                'fielding_double_plays',
                'fielding_passed_balls',
                'fielding_wild_pitches',
                'fielding_opp_stolen_bases',
                'fielding_opp_caught_stealing',
                'fielding_zone_rating'
            ]
        case DatabankDataType.POST_BATTING:
            return [
                'batting_post_games_played',
                'batting_post_at_bats',
                'batting_post_runs',
                'batting_post_hits',
                'batting_post_doubles',
                'batting_post_triples',
                'batting_post_home_runs',
                'batting_post_runs_batted_in',
                'batting_post_stolen_bases',
                'batting_post_caught_stealing',
                'batting_post_base_on_balls',
                'batting_post_strikeouts',
                'batting_post_intentional_walks',
                'batting_post_hit_by_pitch',
                'batting_post_sacrifice_hits',
                'batting_post_sacrifice_flies',
                'batting_post_grounded_into_double_plays'
            ]
        case DatabankDataType.POST_FIELDING:
            return [
                'fielding_post_games_played',
                'fielding_post_games_started',
                'fielding_post_outs_played',
                'fielding_post_putouts',
                'fielding_post_assists',
                'fielding_post_errors',
                'fielding_post_double_plays',
                'fielding_post_triple_plays',
                'fielding_post_passed_balls',
                'fielding_post_opp_stolen_bases',
                'fielding_post_opp_caught_stealing'
            ]
        case _:
            return None


def get_float_cols(data_type: DatabankDataType) -> list:
    match data_type:
        case DatabankDataType.PEOPLE:
            return [
                'weight',
                'height'
            ]
        case _:
            return None


def get_agg_cols(data_type: DatabankDataType) -> list:
    match data_type:
        case DatabankDataType.REG_BATTING:
            return [
                'batting_games_played',
                'batting_at_bats',
                'batting_runs',
                'batting_hits',
                'batting_doubles',
                'batting_triples',
                'batting_home_runs',
                'batting_runs_batted_in',
                'batting_stolen_bases',
                'batting_caught_stealing',
                'batting_base_on_balls',
                'batting_strikeouts',
                'batting_intentional_walks',
                'batting_hit_by_pitch',
                'batting_sacrifice_hits',
                'batting_sacrifice_flies',
                'batting_grounded_into_double_plays'
            ]
        case DatabankDataType.REG_FIELDING:
            return [
                'fielding_games_played',
                'fielding_outs_played',
                'fielding_putouts',
                'fielding_assists',
                'fielding_errors',
                'fielding_double_plays',
                'fielding_passed_balls',
                'fielding_wild_pitches',
                'fielding_opp_stolen_bases',
                'fielding_opp_caught_stealing',
                'fielding_zone_rating'
            ]
        case DatabankDataType.POST_BATTING:
            return [
                'batting_post_games_played',
                'batting_post_at_bats',
                'batting_post_runs',
                'batting_post_hits',
                'batting_post_doubles',
                'batting_post_triples',
                'batting_post_home_runs',
                'batting_post_runs_batted_in',
                'batting_post_stolen_bases',
                'batting_post_caught_stealing',
                'batting_post_base_on_balls',
                'batting_post_strikeouts',
                'batting_post_intentional_walks',
                'batting_post_hit_by_pitch',
                'batting_post_sacrifice_hits',
                'batting_post_sacrifice_flies',
                'batting_post_grounded_into_double_plays'
            ]
        case DatabankDataType.POST_FIELDING:
            return [
                'fielding_post_games_played',
                'fielding_post_games_started',
                'fielding_post_outs_played',
                'fielding_post_putouts',
                'fielding_post_assists',
                'fielding_post_errors',
                'fielding_post_double_plays',
                'fielding_post_triple_plays',
                'fielding_post_passed_balls',
                'fielding_post_opp_stolen_bases',
                'fielding_post_opp_caught_stealing'
            ]
        case _:
            return None


def get_prefix(data_type: DatabankDataType) -> str:
    match data_type:
        case DatabankDataType.ALLSTAR:
            return 'allstar_'
        case DatabankDataType.AWARDS:
            return 'awards_'
        case DatabankDataType.COLLEGE:
            return 'college_'
        case DatabankDataType.TEAMS:
            return 'team_'
        case DatabankDataType.REG_BATTING:
            return 'batting_'
        case DatabankDataType.REG_FIELDING:
            return 'fielding_'
        case DatabankDataType.POST_BATTING:
            return 'batting_post_'
        case DatabankDataType.POST_FIELDING:
            return 'fielding_post_'
        case _:
            return None


def get_key_col(data_type: DatabankDataType) -> str:
    match data_type:
        case DatabankDataType.ALLSTAR:
            return 'player_key'
        case DatabankDataType.APPEARANCES:
            return 'player_id'
        case DatabankDataType.AWARDS:
            return 'player_key'
        case DatabankDataType.COLLEGE:
            return 'player_id'
        case DatabankDataType.HOF:
            return 'player_id'
        case DatabankDataType.MANAGERS:
            return 'team_key'
        case DatabankDataType.PEOPLE:
            return 'player_id'
        case DatabankDataType.SALARIES:
            return 'player_key'
        case DatabankDataType.TEAMS:
            return 'team_key'
        case DatabankDataType.REG_BATTING:
            return 'player_key'
        case DatabankDataType.REG_FIELDING:
            return 'player_key'
        case DatabankDataType.POST_BATTING:
            return 'player_key'
        case DatabankDataType.POST_FIELDING:
            return 'player_key'
        case _:
            return None


def process_data(dataframe: pd.DataFrame,
                 data_type: DatabankDataType) -> pd.DataFrame:
    match data_type:
        case DatabankDataType.ALLSTAR:
            return process_allstar(dataframe)
        case DatabankDataType.APPEARANCES:
            return process_appearances(dataframe)
        case DatabankDataType.AWARDS:
            return process_awards(dataframe)
        case DatabankDataType.COLLEGE:
            return process_college(dataframe)
        case DatabankDataType.HOF:
            return process_hall_of_fame(dataframe)
        case DatabankDataType.MANAGERS:
            return process_managers(dataframe)
        case DatabankDataType.PEOPLE:
            return process_people(dataframe)
        case DatabankDataType.SALARIES:
            return process_salaries(dataframe)
        case DatabankDataType.TEAMS:
            return process_teams(dataframe)
        case DatabankDataType.REG_BATTING:
            return process_reg_batting(dataframe)
        case DatabankDataType.REG_FIELDING:
            return process_reg_fielding(dataframe)
        case DatabankDataType.POST_BATTING:
            return process_post_batting(dataframe)
        case DatabankDataType.POST_FIELDING:
            return process_post_fielding(dataframe)
        case _:
            return dataframe


# =================================================================================================================== #

def process_allstar(dataframe: pd.DataFrame) -> pd.DataFrame:
    df = dfUtils.copy(dataframe)

    # add flag for allstars
    df.insert(1, 'allstar_flag', True)

    return df


def process_appearances(dataframe: pd.DataFrame) -> pd.DataFrame:
    df = dfUtils.copy(dataframe)

    # drop duplicates based on player-team-year key
    df = add_key(df, 'temp_key', ['player_id', 'team_id', 'year_id'])
    df = df.sort_values('temp_key').drop_duplicates('temp_key').reset_index(drop=True)
    df.drop(columns='temp_key', inplace=True)

    # create primary position column
    df = add_primary_position(df)

    # remove pitchers from dataset
    df = df[df['primary_position'] != 'pitcher']

    return df


def process_awards(dataframe: pd.DataFrame) -> pd.DataFrame:
    df = dfUtils.copy(dataframe)

    # add award boolean columns
    df.loc[df['awards_award_name'].astype(str).str.lower() == 'mvp', 'mvp_award'] = True
    df.loc[df['awards_award_name'].astype(str).str.lower() == 'rookie of the year', 'rookie_oty_award'] = True

    # fill na with false for new award columns
    df = na_to_false(df, ['mvp_award', 'rookie_oty_award'])

    # aggregate by player_key
    df = df.groupby('player_key').max().reset_index()

    return df


def process_college(dataframe: pd.DataFrame) -> pd.DataFrame:
    df = dfUtils.copy(dataframe)

    # mutate dataframe
    years_played = df.groupby('player_id').size().reset_index(name='college_years_played')
    names = df.groupby('player_id')['school_id'].unique().apply(
        lambda x: x[0] if len(x) == 1 else 'multiple').reset_index(name='college_name')
    multiple = df.groupby('player_id')['school_id'].unique().apply(
        lambda x: ' | '.join(x) if len(x) > 1 else pd.NA).reset_index(name='college_multiple')
    mutated = pd.merge(years_played, names, on='player_id')
    df = pd.merge(mutated, multiple, on='player_id')

    # add flag for college_play
    df.insert(1, 'college_play_flag', True)

    return df


def process_hall_of_fame(dataframe: pd.DataFrame) -> pd.DataFrame:
    df = dfUtils.copy(dataframe)

    # filter to relevant records
    df = df[df['inducted'] == 'Y']
    df = df[df['category'] == 'Player']

    # mutate dataframe
    df = df['player_id'].to_frame()

    # add flag for hall_of_fame
    df['hall_of_fame'] = True

    return df


def process_managers(dataframe: pd.DataFrame) -> pd.DataFrame:
    df = dfUtils.copy(dataframe)

    # get manager names
    mgrs = dfUtils.load_csv(databankModel.save_path, DatabankDataType.PEOPLE.value)
    mgrs = dataframe_processor(mgrs, DatabankDataType.PEOPLE)
    mgrs = mgrs[['player_id', 'full_name']]
    mgrs.rename(columns={
        'player_id': 'manager_id',
        'full_name': 'manager_name'}, inplace=True)

    # merge manager names into dataframe
    df = pd.merge(df, mgrs, on='manager_id', how='left')

    # mutate dataframe
    names = df.groupby('team_key')['manager_name'].unique().apply(
        lambda x: x[0] if len(x) == 1 else 'multiple').reset_index(name='manager_name')
    multiple = df.groupby('team_key')['manager_name'].unique().apply(
        lambda x: ' | '.join(x) if len(x) > 1 else pd.NA).reset_index(name='manager_multiple')
    df = pd.merge(names, multiple, on='team_key')

    return df


def process_people(dataframe: pd.DataFrame) -> pd.DataFrame:
    df = dfUtils.copy(dataframe)

    # combine birthdate columns
    df = dfUtils.combine_date_parts(df, ['birth_year', 'birth_month', 'birth_day'], 'birth_date')

    # convert date-like columns to datetime64
    df = to_datetime64(df, ['debut_date', 'final_game'])

    # create full name column
    df['full_name'] = df['given_name'] + ' ' + df['last_name']

    return df


def process_salaries(dataframe: pd.DataFrame) -> pd.DataFrame:
    df = dfUtils.copy(dataframe)

    # aggregate by player_key
    df = df.groupby('player_key')['salary'].mean().reset_index()

    return df


def process_teams(dataframe: pd.DataFrame) -> pd.DataFrame:
    df = dfUtils.copy(dataframe)

    # get franchise fields
    franchises = dfUtils.load_csv(databankModel.save_path, 'TeamsFranchises')
    franchises = dfUtils.update_headers(franchises, databankModel.get_headers('TeamsFranchises'))
    franchises.drop(columns='national_association_id', inplace=True)

    # merge franchise fields into dataframe
    df = pd.merge(df, franchises, on='franchise_id', how='left')

    map_cols = [
        'team_division_series',
        'team_wild_card_series',
        'team_league_series',
        'team_world_series'
    ]

    # convert columns with Y/N values to True/False
    for col in map_cols:
        df[col] = df[col].map({
            'Y': True,
            'N': False}).astype(bool)

    return df


# =================================================================================================================== #

def aggregate_stats_df(dataframe: pd.DataFrame,
                       agg_dict: dict,
                       key_col: str) -> pd.DataFrame:
    return dataframe.groupby([key_col]).agg(agg_dict).reset_index()

def process_reg_batting(dataframe: pd.DataFrame) -> pd.DataFrame:
    return aggregate_stats_df(dataframe, get_stats_agg_dict(get_agg_cols(DatabankDataType.REG_BATTING)),
                              get_key_col(DatabankDataType.REG_BATTING)).copy().reset_index(drop=True)

def process_reg_fielding(dataframe: pd.DataFrame) -> pd.DataFrame:
    return aggregate_stats_df(dataframe, get_stats_agg_dict(get_agg_cols(DatabankDataType.REG_FIELDING)),
                              get_key_col(DatabankDataType.REG_FIELDING)).copy().reset_index(drop=True)

def process_post_batting(dataframe: pd.DataFrame) -> pd.DataFrame:
    return aggregate_stats_df(dataframe, get_stats_agg_dict(get_agg_cols(DatabankDataType.POST_BATTING)),
                              get_key_col(DatabankDataType.POST_BATTING)).copy().reset_index(drop=True)

def process_post_fielding(dataframe: pd.DataFrame) -> pd.DataFrame:
    return aggregate_stats_df(dataframe, get_stats_agg_dict(get_agg_cols(DatabankDataType.POST_FIELDING)),
                              get_key_col(DatabankDataType.POST_FIELDING)).copy().reset_index(drop=True)


# =================================================================================================================== #

def process_baseball_df(dataframe: pd.DataFrame) -> pd.DataFrame:
    df = dfUtils.copy(dataframe)

    # add key column
    df = add_key(df, 'bb_key', ['player_id', 'team_id', 'year_id'])

    # add flag for team postseason showings
    team_post_cols = ['team_division_series', 'team_wild_card_series', 'team_league_series', 'team_world_series']
    df['team_postseason_flag'] = df[team_post_cols].notna().any(axis=1)

    # add flag for player postseason showings
    player_post_cols = ['batting_post_games_played', 'fielding_post_games_played']
    df['player_postseason_flag'] = df[player_post_cols].notna().any(axis=1)

    # convert na to false
    na_to_false_cols = [
        'allstar_flag',
        'mvp_award',
        'rookie_oty_award',
        'college_play_flag',
        'hall_of_fame',
        'team_postseason_flag',
        'player_postseason_flag'
    ]
    df = na_to_false(df, na_to_false_cols)

    # convert na stats to 0
    for data_type in [DatabankDataType.POST_BATTING, DatabankDataType.POST_FIELDING]:
        for col in get_final_cols(data_type):
            if col in df.columns:
                df[col] = df[col].fillna(0)

    # convert null values to pd.NA
    df = dfUtils.null_to_pandas_na(df)

    # ensure integer columns are Int64
    df = to_Int64(df, get_final_int_columns())

    # ensure float columns are Float64
    df = to_Float64(df, get_final_float_columns())

    # set final columns
    df = df[get_final_baseball_columns()]

    # sort and drop duplicates
    df = df.sort_values('bb_key').drop_duplicates().reset_index(drop=True)

    return df


def merge_with_master(baseball_df: pd.DataFrame,
                      merge_df: pd.DataFrame,
                      data_type: DatabankDataType) -> pd.DataFrame:
    df = dfUtils.copy(baseball_df)
    key_col = get_key_col(data_type)
    if key_col in baseball_df.columns and key_col in merge_df.columns:
        df = pd.merge(df, merge_df, on=key_col, how='left')
    else:
        print(f'Merge column {key_col} not present in both dataframes...')
    return df


def get_final_int_columns() -> list:
    int_cols = []
    for data_type in DatabankDataType:
        if get_int_cols(data_type) is not None:
            for col in get_int_cols(data_type):
                int_cols.append(col)
    return int_cols


def get_final_float_columns() -> list:
    float_cols = []
    for data_type in DatabankDataType:
        if get_float_cols(data_type) is not None:
            for col in get_float_cols(data_type):
                float_cols.append(col)
    return float_cols


def get_final_baseball_columns() -> list:

    return [
        'bb_key',
        'year_id',
        'player_id',
        'team_id',
        'franchise_id',
        'league_id',
        'division_id',
        'team_name',
        'team_home_park_name',
        'franchise_name',
        'franchise_active',
        'team_home_park_attendance',
        'team_rank',
        'team_home_park_factor_batter',
        'team_postseason_flag',
        'team_wild_card_series',
        'team_division_series',
        'team_league_series',
        'team_world_series',
        'full_name',
        'first_name',
        'last_name',
        'weight',
        'height',
        'batting_hand',
        'throwing_hand',
        'primary_position',
        'debut_date',
        'final_game',
        'birth_country',
        'birth_state',
        'birth_city',
        'birth_date',
        'total_games',
        'games_started',
        'games_batting',
        'games_defense',
        'games_pitcher',
        'games_catcher',
        'games_first_base',
        'games_second_base',
        'games_third_base',
        'games_shortstop',
        'games_outfield',
        'games_left_field',
        'games_center_field',
        'games_right_field',
        'games_designated_hitter',
        'games_pinch_hitter',
        'games_pinch_runner',
        'salary',
        'player_postseason_flag',
        'college_play_flag',
        'college_years_played',
        'college_name',
        'college_multiple',
        'allstar_flag',
        'mvp_award',
        'rookie_oty_award',
        'hall_of_fame',
        'manager_name',
        'manager_multiple',
        'batting_games_played',
        'batting_at_bats',
        'batting_runs',
        'batting_hits',
        'batting_doubles',
        'batting_triples',
        'batting_home_runs',
        'batting_runs_batted_in',
        'batting_stolen_bases',
        'batting_caught_stealing',
        'batting_base_on_balls',
        'batting_strikeouts',
        'batting_intentional_walks',
        'batting_hit_by_pitch',
        'batting_sacrifice_hits',
        'batting_sacrifice_flies',
        'batting_grounded_into_double_plays',
        'fielding_games_played',
        'fielding_outs_played',
        'fielding_putouts',
        'fielding_assists',
        'fielding_errors',
        'fielding_double_plays',
        'fielding_passed_balls',
        'fielding_wild_pitches',
        'fielding_opp_stolen_bases',
        'fielding_opp_caught_stealing',
        'fielding_zone_rating',
        'batting_post_games_played',
        'batting_post_at_bats',
        'batting_post_runs',
        'batting_post_hits',
        'batting_post_doubles',
        'batting_post_triples',
        'batting_post_home_runs',
        'batting_post_runs_batted_in',
        'batting_post_stolen_bases',
        'batting_post_caught_stealing',
        'batting_post_base_on_balls',
        'batting_post_strikeouts',
        'batting_post_intentional_walks',
        'batting_post_hit_by_pitch',
        'batting_post_sacrifice_hits',
        'batting_post_sacrifice_flies',
        'batting_post_grounded_into_double_plays',
        'fielding_post_games_played',
        'fielding_post_games_started',
        'fielding_post_outs_played',
        'fielding_post_putouts',
        'fielding_post_assists',
        'fielding_post_errors',
        'fielding_post_double_plays',
        'fielding_post_triple_plays',
        'fielding_post_passed_balls',
        'fielding_post_opp_stolen_bases',
        'fielding_post_opp_caught_stealing'
    ]


def get_fresh_baseball_df() -> pd.DataFrame:
    # create individual dataframes
    allstar = dataframe_processor(
        dataframe=dfUtils.load_csv(databankModel.save_path, DatabankDataType.ALLSTAR.value),
        data_type=DatabankDataType.ALLSTAR)
    appearances = dataframe_processor(
        dataframe=dfUtils.load_csv(databankModel.save_path, DatabankDataType.APPEARANCES.value),
        data_type=DatabankDataType.APPEARANCES)
    awards = dataframe_processor(
        dataframe=dfUtils.load_csv(databankModel.save_path, DatabankDataType.AWARDS.value),
        data_type=DatabankDataType.AWARDS)
    college = dataframe_processor(
        dataframe=dfUtils.load_csv(databankModel.save_path, DatabankDataType.COLLEGE.value),
        data_type=DatabankDataType.COLLEGE)
    hall_of_fame = dataframe_processor(
        dataframe=dfUtils.load_csv(databankModel.save_path, DatabankDataType.HOF.value),
        data_type=DatabankDataType.HOF)
    managers = dataframe_processor(
        dataframe=dfUtils.load_csv(databankModel.save_path, DatabankDataType.MANAGERS.value),
        data_type=DatabankDataType.MANAGERS)
    people = dataframe_processor(
        dataframe=dfUtils.load_csv(databankModel.save_path, DatabankDataType.PEOPLE.value),
        data_type=DatabankDataType.PEOPLE)
    salaries = dataframe_processor(
        dataframe=dfUtils.load_csv(databankModel.save_path, DatabankDataType.SALARIES.value),
        data_type=DatabankDataType.SALARIES)
    teams = dataframe_processor(
        dataframe=dfUtils.load_csv(databankModel.save_path, DatabankDataType.TEAMS.value),
        data_type=DatabankDataType.TEAMS)
    batting = dataframe_processor(
        dataframe=dfUtils.load_csv(databankModel.save_path, DatabankDataType.REG_BATTING.value),
        data_type=DatabankDataType.REG_BATTING)
    fielding = dataframe_processor(
        dataframe=dfUtils.load_csv(databankModel.save_path, DatabankDataType.REG_FIELDING.value),
        data_type=DatabankDataType.REG_FIELDING)
    batting_post = dataframe_processor(
        dataframe=dfUtils.load_csv(databankModel.save_path, DatabankDataType.POST_BATTING.value),
        data_type=DatabankDataType.POST_BATTING)
    fielding_post = dataframe_processor(
        dataframe=dfUtils.load_csv(databankModel.save_path, DatabankDataType.POST_FIELDING.value),
        data_type=DatabankDataType.POST_FIELDING)

    # create master baseball dataframe
    df = pd.merge(appearances, people, on='player_id', how='left')

    # add keys for merging
    df = add_player_key(add_team_key(df))
    
    # merge individual dataframes with baseball dataframe
    df = merge_with_master(df, allstar, DatabankDataType.ALLSTAR)
    df = merge_with_master(df, awards, DatabankDataType.AWARDS)
    df = merge_with_master(df, college, DatabankDataType.COLLEGE)
    df = merge_with_master(df, hall_of_fame, DatabankDataType.HOF)
    df = merge_with_master(df, managers, DatabankDataType.MANAGERS)
    df = merge_with_master(df, salaries, DatabankDataType.SALARIES)
    df = merge_with_master(df, teams, DatabankDataType.TEAMS)
    df = merge_with_master(df, batting, DatabankDataType.REG_BATTING)
    df = merge_with_master(df, fielding, DatabankDataType.REG_FIELDING)
    df = merge_with_master(df, batting_post, DatabankDataType.POST_BATTING)
    df = merge_with_master(df, fielding_post, DatabankDataType.POST_FIELDING)

    # process baseball dataframe
    df = process_baseball_df(df)
    print(f'Final baseball dataframe shape: {df.shape}')

    return df

# =================================================================================================================== #

def get_numerical_cols() -> list:
    return [
        'bb_key',
        'allstar_flag',
        'team_home_park_attendance',
        'team_rank',
        'team_home_park_factor_batter',
        'team_wild_card_series',
        'team_division_series',
        'team_league_series',
        'team_world_series',
        'weight',
        'height',
        'total_games',
        'games_started',
        'games_batting',
        'games_defense',
        'games_pitcher',
        'games_catcher',
        'games_first_base',
        'games_second_base',
        'games_third_base',
        'games_shortstop',
        'games_outfield',
        'games_left_field',
        'games_center_field',
        'games_right_field',
        'games_designated_hitter',
        'games_pinch_hitter',
        'games_pinch_runner',
        'salary',
        'player_postseason_flag',
        'college_play_flag',
        'college_years_played',
        'mvp_award',
        'rookie_oty_award',
        'hall_of_fame',
        'batting_games_played',
        'batting_at_bats',
        'batting_runs',
        'batting_hits',
        'batting_doubles',
        'batting_triples',
        'batting_home_runs',
        'batting_runs_batted_in',
        'batting_stolen_bases',
        'batting_caught_stealing',
        'batting_base_on_balls',
        'batting_strikeouts',
        'batting_intentional_walks',
        'batting_hit_by_pitch',
        'batting_sacrifice_hits',
        'batting_sacrifice_flies',
        'batting_grounded_into_double_plays',
        'fielding_games_played',
        'fielding_outs_played',
        'fielding_putouts',
        'fielding_assists',
        'fielding_errors',
        'fielding_double_plays',
        'fielding_passed_balls',
        'fielding_wild_pitches',
        'fielding_opp_stolen_bases',
        'fielding_opp_caught_stealing',
        'fielding_zone_rating',
        'batting_post_games_played',
        'batting_post_at_bats',
        'batting_post_runs',
        'batting_post_hits',
        'batting_post_doubles',
        'batting_post_triples',
        'batting_post_home_runs',
        'batting_post_runs_batted_in',
        'batting_post_stolen_bases',
        'batting_post_caught_stealing',
        'batting_post_base_on_balls',
        'batting_post_strikeouts',
        'batting_post_intentional_walks',
        'batting_post_hit_by_pitch',
        'batting_post_sacrifice_hits',
        'batting_post_sacrifice_flies',
        'batting_post_grounded_into_double_plays',
        'fielding_post_games_played',
        'fielding_post_games_started',
        'fielding_post_outs_played',
        'fielding_post_putouts',
        'fielding_post_assists',
        'fielding_post_errors',
        'fielding_post_double_plays',
        'fielding_post_triple_plays',
        'fielding_post_passed_balls'
    ]


def get_numerical_df(dataframe: pd.DataFrame) -> pd.DataFrame:
    df = dfUtils.copy(dataframe)
    df = df[get_numerical_cols()]
    print(f'Numerical dataframe shape: {df.shape}')
    return df


def get_categorical_cols() -> list:
    return [
        'bb_key',
        'allstar_flag',
        'team_name',
        'team_home_park_name',
        'franchise_name',
        'franchise_active',
        'batting_hand',
        'throwing_hand',
        'primary_position',
        'birth_country',
        'birth_state',
        'birth_city',
        'player_postseason_flag',
        'college_play_flag',
        'college_years_played',
        'college_name',
        'mvp_award',
        'rookie_oty_award',
        'hall_of_fame',
        'manager_name'
    ]


def get_categorical_df(dataframe: pd.DataFrame) -> pd.DataFrame:
    df = dfUtils.copy(dataframe)
    df = df[get_categorical_cols()]
    print(f'Categorical dataframe shape: {df.shape}')
    return df

# =================================================================================================================== #

if __name__ == '__main__':
    print(f"\n\n---------------------------------------- {__file__.split('/')[-1]}")
