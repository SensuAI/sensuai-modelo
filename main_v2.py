import numpy as np
from ultralytics import YOLO
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
import cv2
from util_v2 import get_car, read_license_plate, write_csv
from sort.sort import Sort

mot_tracker = Sort()
results = {}

#load models
coco_model = YOLO('yolov8n.pt')
license_plate_detector = YOLO('./license_plate_detector_final.pt')

#load video
cap = cv2.VideoCapture("./sample.mp4")
#vehicles = [2,3,5,7]

#read frames
frame_num = -1
ret = True

while ret:
    frame_num += 1
    ret, frame = cap.read()
    
    if ret: 
        results[frame_num] = {}
        # detect veihicles
        detections = coco_model(frame)[0]
        detections_ = []
        vehicles = []
        for detection in detections.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = detection
            
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

        # track vehicles 
        track_ids = mot_tracker.update(np.asarray(detections_))
        # detect license plates
        license_plates = license_plate_detector(frame)[0]
        for license_plate in license_plates.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = license_plate
            
            print(get_car(license_plate,track_ids,vehicles))
            # assign license plate to car
            xcar1, ycar1, xcar2, ycar2, car_id, vehicle_type = get_car(license_plate,track_ids,vehicles)
            
            # crop license plate
            license_plate_crop = frame[int(y1):int(y2),int(x1):int(x2),:]
            
            # process license plate
            license_plate_color_gey = cv2.cvtColor(license_plate_crop,cv2.COLOR_BGR2GRAY)
            _, license_plate_crop_thresh = cv2.threshold(license_plate_color_gey, 64, 255, cv2.THRESH_BINARY_INV)
            
            
            # read license plate number
            license_plate_text, license_plate_text_score = read_license_plate(license_plate_crop_thresh)
            
            if license_plate_text is not None:
                results[frame_num][car_id] = {"car":{"bbox":[xcar1,ycar1,xcar2,ycar2]},
                                              "license_plate":{"bbox":[x1,y1,x2,y2],
                                                               "text":license_plate_text,
                                                               "bbox_score":score,
                                                               "text_score":license_plate_text_score,
                                                               "vehicle_type":vehicle_type}}
# write results 
write_csv(results, "./test_final.csv")
