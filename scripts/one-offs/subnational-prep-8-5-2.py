# -*- coding: utf-8 -*-
"""

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
HEADER_REGION = 'state'

#SOURCE_GROUP = 'Total'
SOURCE_GROUP = 'Men'

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
        'Virgin Islands': 'VI',
        'Virginia': 'VA',
        'Washington': 'WA',
        'West Virginia': 'WV',
        'Wisconsin': 'WI',
        'Wyoming': 'WY'
    }
    return abbreviations[state]

def main():
    files = {
        1999: 'https://www.bls.gov/lau/table12full99.xlsx',
        2000: 'https://www.bls.gov/lau/table12full00.xlsx',
        2001: 'https://www.bls.gov/lau/table12full01.xlsx',
        2002: 'https://www.bls.gov/lau/table12full02.xlsx',
        2003: 'https://www.bls.gov/lau/table14full03.xlsx',
        2004: 'https://www.bls.gov/lau/table14full04.xlsx',
        2005: 'https://www.bls.gov/lau/table14full05.xlsx',
        2006: 'https://www.bls.gov/lau/table14full06.xlsx',
        2007: 'https://www.bls.gov/lau/table14full07.xlsx',
        2008: 'https://www.bls.gov/lau/table14full08.xlsx',
        2009: 'https://www.bls.gov/lau/table14full09.xlsx',
        2010: 'https://www.bls.gov/lau/table14full10.xlsx',
        2011: 'https://www.bls.gov/lau/table14full11.xlsx',
        2012: 'https://www.bls.gov/lau/table14full12.xlsx',
        2013: 'https://www.bls.gov/lau/table14full13.xlsx',
        2014: 'https://www.bls.gov/lau/table14full14.xlsx',
        2015: 'https://www.bls.gov/lau/table14full15.xlsx',
        2016: 'https://www.bls.gov/lau/table14full16.xlsx',
        2017: 'https://www.bls.gov/lau/ptable14full2017.xlsx'
    }
    all_data = pd.DataFrame({ HEADER_YEAR:[], HEADER_REGION:[], HEADER_ALL:[] })
    all_data[HEADER_YEAR] = all_data[HEADER_YEAR].astype(int)

    for year in files:
        excel_path = files[year]
        excel_params = {
            'io': files[year],
            'skiprows': 6,
            'skip_footer': 9,
            'usecols': [2, 3, 10],
            'names': [HEADER_REGION, 'group', HEADER_ALL]
        }
        df = pd.read_excel(**excel_params).dropna()
        df[HEADER_YEAR] = year
        all_data = all_data.append(df[df['group'] == SOURCE_GROUP])

    all_data = all_data.drop('group', axis='columns')

    print(all_data)

    states = all_data.state.unique()

    # Move year to the front.
    cols = all_data.columns.tolist()
    cols.pop(cols.index(HEADER_YEAR))
    cols = [HEADER_YEAR] + cols
    all_data = all_data[cols]

    for state in states:
        data = all_data[all_data['state'] == state]
        data = data.drop('state', axis='columns')
        abbrev = state_abbreviation(state)
        subfolder = os.path.join(FOLDER_DATA_CSV_SUBNATIONAL, 'state', abbrev)
        os.makedirs(subfolder, exist_ok=True)
        path = os.path.join(subfolder, 'indicator_8-5-2x.csv')
        data.to_csv(path, index=False, header=[HEADER_YEAR, HEADER_ALL])

if __name__ == '__main__':
    main()
