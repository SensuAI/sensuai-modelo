import pandas as pd
from datetime import datetime

def process_csv(folder_location, output_csv_path="./cleandata/clean_data.csv", output_json_path="./cleandata/clean_final.json"):
    # Leer el archivo CSV
    input_csv_path = folder_location + "/raw_data_{}.csv".format(datetime.now().strftime("%Y-%m-%d"))
    print(f"-----------------------SE REALIZARA LA LIMPIEZA DE: {input_csv_path}-----------------------")
    data_raw = pd.read_csv(input_csv_path, dtype={
        'frame_nmr': 'string',
        'car_id': 'int',
        'vehicle_type': 'string',
        'car_bbox': 'string',
        'license_plate_bbox': 'string',
        'license_plate_bbox_score': 'float64',
        'license_number': 'string',
        'license_number_score': 'float64'})

    # Convertir 'frame_nmr' a formato de fecha y hora
    data_raw['frame_nmr'] = pd.to_datetime(data_raw['frame_nmr'])

    # Agrupar y procesar los datos
    car_type = data_raw.groupby(["car_id"])[["vehicle_type", "license_number"]].agg(lambda x: x.value_counts().idxmax())
    car_id_count = data_raw.groupby(["car_id"])[["car_id"]].agg(lambda x: x.count())
    car_id_count = car_id_count.add_suffix("_1")
    interim = pd.merge(car_type, car_id_count, how="left", left_index=True, right_index=True)

    arrival = data_raw.groupby(["car_id"])[["frame_nmr"]].agg(lambda x: x.min())
    interim_2 = pd.merge(interim, arrival, how="left", left_index=True, right_index=True)

    leave = data_raw.groupby(["car_id"])[["frame_nmr"]].agg(lambda x: x.max())
    interim_3 = pd.merge(interim_2, leave, how="left", left_index=True, right_index=True)

    df_sorted = interim_3.sort_values('car_id_1', ascending=False).drop_duplicates('license_number')
    df_sorted["time"] = (df_sorted["frame_nmr_y"] - df_sorted["frame_nmr_x"]) / 30

    df_sorted.reset_index(inplace=True)
    df_sorted.columns = ["car_id", "vehicle_type", "license_number", "car_count", "det_start", "det_end", "tot_time"]

    # Guardar resultados en CSV y JSON
    df_sorted[["vehicle_type", "license_number", "det_start", "det_end"]].to_csv(output_csv_path, index=False)
    df_sorted[["vehicle_type", "license_number", "det_start", "det_end"]].to_json(output_json_path)
