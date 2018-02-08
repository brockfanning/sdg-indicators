# -*- coding: utf-8 -*-
"""
This script parses an Excel file with multiple sheets to gather subnational
time-series data for SDG indicator 2-1-2. It imports the data in "wide" format
with subfolders for US states.

This assumes a file called "State Food Insecurity for SDG.xlsx" exists in the
data-to-import folder.
"""

import os.path
import pandas as pd
import yaml

SITE_VARS_PATH = os.path.join('scripts', 'site_variables.yml')
with open(SITE_VARS_PATH, 'r') as stream:
    try:
        SITE = yaml.load(stream)
    except yaml.YAMLError as e:
        print(e)

# For more concise variables below.
HEADER_ALL = SITE['csv_column_names']['all']
HEADER_YEAR = SITE['csv_column_names']['year']
FOLDER_DATA_CSV_WIDE = SITE['folders']['data_csv_wide']
FOLDER_DATA_CSV_SUBNATIONAL = SITE['folders']['data_csv_subnational']
HEADER_REGION = 'state'

def main():

    # Normally each year is a separate series, but in this case the data is
    # only available in 3-year groups.
    excel_sheets = {
        '1999-2001',
        '2002-04',
        '2005-07',
        '2008-10',
        '2011-13',
        '2014-16'
    }
    excel_path = os.path.join('data-to-import', 'State Food Insecurity for SDG.xlsx')

    # First create a large dataframe with all the info.
    all_data = pd.DataFrame({ HEADER_YEAR:[], HEADER_REGION:[], HEADER_ALL:[] })

    for sheet in excel_sheets:
        excel_params = {
            'io': excel_path,
            'sheet_name': sheet,
            'skiprows': 7,
            'skip_footer': 4,
            'usecols': [0, 4],
            'names': [HEADER_REGION, HEADER_ALL]
        }
        df = pd.read_excel(**excel_params).dropna()
        df[HEADER_YEAR] = sheet
        all_data = all_data.append(df)

    # Move year to the front.
    cols = all_data.columns.tolist()
    cols.pop(cols.index(HEADER_YEAR))
    cols = [HEADER_YEAR] + cols
    all_data = all_data[cols]

    # Loop through the states.
    states = all_data[HEADER_REGION].unique()
    for state in states:
        state_data = all_data[all_data[HEADER_REGION] == state].drop(HEADER_REGION, axis='columns')
        if 'U.S.' in state:
            # Let's not overwrite the federal data.
            continue
        else:
            subfolder = os.path.join(FOLDER_DATA_CSV_SUBNATIONAL, HEADER_REGION, state)
        os.makedirs(subfolder, exist_ok=True)
        path = os.path.join(subfolder, 'indicator_2-1-2.csv')
        state_data.to_csv(path, index=False, header=[HEADER_YEAR, HEADER_ALL])

if __name__ == '__main__':
    main()
