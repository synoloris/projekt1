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

from bs4 import BeautifulSoup
import requests
import json



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
     return send_file("../web/index.html")  

@app.route("/predict")
def predictPage():
    return send_file("../web/predict.html")

@app.route("/webscrape")
def webscrapePage():
    return send_file("../web/webscrape.html")

# Prediction route
@app.route("/api/predict", methods=['GET'])
def predict():
    # Laden der Daten aus der Anfrage
    min_temperature = float(request.args.get('minTemp'))
    prediction_date_str = request.args.get('predictionDate')

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

@app.route("/api/scrapeWeatherDataForVisualization", methods=["GET"])
def getWeatherData():
    predictionType = request.args.get('type')

    weather_url = "https://weather.com/en-IN/weather/"+predictionType+"/l/4c487cf4ef708f64585c6d904db0027f1f40b6cc6ec6a6b5167824614a33eb1b"

    # URL der Wetterseite

    try:
        # GET-Anfrage an die Wetter-URL senden
        response = requests.get(weather_url)
        
        if response.status_code == 200:
            # HTML-Inhalt mit BeautifulSoup parsen
            soup = BeautifulSoup(response.content, 'html.parser')

            # Alle details-Elemente mit der angegebenen Klasse finden

            if (predictionType == "tenday"):
                forecast_items = soup.find_all('details', class_='DaypartDetails--DayPartDetail--2XOOV')
            elif (predictionType == "today"):
                forecast_items = soup.find_all('div', class_='TodayDetailsCard--detailsContainer--2yLtL')
            elif (predictionType == "monthly"):
                forecast_items = soup.find_all("button", class_="CalendarDateCell--dayCell--3ED7m")

            # Eine leere Liste erstellen, um die gescrapten Daten zu speichern
            data = []
            first_iteration = True  # Variable zur Überprüfung der ersten Iteration

            # Durch die Wettervorhersageelemente iterieren und Daten extrahieren
            for item in forecast_items:
                # 10 Tage
                if (predictionType == "tenday"):
                    # Werte extrahieren (falls vorhanden)
                    temperatureMax_elem = item.find('span', class_='DetailsSummary--highTempValue--3PjlX')
                    if temperatureMax_elem:
                        temperatureMax = temperatureMax_elem.text.strip()
                    else:
                        temperatureMax = ''

                    temperatureMin_elem = item.find('span', class_='DetailsSummary--lowTempValue--2tesQ')
                    if temperatureMin_elem:
                        temperatureMin = temperatureMin_elem.text.strip()
                    else:
                        temperatureMin = ''

                    day_elem = item.find('span', class_='DailyContent--daypartDate--3VGlz')
                    if day_elem:
                        day = day_elem.text.strip()
                    else:
                        day = ''

                    humidity_elem = item.find('span', class_='DetailsTable--value--2YD0-')
                    if humidity_elem:
                        humidity = humidity_elem.text.strip()
                    else:
                        humidity = ''

                    uv_index_elem = item.find('span', {'data-testid': 'UVIndexValue'})
                    if uv_index_elem:
                        uv_index = uv_index_elem.text.strip()
                    else:
                        uv_index = ''

                    moonrise_elem = item.find('span', {'data-testid': 'MoonriseTime'})
                    if moonrise_elem:
                        moonrise = moonrise_elem.text.strip()
                    else:
                        moonrise = ''

                    moonphase_elem = item.find('span', class_='DetailsTable--moonPhrase--2rv06')
                    if moonphase_elem:
                        moonphase = moonphase_elem.text.strip()
                    else:
                        moonphase = ''

                    moonset_elem = item.find('span', {'data-testid': 'MoonsetTime'})
                    if moonset_elem:
                        moonset = moonset_elem.text.strip()
                    else:
                        moonset = ''
                    
                    sunrise_elem = item.find('span', {'data-testid': 'SunriseTime'})
                    if sunrise_elem:
                        sunrise = sunrise_elem.text.strip()
                    else:
                        sunrise = ''

                    sunset_elem = item.find('span', {'data-testid': 'SunsetTime'})
                    if sunset_elem:
                        sunset = sunset_elem.text.strip()
                    else:
                        sunset = ''

                    wind_elem = item.find('span', class_='DailyContent--windValue--JPpmk')
                    if wind_elem:
                        wind = wind_elem.text.strip()
                    else:
                        wind = ''

                    wintry_mix_elem = item.find('span', class_='DailyContent--value--1Jers')
                    if wintry_mix_elem:
                        wintry_mix = wintry_mix_elem.text.strip()
                    else:
                        wintry_mix = ''

                    temperature = temperatureMin +" / "+ temperatureMax
                    sun = sunrise + " - " + sunset
                    moon = moonrise + " - " + moonset
                    data.append({
                        'Day': day,
                        'Temperature': temperature,
                        'Humidity': humidity,
                        'UV Index': uv_index,
                        'Sun': sun,
                        'Moon': moon,
                        'Moonphase': moonphase,
                        'Wind': wind,
                        'Wintry Mix': wintry_mix})
                    
                elif (predictionType == "today"):
                    # Heutige Werte extrahieren falls vorhanden
                    temperature_elem = item.find('div', class_='WeatherDetailsListItem--wxData--kK35q')
                    if temperature_elem:
                        temperature = temperature_elem.text.strip()
                    else:
                        temperature = ''

                    wind_elem = item.find('span', class_='Wind--windWrapper--3Ly7c')
                    if wind_elem:
                        wind = wind_elem.text.strip()
                    else:
                        wind = ''

                    humidity_elem = item.find('span', {'data-testid': 'PercentageValue'})
                    if humidity_elem:
                        humidity = humidity_elem.text.strip()
                    else:
                        humidity = ''

                    uv_index_elem = item.find('span', {'data-testid': 'UVIndexValue'})
                    if uv_index_elem:
                        uv_index = uv_index_elem.text.strip()
                    else:
                        uv_index = ''

                    dew_point_elem = item.find('div', text='Dew Point')
                    if dew_point_elem:
                        dew_point = dew_point_elem.find_next_sibling('div').text.strip()
                    else:
                        dew_point = ''

                    pressure_elem = item.find('div', text='Pressure')
                    if pressure_elem:
                        pressure = pressure_elem.find_next_sibling('div').text.strip()
                    else:
                        pressure = ''

                    moonphase_elem = item.find('div', text='Moon Phase')
                    if moonphase_elem:
                        moonphase = moonphase_elem.find_next_sibling('div').text.strip()
                    else:
                        moonphase = ''

                    visibility_elem = item.find('div', text='Visibility')
                    if visibility_elem:
                        visibility = visibility_elem.find_next_sibling('div').text.strip()
                    else:
                        visibility = ''

                    sun = sunrise + " - " + sunset
                    # Daten in ein Dictionary speichern
                    data.append({
                        'Temperature': temperature,
                        'Wind': wind,
                        'Humidity': humidity,
                        'Dew Point': dew_point,
                        'Pressure': pressure,
                        'UV Index': uv_index,
                        'Visibility': visibility,
                        'Moonphase': moonphase
                    })
                
                elif (predictionType == "monthly"):
                    date = item.get("data-id")
                    if date:
                        parts = date.split("/")
                        # Extrahieren der Zahlen
                        month = parts[0].split("-")[-1]
                        day = parts[1] 
                    else:
                        month = ''
                        day =''

                    year_elem = soup.find('select', class_='CalendarMonthPicker--yearPicker--1i9uX')
                    if year_elem:
                        year = year_elem.find("option", selected=True).get("value")
                    else:
                        year = ''

                    temp_high_element = item.find('div', class_="CalendarDateCell--tempHigh--3k9Yr")
                    if temp_high_element:
                        temp_high_span = temp_high_element.find("span")
                        if temp_high_span:
                            temp_high = temp_high_span.text.strip()
                        else:
                            temp_high = ''
                    else:
                        temp_high = ''

                    temp_low_element = item.find('div', class_="CalendarDateCell--tempLow--2WL7c")
                    if temp_low_element:
                        temp_low_span = temp_low_element.find("span")
                        if temp_low_span:
                            temp_low = temp_low_span.text.strip()
                        else:
                            temp_low = ''
                    else:
                        temp_low = ''

                    temperature = temp_low +" / "+ temp_high
                    # Füge das Ergebnis zum Array hinzu
                    data.append({
                        'Day': day,
                        'Month': month,
                        'Year': year,
                        'Temperature': temperature
                    })

            # Die Daten in ein Pandas DataFrame umwandeln
            df = pd.DataFrame(data)

            # DataFrame in JSON konvertieren und als Antwort zurückgeben
            json_data = df.to_json(orient='records')

            # Array in einen formatierten JSON-String umwandeln
            json_ot_string = json.dumps(json_data, indent=4)

            # JSON-String in der Konsole ausgeben
            print(json_ot_string)
    
            # JSON-Daten als Flask-Antwortobjekt zurückgeben
            return jsonify(json_data)
        else:
            return jsonify({"error": "Fehler beim Abrufen der Seite", "status_code": response.status_code})
        
    except Exception as e:
        # Im Falle eines Fehlers eine Fehlermeldung zurückgeben
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)