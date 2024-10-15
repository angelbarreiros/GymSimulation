import re
import json
from datetime import datetime, timedelta

def process_data(input_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    first_line = lines[0].strip()  # Get the first line for the filename
    
    # Extract the day of the week from the first line
    day_of_week = first_line.split()[0].upper()
    
    if day_of_week in ['SABADO', 'DOMINGO']:
        current_hour = datetime(2024, 1, 1, 9, 0)  # Start at 9am
        end_hour = datetime(2024, 1, 1, 20, 0)  # End at 8pm
    else:
        current_hour = datetime(2024, 1, 1, 7, 0)  # Start at 7am
        end_hour = datetime(2024, 1, 1, 22, 0)  # End at 10pm
    
    i = 2
    while current_hour <= end_hour:
        data = []
        hour_end = current_hour + timedelta(hours=1)
        
        while i < len(lines) and len(data) < 14:
            zona_line = lines[i].strip()
            if not zona_line:
                i += 1
                continue
            
            if i + 1 < len(lines):
                data_line = lines[i+1].strip().split('\t')
                
                if len(data_line) >= 3:
                    percentage = re.sub(r'[^0-9]', '', data_line[0])
                    percentage = int(percentage) if percentage else 0
                    
                    aforo = int(data_line[1]) if data_line[1].isdigit() else 0
                    oc_prom = int(data_line[2]) if data_line[2].isdigit() else 0
                    
                    record = {
                        "zona": zona_line,
                        "porcentage_ocupación": str(percentage),
                        "aforo": aforo,
                        "oc.prom": oc_prom
                    }
                    data.append(record)
            
            i += 2
        
        write_json(data, current_hour, first_line)
        current_hour = hour_end
    
    print(f"Processed all data from {input_file}")

def write_json(data, hour, first_line):
    # Create a filename-safe version of the first line
    safe_first_line = re.sub(r'[^\w\-_\. ]', '_', first_line)
    safe_first_line = safe_first_line.replace(' ', '_')
    
    output_file = f'data/aforo-x-horas/{safe_first_line}_{hour.strftime("%H")}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Data has been processed and written to {output_file}")
    print(f"Number of records processed: {len(data)}")

def get_day_name(date_str):
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    days_in_spanish = ["LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES", "SABADO", "DOMINGO"]
    return days_in_spanish[date_obj.weekday()]

def clean_classes_json(input_file):
    with open(input_file) as f:
        data = json.load(f)
    cleaned_data = [event for event in data if "VIRTUAL" not in event["activity"]]
    
    with open(input_file, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
    
    print(f"Cleaned data has been written back to {input_file}")

if __name__ == "__main__":
    # Usage
    input_file = '/home/mateo/projects/gym/GymSimulation/data/clases_7am.json'  # Replace with your input file name
    process_data(input_file)