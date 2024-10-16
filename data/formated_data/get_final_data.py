import get_classes_data as gc
import get_insout_data as io
import get_zones_data as gz



if __name__ == "__main__":
    gz.excel_to_json("/home/angel/startup/GymSimulation/data/excel/zonas-sept-zgz.xlsx")
    gc.transform_json("/home/angel/startup/GymSimulation/data/excel/clases_2024-08-05.json")
    io.get_data("/home/angel/startup/GymSimulation/data/excel/entradas_2024-08-05.json")