# -*- coding: utf-8 -*-
"""
This script parses a spreadsheet provided for subnational test data for 7.2.1,
and outputs it in subnational subfolders for each state. This is clearly not
re-usable but writing this is faster than manually creating the CSV files. The
source data can be downloaded at https://www.eia.gov/state/seds/CDF/Complete_SEDS.csv.

This assumes a CSV file temporarily placed in the data-to-import folder called:
"Complete_SEDS.csv"
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
        'filepath_or_buffer': 'data-to-import/Complete_SEDS.csv',
        'usecols': [1, 2, 3, 4]
    }
    df = pd.read_csv(**csv_parameters)

    # Quickly reduce the total since is over 1 million rows. We only care about:
    # MSN = TETCB (total energy consumption)
    # MSN = RETCB (renewable energy consumption)
    total_mask = df.MSN == 'TETCB'
    renew_mask = df.MSN == 'RETCB'
    df = df[total_mask | renew_mask]
    # Also limit to 2000 and later.
    df = df[df['Year'] >= 2000]
    # Get the masks again.
    total_mask = df.MSN == 'TETCB'
    renew_mask = df.MSN == 'RETCB'
    # Create 2 temporary DataFrames and then merge them together.
    total = df[total_mask].drop('MSN', axis='columns').rename({'Data': 'Total'}, axis='columns')
    renew = df[renew_mask].drop('MSN', axis='columns').rename({'Data': 'Renew'}, axis='columns')
    df = total.merge(renew, on=['Year', 'StateCode'])
    # Create the percentage column we actually want.
    df['percent'] = (df['Renew'] / df['Total']) * 100
    # Drop unneeded columns.
    df = df.drop(['Total', 'Renew'], axis='columns')

    states = df.StateCode.unique()

    for state in states:
        data = df[df['StateCode'] == state]
        data = data.drop('StateCode', axis=1)
        if state == 'US':
            subfolder = FOLDER_DATA_CSV_WIDE
        else:
            subfolder = os.path.join(FOLDER_DATA_CSV_SUBNATIONAL, 'state', state)
            os.makedirs(subfolder, exist_ok=True)
        path = os.path.join(subfolder, 'indicator_7-2-1.csv')
        data.to_csv(path, float_format='%.2f', index=False, header=[HEADER_YEAR, HEADER_ALL])

if __name__ == '__main__':
    main()
