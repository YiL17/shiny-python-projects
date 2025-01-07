import plotly.express as px
from shiny.express import input, ui, render
from shiny import reactive
from shinywidgets import render_plotly

import pandas as pd
from pathlib import Path


ui.page_opts(title="Sales Dashboard", fillable=True)

ui.input_numeric("n", "Number of Items", 5, min=0, max=20)

@reactive.calc
def dat():
    infile = Path(__file__).parent / "data/sales.csv"
    return pd.read_csv(infile)

with ui.layout_columns():

    @render_plotly
    def plot1():
        df = dat()
        top_sales = df.groupby('product')['quantity_ordered'].sum().nlargest(input.n()).reset_index()
        return px.bar(top_sales, x='product', y="quantity_ordered")

    # @render.data_frame
    # def data():
    #     return dat()

