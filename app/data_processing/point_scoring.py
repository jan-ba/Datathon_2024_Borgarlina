import csv
import os 


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

    # TODO: take into account fjoldi starfandi, if there are more people who work than live => many people need to get there, also works the other way around.
    total_score = 0
    income_score = 0
    density_score = 0
    age_score = 0
    for smsv in cov_smsv:
        

        smsv_info = df_features[df_features["smallAreaId"] == smsv["id"]]

        age_dist = smsv_info["age_distribution"].iloc[0].get(2024, {})  # only interested in 2024 for current score
        # print(data_2024)
        age_score = get_age_score(age_dist) * w_age

        income_dist = smsv_info["income_distribution_per_year"].iloc[0].get(2024, {})  # only interested in 2024 for current score
        # print(data_2024)
        income_score = get_income_score(income_dist) * w_income

        density_score = smsv_info["density"].iloc[0] * w_density
        total_score += (age_score + income_score + density_score) * smsv["coverage_percentage"] # TODO: Area of the cricle * percent covered / total area of the small area
    return {"total_score": total_score, "income_score": income_score, "age_score": age_score, "density_score": density_score, "age_data": age_dist}

def get_age_score(age_distribution):
    """
    Calculate a score based on age distribution.

    Parameters:
    ----------
    age_distribution : dict
        A dictionary with age brackets as keys and population as values.

    Returns:
    -------
    float
        Normalized age-based score.
    """
    # Define weights for age groups
    age_weights = {
    "0-4 ára": 0.3,  # Very young children unlikely to use public transport independently
    "5-9 ára": 0.7,  # Primary school pupils
    "10-14 ára": 1.0,  # Secondary school pupils more likely to use public transport
    "15-19 ára": 1.5,  # Teenagers, often students or apprentices, heavy reliance on buses
    "20-24 ára": 1.5,  # Students, apprentices, or young professionals
    "25-29 ára": 1.2,  # Young professionals, still a common demographic for bus users
    "30-34 ára": 1.0,  # Starting to decline as personal vehicle ownership increases
    "35-39 ára": 0.9,
    "40-44 ára": 0.8,
    "45-49 ára": 0.7,
    "50-54 ára": 0.6,
    "55-59 ára": 0.6,
    "60-64 ára": 0.8,  # Approaching retirement, may rely more on buses
    "65-69 ára": 1.2,  # Pensioners starting to rely on public transport
    "70-74 ára": 1.3,  # Active pensioners, heavy bus users
    "75-79 ára": 1.3,
    "80-84 ára": 1.1,  # Decline due to physical limitations
    "85-89 ára": 0.6,  # Very old, fewer likely to use buses
    "90 ára og eldri": 0.2,  # Most unlikely to use public transport independently
}

    # Calculate the weighted sum of the age distribution
    weighted_sum = sum(age_distribution.get(age, 0) * weight for age, weight in age_weights.items())

    # Normalize the score by the total population
    total_population = sum(age_distribution.values())
    if total_population == 0:
        return 0

    return weighted_sum / total_population


def get_income_score(income_distribution):
    """
    Calculate a score based on income distribution.

    Parameters:
    ----------
    income_distribution : dict
        A dictionary with income classes as keys and population as values.

    Returns:
    -------
    float
        Normalized income-based score.
    """
    # Define weights for income classes (1 = highest income, 10 = lowest)
    income_weights = {
        1: 0.5,  # Higher-income groups less dependent on public transport
        2: 0.6,
        3: 0.7,
        4: 0.8,
        5: 1.0,
        6: 1.1,
        7: 1.2,
        8: 1.3,
        9: 1.4,
        10: 1.5,  # Lower-income groups more dependent on public transport
    }

    # Calculate the weighted sum of the income distribution
    weighted_sum = sum(income_distribution.get(income_class, 0) * weight for income_class, weight in income_weights.items())

    # Normalize the score by the total population
    total_population = sum(income_distribution.values())
    if total_population == 0:
        return 0

    return weighted_sum / total_population


if __name__ == '__main__':
    filename = os.path.join('output.csv')
    data = open_file(filename)