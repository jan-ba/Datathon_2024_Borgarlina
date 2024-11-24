import faicons as fa

from ipyleaflet import Map, Marker, LayerGroup, Circle, Icon, AwesomeIcon, DivIcon, basemaps

import geopandas as gpd
from datetime import datetime
# Load data and compute static values
from borgarlina3_leaflet import create_map, load_and_preprocess_data
from shared import app_dir, tips
from shinywidgets import render_widget 

from shiny import reactive, render
from shiny.express import input, ui

def generateStops(year):
    geojson_file = f"../given_data/cityline_geojson/cityline_{year}.geojson"
    pop_file = "../given_data/ibuafjoldi.csv"
    smallarea_file = "../given_data/smasvaedi_2021.json"
    dwellings_file = "../given_data/ibudir.csv"

    gpdStops, _, _ = load_and_preprocess_data(geojson_file, pop_file, smallarea_file, dwellings_file)

    points = []

    # Assuming your GeoDataFrame is named 'gdf'
    for _, row in gpdStops.iterrows():
        point = row["geometry"]
        points.append((point.y, point.x))
    return points

bill_rng = (min(tips.total_bill), max(tips.total_bill))

# Add page title and sidebar
ui.page_opts(title="Borgarlínan", fillable=True)

with ui.sidebar(open="open"):

    ui.input_select("year", "Year:", 
                    {2025: "2025", 2029: "2029", 2030: "2030"})
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
            return Map(
                basemap=basemaps.CartoDB.Positron,
                center=(64.11,-21.90), 
                zoom=11.5)  

    '''with ui.layout_column_wrap(width="250px"):
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
                )'''
        
        
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
def _():
    year = input.year()
    stops = generateStops(year)
    markers = []
    circles = []
    
    for layer in map.widget.layers:
        if layer.name == "stops" or layer.name == "radius":
            map.widget.remove_layer(layer)

    for i in stops:
        circle = Circle()
        circle.location = i
        circle.radius = 400
        circle.color = "green"
        circle.fill_color = "green"
        circles.append(circle)

        icon = AwesomeIcon(name="bus", marker_color="black", icon_color="white")
        icon1 = DivIcon(html = '<div style="border-radius:50%;background-color: black; width: 10px; height: 10px;"></div>')
        icon2 = Icon(icon_url="marker.png")

        marker = Marker(location=i,
                        icon=icon,
                        icon_anchor=(10,10),
                        icon_size=(0,0))
        markers.append(marker)
    
    layerGroup = LayerGroup(layers=markers, name="stops")
    layerGroup2 = LayerGroup(layers=circles, name="radius")
    map.widget.add(layerGroup)
    map.widget.add(layerGroup2)
    
    
