import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px

# Sample DataFrame — replace this with your real data
df = pd.read_csv('../datasets_all/nation-dams.csv')

# Dash app setup
app = dash.Dash(__name__)
app.title = "US Dams Explorer"
app.layout = html.Div([
    html.H1("U.S. Dam Locations by State", style={'textAlign': 'center'}),
    
    dcc.Tabs(id='tabs', value='tab-map', children=[
        dcc.Tab(label='Dam Map', value='tab-map'),
        dcc.Tab(label='Dam Details', value='tab-detail', disabled=True)  # Initially disabled
    ]),


    # Dropdown and Dam Counter in one row
    html.Div([
        # Dropdown to filter by state
        html.Div([
            dcc.Dropdown(
                id='state-dropdown',
                options=[{'label': state, 'value': state} for state in sorted(df['State'].unique())],
                placeholder="Select a state",
                multi=False
            )
        ], style={'width': '30%'}),

        # Dam Counter
        html.Div(id='dam-counter', style={
            'padding': '10px 20px',
            'fontSize': '20px',
            'fontWeight': 'bold',
            'color': '#333',
            'backgroundColor': '#f5f5f5',
            'border': '1px solid #ccc',
            'borderRadius': '10px',
            'marginLeft': 'auto'
        })
    ], style={
        'display': 'flex',
        'justifyContent': 'space-between',
        'alignItems': 'center',
        'padding': '0 5vw',
        'marginBottom': '20px'
    }),

    # Dam map
    dcc.Graph(id='dam-map', style={
        'height': '90vh',
        'width': '80%',
        'paddingLeft': '5vw',
        'paddingRight': '5vw'
    })
])

# ========== CALLBACK: Tab Content ==========
# Callback to update map based on dropdown
@app.callback(
    Output('dam-map', 'figure'),
    Output('dam-counter', 'children'),
    Input('state-dropdown', 'value')
)
def update_map(selected_state):
    filtered_df = df if selected_state is None else df[df['State'] == selected_state]

    # Default to entire US scope
    center = dict(lat=39.8283, lon=-98.5795)  # Approximate center of US
    zoom = 1

    # If a specific state is selected, center on it
    if selected_state and not filtered_df.empty:
        center = {
            'lat': filtered_df['Latitude'].mean(),
            'lon': filtered_df['Longitude'].mean()
        }
        zoom = 3  # You can fine-tune this zoom level

    # map
    fig = px.scatter_geo(
        filtered_df,
        lat='Latitude',
        lon='Longitude',
        # text='Dam Name',
        color='State',
        hover_name='Dam Name',
        scope='usa',
        title=f"Dams in {selected_state or 'the United States'}",
        color_discrete_sequence=px.colors.qualitative.Dark2
    )
    # Enhanced layout and visuals
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
        geo=dict(center=center,projection_scale=zoom, showland=True, landcolor="rgb(217, 217, 217)"),
        margin={"r":0, "t":40, "l":0, "b":0}
    )

    # create counter
    dam_count = len(filtered_df)
    dam_counter = f"Total dams: {dam_count}"
    return fig, dam_counter

if __name__ == '__main__':
    app.run(debug=True)
