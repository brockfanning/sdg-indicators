# -*- coding: utf-8 -*-
"""
This script looks through all of the CSV files in the /data folder
and convert any that are suitable into tidy (long) form.

Suitability is determined by the presence of column names that follow
a strict naming convention. The rules of this convention are:

1. There is a column is called "Year".
2. There is a column is called "All".
3. Optionally, there are columns following the format: category:value
4. Optionally, there are columns following the format: category1:value1|category2|value2

Here are some examples of valid headers:
* Year, All
* Year, All, Gender:Female, Gender:Male
* Year, All, Age:Under 18, Age:18 to 64
* Year, All|Unit:Inches, All|Unit:Centimeters
* Year, All, Gender:Female|Age:Under 18, Gender:Female|Age:18 to 64
etc...
"""

import glob
import os.path
import pandas as pd

# Some variables to be treated as constants in functions below.
HEADER_YEAR = 'Year'
HEADER_TOTAL = 'All'
HEADER_VALUE = 'Value'

def tidy_headers_check(df):
    """This checks to see if the column headers are suitable for tidying."""

    columns = df.columns.tolist()

    if HEADER_YEAR not in columns:
        return False

    if HEADER_TOTAL not in columns:
        return any(column.startswith(HEADER_TOTAL + '|') for column in columns)

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
        if column == HEADER_TOTAL:
            # The 'All' column gets converted into rows without any categories.
            melted = tidy_melt(df, HEADER_TOTAL, HEADER_TOTAL)
            del melted[HEADER_TOTAL]
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
                if category_in_column == HEADER_TOTAL:
                    # Handle the case where the 'All' column has units.
                    melted = tidy_melt(df, column, HEADER_TOTAL)
                    del melted[HEADER_TOTAL]
                    merged = merged.merge(melted, on=[HEADER_YEAR, HEADER_VALUE], how='outer')
                else:
                    category_parts = category_in_column.split(':')
                    category_name = category_parts[0]
                    category_value = category_parts[1]
                    melted = tidy_melt(df, column, category_name)
                    melted[category_name] = category_value
                    merged = merged.merge(melted, on=[HEADER_YEAR, HEADER_VALUE], how='outer')
            tidy = tidy.append(merged)

    # For human readability, move 'Year' to the front, and 'Value' to the back.
    cols = tidy.columns.tolist()
    cols.pop(cols.index(HEADER_YEAR))
    cols.pop(cols.index(HEADER_VALUE))
    cols = [HEADER_YEAR] + cols + [HEADER_VALUE]
    tidy = tidy[cols]

    return tidy

def tidy_csv(csv):
    """This runs all checks and processing on a CSV file and reports exceptions."""

    try:
        df = pd.read_csv(csv, dtype=str)
    except Exception as e:
        print(csv, e)
        return False

    if not tidy_headers_check(df):
        # For now, don't output error, since most will fail this check.
        #print('CSV file ' + csv + ' did not have valid column names.')
        return False

    try:
        tidy = tidy_dataframe(df)
    except Exception as e:
        print(csv, e)
        return False

    try:
        csv_file = os.path.split(csv)[-1]
        tidy_path = os.path.join('data', 'tidy', csv_file)
        tidy.to_csv(tidy_path, index=False, encoding='utf-8')
        print('Converted ' + csv_file + ' to tidy format.')
    except Exception as e:
        print(csv, e)
        return False

    return True

def main():
    """Tidy up all of the indicator CSVs in the data folder."""

    status = True
    # Create the place to put the files
    os.makedirs("data/tidy", exist_ok=True)

    csvs = glob.glob("data/indicator*.csv")
    print("Attempting to tidy " + str(len(csvs)) + " wide CSV files...")

    for csv in csvs:
        status = status & tidy_csv(csv)

    return status

if __name__ == '__main__':
    status = main()
    if not status:
        raise RuntimeError("Failed tidy conversion")
    else:
        print("Success")
