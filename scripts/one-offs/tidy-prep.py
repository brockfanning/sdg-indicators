# -*- coding: utf-8 -*-
"""
This script looks through all of the indicator files in the /data folder
and ensures that they have the appropriate columns named "Year" and "All".

This is specifically written to the way the USG platform is structured as of
12/4/2017. At the time of this writing, the column for year is lowercase
('year') and the value columns all have arbitrary names. This script changes
those columns to "Year" and "All" respectively, so that they can be more
easily used in the tidy.py script.

Note: The "All" change only happens on datasets that have only a single value
column. It's impossible for this script to know how to handle multiple value
columns, so those will need to changed manually.

In theory this only needs to be run one time ever, after which the data
providers will need updated guidelines on CSV column names.
"""

import glob
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
FOLDER_DATA_CSV_TIDY = site['folders']['data_csv_tidy']

def tidy_prep_fix_csv(filename):
    """This changes 'year' to 'Year' and fixes 'All' on single-value datasets."""

    # To prevent Git from thinking that all lines have changed, we
    # go to a little extra trouble here to preserve newlines.
    dos_line_endings = False
    if "\r\n" in open(filename, 'r', newline='').read():
        dos_line_endings = True

    file_can_be_fixed = True

    # Load the CSV into a dataframe and rename some columns.
    df = pd.read_csv(filename, dtype=str)
    cols = df.columns.tolist()
    cols[0] = HEADER_YEAR
    if len(cols) == 2:
        cols[1] = HEADER_ALL
    else:
        file_can_be_fixed = False
    df.columns = cols

    # Export the dataframe to the same CSV file.
    if file_can_be_fixed:
        if dos_line_endings:
            df.to_csv(filename, index=False, encoding='utf-8', line_terminator='\r\n')
        else:
            df.to_csv(filename, index=False, encoding='utf-8')

def main():
    """Fix CSV headers for all of the indicators in the data folder."""

    filenames = glob.glob(FOLDER_DATA_CSV_TIDY + "/indicator*.csv")
    print("Attempting to fix headers in " + str(len(filenames)) + " CSV files...")

    for filename in filenames:
        tidy_prep_fix_csv(filename)

    print("Success.")

if __name__ == '__main__':
    main()