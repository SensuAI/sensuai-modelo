import requests
import json
import pandas as pd
from datetime import datetime

def make_get_request(url):
    response = requests.get(url)
    return response

def make_post_request(url, data):
    json_data = json.dumps(data)
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=json_data, headers=headers)
    return response

def print_response(response):
    if response.status_code == 200:
        print("Respuesta exitosa:")
        print(response.text)
    else:
        print(f"Error al hacer la solicitud. Código de estado: {response.status_code}")

def sending_plates(verbose=False):
    BASE_URL = "http://129.146.46.56:8080"
    BRANCH_ID = "653306f3c692c1d2f08b5d99"
    
    # Read the CSV file into a DataFrame
    df = pd.read_csv("./cleandata/clean_data.csv")

    # Solicitud GET
    # getAllBranches = f"{BASE_URL}/branch/getAll"
    # response_get = make_get_request(getAllBranches)
    # print_response(response_get)

    # Solicitud POST para múltiples placas
    for index, row in df.iterrows():
        license_number = row['license_number']
        vehicle_type = row['vehicle_type']
        det_start = int(datetime.strptime(row['det_start'], "%Y-%m-%d %H:%M:%S.%f").timestamp())
        det_end = int(datetime.strptime(row['det_end'], "%Y-%m-%d %H:%M:%S.%f").timestamp())

        data = {
            "branch_id": BRANCH_ID,
            "license_number": license_number,
            "vehicle_type": vehicle_type,
            "frame_nmr_x": det_start,
            "frame_nmr_y": det_end
        }

        endpoint_plate_identified = f"{BASE_URL}/model/plateIdentified"
        response_post = make_post_request(endpoint_plate_identified, data)
        if verbose == True:
            print(f"-----------------------Solicitud POST para placa {license_number}:-----------------------")
            print_response(response_post)

