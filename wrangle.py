import numpy as np
from shapely.wkt import loads
from pyproj import Proj, transform

def wrangle_data(covid_df):
    # Change Date format to yyyy-mm-dd
    covid_df = covid_df.assign(Date=covid_df['Date'].astype(np.datetime64))

    # Sort data based on Date from oldest to newest
    covid_df.sort_values(by=['Date'], inplace = True)
    covid_df.reset_index(drop=True, inplace=True)

    # Convert WKT to long lat
    long_points = []
    lat_points = []
    inProj = Proj('epsg:4326')
    outProj = Proj('epsg:4326')

    for value in covid_df['the_geom'].values:
        # PROJ honors the axis order of the CRS definition (which is lat, lon)
        longitude, latitude = transform(inProj, outProj, loads(value).x, loads(value).y)
        long_points.append(longitude)
        lat_points.append(latitude)
    covid_df = covid_df.assign(long=long_points)
    covid_df = covid_df.assign(lat=lat_points)
    covid_df = covid_df.drop(['the_geom'], axis=1)

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
                              + 'Tested: ' + covid_df['Tested'].astype(str) + '<br>' \
                              + 'Deaths: ' + covid_df['Deaths'].astype(str) + '<br>' \
                              + 'Confirmed Range: ' + covid_df['log_group'].astype(str) + '<br>'
    return covid_df
