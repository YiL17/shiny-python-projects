import plotly.express as px
from shiny.express import input, ui, render
from shiny import reactive
from shinywidgets import render_plotly, render_altair, render_widget

import pandas as pd
import numpy as np
from pathlib import Path
import calendar
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt

import folium
from folium.plugins import HeatMap


ui.page_opts(window_title="Sales Dashboard", fillable=False)
# ui.input_checkbox("bar_color", "Make Bars Red?", False)

# @reactive.calc
# def color():
#     return "red" if input.bar_color() else "blue"


@reactive.calc
# value will get cached and propagate any changes later on
def dat():
    infile = Path(__file__).parent / "data/sales.csv"
    df = pd.read_csv(infile)
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["month"] = df["order_date"].dt.month_name()
    df["hour"] = df["order_date"].dt.hour
    df["value"] = df["quantity_ordered"] * df["price_each"]
    return df


with ui.div(class_="header-container"):
    with ui.div(class_="logo-container"):

        @render.image
        def image():
            here = Path(__file__).parent
            img = {"src": here / "images/shiny-logo.png", "width": "40px"}
            return img

    with ui.div(class_="title-container"):
        ui.h2("Sales Dashboard")


ui.tags.style(
    """
.header-container {
    display: flex;
    align-items: center;
    height: 60px;
    justify-content: center;
}
.logo-container {
    margin-right: 20px;
              margin-top:10px;
    height: 100%;
              
}
.title-container h2 {
    color: white;
    padding: 5px;
    margin: 0;
}
              
              body{
              background-color: #5DADE2;
              }
              .modebar{
              display: none;}
"""
)

FONT_COLOR = "#4C78A8"
FONT_TYPE = "Arial"


def style_plotly_chart(fig, yaxis_title):
    fig.update_layout(
        xaxis_title="",
        yaxis_title=yaxis_title,
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        coloraxis_showscale=False,
        font=dict(family=FONT_TYPE, size=12, color=FONT_COLOR),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)

    return fig


with ui.card():
    ui.card_header("Sales by City 2023")

    with ui.layout_sidebar():
        with ui.sidebar(bg="#f8f8f8", open="open"):
            ui.input_selectize(
                "city",
                "Select a City:",
                [
                    "Dallas (TX)",
                    "Boston (MA)",
                    "Los Angeles (CA)",
                    "San Francisco (CA)",
                    "Seattle (WA)",
                    "Atlanta (GA)",
                    "New York City (NY)",
                    "Portland (OR)",
                    "Austin (TX)",
                    "Portland (ME)",
                ],
                multiple=False,
                selected="Boston (MA)",
            )

        @render_altair
        def sales_over_time():
            df = dat()
            sales = (
                df.groupby(["city", "month"])["quantity_ordered"].sum().reset_index()
            )
            sales_by_city = sales[sales["city"] == input.city()]
            month_orders = list(calendar.month_name[1:])
            # sales_by_city["month"] = pd.Categorical(sales_by_city["month"], categories=month_orders, ordered=True)

            font_props = alt.Axis(
                labelFont=FONT_TYPE,
                labelColor=FONT_COLOR,
                titleFont=FONT_TYPE,
                titleColor=FONT_COLOR,
                tickSize=0,
                labelAngle=0,
            )

            fig = (
                alt.Chart(sales_by_city)
                .mark_bar(color="#3485BF")
                .encode(
                    x=alt.X("month", sort=month_orders, title="Month", axis=font_props),
                    y=alt.Y(
                        "quantity_ordered", title="Quantity Ordered", axis=font_props
                    ),
                    tooltip=["month", "quantity_ordered"],
                )
                .properties(title=f"Sales over Time -- {input.city()}")
                .configure_axis(grid=False)
                .configure_title(font=FONT_TYPE, color=FONT_COLOR)
            )
            return fig


# with ui.layout_columns(col_widths=(6,6)): # based on 12 column grid
with ui.layout_column_wrap(width=1 / 2):
    with ui.navset_card_underline(
        id="tab", footer=ui.input_numeric("n", "Number of Items", 5, min=0, max=20)
    ):
        with ui.nav_panel("Top Sellers"):

            @render_plotly
            def plot_top_sellers():
                df = dat()
                top_sales = (
                    df.groupby("product")["quantity_ordered"]
                    .sum()
                    .nlargest(input.n())
                    .reset_index()
                )
                fig = px.bar(
                    top_sales,
                    x="product",
                    y="quantity_ordered",
                    color="quantity_ordered",
                    color_continuous_scale="Blues",
                )
                fig = style_plotly_chart(fig, "Quantity Ordered")
                # fig.update_traces(marker_color = color())
                return fig

        with ui.nav_panel("Top Sellers Value"):

            @render_plotly
            def plot_top_sellers_value():
                df = dat()

                top_sales = (
                    df.groupby("product")["value"]
                    .sum()
                    .nlargest(input.n())
                    .reset_index()
                )
                fig = px.bar(
                    top_sales,
                    x="product",
                    y="value",
                    color="value",
                    color_continuous_scale="Blues",
                )
                fig = style_plotly_chart(fig, "Total Sales ($)")
                # fig.update_traces(marker_color = color())
                return fig

        with ui.nav_panel("Lowest Sellers"):

            @render_plotly
            def plot_lowest_sellers():
                df = dat()
                top_sales = (
                    df.groupby("product")["quantity_ordered"]
                    .sum()
                    .nsmallest(input.n())
                    .reset_index()
                )
                fig = px.bar(
                    top_sales,
                    x="product",
                    y="quantity_ordered",
                    color="quantity_ordered",
                    color_continuous_scale="Reds",
                )
                fig = style_plotly_chart(fig, "Quartity Ordered")
                # fig.update_traces(marker_color = color())
                return fig

        with ui.nav_panel("Lowest Sellers Value"):

            @render_plotly
            def plot_smallest_sellers_value():
                df = dat()
                top_sales = (
                    df.groupby("product")["value"]
                    .sum()
                    .nsmallest(input.n())
                    .reset_index()
                )
                fig = px.bar(
                    top_sales,
                    x="product",
                    y="value",
                    color="value",
                    color_continuous_scale="Reds",
                )
                fig = style_plotly_chart(fig, "Total Sales ($)")
                # fig.update_traces(marker_color = color())
                return fig

    with ui.card():
        ui.card_header("Sales by Time of Day Heatmap")

        @render.plot
        def plot_sales_by_time():
            df = dat()
            sales_by_hour = (
                df["hour"].value_counts().reindex(np.arange(0, 24), fill_value=0)
            )

            heatmap_data = sales_by_hour.values.reshape(24, 1)
            sns.heatmap(
                heatmap_data,
                annot=True,
                fmt="d",
                cmap="Blues",
                cbar=False,
                xticklabels=[],
                yticklabels=[f"{i}:00" for i in range(24)],
            )
            # plt.title("Number of Orders by Hour of Day")
            plt.xlabel("Order Count", color=FONT_COLOR, fontname=FONT_TYPE)
            plt.ylabel("Hour of Day", color=FONT_COLOR, fontname=FONT_TYPE)

            plt.yticks(color=FONT_COLOR, fontname=FONT_TYPE)
            plt.xticks(color=FONT_COLOR, fontname=FONT_TYPE)

            # sales_by_hour = df['hour'].value_counts().reset_index()

            # # using matplotlib
            # plt.bar(x=sales_by_hour['hour'], height=sales_by_hour['count'])
            # plt.xticks(np.arange(0,24))

            # # using pandas plot
            # sales_by_hour.plot(x='hour', y='count', kind = 'bar')


with ui.card():
    ui.card_header("Sales by Location Map")

    @render.ui
    def plot_us_heatmap():
        df = dat()
        heatmap_data = df[["lat", "long", "quantity_ordered"]].values
        map = folium.Map(location=[37.0902, -95.7129], zoom_start=4)
        blue_gradient = {
            "0.0": "#E3F2FD",
            "0.2": "#BBDEFB",
            "0.4": "#64B5F6",
            "0.6": "#42A5F5",
            "0.8": "#2196F3",
            "1.0": "#1976D2",
        }
        HeatMap(heatmap_data, gradient=blue_gradient).add_to(map)
        return map


with ui.card():
    ui.card_header("Sample Sales Data")

    @render.data_frame
    def sample_sales_data():
        return render.DataTable(dat().head(100), selection_mode="row", filters=True)
