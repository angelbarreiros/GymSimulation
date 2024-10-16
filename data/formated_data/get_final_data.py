import get_classes_data as gc
import get_insout_data as io
import get_zones_data as gz
import os


if __name__ == "__main__":
    if not os.path.exists('data/formated_data/zones'):
        os.mkdir('data/formated_data/zones')
    gz.excel_to_json("data/excel/zonas-sept-zgz.xlsx")
    try:
        gc.transform_json("data/excel/clases_total.json")
        io.process_json_file("data/excel/entradas_total.json")
        
    except Exception :
        pass
    
        
    
    