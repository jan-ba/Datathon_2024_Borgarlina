import faicons as fa

from ipyleaflet import Map, Marker, LayerGroup, Circle, Icon, AwesomeIcon, DivIcon, basemaps

import geopandas as gpd
from datetime import datetime

from pandas.core.frame import functools
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
    stopData = {}
    # Assuming your GeoDataFrame is named 'gdf'
    for _, row in gpdStops.iterrows():
        point = row["geometry"]
        color = row["line"]
        if color not in ["red", "yellow", "blue", "green", "purple", "orange"]:
            color = color.split("/")
        points.append(((point.y, point.x), color))
    return points

# Add page title and sidebar
ui.page_opts(title="Borgarlínan", fillable=True)

with ui.sidebar(open="open"):

    ui.input_select("year", "Year:", {2025: "2025", 2029: "2029", 2030: "2030"})
    ui.input_text("inputParam", "Param", "")
    ui.input_slider("rad", "Stop reach radius:", min=200, max=1000, value=400),
    
    ui.input_checkbox_group(
        "time",
        "Stuffs",
        ["Param1", "Param2"],
        selected=["Param1", "Param2"],
        inline=True,
    )

    ui.input_action_button("reset", "Reset filter")

with ui.layout_columns(col_widths=[8, 4]):
    with ui.card(full_screen=True):
        ui.card_header("Capital area")

        
        @render_widget  
        def map():
            return Map(
                basemap=basemaps.CartoDB.Positron,
                center=(64.11,-21.90), 
                zoom=11.5)  

    with ui.layout_column_wrap(width="250px"):
        with ui.card(full_screen=False):
            ui.card_header("Stop Data")
            @render.text
            def value():
                return f"Selected bus stop: {stop.get()}"

        
ui.include_css(app_dir / "styles.css")

# --------------------------------------------------------
# Reactive calculations and effects
# --------------------------------------------------------

@reactive.effect
def _():
    year = input.year()
    stops = generateStops(year)
    rad = input.rad()
    markers = []
    circles = []
    
    for layer in map.widget.layers:
        if layer.name == "stops" or layer.name == "radius":
            map.widget.remove_layer(layer)

    for stop, color in stops:
        if type(color) == list:
            smallerRad = 0
            for c in color:
                circle = Circle()
                circle.location = stop
                circle.radius = rad - smallerRad
                circle.color = c
                circles.append(circle)
                smallerRad =+ 50
        else:
            circle = Circle()
            circle.location = stop
            circle.radius = rad
            circle.color = color
            circle.fill_color = color
            circles.append(circle)

        icon = AwesomeIcon(name="bus", marker_color="black", icon_color="white")
        icon1 = DivIcon(html = '<div style="border-radius:50%;background-color: black; width: 10px; height: 10px;"></div>')
        icon2 = Icon(icon_url="marker.png")

        marker = Marker(location=stop,
                        icon=icon,
                        icon_anchor=(10,10),
                        icon_size=(0,0),
                        draggable=False)
        marker.on_click(functools.partial(create_marker_callback, id=f"SET_ID_HERE {stop}"))
        markers.append(marker)
    
    layerGroup = LayerGroup(layers=markers, name="stops")
    layerGroup2 = LayerGroup(layers=circles, name="radius")
    map.widget.add(layerGroup)
    map.widget.add(layerGroup2)
    
stop = reactive.value("Init")

def create_marker_callback(id, **kwargs):
    # We can also get coordinates of the marker here
    map.widget.zoom = 15
    map.widget.center = kwargs["coordinates"]
    stop.set(id)