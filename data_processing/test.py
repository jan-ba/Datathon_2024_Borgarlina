from get_smallAreaInfo import get_smallAreas
from point_scoring import score_current
from get_station_coverage import get_station_coverage
from aggregate_data import get_feature_df
import os
import pandas as pd


smsv_list = get_smallAreas()
df = get_feature_df()


station_coords = (356250.0, 408250.0)  # EPSG:3057 coordinates
w_density = 1
w_income = 1
w_age = 1
radius = 400

if __name__ == '__main__':

    cov = get_station_coverage(smsv_list, station_coords, radius)
    # print(cov)
    final_score = score_current(station_coords, df, cov, w_density, w_income, w_age)

    print(f'final score: {final_score}')
