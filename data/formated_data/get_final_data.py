import get_classes_data as gc
import get_insout_data as io
import get_zones_data as gz
import os



if __name__ == "__main__":
    if not os.path.exists("data/formated_data/zones"):
        os.mkdir("data/formated_data/zones")
    gz.excel_to_json("data/excel/zonas-sept-zgz.xlsx")
    gc.transform_json("data/excel/clases_2024-08-05.json")
    io.get_data("data/excel/entradas_2024-08-05.json")
    