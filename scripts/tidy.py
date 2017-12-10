# -*- coding: utf-8 -*-
"""
This script looks through all of the CSV files in the /data folder
and convert any that are suitable into tidy (long) form.

Suitability is determined by the presence of column names that follow
a strict naming convention. The rules of this convention are:

1. There is a column is called "year".
2. There is a column is called "all", or multiple columns that start with "all|"
   (see examples below).
3. Optionally, there are columns following the format: category:value
4. Optionally, there are columns following the format: category1:value1|category2|value2

Here are some examples of valid headers:
* year, all
* year, all, sex:female, sex:male
* year, all, age:under18, age:18to64
* year, all|unit:gdp_global, all|unit:gdp_national
* year, all, sex:female|age:under18, sex:female|age:18to64
etc...
"""

import glob
import os.path
import pandas as pd
import yaml

scripts_path = os.path.join('scripts', 'site_variables.yml')
with open(scripts_path, 'r') as stream:
    try:
        site = yaml.load(stream)
    except yaml.YAMLError as e:
        print(e)

# For more readable code below.
HEADER_ALL = site['csv_column_names']['all']
HEADER_YEAR = site['csv_column_names']['year']
HEADER_VALUE = site['csv_column_names']['value']
FOLDER_DATA_CSV_TIDY = site['folders']['data_csv_tidy']
FOLDER_DATA_CSV_WIDE = site['folders']['data_csv_wide']

def tidy_headers_check(df):
    """This checks to see if the column headers are suitable for tidying."""

    columns = df.columns.tolist()

    if HEADER_YEAR not in columns:
        return False

    if HEADER_ALL not in columns:
        return any(column.startswith(HEADER_ALL + '|') for column in columns)

    return True

def tidy_blank_dataframe():
    """This starts a blank dataframe with our required tidy columns."""

    blank = pd.DataFrame({HEADER_YEAR:[], HEADER_VALUE:[]})
    blank[HEADER_YEAR] = blank[HEADER_YEAR].astype(int)

    return blank

def tidy_melt(df, value_var, var_name):
    """This runs a Pandas melt() call with common parameters."""

    return pd.melt(
        df,
        id_vars=[HEADER_YEAR],
        value_vars=[value_var],
        var_name=var_name,
        value_name=HEADER_VALUE)

def tidy_dataframe(df):
    """This converts the data from wide to tidy, based on the column names."""

    tidy = tidy_blank_dataframe()
    for column in df.columns.tolist():
        if column == HEADER_ALL:
            # The 'all' column gets converted into rows without any categories.
            melted = tidy_melt(df, HEADER_ALL, HEADER_ALL)
            del melted[HEADER_ALL]
            tidy = tidy.append(melted)
        elif '|' not in column and ':' in column:
            # Columns matching the pattern 'category:value' get converted into
            # rows where 'category' is set to 'value'.
            category_parts = column.split(':')
            category_name = category_parts[0]
            category_value = category_parts[1]
            melted = tidy_melt(df, column, category_name)
            melted[category_name] = category_value
            tidy = tidy.append(melted)
        elif '|' in column and ':' in column:
            # Columns matching the pattern 'category1:value1|category2:value2'
            # get converted to rows where 'category1' is set to 'value1' and
            # 'category2' is set to 'value2'.
            merged = tidy_blank_dataframe()
            categories_in_column = column.split('|')
            for category_in_column in categories_in_column:
                if category_in_column == HEADER_ALL:
                    # Handle the case where the 'all' column has units.
                    # Eg: all|unit:gdp_global, all|unit:gdp_national.
                    melted = tidy_melt(df, column, HEADER_ALL)
                    del melted[HEADER_ALL]
                    merged = merged.merge(melted, on=[HEADER_YEAR, HEADER_VALUE], how='outer')
                else:
                    category_parts = category_in_column.split(':')
                    category_name = category_parts[0]
                    category_value = category_parts[1]
                    melted = tidy_melt(df, column, category_name)
                    melted[category_name] = category_value
                    merged = merged.merge(melted, on=[HEADER_YEAR, HEADER_VALUE], how='outer')
            tidy = tidy.append(merged)

    # For human readability, move 'year' to the front, and 'value' to the back.
    cols = tidy.columns.tolist()
    cols.pop(cols.index(HEADER_YEAR))
    cols.pop(cols.index(HEADER_VALUE))
    cols = [HEADER_YEAR] + cols + [HEADER_VALUE]
    tidy = tidy[cols]

    # Remove any rows with no value.
    tidy = tidy.dropna(subset=[HEADER_VALUE])

    return tidy

def tidy_csv_from_disaggregation_folder(csv, subfolder):
    """This converts a CSV into a dataframe, tweaks the headers, and returns it."""

    try:
        df = pd.read_csv(csv, dtype=str)
    except Exception as e:
        print(csv, e)
        return False

    # Convert the folder structure into a column according to our syntax rules.
    # For example: state/alabama will turn into 'state:alabama'.
    subfolder = subfolder.replace(FOLDER_DATA_CSV_WIDE, '')
    subfolder = subfolder.strip(os.sep)
    subfolder_column = subfolder.replace(os.sep, ':')

    # Add this to the columns in the dataframe.
    columns = dict()
    for column in df.columns.tolist():
        fixed = column
        if column == HEADER_ALL:
            fixed = subfolder_column
        elif column.startswith(HEADER_ALL + '|'):
            fixed = column.replace(HEADER_ALL + '|', subfolder_column + '|')
        elif column == HEADER_YEAR:
            fixed = HEADER_YEAR
        else:
            fixed = subfolder_column + '|' + column
        columns[column] = fixed

    return df.rename(columns, axis='columns')

def tidy_csv(csv, disaggregation_folders):
    """This runs all checks and processing on a CSV file and reports exceptions."""

    csv_filename = os.path.split(csv)[-1]

    try:
        df = pd.read_csv(csv, dtype=str)
    except Exception as e:
        print(csv, e)
        return False

    if not tidy_headers_check(df):
        # For now, don't output error, since most will fail this check.
        #print('CSV file ' + csv + ' did not have valid column names.')
        return False

    # Look in any disaggregation folders for a corresponding file.
    for folder in disaggregation_folders:
        for subfolder in disaggregation_folders[folder]:
            disaggregation_file = subfolder + csv_filename
            if os.path.isfile(disaggregation_file):
                dis_df = tidy_csv_from_disaggregation_folder(disaggregation_file, subfolder)
                df = pd.merge(df, dis_df, how='outer', on=HEADER_YEAR)

    try:
        tidy = tidy_dataframe(df)
    except Exception as e:
        print(csv, e)
        return False

    try:
        tidy_path = os.path.join(FOLDER_DATA_CSV_TIDY, csv_filename)
        tidy.to_csv(tidy_path, index=False, encoding='utf-8')
        print('Converted ' + csv_filename + ' to tidy format.')
    except Exception as e:
        print(csv, e)
        return False

    return True

def main():
    """Tidy up all of the indicator CSVs in the data folder."""

    status = True

    # Create the place to put the files.
    os.makedirs(FOLDER_DATA_CSV_TIDY, exist_ok=True)
    # Read all the files in the source location.
    csvs = glob.glob(FOLDER_DATA_CSV_WIDE + "/indicator*.csv")
    print("Attempting to tidy " + str(len(csvs)) + " wide CSV files...")

    # Check here to see if there are any subfolder-style disaggregations.
    disaggregation_folders = dict()
    folders = glob.glob(FOLDER_DATA_CSV_WIDE + '/*/')
    for folder in folders:
        subfolders = glob.glob(folder + '/*/')
        if (subfolders):
            disaggregation_folders[folder] = subfolders

    for csv in csvs:
        status = status & tidy_csv(csv, disaggregation_folders)

    return status

if __name__ == '__main__':
    if not main():
        raise RuntimeError("Failed tidy conversion")
    else:
        print("Success")
