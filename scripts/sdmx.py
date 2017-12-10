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
import json
import datetime
import pandas as pd
import yaml

scripts_path = os.path.join('scripts', 'site_variables.yml')
with open(scripts_path, 'r') as stream:
    try:
        site = yaml.load(stream)
    except yaml.YAMLError as e:
        print(e)

# For more readable code below.
HEADER_ALL = site['csv_column_names']['all']
HEADER_YEAR = site['csv_column_names']['year']
HEADER_VALUE = site['csv_column_names']['value']
FOLDER_DATA_CSV_TIDY = site['folders']['data_csv_tidy']
FOLDER_DATA_SDMX_JSON = site['folders']['data_sdmx_json']
FOLDER_PAGES_INDICATORS = site['folders']['pages_indicators']
META_KEYS_METHOD = site['indicator_metadata_keys']['method_of_computation']
META_KEYS_UNIT = site['indicator_metadata_keys']['unit_of_measure']
META_KEYS_TITLE = site['indicator_metadata_keys']['title']
META_KEYS_METADATA_DATE = site['indicator_metadata_keys']['data_metadata_updated']

def sdmx_headers_check(df):
    """This checks to see if the column headers are suitable for SDMX."""

    columns = df.columns.tolist()

    if HEADER_YEAR not in columns:
        return False

    if HEADER_VALUE not in columns:
        return False

    return True

def mapped_val(key, map):
    # Return an empty string if there is no value.
    if key not in map:
        return ''
    # Otherwise return the value.
    return map[key]

def map_str(original, map):
    # Return the original if there is no mapping.
    if original not in map:
        return original
    # Otherwise return the mapped version.
    return map[original]

def sdmx_indicator_metadata(indicator_id):
    """This gets the "front matter" metadata about an indicator."""

    path = os.path.join(FOLDER_PAGES_INDICATORS, indicator_id + '.md')
    with open(path, 'r') as file:
        contents = file.read()
        front_matter = contents.split('---')[1]
        metadata = yaml.load(front_matter)
    return metadata

def sdmx_json(df, indicator_id):
    """This converts a dataframe into a json string."""

    # First try to get metadata about this dataset.
    meta = sdmx_indicator_metadata(indicator_id)

    # Get any maps of concepts and values.
    concepts = site['sdmx_concept_columns'].copy()
    if 'sdmx_concept_columns' in meta:
        concepts.update(meta['sdmx_concept_columns'])
    values = site['sdmx_value_codes'].copy()
    if 'sdmx_value_codes' in meta:
        values.update(meta['sdmx_value_codes'])

    json_dict = dict()
    header_dict = dict()
    series_dict = dict()
    attributes_base = dict()

    # Start with some SDMX concept IDs that are assumed to be necessary.
    attributes_base['FREQ'] = 'A'
    attributes_base['COLL_METHOD'] = mapped_val(META_KEYS_METHOD, meta)
    attributes_base['TITLE'] = mapped_val(META_KEYS_TITLE, meta)
    attributes_base['UNIT_MEASURE'] = mapped_val(META_KEYS_UNIT, meta)

    for index, row in df.iterrows():

        # Call out the non-observation columns.
        non_observation_cols = row.drop([HEADER_YEAR, HEADER_VALUE])
        # Use our mapping to change column names.
        non_observation_cols = non_observation_cols.rename(concepts)
        # Use our mapping to change values.
        non_observation_cols = non_observation_cols.replace(values)
        # Uniquely identify each combination of columns.
        series_key = hash(tuple(non_observation_cols))

        # Initialize the series in the series dict, if it does not exist.
        if series_key not in series_dict:
            series_dict[series_key] = dict()
            attributes = attributes_base.copy()
            attributes.update(non_observation_cols.dropna().to_dict())
            # Add the attributes to the series.
            series_dict[series_key]['attributes'] = attributes
            # Initialize an empty list of observations.
            series_dict[series_key]['observations'] = []

        # Enforce certain keys for year and value, because the Jekyll template
        # expects them in a certain way.
        observation = row[[HEADER_YEAR, HEADER_VALUE]].to_dict()
        observation['year'] = observation.pop(HEADER_YEAR)
        observation['value'] = observation.pop(HEADER_VALUE)
        series_dict[series_key]['observations'].append(observation)

    header_dict['id'] = indicator_id
    header_dict['prepared'] = mapped_val(META_KEYS_METADATA_DATE, meta)
    header_dict['sender'] = '???' #TODO

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
        indicator_id = csv_filename.split('.')[0]
        indicator_id = indicator_id.split('indicator_')[1]
        json = sdmx_json(df, indicator_id)
    except Exception as e:
        print(csv, e)
        return False

    try:
        json_path = os.path.join(FOLDER_DATA_SDMX_JSON, json_filename)
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
    os.makedirs(FOLDER_DATA_SDMX_JSON, exist_ok=True)
    # Read all the files in the source location.
    csvs = glob.glob(FOLDER_DATA_CSV_TIDY + "/indicator*.csv")
    print("Attempting to create SDMX data for " + str(len(csvs)) + " CSV files...")

    for csv in csvs:
        status = status & sdmx_csv(csv)

    return status

if __name__ == '__main__':
    if not main():
        raise RuntimeError("Failed SDMX conversion")
    else:
        print("Success")
