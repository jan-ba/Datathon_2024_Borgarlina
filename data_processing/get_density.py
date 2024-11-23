
from typing import List, Tuple
from pyproj import Geod


def get_density(polygon_coordinates: List[Tuple], population: int) -> float:
    """
    Calculate the population density of a polygon with geographic coordinates.

    Args:
        polygon_coordinates (List[Tuple[float, float]]): List of (longitude, latitude) coordinates defining the polygon.
        population (int): Population within the polygon.

    Returns:
        float: Population density (population per square meter).
    """
    geod = Geod(ellps="WGS84")
    
    area, _ = geod.polygon_area_perimeter(polygon_coordinates)
    area = abs(area)    
    if area == 0:
        raise ValueError("The polygon area is zero. Cannot calculate density.")
    
    return population / area