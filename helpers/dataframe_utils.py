import os
from pathlib import Path
from typing import Union

import pandas as pd

from helpers.toad_utils import force_extension


# =================================================================================================================== #

def tally(
        dataframe: pd.DataFrame,
        columns: Union[str, list]
) -> None:

    cols = columns if isinstance(columns, list) else [columns]

    for col in cols:
        group_by_df = dataframe.groupby(col).size().sort_values(ascending=False).reset_index(name='count')
        print(f'{group_by_df}\n')


def copy(dataframe: pd.DataFrame) -> pd.DataFrame:
    return dataframe.copy().reset_index(drop=True)


def concat(
        dataframe_a: pd.DataFrame,
        dataframe_b: pd.DataFrame
) -> pd.DataFrame:
    return pd.concat([dataframe_a, dataframe_b], axis=1)


def drop_columns(
        dataframe: pd.DataFrame,
        columns: Union[str, list]
) -> pd.DataFrame:

    df = copy(dataframe)
    cols = columns if isinstance(columns, list) else [columns]

    for col in cols:
        if col in list(df.columns):
            df.drop(columns=[col], inplace=True)
        else:
            print(f"Column '{col}' does not exist...")

    return df


def load_csv(
        folder: str,
        filename: str
) -> pd.DataFrame:
    """Loads a csv file as a dataframe object.

    Parameters
    ----------
    folder : str
        The folder where the file is located.
    filename : str
        The name of the file.

    Returns
    -------
    df : pd.DataFrame
        The contents of the csv file.

    Raises
    ------
    FileNotFoundError
        If the file is not found in the given folder.
    """
    filename = force_extension(filename, extension='csv')
    path = os.path.join(folder, filename)

    if Path(path).is_file():
        df = pd.read_csv(path)
    else:
        raise FileNotFoundError(f'{filename} not found in {folder}.')

    return df


def rename_columns_ignore_case(df, new_column_names):
    # Convert column names to lowercase
    lower_column_names = df.columns.str.lower()

    # Create a mapping dictionary for renaming columns
    mapping = dict(zip(lower_column_names, new_column_names))

    # Use the mapping dictionary to rename columns
    df.rename(columns=lambda x: mapping[x.lower()] if x.lower() in mapping else x, inplace=True)

    return df


def update_headers(
        dataframe: pd.DataFrame,
        update_dict: dict,
) -> pd.DataFrame:
    df = copy(dataframe)
    df.columns = df.columns.str.lower()
    df.rename(columns=update_dict, inplace=True)
    return df


def combine_date_parts(
        dataframe: pd.DataFrame,
        date_cols: list,
        new_col_name: str
) -> pd.DataFrame:
    df = copy(dataframe)
    for col in date_cols:
        df[col] = df[col].astype('Int64')

    missing = df[date_cols].isnull().any(axis=1)
    df[new_col_name] = pd.NaT
    date_vals = df.loc[~missing, date_cols]
    date_vals.columns = ['year', 'month', 'day']
    df.loc[~missing, new_col_name] = pd.to_datetime(date_vals)
    return df


def check_for_string_matches(
        dataframe: pd.DataFrame,
        check_values: Union[str, list],
        case_sensitive: bool = False
) -> None:
    df = copy(dataframe)
    check_vals = check_values if isinstance(check_values, list) else [check_values]

    for val in check_vals:
        print(f"Checking dataframe for instances of '{val}'...")
        cols_dict = {}

        for col in df.columns:
            if case_sensitive:
                if (df[col].astype(str) == val).any():
                    val_count = df[col].astype(str).value_counts()[val]
                    if val_count > 0:
                        cols_dict[col] = val_count
            else:
                val_lower = str(val).lower()
                if (df[col].astype(str).str.lower() == val_lower).any():
                    val_count = df[col].astype(str).str.lower().value_counts()[val_lower]
                    if val_count > 0:
                        cols_dict[col] = val_count

        if len(cols_dict) > 0:
            print(f"Found {len(cols_dict)} columns that contain '{val}'.")
            for k, v in cols_dict.items():
                print(f'  {k}: {v}')
            print()
        else:
            print(f'No columns found that contain {val}.\n')


def null_to_pandas_na(dataframe: pd.DataFrame) -> pd.DataFrame:
    df = copy(dataframe)
    for col in df.columns:
        if df[col].isna().any():
            df.loc[df[col].isna(), col] = pd.NA
    return df


def get_type_counts(dataframe, columns):
    df = copy(dataframe)
    cols = columns if isinstance(columns, list) else [columns]

    for col in cols:
        type_dict = {}
        total = 0
        for idx, val in df[col].items():
            total += 1
            if type(val) in type_dict:
                type_dict[type(val)] += 1
            else:
                type_dict[type(val)] = 1

        print(f'Type counts for {col}:')
        for k, v in type_dict.items():
            print(f'{k}: {v}')
        print(f'total: {total}\n')


def heads_tails(dataframe):
    max_slice_size = 8
    slice_size = min(len(dataframe) // 2, max_slice_size)
    first_10 = dataframe.head(slice_size)
    last_10 = dataframe.tail(slice_size)
    df = pd.concat([first_10, last_10])
    df = df.reset_index(drop=True)
    return df


# =================================================================================================================== #

if __name__ == '__main__':
    print(f"\n\n---------------------------------------- {__file__.split('/')[-1]}")
