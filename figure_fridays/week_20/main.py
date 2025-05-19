import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

# Load data
df = pd.read_csv('../datasets_all/nation-dams.csv')

# Initialize app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.title = "US Dams Explorer"

# Layout
app.layout = dbc.Container([
    html.Div([
        html.H1("U.S. Dam Locations by State", style={'textAlign': 'center', 'color': '#ffffff'}),

        # Tabs
        dcc.Tabs(
            id='tabs',
            value='tab-map',
            children=[
                dcc.Tab(label='Dam Map', value='tab-map', style={'color': '#ffffff'}),
                dcc.Tab(label='Dam Details', value='tab-detail', disabled=True, style={'color': '#ffffff'})
            ],
            colors={
                "border": "#444",
                "primary": "#00baff",
                "background": "#222"
            }
        ),

        # Dropdown and dam counter
        html.Div([
            dcc.Dropdown(
                id='state-dropdown',
                options=[{'label': s, 'value': s} for s in sorted(df['State'].dropna().unique())],
                placeholder="Select a state",
                multi=False,
                style={
                    'backgroundColor': '#2c2c2c',
                    'color': '#ffffff',
                    'border': '1px solid #555',
                    'borderRadius': '5px',
                    'padding': '8px'
                }
            ),
            html.Div(id='dam-counter', style={
                'padding': '10px 20px',
                'fontSize': '20px',
                'fontWeight': 'bold',
                'color': '#ffffff',
                'backgroundColor': '#2c2c2c',
                'border': '1px solid #555',
                'borderRadius': '10px',
                'marginTop': '10px'
            })
        ], style={'width': '30%', 'margin': '20px auto'}),

        # Map
        dcc.Graph(id='dam-map', style={'height': '90vh', 'width': '80%', 'margin': '0 auto'}),

        # Dam details tab
        html.Div(id='tab-detail-content', style={'padding': '20px', 'maxWidth': '800px', 'margin': '0 auto'})
    ])
], fluid=True, style={'backgroundColor': '#121212', 'minHeight': '100vh', 'color': '#ffffff'})


# Callback: Update map and dam count
@app.callback(
    Output('dam-map', 'figure'),
    Output('dam-counter', 'children'),
    Input('state-dropdown', 'value')
)
def update_map(selected_state):
    filtered_df = df if selected_state is None else df[df['State'] == selected_state]
    center = dict(lat=39.8283, lon=-98.5795)
    zoom = 1

    if selected_state and not filtered_df.empty:
        center = {
            'lat': filtered_df['Latitude'].mean(),
            'lon': filtered_df['Longitude'].mean()
        }
        zoom = 3

    fig = px.scatter_geo(
        filtered_df,
        lat='Latitude',
        lon='Longitude',
        color='State',
        hover_name='Dam Name',
        scope='usa',
        title=f"Dams in {selected_state or 'the United States'}",
        color_discrete_sequence=px.colors.qualitative.Dark2
    )
    fig.update_geos(
        scope="usa",
        projection_type="albers usa",
        showland=True,
        landcolor="#1a1a1a",
        showocean=True,
        oceancolor="#0e1a2b",
        showlakes=True,
        lakecolor="#1c2b3a",
        showrivers=True,
        rivercolor="#1e90ff",
        showcountries=True,
        countrycolor="white",
        center=center,
        projection_scale=zoom
    )
    fig.update_layout(
        template='plotly_dark',
        geo=dict(center=center, projection_scale=zoom),
        showlegend=False,
        margin={"r": 0, "t": 40, "l": 0, "b": 0}
    )

    return fig, f"Total dams: {len(filtered_df)}"


# Callback: Enable Dam Details tab and switch to it
@app.callback(
    Output('tabs', 'value'),
    Output('tabs', 'children'),
    Input('dam-map', 'clickData'),
    State('tabs', 'children'),
    prevent_initial_call=True
)
def open_details_tab(clickData, current_tabs):
    if clickData:
        new_tabs = []
        for tab in current_tabs:
            if tab['props']['value'] == 'tab-detail':
                new_tabs.append(dcc.Tab(label='Dam Details', value='tab-detail', disabled=False, style={'color': '#ffffff'}))
            else:
                new_tabs.append(dcc.Tab(label='Dam Map', value='tab-map', style={'color': '#ffffff'}))
        return 'tab-detail', new_tabs
    return dash.no_update, dash.no_update


# Callback: Show dam details
@app.callback(
    Output('tab-detail-content', 'children'),
    Input('tabs', 'value'),
    Input('dam-map', 'clickData')
)
def render_dam_details(tab, click_data):
    if tab == 'tab-detail' and click_data:
        dam_name = click_data['points'][0].get('hovertext') or click_data['points'][0].get('text')
        selected = df[df['Dam Name'] == dam_name]

        if selected.empty:
            return html.Div("Dam not found.", style={'textAlign': 'center', 'marginTop': '20px'})

        dam = selected.iloc[0]

        return html.Div([
            html.H2(f"Details for {dam['Dam Name']}", style={'color': '#00baff'}),
            html.P(f"State: {dam['State']}"),
            html.P(f"Congressional District: {dam.get('Congressional District', 'N/A')}"),
            html.P(f"Distance to Nearest City: {dam.get('Distance to Nearest City (Miles)', 'N/A')} miles"),
            html.P(f"Dam Height: {dam.get('Dam Height (Ft)', 'N/A')} ft"),
            html.P(f"Hydraulic Height: {dam.get('Hydraulic Height (Ft)', 'N/A')} ft"),
            html.P(f"Structural Height: {dam.get('Structural Height (Ft)', 'N/A')} ft"),
            html.P(f"Year Completed: {dam.get('Year Completed', 'N/A')}"),
            html.P(f"Storage Capacity (Max): {dam.get('Max Storage (Acre-Ft)', 'N/A')} acre-ft"),
            html.P(f"Surface Area: {dam.get('Surface Area (Acres)', 'N/A')} acres"),
            html.P(f"Drainage Area: {dam.get('Drainage Area (Sq Miles)', 'N/A')} sq mi"),
            html.P(f"Hazard Potential: {dam.get('Hazard Potential Classification', 'N/A')}"),
            html.P(f"Condition: {dam.get('Condition Assessment', 'N/A')}"),
            html.P(f"Regulated by State: {dam.get('State Regulated Dam', 'N/A')}"),
            html.P(f"Federally Regulated: {dam.get('Federally Regulated Dam', 'N/A')}"),
            html.P(f"Last Inspected: {dam.get('Last Inspection Date', 'N/A')}"),
            html.P("Website: "),
            html.A(dam.get('Website URL', 'N/A'), href=dam.get('Website URL'), target="_blank")
        ], style={
            'padding': '20px',
            'backgroundColor': '#1e1e1e',
            'borderRadius': '8px',
            'margin': '20px auto',
            'maxWidth': '600px',
            'boxShadow': '0 0 10px rgba(0, 0, 0, 0.5)',
            'color': '#ffffff'
        })

    return html.Div("Select a dam on the map to see details here.", style={'textAlign': 'center', 'marginTop': '20px', 'color': '#ffffff'})


if __name__ == '__main__':
    app.run(debug=True)
