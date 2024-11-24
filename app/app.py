import faicons as fa
import sys
import os
from ipyleaflet import Map, Marker, LayerGroup, Circle, Icon, AwesomeIcon, DivIcon, basemaps

import geopandas as gpd
from datetime import datetime

import seaborn as sns
import matplotlib.pyplot as plt

from pandas.core.frame import functools
# Load data and compute static values
from borgarlina3_leaflet import create_map, load_and_preprocess_data
from shared import app_dir, tips
from shinywidgets import render_widget 

from shiny import reactive, render
from shiny.express import input, ui

# Import from backend
from data_processing.data_provider import Data_provider

initBackend = Data_provider()
def getScore(cords):
    pass

def generateStops(year):
    geojson_file = f"given_data/cityline_geojson/cityline_{year}.geojson"
    pop_file = "given_data/ibuafjoldi.csv"
    smallarea_file = "given_data/smasvaedi_2021.json"
    dwellings_file = "given_data/ibudir.csv"

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
    ui.input_slider("rad", "Stop reach radius:", min=200, max=1000, value=400),
    # station_coord, w_density=1, w_income=1, w_age=1):
    ui.input_numeric("w_density", "Density Weight", "1")
    ui.input_numeric("w_income", "Income Weight", "1")
    ui.input_numeric("w_age", "Age Weight", "1")
    

    ui.input_action_button("reset", "Reset zoom")

with ui.layout_columns(col_widths=[8, 4]):
    with ui.card(full_screen=True):
        ui.card_header("Capital area")

        
        @render_widget  
        def map():
            return Map(
                basemap=basemaps.CartoDB.Positron)  

    with ui.layout_column_wrap(width="250px"):
        with ui.card(full_screen=False):
            ui.card_header("Stop Data")
            with ui.navset_pill(id="tab"):
                with ui.nav_panel("Total Score"):
                    "Total Score"
                    @render.text
                    def totalScore():
                        score = scores()
                        return f"{round(float(score["total_score"]), 2)}"
                
                with ui.nav_panel("Income"):
                    "Income Score"    
                    @render.text
                    def incomeScore():
                        score = scores()
                        return f"{round(float(score["income_score"]), 2)}"
                
                with ui.nav_panel("Age"):
                    "Age Score" 
                    @render.text
                    def ageScore():
                        score = scores()
                        return f"{round(float(score["age_score"]), 2)}"
                    
                with ui.nav_panel("Density"):
                    "Density" 
                    @render.text
                    def sensityScoer():
                        score = scores()
                        return f"{round(float(score["density_score"] * 1000000), 2)} Person / Kilometer"
                
                with ui.nav_panel("The Line"):
                    "The Total Score For Lines" 
                    @render.text
                    def line():
                        return lineScore()
                    
                    
            @render.plot(alt="A b   ar chart of income distribution.")
            def income_plot():
                print("Generating income distribution bar chart")
                
                # Get selected stop coordinates
                x, y = stop.get()
                station_coord = (y, x)
                
                # Fetch income distribution data from the Data_provider instance
                income_data = initBackend.get_station_score(station_coord, radius=input.rad())['income_data']  # Assume this returns a dictionary
                
                # Example structure: {1: 150, 2: 200, 3: 180, ...}
                income_brackets = list(income_data.keys())
                populations = list(income_data.values())
                
                # Create a Matplotlib figure
                fig, ax = plt.subplots(figsize=(8, 4))
                
                # Create the bar chart
                ax.bar(income_brackets, populations, color='lightcoral')
                
                # Customize the plot
                ax.set_title("Population by Income Bracket")
                ax.set_xlabel("Income Bracket")
                ax.set_ylabel("Population")
                ax.set_xticks(income_brackets)
                ax.set_xticklabels(income_brackets, rotation=45, ha="right")
                
                # Return the figure for rendering in Shiny
                return fig


                        

        
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
        marker.on_click(functools.partial(create_marker_callback, id=stop))
        markers.append(marker)
    
    layerGroup = LayerGroup(layers=markers, name="stops")
    layerGroup2 = LayerGroup(layers=circles, name="radius")
    map.widget.add(layerGroup)
    map.widget.add(layerGroup2)
    
    
stop = reactive.value()

def create_marker_callback(id, **kwargs):
    # We can also get coordinates of the marker here
    rad = input.rad()
    zoom = 15.0
    if rad > 500:
        zoom = 14.8
    map.widget.zoom = zoom
    map.widget.center = kwargs["coordinates"]
    stop.set(id)

@reactive.effect
def centerMap():
    mapCenter = input.reset()
    map.widget.zoom = 11.8
    map.widget.center = (64.11,-21.90)

@reactive.calc
def scores():
    x, y = stop.get()
    score = initBackend.get_station_score(station_coord=(y, x), w_density=input.w_density(), w_income=input.w_income(), w_age=input. w_age(), radius=input.rad())
    return score


@reactive.calc
def lineScore():
    listOfStops = generateStops(input.year())
    listOflines = {}
    for stop, color in listOfStops:
        x, y = stop
        listOflines[color] = listOflines.get(color, []).append((y,x))
    

    lines = []
    for key, val in listOflines:
        
        score = initBackend.line_score(val, w_density=input.w_density(), w_income=input.w_income(), w_age=input. w_age(), radius=input.rad())
        print(score)
        lines.append((key, score["final_score"]))
    return lines