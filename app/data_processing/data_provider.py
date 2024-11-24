from typing import List, Tuple
import math
from traitlets import Float
from data_processing.get_smallAreaInfo import get_smallAreas
from data_processing.point_scoring import score_current, calc_score_line
from data_processing.get_station_coverage import get_station_coverage
from data_processing.aggregate_data import get_feature_df
import os
import pandas as pd
from pyproj import Transformer


class Data_provider():

    def __init__(self):
        self.smsv_list = get_smallAreas()
        self.df = get_feature_df()
        self.transformer_to_3057 = Transformer.from_crs("EPSG:4326", "EPSG:3057", always_xy=True)
        self.transformer_to_4326 = Transformer.from_crs("EPSG:3057", "EPSG:4326", always_xy=True)
        self.PENALTY_SCALE = 100
    

    def get_station_score(self, station_coord, w_density=1, w_income=1, w_age=1, radius=400, EPSG_4326=True):
        """
        Calculate the score for a station based on the given weights and radius.

        Parameters:
        ----------
        station_coord : tuple
            Coordinates of the station in EPSG:4326 format (north, east) = (lat, long).
        w_density : float
            Weight for the density factor.
        w_income : float
            Weight for the income factor.
        w_age : float
            Weight for the age factor.
        radius : float
            The radius (in meters) around the station to consider.
        EPSG_4326 : bool
            if a true, station coord of format EPSG:4326 is expected, else EPSG:3057

        Returns:
        -------
        dict
            Dictionary that contains total score and subscores
            {"total_score": total_score, "income_score": income_score, "age_score": age_score, "density_score": density_score}
        """
        if EPSG_4326:
            station_coord = self.__convert_to_3057(station_coord)
        cov = get_station_coverage(self.smsv_list, station_coord, radius)
        scores = score_current(station_coord, self.df, cov, w_density, w_income, w_age)
        return scores

    def __convert_to_3057(self, station_coord):
        """
        Convert coordinates from EPSG:4326 (lon, lat) to EPSG:3057 (x, y).

        Parameters:
        ----------
        station_coord : tuple
            Coordinates in EPSG:4326 format (lon, lat).

        Returns:
        -------
        tuple
            Coordinates in EPSG:3057 format (x, y).
        """
        return self.transformer_to_3057.transform(*station_coord)

    def __convert_to_4326(self, station_coord):
        """
        Convert coordinates from EPSG:3057 (x, y) to EPSG:4326 (lon, lat).

        Parameters:
        ----------
        station_coord : tuple
            Coordinates in EPSG:3057 format (x, y).

        Returns:
        -------
        tuple
            Coordinates in EPSG:4326 format (lon, lat).
        """
        return self.transformer_to_4326.transform(*station_coord)

    def line_score(self, stations_coordinates: List[Tuple[Float]], w_density=1, w_income=1, w_age=1, radius=400, EPSG_4326=True):
        """
        Calculate the total score for a transit line based on station locations and individual station scores.

        Parameters:
            stations_coordinates (List[Tuple[float]]): A list of station coordinates as (x, y) tuples.
            w_density (float): Weight for population density in scoring (default is 1).
            w_income (float): Weight for income level in scoring (default is 1).
            w_age (float): Weight for age distribution in scoring (default is 1).
            radius (float): Radius of influence for each station (default is 400 meters).
            EPSG_4326 (bool): If True, the coordinates are in EPSG:4326 and will be converted to EPSG:3057 (default is True).

        Returns:
            dict: A dictionary containing:
                - "individual_scores": Scores for each station before applying penalties.
                - "adjusted_scores": Scores for each station after applying penalties for proximity.
                - "overlap_factors": (Optional, if calc_score_line returns it) Degree of overlap between stations.
                - "total_individual_score": The aggregated score of all stations before penalties.
                - "final_score": The total line score after penalties.
        """
        coords_formatted = []
        coords_scores = []
        for coord in stations_coordinates:
            coord_formatted = self.__convert_to_3057(coord) if EPSG_4326 else coord
            coords_formatted.append(coord_formatted)
            coords_scores.append(self.get_station_score(coord_formatted, w_density, w_income, w_age, radius, EPSG_4326=False))
        result = calc_score_line(coords_formatted, coords_scores, w_density, w_income, w_age, radius)
        return result




# dummy_coord1 = (356250.0, 408250.0)  # EPSG:3057 coordinates
# dummy_coord2 = (-21.910388, 64.144947)  # EPSG:4326 coordinates
# dummy_coord3 = (358374.26032876654, 407938.72289760906) # ISN93/Lambert

# lane = [
#     (-2427839.8601560914, 9371544.591676729),
#     (-2431634.4660833703, 9372554.640815599),
#     (-2434649.232041, 9374913.131190613),
#     (-2436330.9382214467, 9375856.527340621),
#     (-2438828.8871577685, 9378030.440208027),
#     (-2439956.860815385, 9378055.050542375),
#     (-2442307.1477456186, 9379548.07749282),
#     (-2441441.6843210473, 9380909.849326741),
#     (-2441400.6670971345, 9384909.028658295),
#     (-2441962.6030647475, 9385105.911333079),
#     (-2443122.365070897, 9385984.705355423),
#     (-2441898.000937084, 9387355.706064725),
#     (-2423704.8112703268, 9387223.425517604),
#     (-2425747.4690212114, 9387959.684686847),
#     (-2433768.8998727645, 9383004.29132282),
#     (-2429552.329254474, 9382532.593247818),
#     (-2436008.4402984325, 9385453.019590447),
#     (-2438288.9979480137, 9386006.752113278),
#     (-2439449.7853847607, 9386252.855456758)]

# transformer = Transformer.from_crs("EPSG:3857", "EPSG:3057", always_xy=True)
# for i in range(len(lane)):
#     lane[i] = transformer.transform(*lane[i])


# backend = Data_provider()
# # print("dummy_coord1: ", backend.get_station_score(dummy_coord1, EPSG_4326=False))
# # print("dummy_coord2: ", backend.get_station_score(dummy_coord2))
# # print("dummy_coord3: ", backend.get_station_score(dummy_coord3, EPSG_4326=False))
# print("Line score", backend.line_score(lane, EPSG_4326=False))
