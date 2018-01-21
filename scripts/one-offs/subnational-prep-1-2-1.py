# -*- coding: utf-8 -*-
"""
This script parses a folder full of zip files, each containing a year's worth
of data relevant to indicator 1-2-1. This is clearly not re-usable, but is
included here in case it's helpful for other indicators. This will likely be
useful for any indicator with a data source of the ACS "FactFinder" website.
This script expects zipfiles obtained for all US states for dataset B17001,
years 2005 through 2016.
"""

import os.path
import pandas as pd
import yaml
import zipfile

site_vars_path = os.path.join('scripts', 'site_variables.yml')
with open(site_vars_path, 'r') as stream:
  try:
    site = yaml.load(stream)
  except yaml.YAMLError as e:
    print(e)

# For more readable code below.
HEADER_ALL = site['csv_column_names']['all']
HEADER_YEAR = site['csv_column_names']['year']
FOLDER_DATA_CSV_WIDE = site['folders']['data_csv_wide']
FOLDER_DATA_CSV_SUBNATIONAL = site['folders']['data_csv_subnational']

CSV_COLUMN_STATE = 'GEO.display-label'
CSV_COLUMN_TOTAL = 'HD01_VD01'
CSV_COLUMN_PART = 'HD01_VD02'

# Each year's data is in a separate file.
YEAR_FILES = {
  2005: 'ACS_05_EST_B17001',
  2006: 'ACS_06_EST_B17001',
  2007: 'ACS_07_1YR_B17001',
  2008: 'ACS_08_1YR_B17001',
  2009: 'ACS_09_1YR_B17001',
  2010: 'ACS_10_1YR_B17001',
  2011: 'ACS_11_1YR_B17001',
  2012: 'ACS_12_1YR_B17001',
  2013: 'ACS_13_1YR_B17001',
  2014: 'ACS_14_1YR_B17001',
  2015: 'ACS_15_1YR_B17001',
  2016: 'ACS_16_1YR_B17001',
}

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

csv_parameters = {
  'usecols': [CSV_COLUMN_STATE, CSV_COLUMN_TOTAL, CSV_COLUMN_PART],
  'skiprows': [1]
}

def main():

  # Start with a blank dataframe with an int Year column. This will become one
  # big dataframe with all the years.
  all_data = pd.DataFrame({ HEADER_YEAR:[] })
  all_data[HEADER_YEAR] = all_data[HEADER_YEAR].astype(int)

  for year in YEAR_FILES:

    # Unzip and load the CSV file.
    filebase = YEAR_FILES[year]
    zip_filename = filebase + '.zip'
    csv_filename = filebase + '_with_ann.csv'
    zip_path = os.path.join('data-to-import', zip_filename)
    with zipfile.ZipFile(zip_path) as z:
      with z.open(csv_filename) as f:
        df = pd.read_csv(f, **csv_parameters)
        # Set the year on all rows.
        df[HEADER_YEAR] = year
        # Add this year to the one big dataframe.
        all_data = all_data.append(df)

  # Create the percentage column.
  all_data[HEADER_ALL] = (all_data[CSV_COLUMN_PART] / all_data[CSV_COLUMN_TOTAL]) * 100

  # Drop unneeded columns.
  all_data = all_data.drop([CSV_COLUMN_PART, CSV_COLUMN_TOTAL], axis='columns')

  # Move year to the front.
  cols = all_data.columns.tolist()
  cols.pop(cols.index(HEADER_YEAR))
  cols = [HEADER_YEAR] + cols
  all_data = all_data[cols]

  states = all_data[CSV_COLUMN_STATE].unique()
  for state in states:
    state_data = all_data[all_data[CSV_COLUMN_STATE] == state].drop(CSV_COLUMN_STATE, axis='columns')
    abbrev = state_abbreviation(state)
    subfolder = os.path.join(FOLDER_DATA_CSV_SUBNATIONAL, 'state', abbrev)
    os.makedirs(subfolder, exist_ok=True)
    path = os.path.join(subfolder, 'indicator_1-2-1.csv')
    state_data.to_csv(path, float_format='%.2f', index=False, header=[HEADER_YEAR, HEADER_ALL])

if __name__ == '__main__':
  main()



