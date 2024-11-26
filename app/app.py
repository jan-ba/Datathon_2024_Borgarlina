import faicons as fa
import sys
import os
from ipyleaflet import Map, Marker, LayerGroup, Circle, Icon, AwesomeIcon, DivIcon, basemaps, GeoJSON

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

    gpdStops, _, all_small_areas = load_and_preprocess_data(geojson_file, pop_file, smallarea_file, dwellings_file)

    points = []
    stopData = {}
    # Assuming your GeoDataFrame is named 'gdf'
    for _, row in gpdStops.iterrows():
        point = row["geometry"]
        color = row["line"]
        if color not in ["red", "yellow", "blue", "green", "purple", "orange"]:
            color = color.split("/") 
        points.append(((point.y, point.x), color))
    return points, all_small_areas

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
    
    
    
        


    
            
    with ui.layout_column_wrap(width="450px"):
            with ui.layout_columns(col_widths=(6, 6)):
                with ui.value_box(theme="text-red",  showcase=fa.icon_svg("bus", width="50px"),):
                    "Red line"
                    @render.text
                    def render_line_score():
                        return str(int(lineScore().get("red", 0)))

                with ui.value_box(theme="text-blue",showcase=fa.icon_svg("bus", width="50px"),):
                    
                    "Blue line"
                    @render.text
                    def render_line_score1():
                        return str(int(lineScore().get("blue", 0)))

                with ui.value_box(theme="text-yellow" ,showcase=fa.icon_svg("bus", width="50px"),):
                    "Yellow line"
                    @render.text
                    def render_line_score2():
                        return str(int(lineScore().get("orange", 0)))

                with ui.value_box(theme="text-purple",showcase=fa.icon_svg("bus", width="50px"),):
                    "Purple line"
                    @render.text
                    def render_line_score3():
                        return str(int(lineScore().get("purple", 0)))

                with ui.value_box(theme="text-green",showcase=fa.icon_svg("bus", width="50px"),):
                    "Green line"
                    @render.text
                    def render_line_score4():
                        return str(int(lineScore().get("green", 0)))

                with ui.value_box(theme="text-black",showcase=fa.icon_svg("route", width="50px")):
                    "Total score"
                    @render.text
                    def render_line_score5():
                        return str(int(sum(lineScore().get(color, 0) for color in ["red", "blue", "orange", "purple", "green"])))

            
            with ui.card(min_height="600px"):
                ui.card_header("Stop Data")
                

                with ui.navset_pill(id="tab"):
                    with ui.nav_panel("Score"):
                        
                        @render.text
                        def totalScore():
                            score = scores()
                            return "Total score: " + str(int(score["total_score"]))
                        @render.plot(alt="A pie chart of score contributions from age, income, and density.")
                        def contribution_pie_chart():
                            print("Generating pie chart of contributions")
                            
                            # Get score components
                            score = scores()
                            age_contribution = score["age_score"]
                            income_contribution = score["income_score"]
                            density_contribution = score["density_score"]
                            
                            # Data for the pie chart
                            contributions = [age_contribution, income_contribution, density_contribution]
                            labels = ["Age", "Income", "Density"]
                            colors = ["#FD4D86", "#36DEC2", "#704CB0"]  # Custom colors for the segments
                            
                            # Create a Matplotlib figure
                            fig, ax = plt.subplots(figsize=(6, 6))
                            
                            # Create the pie chart
                            ax.pie(
                                contributions, 
                                labels=labels, 
                                autopct='%1.1f%%', 
                                startangle=90, 
                                colors=colors, 
                                textprops={'fontsize': 12}
                            )
                            
                            # Add a title
                            ax.set_title("Score Contributions", fontsize=16)
                            
                            # Return the figure for rendering in Shiny
                            return fig
                    
                    with ui.nav_panel("Income"):
                        "Income Score"    
                        @render.text
                        def incomeScore():
                            score = scores()
                            return score["income_score"]
                        @render.plot(alt="A chart of income distribution.")
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
                            ax.bar(income_brackets, populations, color='#36DEC2')
                            
                            # Customize the plot
                            ax.set_title("Population by Income Bracket")
                            ax.set_xlabel("Income Bracket")
                            ax.set_ylabel("Population")
                            ax.set_xticks(income_brackets)
                            ax.set_xticklabels(income_brackets, rotation=45, ha="right")
                            
                            # Return the figure for rendering in Shiny
                            return fig

                    
                    with ui.nav_panel("Age"):
                        "Age Score" 
                        @render.text
                        def ageScore():
                            score = scores()
                            return score["age_score"]                    
                        @render.plot(alt="A bar chart of age distribution.")
                        def age_plot():
                            print("Generating age distribution bar chart")
                            
                            # Get selected stop coordinates
                            x, y = stop.get()
                            station_coord = (y, x)
                            
                            # Fetch age distribution data from the Data_provider instance
                            age_data = initBackend.get_station_score(station_coord, radius=input.rad())['age_data']  # Assume this returns a dictionary
                            
                            # Example structure: {'0-4 ára': 120, '5-9 ára': 140, ...}
                            age_brackets = list(age_data.keys())
                            populations = list(age_data.values())
                            
                            # Create a Matplotlib figure
                            fig, ax = plt.subplots(figsize=(8, 4))
                            
                            # Create the bar chart with custom colors
                            ax.bar(age_brackets, populations, color='#FD4D86')
                            
                            # Customize the plot
                            ax.set_title("Population by Age Bracket", fontsize=14)
                            ax.set_xlabel("Age Bracket", fontsize=12)
                            ax.set_ylabel("Population", fontsize=12)
                            ax.set_xticks(range(len(age_brackets)))
                            ax.set_xticklabels(age_brackets, rotation=45, ha="right", fontsize=10)
                            
                            # Return the figure for rendering in Shiny
                            return fig
                        
                    with ui.nav_panel("Density"):
                        "Density" 
                        @render.text
                        def sensityScoer():
                            score = scores()
                            return float(score["density_score"] * 1000000)
                    
                    
                        @render.plot(alt="A bar chart of density scores for all areas within the radius.")
                        def density_plot():
                            print("Generating density score bar chart")
                            
                            # Get selected stop coordinates
                            x, y = stop.get()
                            station_coord = (y, x)
                            
                            # Fetch small area contributions from the Data_provider instance
                            small_area_contributions = initBackend.get_station_score(
                                station_coord, 
                                radius=input.rad(),
                                w_density=input.w_density(), 
                                w_income=input.w_income(), 
                                w_age=input.w_age()
                            )['small_area_contributions']
                            
                            # Extract density scores for each small area
                            area_ids = [area_id for area_id in small_area_contributions.keys()]
                            density_scores = [area_data['density_score'] for area_data in small_area_contributions.values()]
                            
                            # Create a Matplotlib figure
                            fig, ax = plt.subplots(figsize=(8, 4))
                            
                            # Create the bar chart
                            ax.bar(area_ids, density_scores, color='#704CB0')
                            
                            # Customize the plot
                            ax.set_title("Density Scores of Small Areas", fontsize=14)
                            ax.set_xlabel("Small Area ID", fontsize=12)
                            ax.set_ylabel("Density Score", fontsize=12)
                            ax.set_xticks(range(len(area_ids)))
                            ax.set_xticklabels(area_ids, rotation=45, ha="right", fontsize=10)
                            
                            # Return the figure for rendering in Shiny
                            return fig
                        
                    

                        

        
ui.include_css(app_dir / "styles.css")

# --------------------------------------------------------
# Reactive calculations and effects
# --------------------------------------------------------

@reactive.effect
def _():
    
    year = input.year()
    stops, small_areas = generateStops(year)
    rad = input.rad()
    markers = []
    circles = []
    
    for layer in map.widget.layers[:]:
        if layer.name in ["stops", "radius", "polygons", "heatmap"]:
            map.widget.remove_layer(layer)

    # Add polygons from small_areas
    polygons_layer = []
    for _, area in small_areas.iterrows():
        geojson_data = area["geometry"].__geo_interface__
        geojson_dict = {
            "type": "Feature",
            "properties": {},
            "geometry": geojson_data
        }

        geojson = GeoJSON(
            data=geojson_dict,  # Pass the dictionary here
            style={
                "color": "#005485",       # Border color
                "fillColor": "white",  # Fill color
                "opacity": 0.5,        # Border opacity
                "weight": 1.0,         # Border thickness
                "dashArray": "5, 5",   # Optional dashed border
                "fillOpacity": 0.3     # Fill opacity
            },
            hover_style={"color": "#005485", "weight": 1},  # Highlight on hover
            name="polygons"
        )
        polygons_layer.append(geojson)

    i = 0
    for stop, color in stops:
        if type(color) == list:
            smallerRad = 0
            for c in color:
                circle = Circle()
                circle.location = stop
                circle.radius = rad - smallerRad
                circle.color = c
                circle.fill_opacity = 0.1
                circle.name = str(i)
                circles.append(circle)
                smallerRad =+ 50
        else:
            circle = Circle()
            circle.location = stop
            circle.radius = rad
            circle.color = color
            circle.fill_color = color
            circle.fill_opacity = 0.1
            circle.name = str(i)
            circles.append(circle)
        
        

        icon = AwesomeIcon(name="bus", marker_color="black", icon_color="white")
        # icon1 = DivIcon(html = '<div style="border-radius:50%;background-color: black; width: 10px; height: 10px;"></div>')
        # icon2 = Icon(icon_url="marker.png")
        marker = Marker(location=stop,
                        icon=icon,
                        icon_anchor=(10,10),
                        icon_size=(0,0),
                        draggable=True)
        marker.name = str(i)
        marker.on_click(functools.partial(create_marker_callback, id=stop))
        marker.on_move(functools.partial(reset_marker, index=i))
        
        markers.append(marker)
        i += 1
    
    layerGroup = LayerGroup(layers=markers, name="stops")
    layerGroup2 = LayerGroup(layers=circles, name="radius")
    map.widget.add(layerGroup)
    map.widget.add(layerGroup2)

    # Add polygon layers to the map
    polygon_group = LayerGroup(layers=polygons_layer, name="polygons")
    map.widget.add(polygon_group)
    
    
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

def reset_marker(index, **kwargs):
    cord = kwargs["location"]
    x = cord[0]
    y = cord[1]
    for layer in map.widget.layers:
        if layer.name == "radius":  # Check for the correct LayerGroup
            for circle in layer.layers:
                if circle.name == str(index):  # Match the Circle by name
                    circle.location = [x, y]  # Update the Circle's location
    stop.set((x,y))
            

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
    listOfStops, _ = generateStops(input.year())
    listOflines = {}

    # Handle stops with single and multiple colors
    for stop, color in listOfStops:
        x, y = stop
        # If the color is a list (multiple colors), iterate through it
        if isinstance(color, list):
            for single_color in color:
                if single_color not in listOflines:
                    listOflines[single_color] = []
                listOflines[single_color].append((y, x))
        else:
            # If it's a single color, process it normally
            if color not in listOflines:
                listOflines[color] = []
            listOflines[color].append((y, x))

    # Calculate scores for each line
    lines = {}
    for key, val in listOflines.items():
        score = initBackend.line_score(
            val,
            w_density=input.w_density(),
            w_income=input.w_income(),
            w_age=input.w_age(),
            radius=input.rad()
        )
        lines[key] = score["final_score"]

    return lines