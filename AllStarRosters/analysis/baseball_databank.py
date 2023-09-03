# MLB All-Star Roster Analysis - Baseball Databank Data
# =================================================================================================================== #
import os
import warnings

import numpy as np
import pandas as pd

import helpers.analysis_utils as analysisUtils
import models.databank_analysis as databankAnalysis
from helpers.environment_helper import EnvHelper
from models.baseball_databank import BaseballDatabank

warnings.filterwarnings("ignore", category=FutureWarning)
databankModel = BaseballDatabank()

# =================================================================================================================== #

def get_plot_save_path(filename: str) -> str:
    return os.path.join(EnvHelper().workspace, 'analysis', 'plots', filename + '.png')

def get_data_save_path(filename: str) -> str:
    return os.path.join(EnvHelper().workspace, 'analysis', 'data', filename)


def correlation_matrix_analysis(dataframe: pd.DataFrame) -> pd.DataFrame:
    print('\nGenerating Correlation Matrix...')
    df = dataframe.drop(columns=['bb_key']).copy()

    # get correlation coefficients and p-values
    corr_dict = analysisUtils.get_correlation_analysis_dict(df, 'allstar_flag')

    corr_df = pd.DataFrame({
        'Baseball Databank Field': [k for k in corr_dict.keys()],
        'Correlation Coefficient': [round(v[0], 4) for k, v in corr_dict.items()],
        'P-Value': [round(v[1], 4) for k, v in corr_dict.items()]
    })

    # add derived columns to df
    corr_df['Statistically Significant'] = np.where(corr_df['P-Value'] < 0.01, True, False)
    corr_df['Practically Significant'] = np.where(corr_df['Correlation Coefficient'].abs() >= 0.3, True, False)

    condlist = [
        corr_df['Correlation Coefficient'].abs() == round(0.0, 4),
        corr_df['Correlation Coefficient'].abs() == round(1.0, 4),
        corr_df['Correlation Coefficient'].abs() < 0.3,
        corr_df['Correlation Coefficient'].abs() < 0.6,
        corr_df['Correlation Coefficient'].abs() < 0.9,
        corr_df['Correlation Coefficient'].abs() < 1.0
    ]
    choicelist = [
        'No Correlation',
        'Perfect Correlation',
        np.where(corr_df['Correlation Coefficient'] > 0.0, 'Low (Positive)', 'Low (Negative)'),
        np.where(corr_df['Correlation Coefficient'] > 0.0, 'Moderate (Positive)', 'Moderate (Negative)'),
        np.where(corr_df['Correlation Coefficient'] > 0.0, 'High (Positive)', 'High (Negative)'),
        np.where(corr_df['Correlation Coefficient'] > 0.0, 'Very High (Positive)', 'Very High (Negative)')
    ]
    corr_df['Magnitude'] = np.select(condlist, choicelist, default=pd.NA)

    # export corr_df to excel for report
    corr_df.to_excel(get_data_save_path('databank_correlation_analysis.xlsx'))

    # Get top 20 fields by correlation coefficient
    corr_df['abs_corr'] = corr_df['Correlation Coefficient'].abs()
    top20 = corr_df.nlargest(20, 'abs_corr')['Baseball Databank Field'].tolist()
    top20.append('allstar_flag')
    corr_df.drop(columns=['abs_corr'], inplace=True)

    # plot correlation matrix / heatmap
    analysisUtils.get_correlation_matrix(
        dataframe=df[top20],
        plot_title='Correlation Matrix: MLB All-Star Roster Analysis | Baseball Databank',
        save_path=get_plot_save_path('correlation_matrix_top20')
    )


def histogram_analysis(dataframe: pd.DataFrame) -> None:
    print('\nGenerating Histograms...')

    # create list of columns to plot
    histo_cols = []
    for col in dataframe.columns:
        if dataframe[col].dtype == 'Int64' and col != 'bb_key':
            histo_cols.append(col)

    # plot histograms together on grid
    analysisUtils.get_histogram_grid(
        dataframe=dataframe,
        columns=histo_cols,
        num_grid_cols=4,
        save_path=get_plot_save_path('histogram_grid')
    )

    # take a closer look at a few histograms from grid
    closer_look = ['team_home_park_attendance', 'team_home_park_factor_batter', 'total_games', 'games_started',
                   'batting_home_runs', 'batting_runs_batted_in', 'batting_intentional_walks']

    # plot histograms
    for col in closer_look:
        analysisUtils.get_histogram(
            dataframe=dataframe,
            column=col,
            save_path=get_plot_save_path(f'histogram__{col}')
        )


def scatterplot_analysis(dataframe: pd.DataFrame) -> None:
    print('\nGenerating Scatterplots...')

    # create list of columns to plot
    scatterplot_cols = ['weight', 'height', 'batting_home_runs', 'batting_strikeouts', 'batting_runs',
                        'batting_runs_batted_in', 'batting_intentional_walks', 'games_started']

    # create tuple pairs for scatterplots
    scatterplot_pairs = []
    for i, x in enumerate(scatterplot_cols):
        for j, y in enumerate(scatterplot_cols):
            if i < j:
                scatterplot_pairs.append([x, y])

    # plot scatterplots
    for pair in scatterplot_pairs:
        analysisUtils.get_scatterplot(
            dataframe=dataframe,
            column_x=pair[0],
            column_y=pair[1],
            save_path=get_plot_save_path(f'scatterplot__{pair[0]}-{pair[1]}')
        )


def barplot_analysis(dataframe: pd.DataFrame) -> None:
    print('\nGenerating Barplots...')

    # create barplot for allstar_flag
    analysisUtils.get_horizontal_barplot(
        dataframe=dataframe,
        group_by_col='allstar_flag',
        save_path=get_plot_save_path('barplot__allstar_flag')
    )

    # create list of columns to plot
    barplot_cols = []
    for col in dataframe.columns:
        if col not in ['bb_key', 'allstar_flag']:
            barplot_cols.append(col)

    # plot barplots
    for col in barplot_cols:
        analysisUtils.get_bool_dual_horizontal_barplot(
            dataframe=dataframe,
            group_by_col=col,
            bool_col='allstar_flag',
            save_path=get_plot_save_path(f'barplot_split__{col}')
        )


def comparative_statistics_analysis(dataframe: pd.DataFrame) -> None:
    print('\nGenerating Comparative Statistics...')

    # create list of columns
    stats_cols = []
    for col in dataframe.columns:
        if dataframe[col].dtype != bool and col != 'bb_key':
            stats_cols.append(col)

    # export stats
    for col in stats_cols:
        analysisUtils.get_descriptive_stats_df(
            dataframe=dataframe,
            column=col,
            bool_col='allstar_flag',
            save_path=get_data_save_path(f'stats__{col}.csv')
        )

# =================================================================================================================== #

def ready_set_go() -> None:

    # create main baseball dataframe
    bb_df = databankAnalysis.get_fresh_baseball_df()

    # create dataframe subset with numerical columns
    num_df = databankAnalysis.get_numerical_df(bb_df)

    # create dataframe subset with categorical columns
    cat_df = databankAnalysis.get_categorical_df(bb_df)

    correlation_matrix_analysis(num_df)
    histogram_analysis(num_df)
    scatterplot_analysis(num_df)
    barplot_analysis(cat_df)
    comparative_statistics_analysis(num_df)

    # DONE
    print(f'\n# -------- DONE -------- #')

# =================================================================================================================== #

if __name__ == '__main__':
    print(f"\n\n# -------------------- Baseball Databank Analysis -------------------- #")

    ready_set_go()
