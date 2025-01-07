import plotly.express as px
from shiny.express import input, ui, render
from shiny import reactive
from shinywidgets import render_plotly

import pandas as pd
from pathlib import Path
import calendar


ui.page_opts(title="Sales Dashboard", fillable=True)

ui.input_numeric("n", "Number of Items", 5, min=0, max=20)

@reactive.calc
# value will get cached and propagate any changes later on
def dat():
    infile = Path(__file__).parent / "data/sales.csv"
    df = pd.read_csv(infile)
    df['order_date'] = pd.to_datetime(df['order_date'])
    df['month'] = df['order_date'].dt.month_name()
    return df


# @render_plotly
# def plot1():
#     df = dat()
#     top_sales = df.groupby('product')['quantity_ordered'].sum().nlargest(input.n()).reset_index()
#     return px.bar(top_sales, x='product', y="quantity_ordered")


ui.input_selectize(  
    "city",  
    "Select a City:",  
    ['Dallas (TX)', 'Boston (MA)', 'Los Angeles (CA)', 'San Francisco (CA)', 'Seattle (WA)', 'Atlanta (GA)', 'New York City (NY)', 'Portland (OR)', 'Austin (TX)', 'Portland (ME)'],  
    multiple=True,  
)  


@render_plotly
def sales_over_time():
    df = dat()
    print(list(df.city.unique()))
    sales = df.groupby(['city','month'])['quantity_ordered'].sum().reset_index()
    sales_by_city = sales[sales['city']=='Boston (MA)']
    month_orders = calendar.month_name[1:]
    fig = px.bar(sales_by_city, x = 'month', y = 'quantity_ordered', category_orders = {'month': month_orders})
    return fig

with ui.card():
    ui.card_header("Sample Sales Data")
    @render.data_frame
    def sample_sales_data():
        return dat().head(100)

