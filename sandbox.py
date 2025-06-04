import dash
from dash import html, Input, Output, State
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout
app.layout = dbc.Container(
    [
        # Login Section
        html.Div(
            id="login-div",
            children=[
                html.H2("Login Form", className="mb-4"),

                dbc.Form(
                    children=[
                        dbc.Label("Username", html_for="username"),
                        dbc.Input(type="text", id="username", placeholder="Enter username"),

                        html.Br(),

                        dbc.Label("Password", html_for="password"),
                        dbc.Input(type="password", id="password", placeholder="Enter password"),

                        dbc.Button("Login", id="login-button", color="primary", className="mt-3"),
                        html.Div(id="login-message", className="mt-3")
                    ]
                )
            ],
            style={"maxWidth": "400px", "margin": "auto", "padding": "40px"}
        ),

        # Dashboard Section (initially hidden)
        html.Div(
            id="dashboard-div",
            children=[
                html.H2("Welcome to your dashboard!", className="mt-4"),
                html.P("You are now logged in."),
            ],
            style={"display": "none", "textAlign": "center", "marginTop": "100px"}
        ),
    ]
)

# Callback
@app.callback(
    Output("login-message", "children"),
    Output("login-div", "style"),
    Output("dashboard-div", "style"),
    Input("login-button", "n_clicks"),
    State("username", "value"),
    State("password", "value"),
    prevent_initial_call=True,
)
def login(n_clicks, username, password):
    if username == "admin" and password == "secret":
        return (
            dbc.Alert("Login successful!", color="success"),
            {"display": "none"},
            {"display": "block", "textAlign": "center", "marginTop": "100px"},
        )
    else:
        return (
            dbc.Alert("Invalid username or password.", color="danger"),
            {"maxWidth": "400px", "margin": "auto", "padding": "40px"},
            {"display": "none"},
        )

if __name__ == "__main__":
    app.run_server(debug=True)