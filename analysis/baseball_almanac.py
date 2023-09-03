# MLB All-Star Game Television Viewership Analysis
# =================================================================================================================== #
import os
import warnings

import pandas as pd

import helpers.dataframe_utils as dfUtils
import models.baseball_almanac as baseballAlmanac
from helpers.download_helper import DownloadHelper
from helpers.enum_factory import MovingRangeCalc
from helpers.environment_helper import EnvHelper

warnings.filterwarnings("ignore", category=FutureWarning)

# =================================================================================================================== #

def get_url() -> str:
    return ('https://raw.githubusercontent.com/BronzeToad/AllStarRosters/87d0391b48e4a05b3cd1e3bcf7f000e62623ede8/data/'
            'baseball-almanac/all_star_game_tv_stats.csv')

def get_data_dir() -> str:
    return os.path.join(EnvHelper().workspace, 'data', 'baseball-almanac')

def get_save_path(filename: str) -> str:
    return os.path.join(EnvHelper().workspace, 'analysis', 'data', filename)


def get_min_max_years(dataframe: pd.DataFrame) -> list:
    min_years = baseballAlmanac.get_moving_range(dataframe=dataframe,
                                                 column='Year',
                                                 calculation=MovingRangeCalc.MIN)

    max_years = baseballAlmanac.get_moving_range(dataframe=dataframe,
                                                 column='Year',
                                                 calculation=MovingRangeCalc.MAX)

    min_max_years = []
    for _min, _max in zip(min_years, max_years):
        min_max_years.append(f'{_min}-{_max}')

    return min_max_years


def get_moving_avg_rating(dataframe: pd.DataFrame) -> list:
    return baseballAlmanac.get_moving_range(
        dataframe=dataframe,
        column='Rating',
        calculation=MovingRangeCalc.MEAN
    )

def get_moving_avg_share(dataframe: pd.DataFrame) -> list:
    return baseballAlmanac.get_moving_range(
        dataframe=dataframe,
        column='Share',
        calculation=MovingRangeCalc.MEAN
    )

def get_moving_avg_viewers(dataframe: pd.DataFrame) -> list:
    return baseballAlmanac.get_moving_range(
        dataframe=dataframe,
        column='HouseholdViewers',
        calculation=MovingRangeCalc.MEAN
    )


def get_first_last_df(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({
        'Years'              : baseballAlmanac.get_first_last(get_min_max_years(df)),
        'AvgRating'          : baseballAlmanac.get_first_last(get_moving_avg_rating(df)),
        'RatingDelta'        : baseballAlmanac.get_percent_change(get_moving_avg_rating(df)),
        'AvgShare'           : baseballAlmanac.get_first_last(get_moving_avg_share(df)),
        'ShareDelta'         : baseballAlmanac.get_percent_change(get_moving_avg_share(df)),
        'AvgHouseholdViewers': baseballAlmanac.get_first_last(get_moving_avg_viewers(df)),
        'ViewersDelta'       : baseballAlmanac.get_percent_change(get_moving_avg_viewers(df))
    })

# =================================================================================================================== #

def ready_set_go() -> None:

    # download viewership data
    Downloader = DownloadHelper(url=get_url(), save_dir=get_data_dir())
    # Downloader.download()

    # create tv viewership dataframe
    df = dfUtils.load_csv(folder=Downloader.save_path, filename=Downloader.filename)

    # update column names
    new_col_names = {
        'Year | ASG': 'Year',
        'Households': 'HouseholdViewers'
    }
    df.rename(columns=new_col_names, inplace=True)

    # remove unneeded columns
    df.drop(columns=['Network', 'Viewers'], inplace=True)

    # update data types
    df['HouseholdViewers'] = pd.to_numeric(df['HouseholdViewers'].str.replace(',', ''))

    # get first/last comparison df
    df = get_first_last_df(df)
    print(df)

    '''
    After reviewing television viewing data from MLB All-Star games we observe a massive decrease in viewership. 
    From the first time period in this dataset (1967-1976) to the most recent available time period (2012-2022); 
        the average rating for All-Star games dropped by 79%, 
        the average share of the viewership market decreased by 77%, 
        and the number of average household viewers fell by 52%.
    '''

    # save df as csv
    df.to_csv(get_save_path('allstar_viewership_delta.csv'), index=False)

    # DONE
    print(f'\n# -------- DONE -------- #')

# =================================================================================================================== #

if __name__ == '__main__':
    print(f"\n\n# -------------------- Baseball Databank Analysis -------------------- #")

    ready_set_go()
