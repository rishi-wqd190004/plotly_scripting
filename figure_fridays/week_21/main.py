import pandas as pd
import numpy as np
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

from helper import load_model, load_training_cols, parse_years_input, get_combined_df

# Load data
df = pd.read_excel('../datasets_all/nation.1751_2021.xlsx', engine='openpyxl')
nations = df['Nation'].unique()

model = load_model()
training_cols = load_training_cols()

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG], suppress_callback_exceptions=True)
app.title = "Carbon Emission Analysis"

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

        dbc.Col([
            html.Label("Year Range"),
            dbc.ButtonGroup(
                [dbc.Button(f"{i}Y", id=f'btn-{i}', n_clicks=0, color="info", outline=True) for i in range(10, 60, 10)],
                size="md",
                id="preset-buttons",
                className="d-flex flex-wrap"
            )
        ], xs=12, md=4, className="mb-2"),

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
    ]),

    dbc.Row([
        dbc.Col([
            html.Label("Select Emission Types"),
            dcc.Checklist(
                id='fuel-types',
                options=[
                    {'label': 'Solid', 'value': 'solid'},
                    {'label': 'Liquid', 'value': 'liquid'},
                    {'label': 'Gas', 'value': 'gas'},
                ],
                value=['solid', 'liquid', 'gas'],
                labelStyle={'display': 'inline-block', 'margin-right': '10px'},
                inputStyle={"margin-right": "5px"},
                style={'color': 'white'}
            )
        ])
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(dcc.Graph(id='solid-graph'), xs=12, md=4),
        dbc.Col(dcc.Graph(id='liquid-graph'), xs=12, md=4),
        dbc.Col(dcc.Graph(id='gas-graph'), xs=12, md=4)
    ], className="mb-4"),

    dbc.Row([
    dbc.Col([
        html.Label("Select Prediction Years (comma separated)"),
        dbc.InputGroup([
            dbc.Input(
                id='predict-years-input',
                type='text',
                value='2022,2023,2024',
                placeholder='Enter years separated by commas',
                style={
                    'backgroundColor': '#2a2a2a',
                    'color': 'white',
                    'border': '1px solid #555'
                }
            ),
            dbc.Button("Predict", id='predict-button', color='info', n_clicks=0)
        ]),
        html.Div(id='predict-years-error', style={'color': 'red', 'marginTop': '5px'})
        ])
    ], className="mb-4"),

    dbc.Row([
    dbc.Col([
        dcc.Loading(
            id="loading-combined-graph",
            type="circle",   # You can also use 'dot', 'cube', 'graph', etc.
            children=dcc.Graph(id='combined-graph')
        )
    ])
    ]),

], fluid=True)

# Highlight preset buttons
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
        if from_year is None:
            selected_year = 10
        else:
            max_year = df["Year"].max()
            diff = max_year - from_year
            selected_year = min(range(10, 60, 10), key=lambda x: abs(x - diff))

    colors, outlines = [], []
    for i in range(10, 60, 10):
        colors.append("info")
        outlines.append(i != selected_year)

    return colors + outlines

# Update from-year when preset buttons clicked
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

# Main graph
@app.callback(
    Output('emission-graph', 'figure'),
    Input('from-year', 'value'),
    Input('to-year', 'value'),
    Input('country-dropdown', 'value')
)
def update_main_graph(from_year, to_year, selected_country):
    if not selected_country or not from_year or not to_year:
        return dash.no_update

    if from_year > to_year:
        from_year, to_year = to_year, from_year

    country_data = df[df['Nation'] == selected_country]
    filtered = country_data[(country_data['Year'] >= from_year) & (country_data['Year'] <= to_year)]

    # calculate percentage change in CO2 emissions
    col = 'Total CO2 emissions from fossil-fuels and cement production (thousand metric tons of C)'
    filtered['pct_change'] = (filtered[col].pct_change() * 100).round(2)

    fig = px.line(
        filtered,
        x='Year',
        y='Total CO2 emissions from fossil-fuels and cement production (thousand metric tons of C)',
        custom_data=['pct_change'],
        title=f"{selected_country} - CO₂ Emissions ({from_year} to {to_year})",
        labels={'Year': 'Year', 'Total CO2 emissions from fossil-fuels and cement production (thousand metric tons of C)': 'Total CO₂ Emissions'},
    )

    fig.update_traces(
        hovertemplate=
        'Year: %{x}<br>' +
        'Emissions: %{y:,.0f}<br>' +
        'Change: %{customdata[0]:+.2f}%<extra></extra>'
    )

    max_val = filtered['Total CO2 emissions from fossil-fuels and cement production (thousand metric tons of C)'].max()
    fig.update_layout(
        yaxis=dict(range=[0, max_val * 1.1]),
        paper_bgcolor="#2a2a2a",
        plot_bgcolor="#2a2a2a",
        font=dict(color="white")
    )
    return fig

# Subgraphs with checklist
@app.callback(
    Output('solid-graph', 'figure'),
    Output('liquid-graph', 'figure'),
    Output('gas-graph', 'figure'),
    Input('from-year', 'value'),
    Input('to-year', 'value'),
    Input('country-dropdown', 'value'),
    Input('fuel-types', 'value')
)
def update_subgraphs(from_year, to_year, selected_country, selected_graphs):
    if not selected_country or not from_year or not to_year:
        return dash.no_update, dash.no_update, dash.no_update

    if from_year > to_year:
        from_year, to_year = to_year, from_year

    country_data = df[df['Nation'] == selected_country]
    filtered = country_data[(country_data['Year'] >= from_year) & (country_data['Year'] <= to_year)]

    def create_fig(column, title, show):
        if not show:
            return {
                "data": [],
                "layout": {
                    "xaxis": {"visible": False},
                    "yaxis": {"visible": False},
                    "paper_bgcolor": "#2a2a2a",
                    "plot_bgcolor": "#2a2a2a",
                    "annotations": [{
                        "text": "Hidden",
                        "xref": "paper",
                        "yref": "paper",
                        "showarrow": False,
                        "font": {"color": "gray", "size": 18},
                        "x": 0.5,
                        "y": 0.5,
                        "align": "center"
                    }]
                }
            }
        filtered['pct_change'] = (filtered[column].pct_change() * 100).round(2)
        fig = px.line(filtered, x='Year', y=column, custom_data=['pct_change'], title=title, labels={'Year': 'Year', column: title})
        fig.update_traces(
            hovertemplate=
            'Year: %{x}<br>' +
            'Emissions: %{y:,.0f}<br>' +
            'Change: %{customdata[0]:+.2f}%<extra></extra>'
        )

        max_val = filtered[column].max()
        fig.update_layout(
            yaxis=dict(range=[0, max_val * 1.1]),
            paper_bgcolor="#2a2a2a",
            plot_bgcolor="#2a2a2a",
            font=dict(color="white")
        )
        return fig

    solid_fig = create_fig("Emissions from solid fuel consumption", "Solid Fuel Emissions", 'solid' in selected_graphs)
    liquid_fig = create_fig("Emissions from liquid fuel consumption", "Liquid Fuel Emissions", 'liquid' in selected_graphs)
    gas_fig = create_fig("Emissions from gas fuel consumption", "Gas Fuel Emissions", 'gas' in selected_graphs)

    return solid_fig, liquid_fig, gas_fig

# Combined graph: actual + predicted
@app.callback(
    Output('combined-graph', 'figure'),
    Output('predict-years-error', 'children'),
    [
        Input('predict-button', 'n_clicks')
    ],
    [
        State('country-dropdown', 'value'),
        State('from-year', 'value'),
        State('to-year', 'value'),
        State('predict-years-input', 'value')
    ]
)
def update_combined_graph(n_clicks, selected_country, from_year, to_year, predict_years_str):
    # ctx = dash.callback_context
    # if not ctx.triggered or ctx.triggered[0]['prop_id'].split('.')[0] != 'predict-button':
    #     return dash.no_update, ""

    error_msg = ""
    if not selected_country or from_year is None or to_year is None or predict_years_str is None:
        return go.Figure(), error_msg
    
    combined_df = get_combined_df(df, model, training_cols)
    
    if from_year > to_year:
        from_year, to_year = to_year, from_year

    # Parse prediction years input
    try:
        predict_years_input = parse_years_input(predict_years_str)
    except Exception:
        error_msg = "Invalid input for prediction years. Use comma separated integers like 2022,2023,2024."
        predict_years_input = []

    # Filter actual data for country and year range
    actual = combined_df[
        (combined_df['Nation'] == selected_country) &
        (combined_df['Year'] >= from_year) &
        (combined_df['Year'] <= to_year) &
        (combined_df['Source'] == 'Actual')
    ].sort_values('Year')

    # Find which of the input prediction years actually exist in combined_df predicted data
    predicted_all = combined_df[
        (combined_df['Nation'] == selected_country) &
        (combined_df['Source'] == 'Predicted')
    ]
    predicted_years_present = predicted_all['Year'].unique()
    predicted_years = [y for y in predict_years_input if y in predicted_years_present]

    # Filter predicted data to only those years present
    predicted = predicted_all[predicted_all['Year'].isin(predicted_years)].sort_values('Year')

    # Determine x-axis max to be max of to_year and max of user input prediction years (even if missing)
    max_x = max(to_year, max(predict_years_input) if predict_years_input else to_year)

    if actual.empty and predicted.empty:
        return go.Figure(), error_msg

    # Calculate pct change for hover
    actual['pct_change'] = actual['CO2'].pct_change().fillna(0) * 100
    predicted['pct_change'] = predicted['CO2'].pct_change().fillna(0) * 100

    fig = go.Figure()

    # Actual data (blue line + markers)
    fig.add_trace(go.Scattergl(
        x=actual['Year'],
        y=actual['CO2'],
        mode='lines+markers',
        name='Actual',
        line=dict(color='blue', width=2),
        marker=dict(color='blue', size=8),
        fill='tozeroy',
        hovertemplate=(
            'Year: %{x}<br>'
            'Emissions: %{y:,.0f}<br>'
            'Change: %{customdata[0]:+.2f}%<extra></extra>'
        ),
        customdata=actual[['pct_change']].round(2)
    ))

    # Predicted line connecting last actual point to predicted points
    if not actual.empty and not predicted.empty:
        predicted_x = [actual['Year'].iloc[-1]] + predicted['Year'].tolist()
        predicted_y = [actual['CO2'].iloc[-1]] + predicted['CO2'].tolist()

        fig.add_trace(go.Scatter(
            x=predicted_x,
            y=predicted_y,
            mode='lines',
            name='Predicted Trend',
            line=dict(color='yellow', width=2, dash='dash'),
            fill='tozeroy',
            hoverinfo='skip'
        ))

    # Predicted points (yellow markers)
    if not predicted.empty:
        fig.add_trace(go.Scatter(
            x=predicted['Year'],
            y=predicted['CO2'],
            mode='markers',
            name='Predicted',
            marker=dict(color='yellow', size=10, symbol='circle-open'),
            hovertemplate=(
                'Year: %{x}<br>'
                'Emissions: %{y:,.0f}<br>'
                'Change: %{customdata[0]:+.2f}%<extra></extra>'
            ),
            customdata=predicted[['pct_change']].round(2)
        ))
    max_val = actual['CO2'].max()
    fig.update_layout(
        yaxis=dict(range=[0, max_val * 1.1]),
        yaxis_title='CO₂ Emissions (thousand metric tons of C)',
        paper_bgcolor="#2a2a2a",
        plot_bgcolor="#2a2a2a",
        font=dict(color="white"),
        legend=dict(title="Data Source"),
        xaxis=dict(range=[from_year, max_x])
    )

    return fig, error_msg


if __name__ == "__main__":
    app.run(debug=True)
