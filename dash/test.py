import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import dcc, html, Input, Output

# Sample Data
data = pd.DataFrame([
    {"Prop": "Item 1", "Motor": "A", "Status": "Active"},
    {"Prop": "Item 2", "Motor": "B", "Status": "Inactive"},
    {"Prop": "Item 3", "Motor": "A", "Status": "Inactive"},
    {"Prop": "Item 4", "Motor": "C", "Status": "Active"},
    {"Prop": "Item 5", "Motor": "B", "Status": "Active"},
    {"Prop": "Item 6", "Motor": "C", "Status": "Inactive"},
    {"Prop": "Item 7", "Motor": "A", "Status": "Active"},
])

# Initialize Dash App
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    html.H2("Filterable List"),
    
    # Multi-Select Dropdown for Category Filter
    dbc.Row([
        dbc.Col(dcc.Dropdown(
            id="category-filter",
            options=[{"label": cat, "value": cat} for cat in sorted(data["Category"].unique())],
            placeholder="Select Categories",
            multi=True,
            clearable=True
        ), width=6)
    ], className="mb-3"),
    
    # Checklist for Status Filter
    dbc.Row([
        dbc.Col(dcc.Checklist(
            id="status-filter",
            options=[{"label": status, "value": status} for status in data["Status"].unique()],
            value=[],
            inline=True
        ), width=6)
    ], className="mb-3"),

    # Table to Display Data
    dbc.Row([
        dbc.Col(dbc.Table(id="data-table", bordered=True, hover=True, responsive=True, striped=True), width=8)
    ])
])

# Callback to update table based on filters
@app.callback(
    Output("data-table", "children"),
    Input("category-filter", "value"),
    Input("status-filter", "value")
)
def update_table(selected_categories, selected_status):
    filtered_data = data.copy()
    
    if selected_categories:
        filtered_data = filtered_data[filtered_data["Category"].isin(selected_categories)]
    
    if selected_status:
        filtered_data = filtered_data[filtered_data["Status"].isin(selected_status)]

    # Generate Table
    table_header = [html.Thead(html.Tr([html.Th(col) for col in filtered_data.columns]))]
    table_body = [html.Tbody([html.Tr([html.Td(row[col]) for col in filtered_data.columns]) for _, row in filtered_data.iterrows()])]
    
    return table_header + table_body if not filtered_data.empty else [html.Thead(html.Tr([html.Th("No Results Found")]))]

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
