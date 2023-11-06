import requests
import json

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

def main():
    BASE_URL = "http://192.9.251.74:8080"
    BRANCH_ID = "653306f3c692c1d2f08b5d99"
    
    # Solicitud GET
    getAllBranches = f"{BASE_URL}/branch/getAll"
    response_get = make_get_request(getAllBranches)
    print_response(response_get)

    # Solicitud POST para múltiples placas
    plates = ["PAL-13-00", "HBG-188-E"]
    for plate in plates:
        data = {
            "branch_id": BRANCH_ID,
            "plate": plate
        }
        endopointPlateIdentified = f"{BASE_URL}/model/plateIdentified"
        response_post = make_post_request(endopointPlateIdentified, data)
        print(f"Solicitud POST para placa {plate}:")
        print_response(response_post)

if __name__ == "__main__":
    main()
