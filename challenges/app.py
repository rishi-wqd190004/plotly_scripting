import dash
from dash import html, dcc
import plotly.graph_objects as go
import dash_theme_picker  # your plugin

# Create a dummy Plotly figure
dummy_fig = go.Figure(
    data=[go.Bar(x=["A", "B", "C"], y=[4, 7, 2])],
    layout={"title": "Dummy Data Bar Chart"}
)

# Compose the main layout
main_layout = html.Div([
    html.H1("Dash Theme Picker Demo"),
    dcc.Graph(id="main-dummy-graph", figure=dummy_fig),
])

# Pass the layout to the app, and register your plugin
app = dash.Dash(__name__, plugins=[dash_theme_picker],suppress_callback_exceptions=True)
app.layout = main_layout

if __name__ == "__main__":
    app.run(debug=True)
