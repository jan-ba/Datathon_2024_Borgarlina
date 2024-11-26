import csv
import os 
from typing import List, Tuple
import math

from shapely.validation import make_valid

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
    total_income_score = 0
    total_density_score = 0
    total_age_score = 0
    aggregated_age_distribution = {}
    aggregated_income_distribution = {}
    small_area_contributions = {}

    for smsv in cov_smsv:
        smsv_info = df_features[df_features["smallAreaId"] == smsv["id"]]

        # Get age distribution for the year 2024
        age_dist = smsv_info["age_distribution"].iloc[0].get(2024, {})  # only interested in 2024 for current score
        
        # Aggregate proportional age distribution
        for age_group, population in age_dist.items():
            proportion = population * (smsv["small_zone_percentage"]/100)
            if age_group in aggregated_age_distribution:
                aggregated_age_distribution[age_group] += proportion
            else:
                aggregated_age_distribution[age_group] = proportion

        # Get income distribution for the year 2024
        income_dist = smsv_info["income_distribution_per_year"].iloc[0].get(2024, {})  # only interested in 2024 for current score

        # Aggregate proportional income distribution
        for income_group, population in income_dist.items():
            proportion = population * (smsv["small_zone_percentage"] / 100)
            if income_group in aggregated_income_distribution:
                aggregated_income_distribution[income_group] += proportion
            else:
                aggregated_income_distribution[income_group] = proportion

        # Calculate density score
        density_contribution = smsv_info["density"].iloc[0] * w_density * smsv["small_zone_percentage"] * 200

        # Calculate age score
        age_contribution = get_age_score(age_dist) * w_age * smsv["small_zone_percentage"]

        # Calculate income score
        income_contribution = get_income_score(income_dist) * w_income * smsv["small_zone_percentage"]

        # Total contribution for this small area
        area_score = density_contribution + age_contribution + income_contribution
        total_score += area_score
        
        # Total age score
        total_age_score += age_contribution
        # Total income score
        total_income_score += income_contribution
        # Total density score 
        total_density_score += density_contribution

        # Store contribution data for this small area
        small_area_contributions[smsv["id"]] = {
            "density_score": density_contribution,
            "age_score": age_contribution,
            "income_score": income_contribution,
            "total_score": area_score,
        }

    # # Calculate age score
    # age_score = get_age_score(aggregated_age_distribution) * w_age
    # total_score += age_score

    # # Calculate income score
    # income_score = get_income_score(aggregated_income_distribution) * w_income
    # total_score += income_score

    return {"total_score": total_score, 
            "income_score": total_income_score, 
            "age_score": total_age_score, 
            "density_score": total_density_score, 
            "age_data": aggregated_age_distribution, 
            "income_data": aggregated_income_distribution,
            "small_area_contributions": small_area_contributions,
    }

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

def calculate_distance(coord1, coord2):
        """Calculate Euclidean distance between two coordinates in EPSG:3057 format."""
        x1, y1 = coord1
        x2, y2 = coord2
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def calc_score_line(stations_coordinates: List[Tuple[float]], station_scores: dict[str, list[float]], w_density, w_income, w_age, radius):
    # print("stations_coords1 ", stations_coordinates)
    PENALTY_SCALE = 1.0
    individual_total_scores = [station["total_score"] for station in station_scores]
    overlap_factors = [0] * len(stations_coordinates)  # Initialize overlap factors for each station
    total_penalty = 0

    # Aggregate individual scores
    total_individual_score = sum(individual_total_scores) / len(individual_total_scores) if individual_total_scores else 0

    # Calculate overlap factors
    for i, coord1 in enumerate(stations_coordinates):
        for j, coord2 in enumerate(stations_coordinates):
            if i != j:  # Avoid self-comparison
                distance = calculate_distance(coord1, coord2)
                if distance < radius:
                    # Calculate overlap fraction (inverse of distance within the radius)
                    overlap_factor = (radius - distance) / radius  # Normalize overlap to [0, 1]
                    overlap_factors[i] += overlap_factor
                    overlap_factors[j] += overlap_factor

    # Scale down individual scores based on overlap factors
    adjusted_scores = [
        max(0, score * (1 - PENALTY_SCALE * min(1, overlap_factors[i])))  # Cap scaling at 100%
        for i, score in enumerate(individual_total_scores)
    ]

    # Final aggregated score
    final_score = sum(adjusted_scores) / len(adjusted_scores) if adjusted_scores else 0

    # Return detailed results
    result = {
        "individual_scores": individual_total_scores,
        "adjusted_scores": adjusted_scores,
        "overlap_factors": overlap_factors,
        "total_individual_score": total_individual_score,
        "final_score": final_score
    }
    return result

