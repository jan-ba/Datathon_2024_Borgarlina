import csv
from age_distribution_by_id import get_age_distribution

# Small area id: id of the small area
# Density: current density of the small area
# Income distribution: the distribution of income in the small area per year (dictionary, keys: years, values: income distribution [buckets])
# Age distribution: distibution of age in the small area (age buckets of 5 years starting at 0-4)
# Geometry: the lat and long coordinates for the small area polygon
# Projected dwellings: 
columns = ["smallAreaId", "density", "income_distribution_per_year", "age_distribution", "geometry", "projected_dwellings"]

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
    

