import csv

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
    
def get_age_distribution(years, smsv_ids, filename):
    age_distributions = {smsv_id: {year: {} for year in years} for smsv_id in smsv_ids} # Initialize output dict
    csv_data = open_file(filename)

    if csv_data: # Check if data is not empty 
        header = csv_data[0] # Extract header for column indexing
        smsv_id_index = header.index('smasvaedi')
        agegroup_index = header.index('aldursflokkur')
        population_index = header.index('fjoldi')
        year_index = header.index('ar')

        for row in csv_data[1:]: # Skip header
            row_smsv_id = row[smsv_id_index]
            row_year = int(row[year_index])
            if row_smsv_id in smsv_ids and row_year in years:
                age_group = row[agegroup_index]
                population = int(row[population_index])

                if row_smsv_id not in age_distributions:
                    age_distributions[row_smsv_id] = {}
                if row_year not in age_distributions[row_smsv_id]:
                    age_distributions[row_smsv_id][row_year] = {}
                
                if age_group not in age_distributions[row_smsv_id][row_year]:
                    age_distributions[row_smsv_id][row_year][age_group] = population
                else:
                    age_distributions[row_smsv_id][row_year][age_group] += population
    return age_distributions

if __name__ == '__main__':
    # Example usage:
    filename = './given_data/ibuafjoldi.csv'
    smsv_ids_to_find = ['0103', '2903', '4002']  # List of desired smsv_ids
    age_dist = get_age_distribution([2017, 2024],smsv_ids_to_find, filename)

    for smsv_id, distributions in age_dist.items():
        print(f"Age Distribution for SMSV ID: {smsv_id}")
        for age_group, populations in distributions.items():
            print(f"  - {age_group}: {populations}")
        print()  # Empty line for better readability