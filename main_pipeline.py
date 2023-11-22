from utils.data_clean import process_csv
import schedule
import time
from datetime import datetime

######################################################### GLOBAL VAIRABLES #########################################################
# input_csv_path = "./model/rawdata/raw_data_2023-11-22.csv"
# input_csv_path = "./raw_data_2023-11-22.csv"
CLEANING = { 
    'path': "./raw_data_2023-11-22.csv", 
    'time': "15:23"
    }

####################################################### END GLOBAL VAIRABLES #########################################################


def getTaskTime():
    current_time = datetime.now()
    print(f"-----------------------La tarea se ejecutó a las {current_time}-----------------------\n")

def cleaning_of_data():
    input_csv_path = CLEANING['path']
    process_csv(input_csv_path)
    print(f"LIMPIEZA DE RAW DATA")
    getTaskTime()


schedule.every().day.at(CLEANING['time']).do(getTaskTime)
schedule.every().day.at(CLEANING['time']).do(cleaning_of_data)

while True:
    schedule.run_pending()

    time.sleep(1)
