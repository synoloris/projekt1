# cd web/files
# python mongo_import.py -u '***MONGODB_URI***'

import argparse
import os
import json
from pymongo import MongoClient

# Argumente parsen
parser = argparse.ArgumentParser(description='Import JSON')
parser.add_argument('-u', '--uri', required=True, help="MongoDB URI with username/password")
args = parser.parse_args()

# MongoDB-Verbindung herstellen
mongo_uri = args.uri
mongo_db = "weather_prediction"
mongo_collection = "weather_prediction"


try: 
        # Verbindung zur MongoDB herstellen
        
        client = MongoClient(mongo_uri)
        db = client[mongo_db]
        collection = db[mongo_collection]

        # Verzeichnis mit JSON-Dateien (relativer Pfad)
        directory = os.path.join(os.path.dirname(__file__), '..', 'files')  # Aktualisieren Sie den relativen Pfad entsprechend

        # Liste der JSON-Dateien im Verzeichnis
        json_files = [f for f in os.listdir(directory) if f.endswith('.json')]

        # Sortieren Sie die Liste der JSON-Dateien nach dem Änderungsdatum, um die neueste Datei zu erhalten
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
                    # Wenn das Datum bereits vorhanden ist, fügen Sie neue Felder hinzu
                    update_data = {key: value for key, value in entry.items() if key != "day"}  # Alle Felder außer "day"
                    collection.update_one({"day": entry["day"]}, {"$set": update_data})
                    print(f'Die Daten für den Tag "{entry["day"]}" wurden erfolgreich aktualisiert.')
                else:
                    # Wenn das Datum nicht vorhanden ist, fügen Sie es der Datenbank hinzu
                    print(f'Die Daten für den Tag "{entry["day"]}" wurden erfolgreich hinzugefügt.')
                    collection.insert_one(entry)

        print("Die neuesten JSON-Daten wurden erfolgreich in die MongoDB eingefügt.")
except Exception as e:
        print("error " + str(e))