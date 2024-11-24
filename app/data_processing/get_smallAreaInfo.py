import json
import os

# Define the file path
file_path = os.path.join('given_data', 'smasvaedi_2021.json')

# Load the JSON data
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

def get_smallAreas():
    '''
    Returns a list of dict of format {"id": smsv_id, "geometry": [(long, lat), ...]} 
    for all smsv in in Höfuðborgarsvæði.
    '''
    # Extract smsv IDs and geometries for Höfuðborgarsvæði
    hofudborgarsvaedi_areas = []

    for feature in data['features']:
        if feature['properties'].get('nuts3_label') == "Höfuðborgarsvæði":
            smsv = feature['properties'].get('smsv')
            raw_geometry = feature['geometry']
            if smsv and raw_geometry:
                # Extract coordinates and convert to list of tuples
                processed_geometry = []
                for polygon in raw_geometry['coordinates']:
                    # for ring in polygon:  # Each "ring" of the MultiPolygon
                    #     processed_geometry.append([(x, y) for x, y in ring])
                    processed_geometry = [(x, y) for x, y in polygon[0]]

                hofudborgarsvaedi_areas.append({"id": smsv, "geometry": processed_geometry})
    
    ids = [area["id"] for area in hofudborgarsvaedi_areas]
    if len(ids) != len(set(ids)):
        duplicates = [smsv for smsv in ids if ids.count(smsv) > 1]
        raise ValueError(f"Duplicate IDs found: {set(duplicates)}")

    return hofudborgarsvaedi_areas
