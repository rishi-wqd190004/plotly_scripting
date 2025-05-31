from dash import html, hooks, set_props, Input, Output

def generate_error_notification():
    return [
        html.Div(
            [
                html.Div(
                    [
                        html.Span(
                            "Callback errors will display here.",
                            id="error-text",
                        ),
                        html.Button(
                            "×",
                            id="dismiss-button",
                            style={
                                "position": "absolute",
                                "top": "5px",
                                "right": "10px",
                            },
                        ),
                    ],
                    style={
                        "padding": "15px",
                        "border": "1px solid #f5c6cb",
                    },
                )
            ],
            id="callback-error-banner-wrapper",
        )
    ]

def add_error_notifications(error_text="there was an error"):
    @hooks.layout(priority=1)
    def update_layout(layout):
        return generate_error_notification() + (layout if isinstance(layout, list) else [layout])
    
    @hooks.callback(
        Output("callback-error-banner-wrapper", "style"),
        Input("dismiss-button", "n_clicks"),
        prevent_initial_call=True
    )
    def hide_banner(n_clicks):
        if n_clicks:
            return dict(display="none")
    
    @ hooks.error()
    def on_error(err):
        set_props("callback-error-banner-wrapper", dict(style=dict(display="block")))
        set_props("error-text", dict(children=f"{error_text}: {err}"))