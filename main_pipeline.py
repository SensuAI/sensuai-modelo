from utils.data_clean import process_csv
from model.model_main_v2 import car_detection
from utils.request import sending_plates
from datetime import datetime
import schedule
import time
import threading
import json


######################################################### GLOBAL VARIABLES #########################################################

# Cargar valores desde config.json
with open('config.json', 'r') as config_file:
    config_data = json.load(config_file)

CAR_MODEL = config_data["CAR_MODEL"]
CLEANING = config_data["CLEANING"]
DATA_SEND = config_data["DATA_SEND"]

####################################################### END GLOBAL VARIABLES #########################################################


def getTaskTime():
    current_time = datetime.now()
    print(f"-----------------------La tarea se ejecutó el: {current_time}-----------------------\n")


def cleaning_of_data():
    input_csv_path = CLEANING['folder_location']
    print(f"-----------------------LIMPIEZA DE RAW DATA-----------------------")
    process_csv(input_csv_path)
    getTaskTime()


def data_send():
    sending_plates(verbose=DATA_SEND['verbose'])
    print(f"-----------------------ENVIO DE DATOS AL BACKEND-----------------------")
    getTaskTime()


if __name__ == '__main__':
    # Thread creation
    car_detection_thread = threading.Thread(target=car_detection,
                                            args=(CAR_MODEL['cut_time'], CAR_MODEL['verbose_mode'], CAR_MODEL['test_mode']))

    car_detection_thread.start()

    schedule.every().day.at(CLEANING['time']).do(getTaskTime)
    schedule.every().day.at(CLEANING['time']).do(cleaning_of_data)
    schedule.every().day.at(DATA_SEND['time']).do(data_send)

    while True:
        schedule.run_pending()
        time.sleep(1)
