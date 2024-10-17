import json
import json

# Load the JSON data from the file
def get_data(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)


    data_by_hora = {}
    for entry in data:
        hora = entry['hora']
        if hora not in data_by_hora:
            data_by_hora[hora] = []
        data_by_hora[hora].append(entry)

    
    for hora, entries in data_by_hora.items():
        formatedFilename = f"1_{hora}.json"
        with open("data/formated_data/zones/"+formatedFilename, 'r') as f:
            existing_data = json.load(f)
        python_dict = json.loads(existing_data)

        python_dict["entradas"]=entries
        updated_json = json.dumps(python_dict, indent=4)
        
        with open("data/formated_data/zones/"+formatedFilename, 'w') as f:
            json.dump(updated_json, f, indent=4)



if __name__ == "__main__":
    get_data("data/excel/entradas_2024-08-05.json")
    with open("data/formated_data/zones/"+"1_07.json", 'w') as f:
            data = json.load(f)
    print(data)    