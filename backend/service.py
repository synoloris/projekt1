import datetime
import os
import pickle
from pathlib import Path

import pandas as pd
from azure.storage.blob import BlobServiceClient
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import pytz
from dateutil.parser import parse as parse_date
from pandas import Timestamp


# Init app, load model from storage
print("*** Init and load model ***")
if 'AZURE_STORAGE_CONNECTION_STRING' in os.environ:
    azureStorageConnectionString = os.environ['AZURE_STORAGE_CONNECTION_STRING']
    blob_service_client = BlobServiceClient.from_connection_string(azureStorageConnectionString)

    print("Fetching blob containers...")
    containers = blob_service_client.list_containers(include_metadata=True)
    for container in containers:
        existingContainerName = container['name']
        print("Checking container " + existingContainerName)
        if existingContainerName.startswith("weatherpredicter-model"):
            parts = existingContainerName.split("-")
            print(parts)
            suffix = 1
            if (len(parts) == 3):
                newSuffix = int(parts[-1])
                if (newSuffix > suffix):
                    suffix = newSuffix

    container_client = blob_service_client.get_container_client("weatherpredicter-model-" + str(suffix))
    blob_list = container_client.list_blobs()
    for blob in blob_list:
        print("\t" + blob.name)

    # Download the blob to a local file
    Path("../model").mkdir(parents=True, exist_ok=True)
    download_file_path = os.path.join("../model", "ARIMA.pkl")
    print("\nDownloading blob to \n\t" + download_file_path)

    with open(file=download_file_path, mode="wb") as download_file:
         download_file.write(container_client.download_blob(blob.name).readall())

else:
    print("CANNOT ACCESS AZURE BLOB STORAGE - Please set connection string as env variable")
    print(os.environ)
    print("AZURE_STORAGE_CONNECTION_STRING not set")    

# Load the DataFrame with weather data
# Replace this with your actual code to load the weather data
# Example:
# df = pd.read_csv("path_to_your_weather_data.csv")

file_path = Path(".", "../model/", "ARIMA.pkl")
with open(file_path, 'rb') as fid:
    model = pickle.load(fid)

print("*** Init Flask App ***")
app = Flask(__name__)
cors = CORS(app)
app = Flask(__name__, static_url_path='/', static_folder='../web')

@app.route("/")
def indexPage():
     return send_file("../web/predict.html")  

# Funktion zur Konvertierung des Datums in das ISO-Format
def convert_to_iso_format(date_str):
    parsed_date = parse_date(date_str)
    return parsed_date.isoformat()

# Prediction route
@app.route("/api/predict", methods=['GET'])
def predict():
    # Laden der Daten aus der Anfrage
    min_temperature = float(request.args.get('minTemp'))
    prediction_date_str = request.args.get('predictionDate')
    prediction_date = Timestamp(prediction_date_str)

    # Laden des ARIMA-Modells
    model_file_path = os.path.join(os.getcwd(), '..', 'model', 'ARIMA.pkl')

    with open(model_file_path, 'rb') as fid:
        model = pickle.load(fid)

    # Vorhersage durchführen
    prediction = model.forecast(steps=1)[0]

    # Sicherstellen, dass die Vorhersage über der Mindesttemperatur liegt
    while prediction < min_temperature:
        prediction += 1

    return jsonify({
        'max_temperature_prediction': prediction
    })

if __name__ == "__main__":
    app.run(debug=True)