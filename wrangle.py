import numpy as np


def wrangle_data(covid_df):
    # Change Date format to yyyy-mm-dd
    covid_df = covid_df.assign(Date=covid_df['Date'].astype(np.datetime64))

    # Sort data based on Date from oldest to newest
    covid_df.sort_values(by=['Date'], inplace = True)
    covid_df.reset_index(drop=True, inplace=True)

    covid_df['Longitude'] = covid_df['X']
    covid_df['Latitude'] = covid_df['Y']
    covid_df['City_Name'] = covid_df['City_Name']

    covid_df = covid_df.assign(
        logCumConf=np.where(
            covid_df['Confirmed'] > 0,
            np.log(covid_df['Confirmed']) /
            np.where(
                covid_df['Confirmed'] > 700,
                np.log(1.01),
                np.log(1.05)
            ),
            0
        )
    )

    covid_df['log10'] = np.where(covid_df['Confirmed'] > 0,
                                 np.ceil(np.log10(covid_df['Confirmed'])), 0)
    covid_df['log_group'] = np.power(10, covid_df['log10'] - 1).astype(np.int).astype(str) \
                            + '-' + np.power(10, covid_df['log10']).astype(np.int).astype(str)
    covid_df['Description'] = covid_df['City_Name'] + '<br>' \
                              + 'Confirmed: ' + covid_df['Confirmed'].astype(str) + '<br>' \
                              + 'Recovered: ' + covid_df['Recovered'].astype(str) + '<br>' \
                              + 'Active: ' + covid_df['Active'].astype(str) + '<br>' \
                              + 'Deaths: ' + covid_df['Deaths'].astype(str) + '<br>' \
                              + 'Confirmed Range: ' + covid_df['log_group'].astype(str) + '<br>'
    return covid_df
