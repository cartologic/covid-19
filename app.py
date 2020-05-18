import logging
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output
import time, os, re
from datetime import datetime
from pathlib import Path

from plots import plot_config, get_map_plot, get_total_timeseries, get_country_timeseries, get_bar_plot
from wrangle import wrangle_data


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
locks = {}

template = 'plotly_dark'
default_layout = {
    'autosize': True,
    'xaxis': {'title': None},
    'yaxis': {'title': None},
    'margin': {'l': 40, 'r': 20, 't': 40, 'b': 10},
    'paper_bgcolor': '#303030',
    'plot_bgcolor': '#303030',
    'hovermode': 'x',
}

external_stylesheets = [
    'https://codepen.io/mikesmith1611/pen/QOKgpG.css',
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.8.1/css/all.min.css',
]

app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
)

app.index_string = open('index.html', 'r').read()

# Fetch and read the dataset
url = 'http://datagovsa.mapapps.cloud/geoserver/ows?outputFormat=csv&service=WFS&srs=EPSG%3A3857&request=GetFeature&typename=geonode%3Acases&version=1.0.0'
covid_df = pd.read_csv(url)

# Dataset Preprocessing
covid_df = wrangle_data(covid_df)

# # Export the latest dataset and save it to the data folder
# Path("./data").mkdir(parents=True, exist_ok=True)
# covid_df.to_csv(r"./data/Saudi-cases-" + time.strftime("%Y-%m-%d") + ".csv", index=False)
#
# def days_between(date1, date2):
#     date1 = datetime.strptime(date1, "%Y-%m-%d")
#     date2 = datetime.strptime(date2, "%Y-%m-%d")
#     return abs((date2 - date1).days)
#
# # Remove the file if it's time-day delta > 10 days
# directory = os.fsencode("./data")
# for file in os.listdir(directory):
#     fileName = os.fsdecode(file)
#     if fileName.endswith(".csv"):
#         match = re.search(r'\d{4}-\d{2}-\d{2}', fileName)
#         if match:
#             file_date = datetime.strptime(match.group(), '%Y-%m-%d').date()
#             if days_between(str(file_date),time.strftime("%Y-%m-%d")) > 10:
#                 os.remove("./data/" + fileName)
#             else:
#                 pass
#         else:
#             continue

def get_graph(class_name, **kwargs):
    return html.Div(
        className=class_name + ' plotz-container',
        children=[
            dcc.Graph(**kwargs),
            html.I(className='fa fa-expand'),
        ],
    )


def dropdown_options(col):
    return [{'label': name, 'value': name} for name in col]


screen1 = html.Div(
    className='parent',
    children=[
        get_graph(
            class_name='div1',
            figure=get_map_plot(covid_df),
            id='map_graph',
            config=plot_config,
        ),
        get_graph(
            class_name='div2',
            figure=get_bar_plot(covid_df),
            id='bar_graph',
            config=plot_config,
            clear_on_unhover=True,
        ),
        get_graph(
            class_name='div3',
            figure=get_country_timeseries(covid_df),
            id='country_graph',
            config=plot_config,
        ),
        get_graph(
            class_name='div4',
            figure=get_total_timeseries(covid_df),
            id='total_graph',
            config=plot_config,
        ),
    ])

cities = covid_df['City_Name'].unique()
cities.sort()

# dcc.Dropdown(
# options=dropdown_options(countries),

control_panel = html.Div(
    className='header',
    children=[
        dcc.RadioItems(
            id='count_category',
            className='radio-group',
            options=dropdown_options(['Confirmed', 'Active', 'Recovered', 'Deaths']),
            value='Confirmed',
            labelStyle={'display': 'inline-block'}
        ),
        html.Span('|'),
        dcc.RadioItems(
            id='count_type',
            className='radio-group',
            options=[
                {'label': 'Actual', 'value': 'actual'}
            ],
            value='actual',
            labelStyle={'display': 'inline-block'}
        ),
        dcc.Input(
            id='country_input',
            type='text',
            debounce=True,
        ),
    ])


app.title = 'COVID-19 Dashboard | Saudi Arabia'

app.layout = html.Div(
    className='covid-container',
    children=[
        html.Div(
            className='header',
            children=[
                html.Div(
                    className='title',
                    children=[
                        html.H4('COVID-19 Dashboard | Saudi Arabia'),
                    ]
                ),
                html.Div(
                    className='header',
                    children=[
                        control_panel
                    ])
            ]),
        screen1
    ])


@app.callback(
    Output('country_input', 'value'),
    [
        Input('bar_graph', 'hoverData'),
    ])
def update_x_timeseries(hoverData):
    logger.debug(hoverData)
    return hoverData['points'][0]['y'] if hoverData else ''


@app.callback(
    Output('map_graph', 'figure'),
    [
        Input('count_type', 'value'),
        Input('count_category', 'value'),
    ])
def update_map_plot(count_type, count_category):
    count_col = count_category if count_type == 'actual' else count_category + 'PerCapita'
    return get_map_plot(covid_df, count_col)


@app.callback(
    Output('bar_graph', 'figure'),
    [
        Input('count_type', 'value'),
        Input('count_category', 'value'),
    ])
def update_bar_plot(count_type, count_category):
    count_col = count_category if count_type == 'actual' else count_category + 'PerCapita'
    return get_bar_plot(covid_df, count_col)


@app.callback(
    Output('country_graph', 'figure'),
    [
        Input('count_type', 'value'),
        Input('count_category', 'value'),
    ])
def update_bar_plot(count_type, count_category):
    count_col = count_category if count_type == 'actual' else count_category + 'PerCapita'
    return get_country_timeseries(covid_df, count_col)


@app.callback(
    Output('total_graph', 'figure'),
    [
        Input('country_input', 'value'),
        Input('count_type', 'value')
    ])
def update_x_timeseries(country, count_type):
    df = covid_df[covid_df['City_Name'] == country] \
        if country \
        else covid_df
    return get_total_timeseries(
        df,
        country=country,
        per_capita=count_type == 'per_capita')


if __name__ == '__main__':
    logger.info('app running')
    port = os.environ.get('PORT', 9000)
    debug = bool(os.environ.get('PYCHARM_HOSTED', os.environ.get('DEBUG', False)))
    app.run_server(debug=debug,
                   host='0.0.0.0',
                   port=port)
