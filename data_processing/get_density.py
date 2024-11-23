
from typing import List, Tuple
from pyproj import Geod
from get_smallAreaInfo import get_smallAreas

def get_density(polygon_coordinates: List[Tuple], population: int) -> float:
    """
    Calculate the population density of a polygon with geographic coordinates.

    Args:
        polygon_coordinates (List[Tuple[float, float]]): List of (longitude, latitude) coordinates defining the polygon.
        population (int): Population within the polygon.

    Returns:
        float: Population density (population per square meter).
    """
    # parse lat and long into seperate arrays
    # print(polygon_coordinates)
    lat = [lat_val[0] for lat_val in polygon_coordinates]
    long = [long_val[1] for long_val in polygon_coordinates]
    print(lat)
    print(long)
    geod = Geod(ellps="WGS84")
    
    area, _ = geod.polygon_area_perimeter(long, lat)
    print(area)
    area = abs(area)    
    if area == 0:
        raise ValueError("The polygon area is zero. Cannot calculate density.")
    
    return population / area

smsv = get_smallAreas()
example = smsv[1]
res = get_density(example[1], 100)
print(res)
