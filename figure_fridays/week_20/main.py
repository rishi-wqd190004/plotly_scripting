import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash.dependencies import ALL
from helper import get_chatgpt_info

# Load data
df = pd.read_csv('../datasets_all/nation-dams.csv')
df['Dam Height (Ft)'] = pd.to_numeric(df['Dam Height (Ft)'], errors='coerce')

# Initialize app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], suppress_callback_exceptions=True)
app.title = "US Dams Explorer"

# Layout
app.layout = dbc.Container([
    html.H1("U.S. Dams by Locations", style={'textAlign': 'center', 'color': '#ffffff'}),
    dcc.Tabs(
        id='tabs',
        value='tab-map',
        children=[
            dcc.Tab(label='Dam Map', value='tab-map', style={'color': '#ffffff'}),
            dcc.Tab(label='Dam Details', value='tab-detail', disabled=True, style={'color': '#ffffff'}),
            dcc.Tab(label='Dam Filter', value='tab-filter', style={'color': '#ffffff'})
        ],
        colors={
            "border": "#444",
            "primary": "#00baff",
            "background": "#222"
        }
    ),
    dcc.Store(id='selected-dam-store'),

    # Keep all tab content in the DOM; toggle visibility with CSS
    html.Div([
        # Dam Map content
        html.Div(id='tab-map-content', children=[
            dcc.Dropdown(
                id='state-dropdown',
                options=[{'label': s, 'value': s} for s in sorted(df['State'].dropna().unique())],
                placeholder="Select a state",
                style={'backgroundColor': '#2c2c2c', 'color': '#fff', 'margin': '10px auto'}
            ),
            html.Div(id='dam-counter', style={
                'padding': '10px 20px',
                'fontSize': '20px',
                'fontWeight': 'bold',
                'color': '#fff',
                'backgroundColor': '#2c2c2c',
                'border': '1px solid #555',
                'borderRadius': '10px',
                'margin': '10px auto',
                'width': 'fit-content'
            }),
            dcc.Graph(id='dam-map', style={'height': '80vh'})
        ]),

        # Dam Details content
        html.Div(id='tab-detail-content', style={'padding': '20px', 'maxWidth': '800px', 'margin': '0 auto', 'display': 'none'}),

        # Dam Filter content
        html.Div(id='tab-filter-content', style={
            'padding': '20px',
            'maxWidth': '800px',
            'margin': '0 auto',
            'color': '#fff',
            'display': 'none'
        }),
    ]),

], fluid=True, style={'backgroundColor': '#121212', 'minHeight': '100vh', 'color': '#ffffff'})


# Callback: Show/Hide tab content divs
@app.callback(
    Output('tab-map-content', 'style'),
    Output('tab-detail-content', 'style'),
    Output('tab-filter-content', 'style'),
    Input('tabs', 'value')
)
def toggle_tab_content(tab):
    styles = {'display': 'none'}
    if tab == 'tab-map':
        return {'display': 'block'}, styles, styles
    elif tab == 'tab-detail':
        return styles, {'display': 'block'}, styles
    elif tab == 'tab-filter':
        return styles, styles, {'display': 'block'}
    return styles, styles, styles


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


# Callback: Show dam details
@app.callback(
    Output('tab-detail-content', 'children'),
    Input('tabs', 'value'),
    Input('dam-map', 'clickData'),
    Input('selected-dam-store', 'data')
)
def render_dam_details(tab, click_data, stored_dam_name):
    if tab != 'tab-detail':
        return html.Div("Select a dam on the map or from the list to see details here.",
                        style={'textAlign': 'center', 'marginTop': '20px', 'color': '#ffffff'})

    dam_name = None
    if click_data:
        dam_name = click_data['points'][0].get('hovertext') or click_data['points'][0].get('text')
    elif stored_dam_name:
        dam_name = stored_dam_name

    if not dam_name:
        return html.Div([
            html.P("No dam selected.", style={'textAlign': 'center', 'marginTop': '20px', 'color': '#ffffff'}),
            html.Br(),
            html.Button("Get Latest Info via ChatGPT", id='chatgpt-fetch-button', n_clicks=0,
                        style={'marginTop': '15px', 'backgroundColor': '#00baff', 'color': 'white', 'border': 'none', 'padding': '10px'}),
            html.Div(id='chatgpt-response', style={'marginTop': '20px', 'whiteSpace': 'pre-wrap'})
        ])

    selected = df[df['Dam Name'] == dam_name]
    if selected.empty:
        return html.Div("Dam not found.", style={'textAlign': 'center', 'marginTop': '20px'})

    dam = selected.iloc[0]

    fields_to_check = {
        'Dam Height (Ft)': 'Dam Height',
        'Hydraulic Height (Ft)': 'Hydraulic Height',
        'Structural Height (Ft)': 'Structural Height',
        'Year Completed': 'Year Completed',
        'Max Storage (Acre-Ft)': 'Storage Capacity',
        'Surface Area (Acres)': 'Surface Area',
        'Drainage Area (Sq Miles)': 'Drainage Area',
        'Hazard Potential Classification': 'Hazard Potential',
        'Condition Assessment': 'Condition',
        'State Regulated Dam': 'State Regulated',
        'Federally Regulated Dam': 'Federally Regulated',
        'Last Inspection Date': 'Last Inspection Date'
    }

    missing_fields = [readable for field, readable in fields_to_check.items()
                      if pd.isna(dam.get(field)) or dam.get(field) in [None, "", "N/A", "nan"]]

    dam_info = html.Div([
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

    # If missing fields, optionally include ChatGPT-enhanced info
    if missing_fields:
        chatgpt_response = get_chatgpt_info(dam['Dam Name'], dam['State'], missing_fields)
        return html.Div([dam_info,
                         html.H3("Supplemented Info via ChatGPT:", style={'color': '#00baff'}),
                         html.Pre(chatgpt_response, style={'whiteSpace': 'pre-wrap'})])

    # Otherwise, still return dam info + ChatGPT button
    return html.Div([
        dam_info,
        html.Br(),
        html.Button("Get Latest Info via ChatGPT", id='chatgpt-fetch-button', n_clicks=0,
                    style={'marginTop': '15px', 'backgroundColor': '#00baff', 'color': 'white', 'border': 'none', 'padding': '10px'}),
        html.Div(id='chatgpt-response', style={'marginTop': '20px', 'whiteSpace': 'pre-wrap'})
    ])



# Callback: Render Dam Filter tab content (slider + state dropdown + count)
@app.callback(
    Output('tab-filter-content', 'children'),
    Input('tabs', 'value')
)
def render_filter_tab(tab):
    if tab == 'tab-filter':
        min_height = int(df['Dam Height (Ft)'].min())
        max_height = int(df['Dam Height (Ft)'].max())

        return html.Div([
            html.H3("Filter Dams by Height (Ft) and State"),
            dcc.RangeSlider(
                id='height-slider',
                min=min_height,
                max=max_height,
                step=1,
                value=[min_height, max_height],
                marks={min_height: str(min_height), max_height: str(max_height)},
                tooltip={"placement": "bottom", "always_visible": True}
            ),
            dcc.Dropdown(
                id='filter-state-dropdown',
                options=[{'label': s, 'value': s} for s in sorted(df['State'].dropna().unique())],
                placeholder="Select a state (optional)",
                clearable=True,
                style={'backgroundColor': '#2c2c2c', 'color': '#fff', 'marginTop': '20px'}
            ),
            html.Div(id='filtered-dam-list', style={'marginTop': '20px', 'maxHeight': '400px', 'overflowY': 'auto'}),
            html.Div(id='filter-dam-count', style={'paddingTop': '10px', 'fontWeight': 'bold'})
        ])
    return None


# Callback: Filter dams by height and state for Dam Filter tab
@app.callback(
    Output('filtered-dam-list', 'children'),
    Output('filter-dam-count', 'children'),
    Input('height-slider', 'value'),
    Input('filter-state-dropdown', 'value')
)
def filter_dams_by_height_and_state(height_range, selected_state):
    min_h, max_h = height_range
    filtered = df[(df['Dam Height (Ft)'] >= min_h) & (df['Dam Height (Ft)'] <= max_h)]
    if height_range == [int(df['Dam Height (Ft)'].min()), int(df['Dam Height (Ft)'].max())] and not selected_state:
        return html.P("Use the slider or state dropdown to filter dams."), ""

    if selected_state:
        filtered = filtered[filtered['State'] == selected_state]

    if filtered.empty:
        return html.P("No dams found with selected criteria."), ""

    count_text = f"Total dams found: {len(filtered)}"
    return html.Ul([
        html.Li(html.Button(
            f"{row['Dam Name']} ({row['Dam Height (Ft)']} ft) - {row['State']}",
            id={'type': 'dam-button', 'index': row['Dam Name']},
            n_clicks=0,
            style={'background': 'none', 'border': 'none', 'color': '#00baff', 'textAlign': 'left', 'padding': '5px', 'cursor': 'pointer'}
        )) for _, row in filtered.iterrows()
    ]), count_text

@app.callback(
    Output('selected-dam-store', 'data'),
    Output('tabs', 'value'),
    Output('tabs', 'children'),
    Input('dam-map', 'clickData'),
    Input({'type': 'dam-button', 'index': ALL}, 'n_clicks'),
    State({'type': 'dam-button', 'index': ALL}, 'id'),
    State('tabs', 'children'),
    prevent_initial_call=True
)
def handle_dam_selection(map_click, button_clicks, button_ids, current_tabs):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update

    triggered_prop = ctx.triggered[0]['prop_id']
    dam_name = None

    if triggered_prop == 'dam-map.clickData':
        if map_click and map_click['points']:
            dam_name = map_click['points'][0].get('hovertext') or map_click['points'][0].get('text')
    else:
        for i, clicks in enumerate(button_clicks):
            if clicks:
                dam_name = button_ids[i]['index']
                break

    if not dam_name:
        return dash.no_update, dash.no_update, dash.no_update

    new_tabs = []
    for tab in current_tabs:
        if tab['props']['value'] == 'tab-detail':
            new_tabs.append(dcc.Tab(label='Dam Details', value='tab-detail', disabled=False, style={'color': '#ffffff'}))
        else:
            new_tabs.append(tab)

    return dam_name, 'tab-detail', new_tabs

@app.callback(
    Output('chatgpt-response', 'children'),
    Input('chatgpt-fetch-button', 'n_clicks'),
    State('selected-dam-store', 'data'),
    prevent_initial_call=True
)
def fetch_missing_info_from_chatgpt(n_clicks, dam_name):
    if not dam_name:
        return "No dam selected."

    selected = df[df['Dam Name'] == dam_name]
    if selected.empty:
        return "Dam not found in the dataset."

    dam = selected.iloc[0]

    fields_to_check = [
        'Congressional District', 'Distance to Nearest City (Miles)', 'Dam Height (Ft)',
        'Hydraulic Height (Ft)', 'Structural Height (Ft)', 'Year Completed',
        'Max Storage (Acre-Ft)', 'Surface Area (Acres)', 'Drainage Area (Sq Miles)',
        'Hazard Potential Classification', 'Condition Assessment', 'State Regulated Dam',
        'Federally Regulated Dam', 'Last Inspection Date'
    ]
    missing_fields = [field for field in fields_to_check if pd.isna(dam.get(field)) or dam.get(field) in [None, '', 'N/A', 'nan']]

    if not missing_fields:
        return "All data for this dam appears to be complete."

    # Call helper function
    response = get_chatgpt_info(dam_name, dam['State'], missing_fields)

    return response


if __name__ == '__main__':
    app.run(debug=True)
