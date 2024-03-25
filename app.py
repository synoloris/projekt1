from bs4 import BeautifulSoup
from flask_pymongo import PyMongo
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from flask.helpers import send_file
from pymongo import MongoClient
from statsmodels.tsa.arima.model import ARIMA
import json
import pandas as pd
import requests
import os
import datetime
from datetime import datetime, timedelta
from flask import Flask, jsonify
from pymongo import MongoClient
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
import pandas as pd
from sklearn.impute import SimpleImputer
import numpy as np


app = Flask(__name__, static_url_path='/', static_folder='web')
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# MongoDB Konfiguration
app.config['MONGO_URI'] = "mongodb+srv://mongodb:dtYs30jvO1dES5oV@mdm-mongodb-cluster.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"
mongo = PyMongo(app)

if __name__ == "__main__":
    app.run(debug=True)

@app.route("/")
@cross_origin()
def indexPage():
    return send_file("web/index.html")
    
@app.route("/weather", methods=["GET"])
@cross_origin()
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

            # Eine leere Liste erstellen, um die gescrapten Daten zu speichern
            data = []

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
                        'Temperatur': temperature,
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

            # Die Daten in ein Pandas DataFrame umwandeln
            df = pd.DataFrame(data)

            # DataFrame in JSON konvertieren und als Antwort zurückgeben
            json_data = df.to_json(orient='records')

            # Zeitstempel generieren
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

            createJSONFile(json_data, predictionType)
    
            # JSON-Daten als Flask-Antwortobjekt zurückgeben
            return jsonify(json_data)
        else:
            return jsonify({"error": "Fehler beim Abrufen der Seite", "status_code": response.status_code})
        
    except Exception as e:
        # Im Falle eines Fehlers eine Fehlermeldung zurückgeben
        return jsonify({"error": str(e)}), 500

def convertData(jsonData):
    convertedData = []
    # Aktuelles Datum
    current_date = datetime.now()
    for entry in jsonData:
        sunrise_parts = entry["Sun"].split()
        sunset_parts = entry["Sun"].split()
        
        sunrise = sunrise_parts[0] if len(sunrise_parts) > 1 else "--"
        sunset = sunset_parts[2] if len(sunset_parts) > 1 else "--"
        
        moonrise_parts = entry["Moon"].split()
        moonset_parts = entry["Moon"].split()
        
        moonrise = moonrise_parts[0] if len(moonrise_parts) > 1 else "--"
        moonset = moonset_parts[2] if len(moonset_parts) > 1 else "--"
        
        convertedEntry = {
            "day": current_date.strftime("%d.%m.%Y"),
            "temperatureMin": entry["Temperatur"].split()[0][:-1],
            "temperatureMax": entry["Temperatur"].split()[2][:-1] if entry["Temperatur"].split()[2] != "--" else "--",
            "humidity": entry["Humidity"][:-1],
            "uvIndex": entry["UV Index"].split()[0],
            "sunrise": sunrise,
            "sunset": sunset,
            "moonRise": moonrise,
            "moonSet": moonset,
            "moonphase": entry["Moonphase"],
            "wind": entry["Wind"].split()[1],
            "wintryMix": entry["Wintry Mix"][:-1]
        }
        convertedData.append(convertedEntry)
        # Nächsten Tag berechnen
        current_date += timedelta(days=1)
    return convertedData

def createJSONFile(jsonData, predictionType):
    # Absoluten Pfad zum aktuellen Skript erhalten
    current_directory = os.path.dirname(os.path.abspath(__file__))
    
    # Relativen Pfad zum Zielverzeichnis erstellen
    target_directory = os.path.join(current_directory, 'web', 'files')

    # Sicherstellen, dass das Verzeichnis existiert, falls nicht, erstellen
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)

    # Dateinamen erstellen
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = os.path.join(target_directory, f"data_{timestamp}_{predictionType}.json")
    

    # JSON-String in ein Python-Objekt (Dictionary/Liste) konvertieren
    try:
        jsonData = json.loads(jsonData)
    except json.JSONDecodeError as e:
        print(f"Fehler beim Decodieren des JSON-Strings: {str(e)}")
        return
    
    # JSON-Daten umstrukturieren
    converted_data = convertData(jsonData)

    # JSON-Daten in Datei schreiben
    try:
        with open(filename, "w", encoding='utf-8') as file:
            json.dump(converted_data, file, indent=4, ensure_ascii=False)
        print(f"Die JSON-Datei wurde erfolgreich erstellt: {filename}")
    except Exception as e:
        print(f"Fehler beim Erstellen der JSON-Datei: {str(e)}")

@app.route("/writeToDB", methods=["POST"])
def write_latest_json_to_mongodb():
    try: 
        # Verbindung zur MongoDB herstellen
        connection_string = "mongodb+srv://mongodb:dtYs30jvO1dES5oV@mdm-mongodb-cluster.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"
        client = MongoClient(connection_string)
        db = client['weather_prediction']  # Hier den Namen deiner Datenbank einfügen
        collection = db['weather_prediction']  # Hier den Namen deiner Sammlung einfügen

        # Verzeichnis mit JSON-Dateien (relativer Pfad)
        directory = os.path.join(os.path.dirname(__file__), 'web', 'files')

        # Liste der JSON-Dateien im Verzeichnis
        json_files = [f for f in os.listdir(directory) if f.endswith('.json')]

        # Sortiere die Liste der JSON-Dateien nach dem Änderungsdatum, um die neueste Datei zu erhalten
        latest_json_file = sorted(json_files, key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=True)[0]

        # Pfade zur neuesten JSON-Datei
        json_file_path = os.path.join(directory, latest_json_file)

        # JSON-Datei lesen
        with open(json_file_path, 'r') as file:
            json_data = json.load(file)

        # Debugging-Ausgabe
        print("JSON data:", json_data)

        # Für jedes Datum prüfen, ob es bereits in der Datenbank vorhanden ist
        for entry in json_data:
            existing_entry = collection.find_one({"day": entry["day"]})
            if existing_entry:
                print(f'Das Datum "{entry["day"]}" ist bereits in der Datenbank vorhanden. Gehe zum nächsten')
            else:
                # Wenn das Datum nicht vorhanden ist, fügen Sie es der Datenbank hinzu
                collection.insert_one(entry)

        return jsonify({'success': "Die neuesten JSON-Daten wurden erfolgreich in die MongoDB eingefügt."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/trainModel", methods=["POST"])
def trainModel():
    try: 
        # Verbindung zur MongoDB herstellen
        connection_string = "mongodb+srv://mongodb:dtYs30jvO1dES5oV@mdm-mongodb-cluster.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"
        client = MongoClient(connection_string)
        db = client['weather_prediction']
        collection = db['weather_prediction']

        # Daten aus MongoDB abrufen
        cursor = collection.find()

        # Daten in DataFrame konvertieren
        data = pd.DataFrame(list(cursor))

        # Schritt 1: Daten vorbereiten
        # Auswahl nur numerischer Spalten
        numeric_columns = ['temperatureMax', 'temperatureMin', 'humidity', 'uvIndex', 'wind', 'wintryMix']
        data = data[numeric_columns]

        # Fehlende Werte ersetzen oder entfernen
        data.replace('--', np.nan, inplace=True)  # Ersetzt '--' durch NaN
        data.dropna(inplace=True)  # Entfernt Zeilen mit NaN-Werten

        # Konvertiere Datentypen in float
        data = data.astype(float)

        X = data[['temperatureMax', 'humidity', 'uvIndex', 'wind', 'wintryMix']]
        y = data['temperatureMin']  # Zielvariable ist die Mindesttemperatur

        # Schritt 2: Modell auswählen und trainieren
        model = LinearRegression()
        model.fit(X, y)

        # Schritt 3: Modell als JSON serialisieren
        model_json = json.dumps(model.coef_.tolist())  # Hier können Sie die Modellparameter oder andere relevante Informationen serialisieren

        return jsonify({'success': "Das Modell wurde erfolgreich trainiert.", 'model': model_json}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/predictWeatherData", methods=["POST"])
def calculate_prediction():
    try: 
        # Datum aus der POST-Anfrage extrahieren
        prediction_date_str = request.form.get("predictionDate")
        if not prediction_date_str:
            return jsonify({"error": "Datum nicht angegeben."}), 400

        prediction_date = datetime.strptime(prediction_date_str, "%d.%m.%Y")

        # Verbindung zur MongoDB herstellen
        connection_string = "mongodb+srv://mongodb:dtYs30jvO1dES5oV@mdm-mongodb-cluster.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"
        client = MongoClient(connection_string)
        db = client['weather_prediction']
        collection = db['weather_prediction']

        # Vergangene Wetterdaten aus der MongoDB abrufen
        past_weather_data = list(collection.find())

        # Daten in DataFrame konvertieren
        data = pd.DataFrame(past_weather_data)

        # Schritt 1: Daten vorbereiten
        X = data[['temperatureMax', 'humidity', 'uvIndex', 'wind', 'wintryMix']]
        y = data['temperatureMin']

        # Schritt 2: Modell auswählen und trainieren
        model = LinearRegression()
        model.fit(X, y)

        # Schritt 3: Mindesttemperatur für das neue Datum vorhersagen
        new_data = pd.DataFrame({
            'temperatureMax': [0],  # Wert muss für das neue Datum eingefügt werden
            'humidity': [0],         # Wert muss für das neue Datum eingefügt werden
            'uvIndex': [0],          # Wert muss für das neue Datum eingefügt werden
            'wind': [0],             # Wert muss für das neue Datum eingefügt werden
            'wintryMix': [0]         # Wert muss für das neue Datum eingefügt werden
        })

        # Schritt 4: Mindesttemperatur für das neue Datum vorhersagen
        predicted_temperature_min = model.predict(new_data)[0]

        return jsonify({'temperatureMin': predicted_temperature_min}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500