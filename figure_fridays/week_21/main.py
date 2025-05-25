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
    html.H1(
        "🌍 Carbon Emission Analysis",
        className="text-center my-4",
        style={
            "color": "#00FFFF",
            "fontWeight": "bold",
            "fontSize": "2.5rem",
            "letterSpacing": "1px",
            "textShadow": "1px 1px 3px #000"
        }
    ),

    dbc.Row([
        # Country Dropdown
        dbc.Col([
            html.Label("Country"),
            dcc.Dropdown(
                id='country-dropdown',
                options=[{'label': nation, 'value': nation} for nation in sorted(nations)],
                value='UNITED STATES OF AMERICA',
                style={
                    'backgroundColor': '#2a2a2a',
                    'color': '#ffffff',
                    'border': '1px solid #555',
                }
            )
        ], xs=12, md=4, className="mb-2"),

        # Preset Buttons
        dbc.Col([
            html.Label("Year Range"),
            dbc.ButtonGroup(
                [dbc.Button(f"{i}Y", id=f'btn-{i}', n_clicks=0, color="info", outline=True) for i in range(10, 60, 10)],
                size="md",
                id="preset-buttons",
                className="d-flex flex-wrap"
            )
        ], xs=12, md=4, className="mb-2"),

        # From-To Inputs
        dbc.Col([
            html.Label("Custom Range (From - To)"),
            dbc.InputGroup([
                dbc.Input(
                    id="from-year",
                    type="number",
                    value=df["Year"].max() - 10,
                    max=df["Year"].max(),
                    style={
                        'backgroundColor': '#2a2a2a',
                        'color': 'white',
                        'border': '1px solid #555'
                    }
                ),
                dbc.Input(
                    id="to-year",
                    type="number",
                    value=df["Year"].max(),
                    min=df["Year"].min(),
                    max=df["Year"].max(),
                    style={
                        'backgroundColor': '#2a2a2a',
                        'color': 'white',
                        'border': '1px solid #555'
                    }
                ),
            ])
        ], xs=12, md=4, className="mb-2"),
    ], className="mb-4 g-2 align-items-end"),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='emission-graph')
        ])
    ])
], fluid=True)


@app.callback(
    [Output(f'btn-{i}', 'color') for i in range(10, 60, 10)] +
    [Output(f'btn-{i}', 'outline') for i in range(10, 60, 10)],
    [Input(f'btn-{i}', 'n_clicks') for i in range(10, 60, 10)],
    Input('from-year', 'value'),
)
def highlight_selected(*btn_clicks_and_from_year):
    btn_clicks = btn_clicks_and_from_year[:-1]
    from_year = btn_clicks_and_from_year[-1]

    ctx = dash.callback_context
    if ctx.triggered and ctx.triggered[0]['prop_id'].startswith('btn-'):
        clicked_id = ctx.triggered[0]["prop_id"].split('.')[0]
        selected_year = int(clicked_id.split('-')[1])
    else:
        # No button clicked recently, fallback to from_year
        if from_year is None:
            selected_year = 10  # default to 10Y
        else:
            # Calculate selected_year from from_year
            max_year = df["Year"].max()
            diff = max_year - from_year
            # Find closest preset button
            possible_years = list(range(10, 60, 10))
            selected_year = min(possible_years, key=lambda x: abs(x - diff))

    colors = []
    outlines = []
    for i in range(10, 60, 10):
        if i == selected_year:
            colors.append("info")
            outlines.append(False)  # Solid fill for selected
        else:
            colors.append("info")
            outlines.append(True)   # Outline for others

    return colors + outlines



@app.callback(
    Output('from-year', 'value'),
    [Input(f'btn-{i}', 'n_clicks') for i in range(10, 60, 10)],
    prevent_initial_call=True
)
def update_from_year(*btn_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update

    btn_id = ctx.triggered[0]["prop_id"].split(".")[0]
    years = int(btn_id.split("-")[1])
    return df["Year"].max() - years


@app.callback(
    Output('emission-graph', 'figure'),
    Input('from-year', 'value'),
    Input('to-year', 'value'),
    Input('country-dropdown', 'value')
)
def update_graph(from_year, to_year, selected_country):
    if not selected_country or not from_year or not to_year:
        return dash.no_update

    # Ensure correct order
    if from_year > to_year:
        from_year, to_year = to_year, from_year

    country_data = df[df['Nation'] == selected_country].sort_values('Year')
    filtered_data = country_data[
        (country_data['Year'] >= from_year) & 
        (country_data['Year'] <= to_year)
    ]

    fig = px.line(
        filtered_data,
        x='Year',
        y='Total CO2 emissions from fossil-fuels and cement production (thousand metric tons of C)',
        title=f"{selected_country} - CO₂ Emissions ({from_year} to {to_year})",
        labels={'Year': 'Year', 'Total CO2 emissions from fossil-fuels and cement production (thousand metric tons of C)': 'Total CO₂ Emissions'},
    )
    fig.update_layout(
        paper_bgcolor="#2a2a2a",
        plot_bgcolor="#2a2a2a",
        font=dict(color="white")
    )
    return fig



if __name__ == "__main__":
    app.run(debug=True)