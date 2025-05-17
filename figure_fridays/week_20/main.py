import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import plotly.express as px

df = pd.read_csv('../datasets_all/nation-dams.csv')

app = dash.Dash(__name__)
app.title = "US Dams Explorer"

app.layout = html.Div([
    html.H1("U.S. Dam Locations by State", style={'textAlign': 'center'}),

    dcc.Tabs(id='tabs', value='tab-map', children=[
        dcc.Tab(label='Dam Map', value='tab-map'),
        dcc.Tab(label='Dam Details', value='tab-detail', disabled=True)  # Initially disabled
    ]),

    # Dropdown and Dam Counter always shown
    html.Div([
        # Dropdown
        dcc.Dropdown(
            id='state-dropdown',
            options=[{'label': s, 'value': s} for s in sorted(df['State'].unique())],
            placeholder="Select a state",
            multi=False
        ),

        # Dam counter
        html.Div(id='dam-counter', style={
            'padding': '10px 20px',
            'fontSize': '20px',
            'fontWeight': 'bold',
            'color': '#333',
            'backgroundColor': '#f5f5f5',
            'border': '1px solid #ccc',
            'borderRadius': '10px',
            'marginTop': '10px'
        })
    ], style={'width': '30%', 'margin': '20px auto'}),

    # Graph always present, hidden/shown by tabs
    dcc.Graph(id='dam-map', style={'height': '90vh', 'width': '80%', 'margin': '0 auto'}),

    # Div for dam details info; visible only when tab-detail active
    html.Div(id='tab-detail-content', style={'padding': '20px', 'maxWidth': '800px', 'margin': '0 auto'})
])

# Update dam map and dam count based on state dropdown
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
        landcolor="rgb(240, 240, 240)",
        showocean=True,
        oceancolor="lightblue",
        showlakes=True,
        lakecolor="lightblue",
        showrivers=True,
        rivercolor="blue",
        showcountries=True,
        countrycolor="white",
        center=center,
        projection_scale=zoom
    )

    fig.update_layout(
        geo=dict(center=center, projection_scale=zoom, showland=True, landcolor="rgb(217, 217, 217)"),
        margin={"r": 0, "t": 40, "l": 0, "b": 0}
    )

    dam_count = len(filtered_df)
    dam_counter = f"Total dams: {dam_count}"
    return fig, dam_counter


# Enable the details tab and switch to it on dam click
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
                new_tabs.append(dcc.Tab(label='Dam Details', value='tab-detail', disabled=False))
            else:
                new_tabs.append(tab)
        return 'tab-detail', new_tabs
    return dash.no_update, dash.no_update


# Render dam details content only when details tab is active
@app.callback(
    Output('tab-detail-content', 'children'),
    Input('tabs', 'value'),
    Input('dam-map', 'clickData')
)
def render_dam_details(tab, click_data):
    if tab == 'tab-detail' and click_data:
        dam_name = click_data['points'][0].get('hovertext') or click_data['points'][0].get('text')
        dam_info = df[df['Dam Name'] == dam_name].iloc[0]

        return html.Div([
            html.H2(f"Details for {dam_info['Dam Name']}"),
            html.P(f"State: {dam_info['State']}"),
            html.P(f"Dam Height (Ft): {dam_info.get('Dam Height (Ft)', 'N/A')}"),
            html.P(f"Year Completed: {dam_info.get('Year Completed', 'N/A')}"),
            html.P(f"Latitude: {dam_info['Latitude']}"),
            html.P(f"Longitude: {dam_info['Longitude']}")
        ], style={
            'padding': '20px',
            'backgroundColor': '#f9f9f9',
            'borderRadius': '8px',
            'margin': '20px auto',
            'maxWidth': '600px'
        })
    return html.Div("Select a dam on the map to see details here.", style={'textAlign': 'center', 'marginTop': '20px'})

if __name__ == '__main__':
    app.run(debug=True)
