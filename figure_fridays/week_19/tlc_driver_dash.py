from dash import Dash, dcc
import dash_ag_grid as dag
import plotly.express as px
import pandas as pd

from helpers import summary_metrics

df = pd.read_csv("/Users/rishinigam/plotly_scripting/figure_fridays/week_19/dataset/TLC_New_Driver_Application.csv")
df['App Date'] = pd.to_datetime(df['App Date'])

# adding month and week
df['Month'] = df['App Date'].dt.strftime("%B %Y")
df["Week"] = df['App Date'].dt.strftime("%U-%Y")
df['Week_label'] = 'Week' + df['App Date'].dt.strftime("%U, %Y")

#group by monthly counts
monthly_counts = df.groupby(['Month', 'Status']).size().reset_index(name="Count")

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

app = Dash()
app.layout = [
    grid,
    dcc.Graph(figure=fig)
]

if __name__ == "__main__":
    app.run(debug=False)