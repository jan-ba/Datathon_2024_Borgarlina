import csv
import os 


def open_file(filename):
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            data = list(csv_reader)
            return data
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    

def score_current(station_coord, df_features, cov_smsv, w_density, w_income, w_age) -> float:
    """
    Calculate a score for a station based on density, income, and age factors.

    Parameters:
    ----------
    station_coord : tuple or list
        Coordinates of the station in EPSG:3057 format (long, lat).
    df_features : pandas.DataFrame
        DataFrame containing small area features, including 'geometry', 'density', 
        'income_distribution_per_year', and 'age_distribution'.
    cov_smsv : list[dict[int, perc. cov]]
        For the given station, this includes id and percentage of the circle
        covered by the respective small area (as specified by the) for every small area
        that is within the radius
    w_density : float
        Weight for the density factor.
    w_income : float
        Weight for the income factor.
    w_age : float
        Weight for the age factor.
    # TODO add weight for traffic around this stop

    Returns:
    -------
    float
        Weighted score for the station location.
    """
    # 1. Get small area ids in range
    # 2. 
    # Score = [for all areas in range((density) * coverage percentage)]
    final_score = 0
    for smsv in cov_smsv:
        

        smsv_info = df_features[df_features["smallAreaId"] == smsv["id"]]

        row_data = smsv_info["age_distribution"].iloc[0]
        data_2024 = row_data.get(2024, {})
        print(data_2024)
        age_score = get_age_score(data_2024) * w_age

        row_data = smsv_info["income_distribution_per_year"].iloc[0]
        data_2024 = row_data.get(2024, {})
        print(data_2024)
        income_score = get_income_score(smsv_info["income_distribution_per_year"]) * w_income

        density_score = smsv_info["density"].iloc[0] * w_density
        final_score += (age_score + income_score + density_score) * smsv["coverage_percentage"]
    return final_score

def get_age_score(smsv_age_dict):
    age_score = 0

    # for age_bracket in age_brackets:
    #     pass
    return age_score

def get_income_score(smsv):
    income_score = 0

    # for age_bracket in age_brackets:
    #     pass
    return income_score


if __name__ == '__main__':
    filename = os.path.join('output.csv')
    data = open_file(filename)