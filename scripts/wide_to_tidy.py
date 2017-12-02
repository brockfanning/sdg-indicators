# -*- coding: utf-8 -*-
"""
This script looks through all of the CSV files in the /data folder
and convert any that are suitable into tidy (long) form.

Suitability is determined by the presence of column names that follow
a strict naming convention. The rules of this convention are:

1. The first column is called "year".
2. The second column is called "total".
3. At least one column following the format [category]:[value].
4. Multiple category/value pairs can be separated by a pipe (|).

"""

import glob
import os.path
import pandas as pd

def check_headers(df, csv):
    """This checks to see if the column headers are suitable for tidying."""
    status = True
    cols = df.columns

    if cols[0] != 'year':
        status = False
        print(csv, ': First column not called "year"')
    if cols[1] != 'total':
        status = False
        print(csv, ': Second column not called "total"')

    return status

def wide_to_tidy(df, csv):

    categories = dict()
    columns = list(df.columns.values)
    # Look for all the columns following the naming convention for
    # disaggregation: "[Category]:[Value]" (eg, "Gender:Female")
    for column in columns:
        categories_in_column = column.split('|')
        for category_in_column in categories_in_column:
            category_parts = category_in_column.split(':')
            if len(category_parts) > 1:
                category_name = category_parts[0]
                category_value = category_parts[1]
                if category_name not in categories:
                    categories[category_name] = []
                categories[category_name].append(category_value)
                # Rename the column now because we no longer need the naming
                # convention.
                df.rename(columns = {column: category_value}, inplace = True)
    # If we didn't find anything, no tidying is possible.
    if not categories:
        print('No categories found.')
        return False

    # "Melt" each category and concat them for a tidy format.
    melts = []
    for category in categories:
        melts.append(pd.melt(df, id_vars=['year'], value_vars=categories[category], var_name=category))
    # Also add the totals.
    total = pd.melt(df, id_vars=['year'], value_vars=['total'], var_name='total')
    del total['total']
    melts.append(total)
    tidy = pd.concat(melts)

    # For human readability, move the 'year' column to the front.
    cols = tidy.columns.tolist()
    cols.insert(0, cols.pop(-1))
    tidy = tidy[cols]

    return tidy

def tidy_csv(csv):
    """Convert wide CSV file to tidy format

    If there are any problems return False to stop the build.

    Args:
        csv (str): The file name that we want to tidy

    Returns:
        bool: Status
    """
    status = True

    try:
        df = pd.read_csv(csv)
    except Exception as e:
        print(csv, e)
        return False

    if not check_headers(df, csv):
        return False

    try:
        tidy = wide_to_tidy(df, csv)
    except Exception as e:
        print(csv, e)
        return False

    try:
        csv_file = os.path.split(csv)[-1]
        tidy_file = csv_file.replace('indicator', 'tidy.indicator')
        tidy_path = os.path.join('data', 'tidy', tidy_file)
        tidy.to_csv(tidy_path, index=False, encoding='utf-8')
    except Exception as e:
        print(csv, e)
        return False

    return status

def main():
    """Tidy up all of the indicator CSVs in the data folder"""
    status = True
    # Create the place to put the files
    os.makedirs("data/tidy", exist_ok=True)

    csvs = glob.glob("data/convert-to-tidy/indicator*.csv")
    print("Tidying " + str(len(csvs)) + " wide CSV files...")

    for csv in csvs:
        status = status & tidy_csv(csv)
    return(status)

if __name__ == '__main__':
    status = main()
    if (not status):
        raise RuntimeError("Failed tidy conversion")
    else:
        print ("Success")
