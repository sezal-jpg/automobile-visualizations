# Final Assignment: Part 2 - Create Dashboard with Plotly and Dash
# Automobile Sales Statistics Dashboard
#
# This script completes Tasks 2.1 through 2.6:
# 2.1 Create a Dash application with a meaningful title
# 2.2 Add dropdown menus
# 2.3 Add an output division with id/className
# 2.4 Create the callback
# 2.5 Display Recession Report Statistics
# 2.6 Display Yearly Report Statistics

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# -------------------------------------------------------------------
# Load the historical automobile sales dataset used in the lab
# -------------------------------------------------------------------
DATA_URL = (
    "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
    "IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/"
    "Data%20Files/historical_automobile_sales.csv"
)

df = pd.read_csv(DATA_URL)

# Make sure Year is numeric.
df["Year"] = pd.to_numeric(df["Year"], errors="coerce")

# -------------------------------------------------------------------
# Task 2.1: Create Dash application with a meaningful title
# -------------------------------------------------------------------
app = Dash(__name__)
app.title = "Automobile Sales Statistics Dashboard"

# -------------------------------------------------------------------
# Task 2.2 and 2.3: Dashboard layout, dropdowns and output division
# -------------------------------------------------------------------
year_options = [
    {"label": str(int(year)), "value": int(year)}
    for year in sorted(df["Year"].dropna().unique())
]

default_year = year_options[-1]["value"]

app.layout = html.Div(
    [
        html.H1(
            "Automobile Sales Statistics Dashboard",
            style={"textAlign": "center", "color": "#503D36"},
        ),

        html.Div(
            [
                html.Label(
                    "Select Statistics:",
                    style={"fontWeight": "bold"},
                ),
                dcc.Dropdown(
                    id="statistics-dropdown",
                    options=[
                        {
                            "label": "Recession Period Statistics",
                            "value": "recession",
                        },
                        {
                            "label": "Yearly Statistics",
                            "value": "yearly",
                        },
                    ],
                    value="recession",
                    clearable=False,
                ),
            ],
            style={"width": "80%", "margin": "auto"},
        ),

        html.Br(),

        html.Div(
            [
                html.Label(
                    "Select Year:",
                    style={"fontWeight": "bold"},
                ),
                dcc.Dropdown(
                    id="year-dropdown",
                    options=year_options,
                    value=default_year,
                    clearable=False,
                ),
            ],
            id="year-dropdown-container",
            style={"width": "80%", "margin": "auto", "display": "none"},
        ),

        html.Br(),

        html.Div(
            id="output-container",
            className="output-container",
            style={"width": "95%", "margin": "auto"},
        ),
    ]
)

# -------------------------------------------------------------------
# Helper functions for the two dashboard reports
# -------------------------------------------------------------------
def recession_report():
    """Create all graphs required for the Recession Period Statistics."""

    recession_data = df[df["Recession"] == 1].copy()

    # Graph 1: Average automobile sales by year during recession
    yearly_sales = (
        recession_data.groupby("Year", as_index=False)["Automobile_Sales"]
        .mean()
        .sort_values("Year")
    )

    fig1 = px.line(
        yearly_sales,
        x="Year",
        y="Automobile_Sales",
        markers=True,
        title="Average Automobile Sales During Recession",
    )

    # Graph 2: Average automobile sales by vehicle type
    vehicle_sales = (
        recession_data.groupby("Vehicle_Type", as_index=False)["Automobile_Sales"]
        .mean()
        .sort_values("Automobile_Sales", ascending=False)
    )

    fig2 = px.bar(
        vehicle_sales,
        x="Vehicle_Type",
        y="Automobile_Sales",
        title="Average Automobile Sales by Vehicle Type During Recession",
    )

    # Graph 3: Advertising expenditure distribution by vehicle type
    advertising = (
        recession_data.groupby("Vehicle_Type", as_index=False)[
            "Advertising_Expenditure"
        ]
        .sum()
        .sort_values("Advertising_Expenditure", ascending=False)
    )

    fig3 = px.pie(
        advertising,
        values="Advertising_Expenditure",
        names="Vehicle_Type",
        title="Advertising Expenditure by Vehicle Type During Recession",
    )

    # Graph 4: Unemployment rate and automobile sales by vehicle type
    unemployment = (
        recession_data.groupby(
            ["unemployment_rate", "Vehicle_Type"], as_index=False
        )["Automobile_Sales"]
        .mean()
        .sort_values("unemployment_rate")
    )

    fig4 = px.line(
        unemployment,
        x="unemployment_rate",
        y="Automobile_Sales",
        color="Vehicle_Type",
        markers=True,
        title="Unemployment Rate vs Automobile Sales During Recession",
    )

    return html.Div(
        [
            dcc.Graph(figure=fig1),
            dcc.Graph(figure=fig2),
            dcc.Graph(figure=fig3),
            dcc.Graph(figure=fig4),
        ]
    )


def yearly_report(selected_year):
    """Create all graphs required for the Yearly Statistics report."""

    yearly_data = df[df["Year"] == selected_year].copy()

    # Graph 1: Monthly automobile sales for selected year
    monthly_sales = (
        yearly_data.groupby("Month", as_index=False)["Automobile_Sales"]
        .mean()
    )

    # Preserve calendar order when Month is represented by month names.
    month_order = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    ]

    if monthly_sales["Month"].dtype == "object":
        monthly_sales["Month"] = pd.Categorical(
            monthly_sales["Month"],
            categories=month_order,
            ordered=True,
        )
        monthly_sales = monthly_sales.sort_values("Month")

    fig1 = px.line(
        monthly_sales,
        x="Month",
        y="Automobile_Sales",
        markers=True,
        title=f"Monthly Automobile Sales - {selected_year}",
    )

    # Graph 2: Average automobile sales by vehicle type
    vehicle_sales = (
        yearly_data.groupby("Vehicle_Type", as_index=False)["Automobile_Sales"]
        .mean()
        .sort_values("Automobile_Sales", ascending=False)
    )

    fig2 = px.bar(
        vehicle_sales,
        x="Vehicle_Type",
        y="Automobile_Sales",
        title=f"Average Automobile Sales by Vehicle Type - {selected_year}",
    )

    # Graph 3: Advertising expenditure by vehicle type
    advertising = (
        yearly_data.groupby("Vehicle_Type", as_index=False)[
            "Advertising_Expenditure"
        ]
        .sum()
        .sort_values("Advertising_Expenditure", ascending=False)
    )

    fig3 = px.pie(
        advertising,
        values="Advertising_Expenditure",
        names="Vehicle_Type",
        title=f"Advertising Expenditure by Vehicle Type - {selected_year}",
    )

    # Graph 4: Average GDP by month
    gdp_monthly = yearly_data.groupby("Month", as_index=False)["GDP"].mean()

    if gdp_monthly["Month"].dtype == "object":
        gdp_monthly["Month"] = pd.Categorical(
            gdp_monthly["Month"],
            categories=month_order,
            ordered=True,
        )
        gdp_monthly = gdp_monthly.sort_values("Month")

    fig4 = px.line(
        gdp_monthly,
        x="Month",
        y="GDP",
        markers=True,
        title=f"Average GDP by Month - {selected_year}",
    )

    return html.Div(
        [
            dcc.Graph(figure=fig1),
            dcc.Graph(figure=fig2),
            dcc.Graph(figure=fig3),
            dcc.Graph(figure=fig4),
        ]
    )


# -------------------------------------------------------------------
# Task 2.4: Callback function
# -------------------------------------------------------------------
@app.callback(
    Output("year-dropdown-container", "style"),
    Output("output-container", "children"),
    Input("statistics-dropdown", "value"),
    Input("year-dropdown", "value"),
)
def update_dashboard(selected_statistics, selected_year):

    if selected_statistics == "recession":
        # Disable/hide the year selector for recession statistics.
        return (
            {"width": "80%", "margin": "auto", "display": "none"},
            recession_report(),
        )

    if selected_statistics == "yearly":
        # Enable/show the year selector for yearly statistics.
        return (
            {"width": "80%", "margin": "auto", "display": "block"},
            yearly_report(selected_year),
        )

    return (
        {"width": "80%", "margin": "auto", "display": "none"},
        html.Div("Please select a report."),
    )


# -------------------------------------------------------------------
# Run the Dash application
# -------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
