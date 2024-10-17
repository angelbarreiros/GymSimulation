import json
from datetime import datetime

def process_json_file(input_file):
    # Read the input JSON file
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Process each entry
    for entry in data:
        # Parse the date to get the weekday
        date_obj = datetime.strptime(entry['dia'], '%Y-%m-%d')
        weekday = date_obj.isoweekday()  # This gives 1 for Monday, 7 for Sunday
        
        # Get the hour
        hour = entry['hora']
        
        # Create filename in the format weekday_hour:00.json
        filename = f"{weekday}_{hour}.json"
        file_path = f"data/formated_data/zones/{filename}"
        
        try:
            # Try to read existing file
            with open(file_path, 'r') as f:
                existing_data = json.load(f)
        except FileNotFoundError:
            existing_data = {}
        
        # Update the data with a single "entradas" object
        existing_data["entradas"] = {
            "entrada_total": entry["total_entrada"],
            "entrada_validas": entry["entrada"],
            "entrada_menores": entry["menores-entrada"],
            "entrada_errores": entry["error-entrada"],
            "entrada_duplicados": entry["duplicados-entrada"],
            "salida_total": entry["total_salida"],
            "salida_validas": entry["salida"],
            "salida_menores": entry["menores-salida"],
            "salida_errores": entry["error-salida"],
            "salida_duplicados": entry["duplicados-salida"]
        }
        
        # Write the updated data back to the file
        with open(file_path, 'w') as f:
            json.dump(existing_data, f, indent=4)
        
        print(f"Processed and saved: {filename}")

if __name__ == "__main__":
    input_file = "data/excel/entradas_total.json"
    process_json_file(input_file)