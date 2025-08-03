import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

external_stylesheets = [dbc.themes.BOOTSTRAP]

df = pd.read_csv('../dataset/candy-data.csv')
num_cols = ['chocolate', 'fruity', 'caramel', 'peanutyalmondy', 'nougat', 
            'crispedricewafer', 'hard', 'bar', 'pluribus', 'sugarpercent']
corr = df[num_cols].corr()

fig_heatmap = px.imshow(
    corr, 
    text_auto=True, 
    color_continuous_scale='Oranges', 
    aspect='auto'
)
# fig_heatmap.update_layout(
#     plot_bgcolor='#81377D',
#     paper_bgcolor='#81377D'
# )
# fig_heatmap.update_traces(textfont_color='#FA7B05')

# Appeal score calculation
df['win_norm'] = (df['winpercent'] - df["winpercent"].min()) / (df['winpercent'].max() - df['winpercent'].min())
df['price_norm'] = (df['pricepercent'] - df['pricepercent'].min()) / (df['pricepercent'].max() - df['pricepercent'].min())

w_win = 0.6
w_choc = 0.15
w_peanut = 0.15
w_price = 0.1

df['appeal_score'] = (
    w_win * df['win_norm'] +
    w_choc * df['chocolate'] +
    w_peanut * df['peanutyalmondy'] -
    w_price * df['price_norm']
)

top_candies = df.sort_values(by='appeal_score', ascending=False)

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

def create_candy_card(rank, candy_row):
    score = f"{candy_row.appeal_score:.2f}"
    return dbc.Card(
        [
            dbc.CardHeader(
                f"#{rank} - {candy_row.competitorname}",
                style={"backgroundColor": "#54278f", "color": "#FA7B05", "fontWeight": "bold", "fontSize": "1.1em"}
            ),
            dbc.CardBody([
                html.P(f"Appeal Score: {score}", style={"color": "#F28F1C", "fontWeight": "bold"}),
                html.P(f"Win Percent: {candy_row.winpercent:.1f}%", className="mb-1"),
                html.P(f"Price Percentile: {candy_row.pricepercent:.2f}", className="mb-1"),
                html.P(f"Chocolate: {'Yes' if candy_row.chocolate == 1 else 'No'}", className="mb-1"),
                html.P(f"Peanut/Almond: {'Yes' if candy_row.peanutyalmondy == 1 else 'No'}", className="mb-1"),
            ], style={"backgroundColor": "#673AB7", "color": "white"})
        ],
        style={"marginBottom": "1rem", "boxShadow": "2px 2px 10px rgba(0,0,0,0.6)", "borderRadius": "1rem"}
    )


app.layout = html.Div(
    style={
        "backgroundColor": "#222222",
        "minHeight": "100vh",
        "padding": "2rem 1rem",
        "fontFamily": "cursive"
    },
    children=[
        html.H1(
            "🎃 Trick or Treat! Lets Check with DATA🍬",
            style={
                "textAlign": "center",
                "marginBottom": "2rem",
                "color": "#FA7B05",
                "textShadow": "2px 2px 8px #000"
            }
        ),
        # Top picks cards in a row (static)
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.Div("🥇", style={"fontSize": "2em", "textAlign": "center"}),
                    html.Div("KitKat", style={"color": "#F28F1C", "fontWeight": "bold", "fontSize": "1.2em", "textAlign": "center"}),
                    html.Small("Top 5 Pick (2017)", style={"color": "#FFF", "display": "block", "textAlign": "center"})
                ])
            ], style={"backgroundColor": "#81377D", "borderRadius": "1rem", "boxShadow": "2px 2px 10px rgba(0,0,0,0.6)"}), md=4),
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.Div("🥈", style={"fontSize": "2em", "textAlign": "center"}),
                    html.Div("Snickers", style={"color": "#F28F1C", "fontWeight": "bold", "fontSize": "1.2em", "textAlign": "center"}),
                    html.Small("Top 5 Pick (2017)", style={"color": "#FFF", "display": "block", "textAlign": "center"})
                ])
            ], style={"backgroundColor": "#81377D", "borderRadius": "1rem", "boxShadow": "2px 2px 10px rgba(0,0,0,0.6)"}), md=4),
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.Div("🥉", style={"fontSize": "2em", "textAlign": "center"}),
                    html.Div("Reese’s", style={"color": "#F28F1C", "fontWeight": "bold", "fontSize": "1.2em", "textAlign": "center"}),
                    html.Small("Top 5 Pick (2017)", style={"color": "#FFF", "display": "block", "textAlign": "center"})
                ])
            ], style={"backgroundColor": "#81377D", "borderRadius": "1rem", "boxShadow": "2px 2px 10px rgba(0,0,0,0.6)"}), md=4),
        ], className="g-4", justify="center", style={"marginBottom": "2rem"}),
        # Correlation heatmap card below
        dbc.Row(
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader(
                        html.H2(
                            "Candy Characteristics Correlation", 
                            style={"color": "#FA7B05", "textAlign": "center", "margin": "1rem 0"}
                        )
                    ),
                    dbc.CardBody(
                        dcc.Graph(figure=fig_heatmap)
                    ),
                ],
                style={"backgroundColor": "#81377D", "borderRadius": "1rem", "boxShadow": "3px 3px 12px rgba(0,0,0,0.7)"}
                ),
                md=8
            ),
            justify="center",
            className="my-3"
        ),
        # Toggle for top 5 / top 10 - cards instead of graph
        dbc.Row([
            dbc.Col([
                html.Div(
                    [
                        html.Label("Show Top N Candies:", style={"color": "#FA7B05", "fontWeight": "bold", "marginBottom": "0.5rem"}),
                        dcc.RadioItems(
                            id='top-n-toggle',
                            options=[
                                {'label': 'Top 5', 'value': 5},
                                {'label': 'Top 10', 'value': 10}
                            ],
                            value=5,
                            labelStyle={'display': 'inline-block', 'marginRight': '20px', 'color': '#FA7B05', 'fontWeight':'bold'}
                        )
                    ],
                    style={"textAlign": "center", "marginBottom": "1rem"}
                ),
                html.Div(id='top-candies-cards')
            ], md=8)
        ], justify="center"),
        html.Div(id='appeal-summary'),
        html.Div(
            "Happy Halloween! 🍭👻",
            style={
                "textAlign": "center",
                "color": "#FA7B05",
                "marginTop": "2rem",
                "fontSize": "1.3em"
            }
        ),
    ]
)

@app.callback(
    Output('top-candies-cards', 'children'),
    Output('appeal-summary', 'children'),
    Input('top-n-toggle', 'value')
)
def update_top_candies_cards(top_n):
    selected = top_candies.head(top_n)
    cards = []
    for i, row in enumerate(selected.itertuples(), 1):
        card = create_candy_card(i, row)
        cards.append(dbc.Col(card, md=6, style={"marginBottom": "1rem"}))
    # Arrange cards in rows of 2 columns
    rows = []
    for i in range(0, len(cards), 2):
        rows.append(dbc.Row(cards[i:i+2], className="g-4"))
    # Prepare a conclusion line for the top 3 candies
    top3 = top_candies.head(3)
    lines = []
    for i, row in enumerate(top3.itertuples(), 1):
        lines.append(f"#{i} {row.competitorname} (Appeal Score: {row.appeal_score:.2f})")
    conclusion_line = "Top 3 candies by appeal score are: " + ", ".join(lines) + "."

    conclusion_html = html.Div(
        conclusion_line,
        style={"color": "#FA7B05", "fontWeight": "bold", "textAlign": "center", "marginTop": "1rem", "fontSize": "1.2em"}
    )
    return rows, conclusion_html

if __name__ == "__main__":
    app.run(debug=True)
