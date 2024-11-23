import json
import os
import geopandas as gpd


def get_smallAreas(file_path):
    '''
    Reads the given GeoJSON file and returns a list of dicts of the format 
    {"id": smsv_id, "geometry": [(long, lat), ...]} for all smsv in Höfuðborgarsvæði.
    The function reads the data using GeoPandas, converts coordinates to a specified CRS, 
    and processes the data to extract the required information.
    '''
    # Load the data using GeoPandas
    gdf = gpd.read_file(file_path)
    
    # Define the desired coordinate reference system (CRS)
    gdf = gdf.to_crs(epsg=3057)
    
    # Extract smsv IDs and geometries for Höfuðborgarsvæði
    hofudborgarsvaedi_areas = []

    # Filter the GeoDataFrame for features in Höfuðborgarsvæði
    filtered_gdf = gdf[gdf['nuts3_label'] == "Höfuðborgarsvæði"]

    for idx, row in filtered_gdf.iterrows():
        smsv = row.get('smsv')
        geometry = row.geometry  # This is a shapely geometry object
        if smsv and geometry:
            # Extract coordinates from the geometry
            processed_geometry = []

            if geometry.geom_type == 'Polygon':
                # For Polygons, get the exterior coordinates
                coords = list(geometry.exterior.coords)
                processed_geometry = [(x, y) for x, y in coords]
            elif geometry.geom_type == 'MultiPolygon':
                # For MultiPolygons, iterate over each polygon (in the future perhaps)
                # for polygon in geometry.geoms:
                #     coords = list(polygon.exterior.coords)
                #     processed_geometry.extend([(x, y) for x, y in coords])
                coords = list(geometry.geoms[0].exterior.coords)
                processed_geometry = [(x, y) for x, y in coords]
            else:
                # Handle other geometry types if necessary
                continue

            hofudborgarsvaedi_areas.append({"id": smsv, "geometry": processed_geometry})

    # Check for duplicate IDs
    ids = [area["id"] for area in hofudborgarsvaedi_areas]
    if len(ids) != len(set(ids)):
        duplicates = [smsv for smsv in ids if ids.count(smsv) > 1]
        raise ValueError(f"Duplicate IDs found: {set(duplicates)}")

    return hofudborgarsvaedi_areas