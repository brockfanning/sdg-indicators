import csv
import pandas as pd

# Todos
# 1. Operate on all indicators.
# 2. Operate on subnational data according to file structure:
#    /data/subnational/state/alabama/indicator_1-1-1.csv
#    /data/subnational/state/alabama/city/montgomery/indicator_1-1-1.csv
#    etc
# 3. End up with several tidy CSV files:
#    - /data/tidy/indicator_1-1-1.csv (all data, national and subnational)
#    - /data/subnational/state/alabama/tidy/indicator_1-1-1.csv (all state and city data)
#    - /data/subnational/state/alabama/city/montgomery/tidy/indicator_1-1-1.csv (only city data)
# 4. Incorporate units into naming convention
#    - field:value:unit, eg:
#        - gender:total|per capita
#        - gender:total|average
#        - gender:male|per capita
#        - gender:male|average
#        - gender:female|per capita
#        - gender:female|average

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

