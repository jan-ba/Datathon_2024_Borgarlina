from typing import List, Tuple

from traitlets import Float
from data_processing.get_smallAreaInfo import get_smallAreas
from data_processing.point_scoring import score_current
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

    def total_score(self, stations_coordinates: List[Tuple[Float]], w_density=1, w_income=1, w_age=1, radius=400, EPSG_4326=True):
        scores = []
        for coord in stations_coordinates:
            score = self.get_station_scores(coord) - get_penalty()



if __name__ == '__main__':
    dummy_coord1 = (356250.0, 408250.0)  # EPSG:3057 coordinates
    dummy_coord2 = (-21.910388, 64.144947)  # EPSG:4326 coordinates
    dummy_coord3 = (358374.26032876654, 407938.72289760906) # ISN93/Lambert
    # dummy_coord3 = 
    backend = Data_provider()
    print("dummy_coord1: ", backend.get_station_score(dummy_coord1, EPSG_4326=False))
    print("dummy_coord2: ", backend.get_station_score(dummy_coord2))
    print("dummy_coord3: ", backend.get_station_score(dummy_coord3, EPSG_4326=False))


