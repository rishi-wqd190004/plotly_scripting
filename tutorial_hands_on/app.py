from dash import dcc, html, callback, Input, Output, Dash
from callback_error_plugin import add_error_notifications

add_error_notifications("here is the error message")

app = Dash()
app.layout = html.Div([
    dcc.Input(id='input-number', type='number', value=1),
    html.Div(id='output-div')
])

@callback(
    Output('output-div', 'children'),
    Input('input-number', 'value')
)
def update_output(value):
    result = 10 / value
    return f'The result is {result}'

if __name__ == "__main__":
    app.run(debug=True)