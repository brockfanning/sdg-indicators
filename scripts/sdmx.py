# -*- coding: utf-8 -*-
"""
This script looks through all of the CSV files in the /data folder
and generates JSON output that will be used by Jekyll layouts to output
SDMX-formatted files. Essentially this structures the data so that each
row of JSON represents one "series" (equivalent to one column in a "wide"
CSV file) that contains "attributes" (metadata and disaggregation values)
and "observations" (the year and the value).

The files are generated and placed in an "sdmx" folder inside the data folder.
"""

import glob
import os.path
import pandas as pd
import json
import datetime

# Some variables to be treated as constants in functions below.
HEADER_YEAR = 'year'
HEADER_VALUE = 'value'
FOLDER = 'data'
SUBFOLDER = 'sdmx'

def sdmx_headers_check(df):
    """This checks to see if the column headers are suitable for SDMX."""

    columns = df.columns.tolist()

    if HEADER_YEAR not in columns:
        return False

    if HEADER_VALUE not in columns:
        return False

    return True

def sdmx_json(df):
    """This converts a dataframe into a json string."""

    json_dict = dict()
    header_dict = dict()
    series_dict = dict()
    attributes_base = dict()

    # TODO: Get global attributes from metadata, etc.
    attributes_base['FREQ'] = 'A'
    attributes_base['UNIT_MULT'] = 'TODO'
    attributes_base['COLL_METHOD'] = 'TODO'
    attributes_base['TITLE'] = 'TODO'

    for index,row in df.iterrows():

        # Uniquely identify (hash) each combination of non-observation columns.
        non_observation_cols = row.drop([HEADER_YEAR, HEADER_VALUE])
        series_key = hash(tuple(non_observation_cols))

        # Initialize the series in the series dict, if it does not exist.
        if series_key not in series_dict:
            series_dict[series_key] = dict()
            attributes = attributes_base.copy()
            attributes.update(non_observation_cols.dropna().to_dict())
            series_dict[series_key]['attributes'] = attributes
            series_dict[series_key]['observations'] = []

        observation = row[[HEADER_VALUE, HEADER_YEAR]]
        series_dict[series_key]['observations'].append(observation.to_dict())

    # TODO: Get proper ID and Sender.
    header_dict['ID'] = 'TODO'
    header_dict['Prepared'] = datetime.datetime.now().isoformat()
    header_dict['Sender'] = 'TODO'

    json_dict['header'] = header_dict
    json_dict['series'] = list(series_dict.values())

    return json.dumps(json_dict, indent=4)

def sdmx_csv(csv):
    """This runs all checks and processing on a CSV file and reports exceptions."""

    csv_filename = os.path.split(csv)[-1]
    json_filename = csv_filename.split('.')[0] + '.json'

    try:
        df = pd.read_csv(csv)
    except Exception as e:
        print(csv, e)
        return False

    if not sdmx_headers_check(df):
        # For now, don't output error, since most will fail this check.
        #print('CSV file ' + csv + ' did not have valid column names.')
        return False

    try:
        json = sdmx_json(df)
    except Exception as e:
        print(csv, e)
        return False

    try:
        json_path = os.path.join(FOLDER, SUBFOLDER, json_filename)
        with open(json_path, 'w') as json_file:
            json_file.write(json)
        print('Created ' + json_filename + ' for SDMX use.')
    except Exception as e:
        print(csv, e)
        return False

    return True

def main():
    """Produce SDMX data for all of the indicator CSVs in the data folder."""

    status = True

    # Create the place to put the files.
    os.makedirs(os.path.join(FOLDER, SUBFOLDER), exist_ok=True)
    # Read all the files in the source location.
    csvs = glob.glob(FOLDER + "/indicator*.csv")
    print("Attempting to create SDMX data for " + str(len(csvs)) + " CSV files...")

    for csv in csvs:
        status = status & sdmx_csv(csv)

    return status

if __name__ == '__main__':
    if not main():
        raise RuntimeError("Failed SDMX conversion")
    else:
        print("Success")
