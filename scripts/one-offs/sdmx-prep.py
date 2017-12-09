# -*- coding: utf-8 -*-
"""
This script looks through all of the json files in the /data/sdmx folder
and creates corresponding Jekyll files in the api/sdmx folder.

This assumes that the sdmx.py script has already been run at least once,
so that the json files in /data/sdmx exist.
"""

import glob
import os.path
import pandas as pd

FOLDER_DATA_SDMX_JSON = 'data/sdmx'
FOLDER_PAGES_SDMX = 'api/sdmx'

def main():
    """Create .md versions of al the .json files in data/sdmx."""

    os.makedirs(FOLDER_PAGES_SDMX, exist_ok=True)
    filenames = glob.glob(FOLDER_DATA_SDMX_JSON + "/indicator*.json")
    print("Attempting to creates pages for " + str(len(filenames)) + " SDMX files...")

    for file_in in filenames:
        indicator_id = file_in.split('indicator_')[1]
        indicator_id = indicator_id.split('.')[0]
        file_out = os.path.join(FOLDER_PAGES_SDMX, indicator_id + '.md')
        with open(file_out, 'w') as new_file:
            lines = [
                '---',
                'permalink: /api/sdmx/' + indicator_id + '.xml',
                'layout: sdmx_generic',
                'indicator: "' + indicator_id.replace('-', '.') + '"',
                '---'
            ]
            new_file.write('\n'.join(lines))

    print("Success.")

if __name__ == '__main__':
    main()
