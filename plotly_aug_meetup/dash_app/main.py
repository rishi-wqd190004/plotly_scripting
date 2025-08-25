import pandas as pd
import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objects as go

df = pd.read_csv('/Users/rishi/plotly_scripting/plotly_aug_meetup/laq-merged-30/laq-merged-30.csv', parse_dates=['MeasurementDateGMT'])

# some preprocessing and converting to long df
pollutants = ["CO", "NO2", "O3", "PM10", "PM25", "SO2"]

long_df = (
    df.melt(
        id_vars=[
            "SiteCode", "MeasurementDateGMT", "LocalAuthorityCode",
            "LocalAuthorityName", "SiteName", "SiteType", "DateClosed",
            "DateOpened", "Latitude", "Longitude", "DataOwner", "DataManager",
            "SiteLink", "SiteActive"
        ],
        value_vars=pollutants,
        var_name="species_code",
        value_name="value"
    )
    .dropna(subset=["value"])
)
long_df.rename(columns={"MeasurementDateGMT": "datetime", "SiteCode": "site_code"}, inplace=True)

# site info
sites_df = (
    long_df[['site_code', 'SiteName', 'SiteType', 'Latitude', 'Longitude', 'SiteActive']].drop_duplicates().reset_index(drop=True)
)

species_df = pd.DataFrame({
    "species_code": sorted(long_df['species_code'].unique())
})

# -------------------
# Dash app
# -------------------

app = dash.Dash(__name__)
app.title = "London Air Quality Explorer"

app.layout = html.Div([
    html.H1("London Air Quality Explorer", style={"textAlign": "center"}),

    dcc.Tabs([
        dcc.Tab(label="Sites Map", children=[
            html.Div([
                dcc.Dropdown(
                    id="site-type-filter",
                    options=[{"label": t, "value": t} for t in sites_df["SiteType"].unique()],
                    multi=True,
                    placeholder="Filter by site type"
                ),
                dcc.Graph(id="sites-map")
            ])
        ]),
        dcc.Tab(label="Time Series", children=[
            html.Div([
                dcc.Dropdown(
                    id="site-dropdown",
                    options=[{"label": f"{row.SiteName} ({row.site_code})", "value": row.site_code}
                             for row in sites_df.itertuples()],
                    multi=True,
                    placeholder="Select site(s)"
                ),
                dcc.Dropdown(
                    id="species-dropdown",
                    options=[{"label": s, "value": s} for s in species_df["species_code"]],
                    value="NO2",
                    clearable=False
                ),
                dcc.DatePickerRange(
                    id="date-range",
                    min_date_allowed=long_df["datetime"].min().date(),
                    max_date_allowed=long_df["datetime"].max().date(),
                    start_date=long_df["datetime"].min().date(),
                    end_date=long_df["datetime"].max().date()
                ),
                dcc.Graph(id="time-series")
            ])
        ]),
        dcc.Tab(label="Comparisons", children=[
            html.Div([
                dcc.Dropdown(
                    id="corr-site",
                    options=[{"label": f"{row.SiteName} ({row.site_code})", "value": row.site_code}
                             for row in sites_df.itertuples()],
                    value=sites_df.iloc[0]["site_code"],
                    clearable=False
                ),
                dcc.Graph(id="corr-heatmap"),
                dcc.Dropdown(
                    id="scatter-x",
                    options=[{"label": s, "value": s} for s in species_df["species_code"]],
                    value="NO2"
                ),
                dcc.Dropdown(
                    id="scatter-y",
                    options=[{"label": s, "value": s} for s in species_df["species_code"]],
                    value="O3"
                ),
                dcc.Graph(id="scatter-plot")
            ])
        ]),
        dcc.Tab(label="Data Table", children=[
            html.Div([
                dash_table.DataTable(
                    id="data-table",
                    columns=[{"name": col, "id": col} for col in long_df.columns],
                    page_size=10,
                    filter_action="native",
                    sort_action="native",
                )
            ])
        ])
    ])
])

# --------------------------------
# Callbacks
# --------------------------------
@app.callback(
    Output("sites-map", "figure"),
    Input("site-type-filter", "value")
)
def update_map(site_types):
    df = sites_df.copy()
    if site_types:
        df = df[df['SiteType'].isin(site_types)]
    fig = px.scatter_map(
        df,
        lat='Latitude', lon='Longitude',
        color = "SiteType",
        hover_name='SiteName',
        zoom=9, height=600
    )
    fig.update_layout(mapbox_style="open-street-map")
    return fig

@app.callback(
    Output("time-series", "figure"),
    [Input("site-dropdown", "value"),
     Input("species-dropdown", "value"),
     Input("date-range", "start_date"),
     Input("date-range", "end_date")]
)
def update_timeseries(site_codes, species, start_date, end_date):
    df = long_df.copy()
    if site_codes:
        df = df[df["site_code"].isin(site_codes)]
    if species:
        df = df[df["species_code"] == species]
    if start_date:
        df = df[df["datetime"] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df["datetime"] <= pd.to_datetime(end_date)]

    fig = px.line(df, x="datetime", y="value", color="site_code",
                  labels={"value": species, "datetime": "Date"})
    return fig


@app.callback(
    Output("corr-heatmap", "figure"),
    Input("corr-site", "value")
)
def update_heatmap(site_code):
    df = long_df[long_df["site_code"] == site_code]
    pivot = df.pivot(index="datetime", columns="species_code", values="value")
    corr = pivot.corr()
    fig = px.imshow(corr, text_auto=True, aspect="auto",
                    title=f"Correlation heatmap for {site_code}")
    return fig


@app.callback(
    Output("scatter-plot", "figure"),
    [Input("corr-site", "value"),
     Input("scatter-x", "value"),
     Input("scatter-y", "value")]
)
def update_scatter(site_code, x, y):
    df = long_df[long_df["site_code"] == site_code]
    pivot = df.pivot(index="datetime", columns="species_code", values="value")
    if x not in pivot.columns or y not in pivot.columns:
        return go.Figure()
    fig = px.scatter(pivot, x=x, y=y, trendline="ols",
                     title=f"{x} vs {y} at {site_code}")
    return fig


@app.callback(
    Output("data-table", "data"),
    Input("data-table", "page_current")
)
def update_table(page):
    return long_df.to_dict("records")

# ------------------------
# Run
# ------------------------
if __name__ == "__main__":
    app.run(debug=True)