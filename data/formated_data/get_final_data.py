import get_classes_data as gc
import get_insout_data as io
import get_zones_data as gz



if __name__ == "__main__":
    gz.excel_to_json("data/excel/zonas-sept-zgz.xlsx")
    try:
        gc.transform_json("data/excel/clases_2024-08-05.json")
        
    except Exception :
        pass
    io.process_json_file("data/excel/entradas_2024-08-05.json")
        
    
    