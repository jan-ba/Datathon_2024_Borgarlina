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
    
def get_income_decile(years, smsv_ids, filename):
    income_deciles = {smsv_ids: {year: {} for year in years} for smsv_id in smsv_ids} # Initialize output dict
    csv_data = open_file(filename)

    if csv_data(): # Check if data is empty
        header = csv_data[0] # Extract header for column indexing
        smsv_id_index = header.index('smasvaedi')
        decile_index = header.index('tekjutiund')
           
    

if __name__ == '__main__':
    # Example usage:
    filename = './given_data/ibuafjoldi.csv'
    smsv_ids_to_find = ['0103', '2903', '4002']  # List of desired smsv_ids