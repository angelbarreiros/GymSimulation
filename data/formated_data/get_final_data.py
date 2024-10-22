import get_classes_data as gc
import get_zones_data as gz
import os


if __name__ == "__main__":
    if not os.path.exists('data/formated_data/zones'):
        os.mkdir('data/formated_data/zones')
    gz.getZonesData()
    gc.getClassData()


        
    
    