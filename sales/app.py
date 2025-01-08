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


ui.page_opts(title="Sales Dashboard", fillable=False)
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
    df['hour'] = df['order_date'].dt.hour
    df['value'] = df['quantity_ordered'] * df['price_each']
    return df



with ui.card():  
    ui.card_header("Sales by City 2023")

    with ui.layout_sidebar():  
        with ui.sidebar(bg="#f8f8f8", open='open'):  
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
                selected = 'Boston (MA)'
            )
 

        @render_altair
        def sales_over_time():
            df = dat()
            sales = df.groupby(["city", "month"])["quantity_ordered"].sum().reset_index()
            sales_by_city = sales[sales["city"] == input.city()]
            month_orders = list(calendar.month_name[1:])
            sales_by_city["month"] = pd.Categorical(sales_by_city["month"], categories=month_orders, ordered=True)
            
            fig = alt.Chart(sales_by_city).mark_bar().encode(
            x=alt.X("month", sort=month_orders, title="Month"),
            y=alt.Y("quantity_ordered", title="Quantity Ordered"),
            tooltip=["month", "quantity_ordered"]
            ).properties(
            title=f"Sales over Time -- {input.city()}"
            )
            return fig


# with ui.layout_columns(col_widths=(6,6)): # based on 12 column grid
with ui.layout_column_wrap(width=1/2): 
    with ui.navset_card_underline(id="tab", footer = ui.input_numeric("n", "Number of Items", 5, min=0, max=20)):  
        with ui.nav_panel("Top Sellers"):
            @render_plotly
            def plot_top_sellers():
                df = dat()
                top_sales = df.groupby('product')['quantity_ordered'].sum().nlargest(input.n()).reset_index()
                fig = px.bar(top_sales, x='product', y="quantity_ordered")
                # fig.update_traces(marker_color = color())
                return fig


        with ui.nav_panel("Top Sellers Value"):
            @render_plotly
            def plot_top_sellers_value():
                df = dat()
                
                top_sales = df.groupby('product')['value'].sum().nlargest(input.n()).reset_index()
                fig = px.bar(top_sales, x='product', y="value")
                # fig.update_traces(marker_color = color())
                return fig

        with ui.nav_panel("Lowest Sellers"):
            @render_plotly
            def plot_lowest_sellers():
                df = dat()
                top_sales = df.groupby('product')['quantity_ordered'].sum().nsmallest(input.n()).reset_index()
                fig = px.bar(top_sales, x='product', y="quantity_ordered")
                # fig.update_traces(marker_color = color())
                return fig

        with ui.nav_panel("Lowest Sellers Value"):
            @render_plotly
            def plot_smallest_sellers_value():
                df = dat()                
                top_sales = df.groupby('product')['value'].sum().nsmallest(input.n()).reset_index()
                fig = px.bar(top_sales, x='product', y="value")
                # fig.update_traces(marker_color = color())
                return fig
            
    with ui.card():
        ui.card_header("Sales by Time of Day Heatmap")
        @render.plot
        def plot_sales_by_time():
            df = dat()
            sales_by_hour = df['hour'].value_counts().reindex(np.arange(0,24), fill_value=0)

            heatmap_data = sales_by_hour.values.reshape(24,1)
            sns.heatmap(heatmap_data,
                        annot=True,
                        fmt="d",
                        cmap="coolwarm",
                        cbar=False,
                        xticklabels=[],
                        yticklabels=[f"{i}:00" for i in range(24)]
                        )
            plt.title("Number of Orders by Hour of Day")
            plt.xlabel("Hour of Day")
            plt.ylabel("Order Count")

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
        heatmap_data = df[['lat','long', 'quantity_ordered']].values
        map = folium.Map(location = [37.0902, -95.7129], zoom_start = 4)
        HeatMap(heatmap_data).add_to(map)
        return map

with ui.card():
    ui.card_header("Sample Sales Data")

    @render.data_frame
    def sample_sales_data():
        return render.DataTable(dat().head(100), selection_mode='row', filters=True)



