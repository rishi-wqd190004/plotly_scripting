from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import plotly.express as px
import pandas as pd

from helpers import summary_metrics  # Import from your helpers.py

# Theme dictionary
THEMES = {
    "Dark": dbc.themes.CYBORG,
    "Light": dbc.themes.FLATLY
}

# Load and preprocess data
df = pd.read_csv("dataset/TLC_New_Driver_Application.csv") 
df['App Date'] = pd.to_datetime(df['App Date'])
df['Month'] = df['App Date'].dt.strftime("%B %Y")
df['Week'] = df['App Date'].dt.strftime("%U-%Y")
df['Week_label'] = 'Week' + df['App Date'].dt.strftime("%U, %Y")

# Dropdown options
month_options = [{'label': m, 'value': m} for m in df['Month'].unique()]

# Initialize app
app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])  # default to dark mode

# Layout
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
        html.Div(id='filtered-table')  # Table inserted dynamically
    ], fluid=True)
])

# Callback to update summary, chart, and table based on selected month
@app.callback(
    Output('summary-metrics', 'children'),
    Output('monthly-status-graph', 'figure'),
    Output('filtered-table', 'children'),
    Input('month-dropdown', 'value')
)
def update_dashboard(selected_month):
    # Filter data
    df_month = df[df['Month'] == selected_month]

    # Compute metrics
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

    # Create filtered bar chart
    filtered_counts = df_month.groupby(['Month', 'Status']).size().reset_index(name='Count')
    fig = px.bar(
        filtered_counts,
        x='Month',
        y='Count',
        color='Status',
        title=f'Status Counts for {selected_month}',
        labels={'Count': 'Number of Applications', 'Month': 'Month', 'Status': 'Application Status'},
        barmode='group'
    )

    # Filtered AgGrid table
    table = dag.AgGrid(
        rowData=df_month.to_dict("records"),
        columnDefs=[{"field": col, 'filter': True, 'sortable': True} for col in df_month.columns],
        dashGridOptions={"pagination": True},
        columnSize="sizeToFit"
    )

    return summary, fig, table

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
