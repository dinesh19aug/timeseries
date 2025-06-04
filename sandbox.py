import dash
from dash import html, dcc, Input, Output, State
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

        # Dashboard Section
        html.Div(
            id="dashboard-div",
            children=[
                html.H2("Welcome to your dashboard!", className="mt-4 text-center"),

                dbc.Row(
                    [
                        # Column 1 - Instant Payments
                        dbc.Col(
                            [
                                html.H4("Instant Payments"),
                                dbc.Label("Amount"),
                                dbc.Input(type="number", id="amount-input", placeholder="Enter amount"),
                                dbc.Button("Submit", id="submit-payment", color="success", className="mt-2"),
                                html.Div(id="payment-response", className="mt-3"),
                            ],
                            width=4,
                        ),

                        # Column 2 - Transactions
                        dbc.Col(
                            [
                                html.H4("Transaction"),
                                dbc.Label("Transaction JSON"),
                                dcc.Textarea(
                                    id="transaction-input",
                                    placeholder='{"name":"ddd"}',
                                    style={"width": "100%", "height": "150px"},
                                    value='{"name":"ddd"}'
                                ),
                                dbc.Button("Get Transaction", id="get-transaction", color="info", className="mt-2"),
                                html.Div(id="transaction-response", className="mt-3"),
                            ],
                            width=4,
                        ),

                        # Column 3 - Account Balance
                        dbc.Col(
                            [
                                html.H4("Account Balance"),
                                dbc.Button("Get Balance", id="get-balance", color="primary", className="mb-2"),
                                dcc.Textarea(
                                    id="balance-output",
                                    placeholder="Balance JSON will appear here...",
                                    style={"width": "100%", "height": "150px"},
                                    readOnly=True
                                ),
                            ],
                            width=4,
                        ),
                    ],
                    className="mt-4",
                )
            ],
            style={"display": "none"}
        ),
    ],
    fluid=True
)

# Callback to toggle login/dashboard
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
            {"display": "block"},
        )
    else:
        return (
            dbc.Alert("Invalid username or password.", color="danger"),
            {"maxWidth": "400px", "margin": "auto", "padding": "40px"},
            {"display": "none"},
        )

# Optional: Add dummy callbacks to simulate processing
@app.callback(
    Output("payment-response", "children"),
    Input("submit-payment", "n_clicks"),
    State("amount-input", "value"),
    prevent_initial_call=True
)
def handle_payment(n, amount):
    return dbc.Alert(f"Payment of ${amount} submitted!", color="success")

@app.callback(
    Output("transaction-response", "children"),
    Input("get-transaction", "n_clicks"),
    State("transaction-input", "value"),
    prevent_initial_call=True
)
def handle_transaction(n, json_text):
    return dbc.Alert(f"Transaction data received: {json_text}", color="info")

@app.callback(
    Output("balance-output", "value"),
    Input("get-balance", "n_clicks"),
    prevent_initial_call=True
)
def get_balance(n):
    return '{"balance": 1234.56, "currency": "USD"}'

if __name__ == "__main__":
    app.run_server(debug=True)