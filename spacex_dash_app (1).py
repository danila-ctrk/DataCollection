# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                             options=[{'label': 'All Sites', 'value': 'ALL'},
                                                      {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                                      {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                                      {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                                      {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}],
                                             value='ALL',
                                             placeholder="Select a Launch Site",
                                             searchable=True
                                             ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=min_payload,
                                                max=max_payload,
                                                step=1000,
                                                value=[min_payload, max_payload],
                                                marks={i: str(i) for i in range(int(min_payload), int(max_payload)+1, 1000)}
                                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output('success-pie-chart', 'figure'),
    [Input('site-dropdown', 'value')]
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        title = 'Success Launches Percentage for All Sites'
        success_counts = spacex_df[spacex_df['class'] == 1].groupby('Launch Site')['class'].count()
        total_counts = spacex_df.groupby('Launch Site')['class'].count()
    else:
        title = f'Success Launches Percentage for Site {selected_site}'
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        success_counts = filtered_df[filtered_df['class'] == 1]['class'].count()
        total_counts = filtered_df['class'].count()

    success_percentage = (success_counts / total_counts) * 100

    fig = px.pie(names=success_percentage.index, values=success_percentage.values, title=title)
    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, payload_range):
    if selected_site == 'ALL':
        filtered_df = spacex_df
        title = 'Correlation between Payload and Launch Success for All Sites'
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        title = f'Correlation between Payload and Launch Success for Site {selected_site}'

    if payload_range is not None:
        filtered_df = filtered_df[(filtered_df['Payload Mass (kg)'] >= payload_range[0]) &
                                  (filtered_df['Payload Mass (kg)'] <= payload_range[1])]

    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', title=title,
                     color='Booster Version Category', hover_data=['Launch Site'])
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
