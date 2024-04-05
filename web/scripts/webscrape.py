# cd web/files
# python webscrape.py -t 'monthly'

import argparse
import os
import json
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
import pandas as pd


# Argumente parsen
parser = argparse.ArgumentParser(description='Webscrape')
parser.add_argument('-t', '--type', required=True, help="Type of crawl (tenday / monthly)")
args = parser.parse_args()

predictionType = args.type

def convertData(jsonData, predictionType):
    convertedData = []
    # Aktuelles Datum
    current_date = datetime.now()

    first_iteration = True

    for entry in jsonData:
        if (predictionType == "tenday"):
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
                "temperatureMin": entry["Temperature"].split()[0][:-1],
                "temperatureMax": entry["Temperature"].split()[2][:-1] if entry["Temperature"].split()[2] != "--" else "--",
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
        elif (predictionType == "monthly"):
            
            month = entry["Month"]
            year = entry["Year"]
            day = entry["Day"]
            
            convertedEntry = {
                "day": str(day).zfill(2) + "." + str(month).zfill(2) + "." + year,
                "temperatureMin": entry["Temperature"].split()[0][:-1] if entry["Temperature"].split()[0] != "--" else "--",
                "temperatureMax": entry["Temperature"].split()[2][:-1] if entry["Temperature"].split()[2] != "--" else "--"
            }
            convertedData.append(convertedEntry)
        
    return convertedData

def createJSONFile(jsonData, predictionType):
    print(f"Erstelle JSON File...")
    # Absoluten Pfad zum aktuellen Skript erhalten
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Relativen Pfad zum Zielverzeichnis erstellen (web/files)
    target_directory = os.path.join(current_directory, '..', 'files')

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
    converted_data = convertData(jsonData, predictionType)

    # JSON-Daten in Datei schreiben
    try:
        with open(filename, "w", encoding='utf-8') as file:
            json.dump(converted_data, file, indent=4, ensure_ascii=False)
        print(f"Die JSON-Datei wurde erfolgreich erstellt: {filename}")
    except Exception as e:
        print(f"Fehler beim Erstellen der JSON-Datei: {str(e)}")




# URL der Wetterseite
weather_url = "https://weather.com/en-IN/weather/"+predictionType+"/l/4c487cf4ef708f64585c6d904db0027f1f40b6cc6ec6a6b5167824614a33eb1b" 

try:
    # GET-Anfrage an die Wetter-URL senden
    response = requests.get(weather_url)
    
    if response.status_code == 200:
        # HTML-Inhalt mit BeautifulSoup parsen
        soup = BeautifulSoup(response.content, 'html.parser')

        # Alle details-Elemente mit der angegebenen Klasse finden

        if (predictionType == "tenday"):
            forecast_items = soup.find_all('details', class_='DaypartDetails--DayPartDetail--2XOOV')
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
        createJSONFile(json_data, predictionType)

    else:
        print("error: " + "Fehler beim Abrufen der Seite" + ", status_code: " + response.status_code)
    
except Exception as e:
    # Im Falle eines Fehlers eine Fehlermeldung zurückgeben
    print("error" + str(e))