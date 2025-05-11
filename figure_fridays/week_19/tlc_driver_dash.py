from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import plotly.express as px
import pandas as pd

from helpers import summary_metrics

THEMES = {
    "Dark": dbc.themes.CYBORG,
    "Light": dbc.themes.FLATLY
}

df = pd.read_csv("/Users/rishinigam/plotly_scripting/figure_fridays/week_19/dataset/TLC_New_Driver_Application.csv")
df['App Date'] = pd.to_datetime(df['App Date'])

# adding month and week
df['Month'] = df['App Date'].dt.strftime("%B %Y")
df["Week"] = df['App Date'].dt.strftime("%U-%Y")
df['Week_label'] = 'Week' + df['App Date'].dt.strftime("%U, %Y")

#group by monthly counts
monthly_counts = df.groupby(['Month', 'Status']).size().reset_index(name="Count")
month_options = [{'label':m , 'value': m} for m in df['Month'].unique()]

fig = px.bar(
    monthly_counts,
    x='Month',
    y='Count',
    color='Status',
    title='Status Counts by Month',
    labels={'Count': 'Number of Applications', 'Month': 'Month', 'Status': 'Application Status'},
    barmode='group'
)

grid = dag.AgGrid(
    rowData=df.to_dict("records"),
    columnDefs=[{"field": i, 'filter': True, 'sortable': True} for i in df.columns],
    dashGridOptions={"pagination": True},
    columnSize="sizeToFit"
)

app = Dash(external_stylesheets=[dbc.themes.CYBORG])
app.layout = html.Div([
    dcc.Store(id='theme-store', data='Dark'),
    dbc.Container([
        html.Br(),
        dbc.Row([
            dbc.Col(html.H1("TLC Applications Dashboard"), width=9),
            dbc.Col(
                dbc.RadioItems(
                    id='theme-toggle',
                    options=[{"label": k, "value": k} for k in THEMES.keys()],
                    value="Dark",
                    inline=True,
                    labelStyle={"margin-right": "15px"},
                    className="text-end"
                ),
                width=3
            )
        ]),

        html.Br(),

        dbc.Label("Select Month: ", className="text-light", id='month-label'),
        dcc.Dropdown(id='month-dropdown', options=month_options, value=month_options[0]['value']),

        html.Br(),
        html.Div(id='summary-metrics', className="mt-3"),

        dcc.Graph(id='monthly-status-graph', className="mt-4"),

        html.Hr(),

        html.H4("Applications Table", className="mt-3 text-info"),
        grid
    ], fluid=True)
])

# callbacks
@app.callback(
    Output('summary-metrics', 'children'),
    Output('monthly-status-graph', 'figure'),
    Input('month-dropdown', 'value')
)

def update_dashboard(selected_month):
    df_month = df[df['Month'] == selected_month]
    metrics = summary_metrics(df_month)
    summary = html.Div([
        html.H4(f"Summary for {selected_month}"),
        html.P(f"✅ Acceptance Rate: {metrics['acceptance_rate']}%"),
        html.P(f"❌ Rejection Rate: {metrics['rejection_rate']}%"),
        html.P(f"⏳ Pending Applications: {metrics['pending_applications']}"),
        html.P(f"🔄 Applications under review: {metrics['under_review']}"),
        html.P(f"❓ Incomplete Applications: {metrics['incomplete_applications']}"),
        html.P(f"📊 Total Applications: {metrics['total_applications']}"),
    ])

    return summary, fig

if __name__ == "__main__":
    app.run(debug=False)