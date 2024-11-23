
from typing import List, Tuple
from pyproj import Geod
from shapely.geometry import Polygon

def get_density(polygon_coordinates: List[Tuple[float, float]], population: int) -> float:
    """
    Calculate the population density of a polygon with geographic coordinates.

    Args:
        polygon_coordinates (List[Tuple[float, float]]): List of (longitude, latitude) coordinates defining the polygon.
        population (int): Population within the polygon.

    Returns:
        float: Population density (population per square meter).
    """
    if polygon_coordinates[0] != polygon_coordinates[-1]:
        polygon_coordinates.append(polygon_coordinates[0])

    polygon = Polygon(polygon_coordinates)

    area = polygon.area
    if area == 0:
        raise ValueError("The polygon area is zero. Cannot calculate density.")

    return population / area


