import csv
import pandas as pd

with open('../data/indicator_1-2-1.csv', newline='') as csvfile:
    df = pd.read_csv(csvfile)
    disaggregations = dict()
    other_columns = []
    columns = list(df.columns.values)
    # Look for all the columns following the naming convention for
    # disaggregation: "[Category]:[Value]" (eg, "Gender:Female")
    for column in columns:
        if ':' in column:
            parts = column.split(':')
            disaggregation_name = parts[0]
            disaggregation_value = parts[1]
            if disaggregation_name not in disaggregations:
                disaggregations[disaggregation_name] = []
            disaggregations[disaggregation_name].append(disaggregation_value)
            # Rename the column now because we no longer need the naming
            # convention.
            df.rename(columns = {column: disaggregation_value}, inplace = True)
        elif column != 'year':
            other_columns.append(column)
    # If we didn't find anything, no tidying is possible.
    if not disaggregations:
        print('foo')
        quit()

    # "Melt" each disaggregation and concat them for a tidy format.
    melts = []
    for disaggregation in disaggregations:
        melts.append(pd.melt(df, id_vars=['year'], value_vars=disaggregations[disaggregation], var_name=disaggregation))
    # Also add the totals.
    total = pd.melt(df, id_vars=['year'], value_vars=['total'], var_name='total')
    del total['total']
    melts.append(total)
    tidy = pd.concat(melts)
    print(tidy.to_csv(index=False))

