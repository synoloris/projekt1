# Weather Prediction from weather.com

inspired by https://www.geeksforgeeks.org/scrapping-weather-prediction-data-using-python-and-bs4/amp/

## BeautifulSoup

* Scrape new additional data
* Output file.jl (json list)
* Load data into MongoDB
* Update model
    * Produce correlation heatmap
    * Check R2 (bigger and close to 1 is better)
    * Check MSE (lower better, square seconds)
* Save model to model/GradientBoostingRegressor.pkl

## Azure Blob Storage

* Save model to Azure Blob Storage
* Always save new version of model
* Zugriff: Speicherkonto > Zugriffsschlüssel
    * Als Umgebungsvariable für Docker
    * Als Secret für GitHub

## GitHub Action

* Scrape
* Load data to MongoDB (Azure Cosmos DB)
* Update model and save to Azure Blob Storage

## App
* Backend: Python Flask (backend/service.py)
* Frontend: Bootstrap / VanillaJS (web Folder)

## Deployment with Docker

* Dockerfile
* Install dependencies with pip
* Copy Frontend (prebuilt)
* Azure Blob Storage: Zugriffsschlüssel als Umgebungsvariable

