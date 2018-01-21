# -*- coding: utf-8 -*-
"""
This script parses a folder full of zip files, each containing a year's worth
of data relevant to indicator 5-5-2. This is clearly not re-usable, but is
included here in case it's helpful for other indicators. This will likely be
useful for any indicator with a data source of the ACS "FactFinder" website.
This script expects zipfiles obtained for all US states for dataset S2402,
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

YEAR_FILES = {
  2005: 'ACS_05_EST_S2402',
  2006: 'ACS_06_EST_S2402',
  2007: 'ACS_07_1YR_S2402',
  2008: 'ACS_08_1YR_S2402',
  2009: 'ACS_09_1YR_S2402',
  2010: 'ACS_10_1YR_S2402',
  2011: 'ACS_11_1YR_S2402',
  2012: 'ACS_12_1YR_S2402',
  2013: 'ACS_13_1YR_S2402',
  2014: 'ACS_14_1YR_S2402',
  2015: 'ACS_15_1YR_S2402',
  2016: 'ACS_16_1YR_S2402',
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

CSV_COLUMN_STATE = 'GEO.display-label'
CSV_COLUMN_VALUE = 'HC03_EST_VC04'

csv_parameters = {
  'usecols': [CSV_COLUMN_STATE, CSV_COLUMN_VALUE],
  'skiprows': [1]
}

def main():

  all_data = pd.DataFrame({HEADER_YEAR:[], CSV_COLUMN_VALUE:[], CSV_COLUMN_STATE:[]})
  all_data[HEADER_YEAR] = all_data[HEADER_YEAR].astype(int)

  for year in YEAR_FILES:

    filebase = YEAR_FILES[year]
    zip_filename = filebase + '.zip'
    csv_filename = filebase + '_with_ann.csv'
    zip_path = os.path.join('data-to-import', zip_filename)

    with zipfile.ZipFile(zip_path) as z:
      with z.open(csv_filename) as f:
        df = pd.read_csv(f, **csv_parameters)
        df[HEADER_YEAR] = year
        all_data = all_data.append(df)

  all_data = all_data.rename({
    CSV_COLUMN_STATE: 'state',
    CSV_COLUMN_VALUE: HEADER_ALL
  }, axis='columns')

  # Move year to the front.
  cols = all_data.columns.tolist()
  cols.pop(cols.index(HEADER_YEAR))
  cols = [HEADER_YEAR] + cols
  all_data = all_data[cols]

  states = all_data.state.unique()
  for state in states:
    state_data = all_data[all_data['state'] == state].drop('state', axis='columns')
    abbrev = state_abbreviation(state)
    subfolder = os.path.join(FOLDER_DATA_CSV_SUBNATIONAL, 'state', abbrev)
    os.makedirs(subfolder, exist_ok=True)
    path = os.path.join(subfolder, 'indicator_5-5-2.csv')
    state_data.to_csv(path, index=False, header=[HEADER_YEAR, HEADER_ALL])

if __name__ == '__main__':
  main()



