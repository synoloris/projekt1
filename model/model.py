import argparse
import pandas as pd
from pymongo import MongoClient
from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime, timedelta
import pickle
import os

# Argumente parsen
parser = argparse.ArgumentParser(description='Create Model')
parser.add_argument('-u', '--uri', required=True, help="MongoDB URI with username/password")
args = parser.parse_args()

# MongoDB-Verbindung herstellen
mongo_uri = args.uri
mongo_db = "weather_prediction"
mongo_collection = "weather_prediction"

client = MongoClient(mongo_uri)
db = client[mongo_db]
collection = db[mongo_collection]

# Daten aus MongoDB abrufen
cursor = collection.find({}, {"_id": 0, "day": 1, "temperatureMax": 1})  # Nur benötigte Felder abrufen
data = list(cursor)
df = pd.DataFrame(data)

# Ersetzen Sie "--" durch NaN in der Spalte "temperatureMax"
df['temperatureMax'] = df['temperatureMax'].replace("--", pd.NA)

# Entfernen Sie Zeilen mit fehlenden Werten in der "temperatureMax"-Spalte
df = df.dropna(subset=['temperatureMax'])

# Datentypen konvertieren
df['temperatureMax'] = pd.to_numeric(df['temperatureMax'])

# Konvertieren Sie das Datum in das richtige Format
df['day'] = pd.to_datetime(df['day'], format="%d.%m.%Y")

# Index des DataFrames zurücksetzen
df.reset_index(drop=True, inplace=True)

# Index des DataFrames zurücksetzen und eine Frequenz von "D" (täglich) festlegen
start_date = df['day'].min()  # Das erste Datum im DataFrame
df.index = pd.date_range(start=start_date, periods=len(df), freq='D')

# ARIMA-Modell anwenden
model = ARIMA(df['temperatureMax'], order=(5,1,0))  
model_fit = model.fit()

# Modell als pickle-Datei speichern
with open('ARIMA.pkl', 'wb') as fid:
    pickle.dump(model_fit, fid)

# Berechnung der Vorhersagen
predictions = model_fit.predict(start=start_date, end=df.index[-1], typ='levels')

# Berechnung der Residuen
residuals = df['temperatureMax'] - predictions

# Berechnung des MSE
mse = ((residuals)**2).mean()

# Berechnung des R2
sst = ((df['temperatureMax'] - df['temperatureMax'].mean())**2).sum()
ssr = ((predictions - df['temperatureMax'].mean())**2).sum()
r2 = 1 - (ssr/sst)

# Berechnung des Korrelationskoeffizienten
corr_coef = df['temperatureMax'].corr(predictions)

# Ausgabe der Kennzahlen
print("Mean Squared Error (MSE):", mse)
print("R-squared (R2):", r2)
print("Correlation Coefficient:", corr_coef)
