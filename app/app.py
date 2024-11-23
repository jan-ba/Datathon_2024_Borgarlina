import faicons as fa

from ipyleaflet import Map

from datetime import datetime
# Load data and compute static values
from borgarlina3_leaflet import create_map, load_and_preprocess_data
from shared import app_dir, tips
from shinywidgets import render_widget 

from shiny import reactive, render
from shiny.express import input, ui

def generateStops():
    geojson_file = "../given_data/cityline_geojson/cityline_2025.geojson"
    pop_file = "../given_data/ibuafjoldi.csv"
    smallarea_file = "../given_data/smasvaedi_2021.json"
    dwellings_file = "../given_data/ibudir.csv"

    lina1_wgs84, pop2024_smallarea, all_dwellings_smallarea = load_and_preprocess_data(geojson_file, pop_file, smallarea_file, dwellings_file)
    return create_map(lina1_wgs84, all_dwellings_smallarea)

bill_rng = (min(tips.total_bill), max(tips.total_bill))

# Add page title and sidebar
ui.page_opts(title="Borgarlínan", fillable=True)

with ui.sidebar(open="open"):

    ui.input_slider("year", "Years:", min=2024 , max=2030, value=1)
    ui.input_text("inputParam", "Param", "")
    
    ui.input_checkbox_group(
        "time",
        "Stuffs",
        ["Param1", "Param2"],
        selected=["Param1", "Param2"],
        inline=True,
    )

    ui.input_action_button("reset", "Reset filter")

# Add main content
ICONS = {
    "user": fa.icon_svg("user", "regular"),
    "wallet": fa.icon_svg("wallet"),
    "currency-dollar": fa.icon_svg("dollar-sign"),
    "ellipsis": fa.icon_svg("ellipsis"),
}


# MAP 
with ui.layout_columns(col_widths=[8, 4]):
    with ui.card(full_screen=True):
        ui.card_header("Capital area")

        
        @render_widget  
        def map():
            return Map(generateStops(), center=(50.6252978589571, 0.34580993652344), zoom=3)  
    with ui.layout_column_wrap(width="250px"):
        with ui.card(full_screen=False):
            ui.card_header("Stop Data")
            @render_widget  
            def table1():
                return render.DataTable(
                    {},
                    width="250px",
                    height="100px"
                )
        
        with ui.card(full_screen=False):
            ui.card_header("Stop Data1")
            @render_widget  
            def table2():
                return render.DataTable(
                    {},
                    width="250px",
                    height="100px"
                )
        
        with ui.card(full_screen=False):
            ui.card_header("Stop Data2")
            @render_widget  
            def table3():
                return render.DataTable(
                    {},
                    width="250px",
                    height="100px"
                )
        
        
ui.include_css(app_dir / "styles.css")

# --------------------------------------------------------
# Reactive calculations and effects
# --------------------------------------------------------


@reactive.calc
def tips_data():
    bill = input.total_bill()
    idx1 = tips.total_bill.between(bill[0], bill[1])
    idx2 = tips.time.isin(input.time())
    return tips[idx1 & idx2]


@reactive.effect
@reactive.event(input.reset)
def _():
    ui.update_slider("total_bill", value=bill_rng)
    ui.update_checkbox_group("time", selected=["Lunch", "Dinner"])