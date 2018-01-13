# -*- coding: utf-8 -*-
"""
This script parses a spreadsheet provided for subnational test data for 8.1.1,
and outputs it in subnational subfolders for each state. This is clearly not
re-usable but writing this is faster than manually creating the CSV files.

This assumes a CSV file temporarily placed in the repo root called:
"SDG 8.1.1 SubNational Example.csv"

"""

import os.path
import pandas as pd
import yaml

scripts_path = os.path.join('scripts', 'site_variables.yml')
with open(scripts_path, 'r') as stream:
    try:
        site = yaml.load(stream)
    except yaml.YAMLError as e:
        print(e)

# For more concise variables below.
HEADER_ALL = site['csv_column_names']['all']
HEADER_YEAR = site['csv_column_names']['year']
FOLDER_DATA_CSV_WIDE = site['folders']['data_csv_wide']
FOLDER_DATA_CSV_SUBNATIONAL = site['folders']['data_csv_subnational']

def main():

    csv_parameters = {
        'filepath_or_buffer': 'SDG 8.1.1 SubNational Example.csv',
        'usecols': [1, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27],
        'skiprows': 3,
        'skipfooter': 11
    }
    df = pd.read_csv(**csv_parameters)

    for index,row in df.iterrows():
        state_name = row['GeoName'].lower().replace(' ', '-')
        row = row.iloc[1:]
        subfolder = os.path.join(FOLDER_DATA_CSV_SUBNATIONAL, 'state', state_name)

        if state_name == 'united-states':
            subfolder = FOLDER_DATA_CSV_WIDE
        else:
            os.makedirs(subfolder, exist_ok=True)

        path = os.path.join(subfolder, 'indicator_8-1-1.csv')
        row.to_csv(path, index_label=HEADER_YEAR, header=[HEADER_ALL])

if __name__ == '__main__':
    main()
