from utils.data_clean import process_csv
from model.model_main_v2 import car_detection
from utils.request import sending_plates
from datetime import datetime
import schedule
import time
import threading

######################################################### GLOBAL VARIABLES #########################################################
CAR_MODEL = {
    'cut_time': "01:00",
    'verbose_mode': False,
    'test_mode': True
}

CLEANING = {
    # For the test file
    # 'folder_location': ".",

    # Path where it is stored
    'folder_location': "./model/rawdata",
    'time': "19:50"
}

DATA_SEND = {
    'time': "19:52",
    'verbose': True
}
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
