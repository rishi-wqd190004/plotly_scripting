import pandas as pd
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px

df = pd.read_excel('../datasets_all/nation.1751_2021.xlsx', engine='openpyxl')
nations = df['Nation'].unique()

#initialize app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG], suppress_callback_exceptions=True)
app.title = "Carbon Emission analysis"

# Layout
app.layout = dbc.Container([
    html.H1("Carbon Emission Analysis", className="text-center my-4"),

    dbc.Row([
        dbc.Col([
            html.Label("Select Country:"),
            dcc.Dropdown(
                id='country-dropdown',
                options=[{'label': nation, 'value': nation} for nation in sorted(nations)],
                value='UNITED STATES OF AMERICA',
            )
        ], width=6)
    ], className='mb-4'),

    dbc.Row([
        dbc.Col([
            html.Label("Select Year Range:"),
            dbc.ButtonGroup(
                [dbc.Button(f"{i}Y", id=f'btn-{i}', n_clicks=0, color="primary", outline=True) for i in range(10, 60, 10)],
                size="md",
                id="preset-buttons"
            )
        ], width=6),

        dbc.Col([
            html.Label("Custom Range:"),
            dcc.RangeSlider(
                id='year-slider',
                min=df["Year"].min(),
                max=df["Year"].max(),
                value=[df["Year"].min(), df["Year"].min() + 10],
                marks={str(year): str(year) for year in range(df["Year"].min(), df["Year"].max()+1, 10)},
                step=1,
                tooltip={"placement": "bottom", "always_visible": False}
            )
        ], width=6)
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='emission-graph')
        ])
    ])
], fluid=True)

@app.callback(
    Output('emission-graph', 'figure'),
    [Input(f'btn-{i}', 'n_clicks') for i in range(10, 60, 10)],
    State('country-dropdown', 'value')
)
def update_graph(n10, n20, n30, n40, n50, selected_cntry):
    ctx = dash.callback_context
    if not ctx.triggered:
        years=10
    else:
        btn_id = ctx.triggered[0]['prop_id'].split('.')[0]
        years = int(btn_id.split('-')[1])
    
    country_data = df[df['Nation'] == selected_cntry].sort_values('Year')
    latest_year = country_data['Year'].max()
    filtered_data = country_data[country_data['Year'] > latest_year - years]

    fig = px.line(
        filtered_data,
        x='Year',
        y='Total CO2 emissions from fossil-fuels and cement production (thousand metric tons of C)',
        title=f"{selected_cntry} - CO2 Emissions Over Last {years} Years",
        labels={'Year': 'Year', 'Total CO2 emissions from fossil-fuels and cement production (thousand metric tons of C)': 'Total CO2 Emissions'}
    )

    return fig


if __name__ == "__main__":
    app.run(debug=True)