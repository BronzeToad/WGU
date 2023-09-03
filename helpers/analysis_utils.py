import warnings
from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import pearsonr

import helpers.dataframe_utils as dfUtils

warnings.filterwarnings("ignore", category=FutureWarning)
# =================================================================================================================== #

def get_scatterplot(dataframe: pd.DataFrame,
                    column_x: str,
                    column_y: str,
                    plot_title: str = None,
                    save_path: str = None) -> None:
    color = 'steelblue' if save_path is not None else (0.933, 0.098, 0.463, 1)
    plt.figure(figsize=(16, 9))
    sns.set(font_scale=1)
    sns.scatterplot(data=dataframe, x=column_x, y=column_y, color=color)
    plt.title(plot_title or f'Scatterplot : {column_x} v. {column_y}')
    if save_path is not None:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


def get_histogram(dataframe: pd.DataFrame,
                  column: str,
                  plot_title: str = None,
                  save_path: str = None) -> None:
    color = 'steelblue' if save_path is not None else (0.933, 0.098, 0.463, 1)
    plt.figure(figsize=(16, 9))
    sns.set(font_scale=1)

    try:
        sns.histplot(dataframe[column], color=color, kde=True)
    except TypeError:
        sns.histplot(dataframe[column], color=color, kde=False)

    plt.title(plot_title or f'Histogram: {column}')

    if save_path is not None:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


def get_histogram_grid(dataframe: pd.DataFrame,
                       columns: list,
                       num_grid_cols: int = None,
                       plot_title: str = None,
                       save_path: str = None) -> None:
    num_plots = len(columns)
    max_plots_per_grid = 100
    if num_plots > max_plots_per_grid:
        raise ValueError("Number of columns exceeds maximum limit of 100. Please select 100 or fewer columns.")

    num_cols = num_grid_cols or 2
    num_rows = num_plots // num_cols
    if num_plots % num_cols != 0:
        num_rows += 1

    fig_width = num_cols * 6
    fig_height = num_rows * 3.5

    color = 'steelblue' if save_path is not None else (0.933, 0.098, 0.463, 1)

    fig, axes = plt.subplots(num_rows, num_cols, figsize=(fig_width, fig_height))
    fig.tight_layout(pad=4.0)
    axes = axes.flatten() if isinstance(axes, np.ndarray) else [axes]
    for i, column_idx in enumerate(range(num_plots)):
        col = columns[column_idx]
        ax = axes[i]
        sns.histplot(data=dataframe[col], color=color, ax=ax)
        ax.set_title(plot_title or f'Histogram: {col}')
    for j in range(num_plots, num_rows * num_cols):
        ax = axes[j]
        ax.axis('off')
    if save_path is not None:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


def get_horizontal_barplot(dataframe: pd.DataFrame,
                           group_by_col: str,
                           plot_title: str = None,
                           save_path: str = None) -> None:
    color = 'steelblue' if save_path is not None else (0.933, 0.098, 0.463, 1)
    plt.figure(figsize=(16, 9))
    sns.set(font_scale=1)

    grouped_data = dataframe.groupby(group_by_col).size().reset_index(name='count')
    grouped_data = grouped_data.sort_values('count', ascending=False)

    ax = sns.barplot(x='count', y=group_by_col, data=grouped_data, color=color, orient='h')

    ax.set_xlabel('Count')
    ax.set_ylabel(group_by_col)
    ax.set_title(plot_title or f'Barplot: {group_by_col} counts')

    if save_path is not None:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


def get_bool_dual_horizontal_barplot(dataframe: pd.DataFrame,
                                     group_by_col: str,
                                     bool_col: str,
                                     plot_title: str = None,
                                     save_path: str = None) -> None:
    plt.figure(figsize=(16, 9))
    sns.set(font_scale=1)

    color1 = 'steelblue' if save_path is not None else (0.933, 0.098, 0.463, 1)
    color2 = 'seagreen' if save_path is not None else (0.502, 0.149, 0.647, 1)

    grouped_data = dataframe.groupby([group_by_col, bool_col]).size().reset_index(name='count')
    grouped_data = grouped_data.sort_values('count', ascending=False)

    top_values = grouped_data[group_by_col].value_counts().nlargest(20).index
    grouped_data = grouped_data[grouped_data[group_by_col].isin(top_values)]
    grouped_data = grouped_data[grouped_data[group_by_col] != 'multiple']

    fig, axes = plt.subplots(2, 1, figsize=(16, 18))

    true_data = grouped_data[grouped_data[bool_col] == True]
    false_data = grouped_data[grouped_data[bool_col] == False]

    ax1 = sns.barplot(x='count', y=group_by_col, data=true_data, color=color1, orient='h', ax=axes[0])
    ax2 = sns.barplot(x='count', y=group_by_col, data=false_data, color=color2, orient='h', ax=axes[1])

    ax1.set_xlabel('')
    ax1.set_ylabel('True')
    ax1.set_title(plot_title or f'Barplot | Counts by {bool_col}: {group_by_col}')

    ax2.set_xlabel('Count')
    ax2.set_ylabel('False')

    plt.tight_layout()

    if save_path is not None:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


def get_pearsonr(dataframe: pd.DataFrame,
                 column_x: str,
                 column_y: str,) -> Tuple[float, float]:
    df = dfUtils.copy(dataframe)
    df.dropna(subset=[column_x, column_y], inplace=True)
    x = np.array(df[column_x])
    y = np.array(df[column_y])
    pear = pearsonr(x, y)
    return round(pear[0], 8), round(pear[1], 8)


def get_correlation_analysis_dict(dataframe: pd.DataFrame,
                                  analysis_column: str) -> dict:
    pears = {}
    for col in dataframe.columns:
        if col != analysis_column:
            pears[col] = get_pearsonr(dataframe, analysis_column, col)
    return pears


def get_correlation_matrix(dataframe: pd.DataFrame,
                           plot_title: str = None,
                           save_path: str = None) -> None:
    plt.figure(figsize=(16, 16))
    heatmap = sns.heatmap(data=dataframe.corr(), square=True, annot=True, cbar=True)
    heatmap.set_xticklabels(heatmap.get_xticklabels(), rotation=45, ha='right')
    plt.title(plot_title or f'Correlation Matrix')
    if save_path is not None:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


def get_descriptive_statistics(dataframe: pd.DataFrame,
                               column: str) -> dict:
    data = dataframe[column]
    return {
        'Mean': round(data.mean(), 2),
        'Median': round(data.median(), 2),
        'Standard Deviation': round(data.std(), 2),
        'Minimum': round(data.min(), 2),
        'Maximum': round(data.max(), 2),
        'Count': round(data.count(), 2)
    }


def get_descriptive_stats_df(dataframe: pd.DataFrame,
                             column: str,
                             bool_col: str = None,
                             save_path: str = None) -> None:
    df_base = pd.DataFrame.from_dict(
        data=get_descriptive_statistics(dataframe, column),
        orient='index',
        columns=['value'])

    if bool_col is None:
        return df_base
    else:
        df_true = pd.DataFrame.from_dict(
            data=get_descriptive_statistics(dataframe[dataframe[bool_col] == True], column),
            orient='index',
            columns=[f'{bool_col}-true']
        )
        df_false = pd.DataFrame.from_dict(
            data=get_descriptive_statistics(dataframe[dataframe[bool_col] == False], column),
            orient='index',
            columns=[f'{bool_col}-false']
        )
        df = pd.concat([df_base, df_true, df_false], axis=1)
        df.rename(columns={'value': 'baseline'}, inplace=True)

        if save_path is not None:
            df.to_csv(save_path)
        else:
            print(f'\n# Comparative Statistics: {column}')
            print(df)

# =================================================================================================================== #

if __name__ == '__main__':
    print(f"\n\n---------------------------------------- {__file__.split('/')[-1]}")
