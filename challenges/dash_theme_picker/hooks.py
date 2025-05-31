from dash import html, dcc, hooks, Input, Output
import plotly.graph_objects as go
import dash_daq as daq
from .theme_utils import get_theme

@hooks.layout()
def layout(existing_layout):
    return html.Div([
        dcc.RadioItems(
            id="theme-mode",
            options=[
                {"label": "Light", "value": "light"},
                {"label": "Dark", "value": "dark"},
                {"label": "Custom", "value": "custom"}
            ],
            value="light",
            style={"marginBottom": "1rem"}
        ),
        html.Div(id="custom-color-inputs", children=[
            daq.ColorPicker(id="bg-color", value={"hex": "#ffffff"}, disabled=True),
            daq.ColorPicker(id="text-color", value={"hex": "#000000"}, disabled=True),
        ], style={"display": "none", "gap": "1rem", "marginBottom": "1rem"}),
        dcc.Graph(id="theme-graph")
    ], id="app-container")


@hooks.callback(
    Output("app-container", "style"),
    Output("theme-graph", "figure"),
    Output("bg-color", "disabled"),
    Output("text-color", "disabled"),
    Input("theme-mode", "value"),
    Input("bg-color", "value"),
    Input("text-color", "value"),
)
def update_theme(mode, bg, text):
    # Prepare custom colors dict only if mode is custom
    custom_colors = {"bg": bg, "text": text} if mode == "custom" else None
    
    # Get theme dict from theme_utils
    theme = get_theme(mode, custom_colors)

    # Create plotly figure with theme's plotly template
    fig = go.Figure(go.Scatter(x=[1,2,3], y=[3,1,2]))
    fig.update_layout(template=theme["plotly_template"])

    # Explicitly set graph background and font colors to match the theme
    bg_color = theme["layout_style"].get("backgroundColor", "#FFFFFF")
    text_color = theme["layout_style"].get("color", "#000000")

    fig.update_layout(
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        font=dict(color=text_color)
    )
    # Enable color pickers only in custom mode
    bg_disabled = mode != "custom"
    text_disabled = mode != "custom"

    return theme["layout_style"], fig, bg_disabled, text_disabled


@hooks.callback(
    Output("custom-color-inputs", "style"),
    Input("theme-mode", "value")
)
def toggle_custom_color_inputs(mode):
    if mode == "custom":
        return {"display": "flex", "gap": "1rem", "marginTop": "1rem", "marginBottom": "1rem"}
    return {"display": "none"}
