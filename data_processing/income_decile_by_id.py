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
    
def get_income_decile(years, smsv_ids, filename):
    income_deciles = {smsv_id: {year: {} for year in years} for smsv_id in smsv_ids} # Initialize output dict
    csv_data = open_file(filename)

    if csv_data: # Check if data is empty
        header = csv_data[0] # Extract header for column indexing
        smsv_id_index = header.index('smasvaedi')
        decile_index = header.index('tekjutiund')
        population_index = header.index('fjoldi')
        year_index = header.index('ar')

        for row in csv_data[1:]: # Skip header
            row_smsv_id = row[smsv_id_index]
            row_year = int(row[year_index])
            if row_smsv_id in smsv_ids and row_year in years:
                decile_group = row[decile_index]
                population = int(row[population_index])

                if row_smsv_id not in income_deciles:
                    income_deciles[row_smsv_id] = {}

                if row_year not in income_deciles[row_smsv_id]:
                    income_deciles[row_smsv_id][row_year] = {}

                if decile_group not in income_deciles[row_smsv_id][row_year]:
                    income_deciles[row_smsv_id][row_year][int(decile_group)] = population
    return income_deciles

if __name__ == '__main__':
    # Example usage:
    filename = os.path.join('given_data', 'tekjutiundir.csv')
    smsv_ids_to_find = ['0103', '2903', '4002']  # List of desired smsv_ids
    years = [2017, 2024]
    income_decile = get_income_decile(years, smsv_ids_to_find, filename)

    for smsv_id, deciles in  income_decile.items():
        print(f"Income Deciles for SMSV ID: {smsv_id}")
        for decile, population in deciles.items():
            print(f" - {decile}: {population}")
        print()