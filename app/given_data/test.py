import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point

# Load data (assuming file paths are correct)
lina1 = gpd.read_file("given_data/cityline_geojson/cityline_2025.geojson")
pop = pd.read_csv("given_data/ibuafjoldi.csv")
smallarea = gpd.read_file("given_data/smasvaedi_2021.json")
dwellings = pd.read_csv("given_data/ibudir.csv")

# Reproject to EPSG:3057 (projected CRS for Iceland, distances in meters)
lina1 = lina1.to_crs(epsg=3057)
smallarea = smallarea.to_crs(epsg=3057)

# Add 400m radius circle using projected coordinates
# Define station coordinates (in EPSG:3057)
station_x = 356250.0
station_y = 408250.0

# Create a Shapely Point for the station
station_point = Point(station_x, station_y)

# Create a 400-meter buffer around the station
buffered_circle = station_point.buffer(400)  # 400 meters in projected CRS

# Convert the circle into a GeoDataFrame for plotting
circle_gdf = gpd.GeoDataFrame(geometry=[buffered_circle], crs="EPSG:3057")

# Data processing
pop['smasvaedi'] = pop['smasvaedi'].astype(str).str.zfill(4)
pop2024 = pop[(pop['ar'] == 2024) & (pop['aldursflokkur'] == "10-14 ára") & (pop['kyn'] == 1)]
pop2024_smallarea = pd.merge(smallarea, pop2024, left_on='smsv', right_on='smasvaedi', how='left')

# Filter for nuts3 == "001"
filtered_smallarea = pop2024_smallarea[pop2024_smallarea['nuts3'] == "001"]

# Plot the filtered small areas and write the IDs
fig, ax = plt.subplots(1, 1, figsize=(10, 10))  # Adjust figsize as needed
filtered_smallarea.plot(ax=ax, facecolor='none', edgecolor='blue')  # Plot small areas with blue borders
lina1.plot(ax=ax, facecolor='none', edgecolor='black')  # Plot cityline data
circle_gdf.plot(ax=ax, facecolor='none', edgecolor='red', linewidth=2)  # Add the circle in red
# Set x and y axis limits to zoom into the area
ax.set_xlim(355500, 357000)  # Adjust to your desired x-axis range
ax.set_ylim(407500, 409000)  # Adjust to your desired y-axis range

# Add IDs as text labels
for _, row in filtered_smallarea.iterrows():
    # Get the centroid of each small area
    centroid = row.geometry.centroid
    # Place the ID as text at the centroid
    ax.text(centroid.x, centroid.y, str(row['smsv']), fontsize=8, color='darkred', ha='center')

ax.set_title("Filtered Small Areas with IDs Written Inside")
plt.show()
