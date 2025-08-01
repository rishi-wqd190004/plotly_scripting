import pandas as pd
import dash
from dash import dcc, html
import plotly.express as px
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

# Load your dataset
df = pd.read_csv("../dataset/europe_monthly_electricity.csv")

# Use Electricity demand (TWh) as proxy for generation
gen_df = df[(df['Category'] == 'Electricity demand') & (df['Unit'] == 'TWh')].copy()
gen_df['Year'] = pd.to_datetime(gen_df['Date']).dt.year

countries = sorted(gen_df['Area'].unique())
units = sorted(df['Unit'].unique())
years = sorted(gen_df['Year'].unique())

min_gen = gen_df['Value'].min()
max_gen = gen_df['Value'].max()

# External stylesheet for Bootstrap and icons
external_stylesheets = [dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# DBC Filter Card
filter_card = dbc.Card([
    dbc.CardHeader([
        html.H5([
            html.I(className="fas fa-cogs me-2"),
            "Control Panel"
        ], className="mb-0 text-primary")
    ]),
    dbc.CardBody([
        dbc.Row([
            dbc.Col([
                html.Label([
                    html.I(className="fas fa-flag me-2"),
                    "Countries to Compare"
                ], className="fw-bold mb-2"),
                dcc.Dropdown(
                    id='country_dd',
                    options=[{'label': f"{c}", 'value': c} for c in countries],
                    value=countries[0] if countries else None,
                    clearable=False,
                    className="mb-2"
                ),
                html.Small(f"Available: {len(countries)} countries", className="text-muted"),
            ], md=3),

            dbc.Col([
                html.Label([
                    html.I(className="fas fa-balance-scale me-2"),
                    "Unit of Measure"
                ], className="fw-bold mb-2"),
                dcc.Dropdown(
                    id='unit-selector',
                    options=[{'label': u, 'value': u} for u in units],
                    value='TWh' if 'TWh' in units else units[0],
                    clearable=False,
                    className="mb-2"
                ),
                html.Small(f"Units: {', '.join(units)}", className="text-muted"),
            ], md=2),

            dbc.Col([
                html.Label([
                    html.I(className="fas fa-calendar me-2"),
                    "Analysis Year"
                ], className="fw-bold mb-2"),
                dcc.Dropdown(
                    id='year-selector',
                    options=[{'label': str(y), 'value': y} for y in years],
                    value=years[-2] if len(years) > 1 else (years[-1] if years else None),
                    placeholder="Select year...",
                    className="mb-2"
                ),
                html.Small(f"Range: {min(years)}-{max(years)}", className="text-muted"),
            ], md=2),

            dbc.Col([
                html.Label([
                    html.I(className="fas fa-plug me-2"),
                    "Generation Range"
                ], className="fw-bold mb-2"),
                dcc.RangeSlider(
                    id='gen_slider',
                    min=min_gen,
                    max=max_gen,
                    step=0.1,
                    marks={int(min_gen): f'{int(min_gen)}', int(max_gen): f'{int(max_gen)}'},
                    value=[min_gen, max_gen],
                    tooltip={"placement": "bottom", "always_visible": False}
                ),
            ], md=5),
        ])
    ])
], className="mb-4 shadow-sm")

app.layout = dbc.Container([
    html.H1("Electricity Generation and Emissions by Country", className="mb-3"),
    filter_card,
    html.Div(id='top_country_info', className="mb-4"),
    dcc.Graph(id='generation_bar'),
    html.H3("Change in Electricity-related Emissions Over Time", className="mt-4"),
    dcc.Graph(id="emissions_time")
], fluid=True)

@app.callback(
    [Output('generation_bar', 'figure'),
     Output('emissions_time', 'figure'),
     Output('top_country_info', 'children')],
    [Input('country_dd', 'value'),
     Input('unit-selector', 'value'),
     Input('year-selector', 'value'),
     Input('gen_slider', 'value')]
)
def update_graph(selected_country, selected_unit, selected_year, gen_range):
    filtered_df = gen_df[
        (gen_df['Area'] == selected_country) &
        (gen_df['Unit'] == selected_unit) &
        (gen_df['Year'] == selected_year) &
        (gen_df['Value'] >= gen_range[0]) &
        (gen_df['Value'] <= gen_range[1])
    ]
    if not filtered_df.empty:
        top_value = filtered_df['Value'].max()
        top_info = html.H2(f"{selected_country}: {top_value} {selected_unit} in {selected_year}")
    else:
        top_info = html.H2("No data for selection.")

    # For the bar, also show a trend for this country (across years and unit)
    trend_df = gen_df[(gen_df['Area'] == selected_country) & (gen_df['Unit'] == selected_unit)]
    bar_fig = px.bar(trend_df, x="Year", y="Value", title=f"Generation Over Time - {selected_country}",
                     labels={"Value": f"Generation ({selected_unit})", "Year": "Year"})

    # Emissions chart (if emissions data available)
    emissions_df = df[
        ((df['Category'].str.contains('emission', case=False, na=False)) |
         (df['Variable'].str.contains('emission', case=False, na=False))) &
        (df['Area'] == selected_country)
    ].copy()
    if not emissions_df.empty:
        emissions_df['Year'] = pd.to_datetime(emissions_df['Date']).dt.year
        emissions_fig = px.line(
            emissions_df, x='Year', y='Value', color='Area',
            labels={"Value": "Emissions (as reported)", "Year": "Year", "Area": "Country"},
            title=f"Emissions for {selected_country} Over Time"
        )
    else:
        emissions_fig = {}

    return bar_fig, emissions_fig, top_info

if __name__ == "__main__":
    app.run(debug=True)
