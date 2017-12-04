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
import csv
import shutil
import os
import stat

def copy_complete(source, target):
    # copy content, stat-info (mode too), timestamps...
    shutil.copy2(source, target)
    # copy owner and group
    st = os.stat(source)
    os.chown(target, st[stat.ST_UID], st[stat.ST_GID])

def tidy_prep_fix_csv(filename):
    """This changes 'year' to 'Year', and fixes 'All' on single-value datasets."""

    temp_file = filename + '.tmp'
    copy_complete(filename, temp_file)
    with open(filename, newline='') as in_file, open(temp_file, 'w', newline='') as out_file:
        reader = csv.reader(in_file)
        writer = csv.writer(out_file)

        header = True
        for row in reader:
            if header:
                header = False
                row[0] = 'Year'
                if len(row) == 2:
                    row[1] = 'All'
            writer.writerow(row)

    shutil.move(temp_file, filename)

def main():
    """Fix CSV headers for all of the indicators in the data folder."""

    filenames = glob.glob("data/indicator*.csv")
    print("Attempting to fix headers in " + str(len(filenames)) + " CSV files...")

    for filename in filenames:
        tidy_prep_fix_csv(filename)

if __name__ == '__main__':
    main()
