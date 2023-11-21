import string
import easyocr
import cv2
import re

# Initialize the OCR reader
reader = easyocr.Reader(['en'], gpu=False)

def write_csv(results, output_path):
    """
    Write the results to a CSV file.

    Args:
        results (dict): Dictionary containing the results.
        output_path (str): Path to the output CSV file.
    """
    with open(output_path, 'w') as f:
        f.write('{},{},{},{},{},{},{},{}\n'.format('frame_nmr','car_id','vehicle_type','car_bbox',
                                                'license_plate_bbox','license_plate_bbox_score','license_number',
                                                'license_number_score'))

        for frame_nmr in results.keys():
            for car_id in results[frame_nmr].keys():
                print(results[frame_nmr][car_id])
                if 'car' in results[frame_nmr][car_id].keys() and \
                   'license_plate' in results[frame_nmr][car_id].keys() and \
                   'text' in results[frame_nmr][car_id]['license_plate'].keys():
                    f.write('{},{},{},{},{},{},{},{}\n'.format(frame_nmr,
                                                            car_id,
                                                            results[frame_nmr][car_id]['license_plate']["vehicle_type"],
                                                            '[{} {} {} {}]'.format(
                                                                results[frame_nmr][car_id]['car']['bbox'][0],
                                                                results[frame_nmr][car_id]['car']['bbox'][1],
                                                                results[frame_nmr][car_id]['car']['bbox'][2],
                                                                results[frame_nmr][car_id]['car']['bbox'][3]),
                                                            '[{} {} {} {}]'.format(
                                                                results[frame_nmr][car_id]['license_plate']['bbox'][0],
                                                                results[frame_nmr][car_id]['license_plate']['bbox'][1],
                                                                results[frame_nmr][car_id]['license_plate']['bbox'][2],
                                                                results[frame_nmr][car_id]['license_plate']['bbox'][3]),
                                                            results[frame_nmr][car_id]['license_plate']['bbox_score'],
                                                            results[frame_nmr][car_id]['license_plate']['text'],
                                                            results[frame_nmr][car_id]['license_plate']['text_score'])
                            )
        f.close()


def read_license_plate(license_plate_crop):
    """
    Read the license plate text from the given cropped image.

    Args:
        license_plate_crop (PIL.Image.Image): Cropped image containing the license plate.

    Returns:
        tuple: Tuple containing the formatted license plate text and its confidence score.
    """
    
    box_size = 100
    
    license_plate_resized = cv2.resize(license_plate_crop, (260, 130))

    detections = reader.readtext(license_plate_resized, allowlist="ABCDEFGHJKLMNPRSTUVWXYZ0123456789-", min_size=box_size)

    # print(detections)
    
    while box_size >= 10:
        
        if len(detections) == 0: 
            box_size -= 10
            detections = reader.readtext(license_plate_resized, allowlist="ABCDEFGHJKLMNPRSTUVWXYZ0123456789-",min_size=box_size)
        
        if len(detections) >= 1:
            # print([txt[1] for txt in detections])
            break
        
    for detection in detections:
        bbox, text, score = detection
        
        if ("-" in text) and (len(text)>=7) and (len(text)<=10) and (len(re.findall(r"[0-9]{4}[-][0-9]{4}", text)) == 0):
            text = text.upper().replace(' ', '')
            return text,score
        else:
            continue
        
    return None, None

def get_car(license_plate, vehicle_track_ids, vehicle_list):
    """
    Retrieve the vehicle coordinates and ID based on the license plate coordinates.

    Args:
        license_plate (tuple): Tuple containing the coordinates of the license plate (x1, y1, x2, y2, score, class_id).
        vehicle_track_ids (list): List of vehicle track IDs and their corresponding coordinates.

    Returns:
        tuple: Tuple containing the vehicle coordinates (x1, y1, x2, y2) and ID.
    """
    x1, y1, x2, y2, score, class_id = license_plate

    foundIt = False
    for j in range(len(vehicle_track_ids)):
        xcar1, ycar1, xcar2, ycar2, car_id = vehicle_track_ids[j]

        if x1 > xcar1 and y1 > ycar1 and x2 < xcar2 and y2 < ycar2:
            car_indx = j
            foundIt = True
            break

    if foundIt:
        xcar1, ycar1, xcar2, ycar2, car_id = vehicle_track_ids[car_indx]
        return (xcar1, ycar1, xcar2, ycar2, car_id, vehicle_list[car_indx])

    return -1, -1, -1, -1, -1, -1