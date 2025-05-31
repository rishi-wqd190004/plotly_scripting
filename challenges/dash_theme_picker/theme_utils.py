def get_theme(mode, custom_colors=None):
    if mode == "dark":
        return {
            "layout_style": {"backgroundColor": "#111111", "color": "#FFFFFF"},
            "plotly_template": "plotly_dark"
        }
    elif mode == "custom" and custom_colors:
        return {
            "layout_style": {
                "backgroundColor": custom_colors["bg"]["hex"],
                "color": custom_colors["text"]["hex"]
            },
            "plotly_template": "none"  # no preset
        }
    else:  # light or default
        return {
            "layout_style": {"backgroundColor": "#FFFFFF", "color": "#000000"},
            "plotly_template": "plotly_white"
        }
