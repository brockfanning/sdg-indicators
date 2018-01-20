# -*- coding: utf-8 -*-
"""
This script parses a spreadsheet provided for subnational test data for 3.3.1,
and outputs it in subnational subfolders for each state. This is clearly not
re-usable but writing this is faster than manually creating the CSV files. The
source data can be downloaded from https://www.cdc.gov/nchhstp/atlas/index.htm
after going through the steps to get to the "Export" button.

This assumes a CSV file temporarily placed in the data-to-import folder called:
"AtlasPlusTableData_HIV_Diagnoses.csv"
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

def state_abbreviation(state):
    abbreviations = {
        'United States': 'US',
        'Alabama': 'AL',
        'Alaska': 'AK',
        'American Samoa': 'AS',
        'Arizona': 'AZ',
        'Arkansas': 'AR',
        'California': 'CA',
        'Colorado': 'CO',
        'Connecticut': 'CT',
        'Delaware': 'DE',
        'District of Columbia': 'DC',
        'Federated States Of Micronesia': 'FM',
        'Florida': 'FL',
        'Georgia': 'GA',
        'Guam': 'GU',
        'Hawaii': 'HI',
        'Idaho': 'ID',
        'Illinois': 'IL',
        'Indiana': 'IN',
        'Iowa': 'IA',
        'Kansas': 'KS',
        'Kentucky': 'KY',
        'Louisiana': 'LA',
        'Maine': 'ME',
        'Marshall Islands': 'MH',
        'Maryland': 'MD',
        'Massachusetts': 'MA',
        'Michigan': 'MI',
        'Minnesota': 'MN',
        'Mississippi': 'MS',
        'Missouri': 'MO',
        'Montana': 'MT',
        'Nebraska': 'NE',
        'Nevada': 'NV',
        'New Hampshire': 'NH',
        'New Jersey': 'NJ',
        'New Mexico': 'NM',
        'New York': 'NY',
        'North Carolina': 'NC',
        'North Dakota': 'ND',
        'Northern Mariana Islands': 'MP',
        'Ohio': 'OH',
        'Oklahoma': 'OK',
        'Oregon': 'OR',
        'Palau': 'PW',
        'Pennsylvania': 'PA',
        'Puerto Rico': 'PR',
        'Rhode Island': 'RI',
        'South Carolina': 'SC',
        'South Dakota': 'SD',
        'Tennessee': 'TN',
        'Texas': 'TX',
        'Utah': 'UT',
        'Vermont': 'VT',
        'U.S. Virgin Islands': 'VI',
        'Virginia': 'VA',
        'Washington': 'WA',
        'West Virginia': 'WV',
        'Wisconsin': 'WI',
        'Wyoming': 'WY'
    }
    return abbreviations[state]

def main():

    csv_parameters = {
        'filepath_or_buffer': 'data-to-import/AtlasPlusTableData_HIV_Diagnoses.csv',
        'usecols': [0, 1, 2],
        'index_col': 0,
        'skiprows': 6
    }
    df = pd.read_csv(**csv_parameters)

    states = df.Geography.unique()

    for state in states:
        data = df[df['Geography'] == state]
        data = data.drop('Geography', axis=1)
        abbrev = state_abbreviation(state)
        subfolder = os.path.join(FOLDER_DATA_CSV_SUBNATIONAL, 'state', abbrev)
        os.makedirs(subfolder, exist_ok=True)
        path = os.path.join(subfolder, 'indicator_3-3-1.csv')
        data.to_csv(path, index_label=HEADER_YEAR, header=[HEADER_ALL])

if __name__ == '__main__':
    main()
