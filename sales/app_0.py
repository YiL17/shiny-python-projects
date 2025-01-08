import plotly.express as px
from shiny.express import input, ui, render
from shiny import reactive
from shinywidgets import render_plotly

import pandas as pd
from pathlib import Path
import calendar


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
    df['value'] = df['quantity_ordered'] * df['price_each']
    return df


# with ui.card():  
#     ui.card_header("TopN Sales")

#     with ui.layout_sidebar():  
#         with ui.sidebar(bg="#f8f8f8", open='open'):  
#             ui.input_numeric("n", "Number of Items", 5, min=0, max=20)
      
#         @render_plotly
#         def plot1():
#             df = dat()
#             top_sales = df.groupby('product')['quantity_ordered'].sum().nlargest(input.n()).reset_index()
#             fig = px.bar(top_sales, x='product', y="quantity_ordered")
#             # fig.update_traces(marker_color = color())
#             return fig

# with ui.card():
#     ui.input_numeric("n", "Number of Items", 5, min=0, max=20)
    
#     @render_plotly
#     def plot1():
#         df = dat()
#         top_sales = df.groupby('product')['quantity_ordered'].sum().nlargest(input.n()).reset_index()
#         fig = px.bar(top_sales, x='product', y="quantity_ordered")
#         # fig.update_traces(marker_color = color())
#         return fig


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
        "Heatmap"

with ui.card():
    ui.card_header("Sales by Location Map")
    "Content here"


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
 

        @render_plotly
        def sales_over_time():
            df = dat()
            print(list(df.city.unique()))
            sales = df.groupby(["city", "month"])["quantity_ordered"].sum().reset_index()
            sales_by_city = sales[sales["city"]==input.city()]
            month_orders = calendar.month_name[1:]
            fig = px.bar(
                sales_by_city,
                x="month",
                y="quantity_ordered",
                title = f"Sales over Time -- {input.city()}",
                category_orders={"month": month_orders},
            )
            # fig.update_traces(marker_color = color())
            return fig  




# with ui.card():
#     ui.card_header("Sample Sales Data")

#     @render.data_frame
#     def sample_sales_data():
#         return dat().head(100)
