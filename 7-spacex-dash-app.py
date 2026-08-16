# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
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
                                dcc.Dropdown(id='site-dropdown',options=[{'label': 'All Sites', 'value': 'ALL'},
                                {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},{'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}]
                                ,value='ALL',placeholder="Select a Launch Site here",
                                searchable=True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                # TASK 3: Add a slider to select payload range
                                html.P("Payload range (Kg):"),
                                dcc.RangeSlider(
                                id='payload-slider',
                                min=min_payload,
                                max=max_payload,
                                step=1000,
                                value=[min_payload, max_payload]),
                                html.Br(),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart'))
])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    
    if entered_site == 'ALL':
        # Isolating rows where class == 1 to show proportional success volume per site
        success_df = filtered_df[filtered_df['class'] == 1]
        fig = px.pie(
            success_df, 
            names='Launch Site', 
            title='Total Successful Launches Contribution by Site'
        )
        return fig
    else:
        # Isolating rows belonging to the single designated pad location
        site_specific_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        
        # Gathering individual binary outcome frequencies
        site_counts = site_specific_df['class'].value_counts().reset_index()
        site_counts.columns = ['class', 'Count']
        site_counts['class'] = site_counts['class'].map({1: 'Success', 0: 'Failure'})
        
        fig = px.pie(
            site_counts, 
            values='Count', 
            names='class', 
            title=f'Success vs. Failure Proportions for Site: {entered_site}',
            color='class',
            color_discrete_map={'Success': '#2ca02c', 'Failure': '#d62728'}
        )
        return fig
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure')
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def get_scatter_chart(entered_site, payload_range):
    # Slice rows that fall completely within the chosen range boundary limits
    low, high = payload_range
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    filtered_df = spacex_df[mask]
    if entered_site == 'ALL':
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='class',
            title='Correlation Between Payload and Success for All Sites',
            labels={'class': 'Launch Outcome (0=Fail, 1=Success)'}
        )
    return fig
    else:
        # Pinpoint rows matching selected launch coordinates
        site_specific_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(
            site_specific_df,
            x='Payload Mass (kg)',
            y='class',
            color='class',
            title=f'Correlation Between Payload and Success for Site: {entered_site}',
            labels={'class': 'Launch Outcome (0=Fail, 1=Success)'}
        )
    return fig

# Run the app
if __name__ == '__main__':
    app.run()
