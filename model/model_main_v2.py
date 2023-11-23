#Importamos las librerías necesarias para correr el main
import numpy as np
from ultralytics import YOLO
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
import cv2
from model.util_v2 import get_car, read_license_plate, write_csv
from model.sort.sort import Sort
from datetime import datetime

def car_detection(cut_time: str, verbose_mode: bool, test_mode: bool):
    print("-----------------------Iniciando el reconocimiento de vehiculos-----------------------")
    #Creamos los objetos para rastear la ubicación de los vehículos y guardar todos los resultados
    mot_tracker = Sort()
    results = {}

    #Cargamos los modelos previamente guardados
    coco_model = YOLO('yolov8n.pt')
    license_plate_detector = YOLO('./model/license_plate_detector_final.pt')

    #Cargamos el video o cámara en vivo
    if test_mode == True:
        cap = cv2.VideoCapture("./model/testing/PlatesDataSet.mp4")
    else:
        cap = cv2.VideoCapture(0)

    #Creamos variables que nos servirán para iterar 
    frame_num = -1
    ret = True
    general_detections = []

    #Iteramos infinitamente siempre y cuando el programa esté recibiendo información de la cámara
    while ret:
        
        #Hacemos el timestamp por cada frame
        frame_num += 1
        now = datetime.now()
        ret, frame = cap.read()
        
        #Agregamos condición para que el código corra cada 15 frames (~4 veces por segundo)
        if ret and (frame_num % 15 == 0): 
            #Guardamos los resultados con la clave de la hora
            results[now] = {}
            #Utilizamos el coco_model para realizar todas las detecciones disponibles
            detections = coco_model(frame,verbose=verbose_mode)[0]
            detections_ = []
            vehicles = []
            
            #Extraemos la información de cada detección 
            for detection in detections.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = detection
                
                #Guardamos aquellas detecciones que corresponded a camiones, trailers, autos y motocicletas
                if class_id == 2:
                    detections_.append([x1, y1, x2, y2, score])
                    vehicles.append("car")
                elif class_id == 3:
                    detections_.append([x1, y1, x2, y2, score])
                    vehicles.append("motorcycle")
                elif class_id == 5:
                    detections_.append([x1, y1, x2, y2, score])
                    vehicles.append("bus")
                elif class_id == 7:
                    detections_.append([x1, y1, x2, y2, score])
                    vehicles.append("truck")
                else:
                    continue 

            #Realizamos el rastreo de los vehículos para extraer las ubicaciones correctas
            try:
                track_ids = mot_tracker.update(np.asarray(detections_))
            except:
                continue
            
            #Utilizamos nuestro modelo para detección de placas
            license_plates = license_plate_detector(frame,verbose=False)[0]
            
            #Extraemos la data de cada una de las placas registradas y le asignamos un vehículo que servirá para la limpieza de datos
            for license_plate in license_plates.boxes.data.tolist():

                x1, y1, x2, y2, score, class_id = license_plate
                
                # Asignamos la placa a el vehículo. 
                xcar1, ycar1, xcar2, ycar2, car_id, vehicle_type = get_car(license_plate,track_ids,vehicles)
                
                # crop license plate
                license_plate_crop = frame[int(y1):int(y2),int(x1):int(x2),:]
                
                #Pasamos la placa a escala de grises para facilitar la detección
                license_plate_color_gey = cv2.cvtColor(license_plate_crop,cv2.COLOR_BGR2GRAY)
                
                #Leemos la placa junto con el puntaje de confianza
                license_plate_text, license_plate_text_score = read_license_plate(license_plate_color_gey)
                
                
                #En caso de detectar una placa, guardamos los resultados en el diccionario 
                if license_plate_text is not None:
                    #Revisamos si la placa contiene una M, H, W, G o 6 y guardamos la imágen para realizar verificación manual
                    chars = ['M', 'W', 'H', 'G', '6']
                    if any(substring in license_plate_text for substring in chars):
                        #Guardamos la imágen para validación manual
                        cv2.imwrite('./images_output/{}_{}.jpg'.format(frame_num, car_id), license_plate_color_gey)
                    else:
                        continue
                    results[now][car_id] = {"car":{"bbox":[xcar1,ycar1,xcar2,ycar2]},
                                                "license_plate":{"bbox":[x1,y1,x2,y2],
                                                                "text":license_plate_text,
                                                                "bbox_score":score,
                                                                "text_score":license_plate_text_score,
                                                                "vehicle_type":vehicle_type}}
            
            #Revisamos si el modelo está corriendo a las 2AM y, en caso de que sí, guardamos los resultados en un csv
            if datetime.now().strftime('%H:%M') == cut_time:
                print("-----------------------DATOS DEL DIA REGISTRADOS-----------------------")
                write_csv(results, "./model/rawdata/raw_data_{}.csv".format(datetime.now().strftime("%Y-%m-%d")))
                results = {}
                
    #En caso de que la cámara se detenga guardamos todos los resultados del día
    write_csv(results, "./model/rawdata/raw_data_{}.csv".format(datetime.now().strftime("%Y-%m-%d")))