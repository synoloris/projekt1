function getWeatherData(type) {
    if (!type || type == "") {
        answer.innerHTML = 'Bitte Art der Vorhersage auswählen';
        answerPart.style.visibility = "visible";
        return
    }
    // Get Sentiment
    fetch('/weather?' + new URLSearchParams({
        type: type,
    }), {
        method: 'GET',
        headers: {}
    }).then(
        response => {
            response.text().then(function (data) {
                var contentArray = parseJSONToObj(data);
                answer.innerHTML = generateTableHTML(contentArray);
                buttonContainer.innerHTML = '<button class="form-control btn-primary my-5" onclick="writeToDB()">Daten in MongoDB integrieren</button>';
                answerPart.style.visibility = "visible";
                scrapeDataFields.style.display = "none";
            });
        }
    ).catch(
        error => console.log(error)
    );
}
function writeToDB() {
    /* Hier aufruf ans Backend um anhand den Daten eine Training & Model zu erstellen */
    fetch('/writeToDB', {
        method: 'POST',
        headers: {}
    }).then(
        response => {
            response.json().then(function (data) {
                buttonContainer.innerHTML = '<p>Die Daten wurden erfolgreich in die MongoDB geschrieben.</p><button class="form-control btn-primary my-5" onclick="trainModel()">Model anhand MongoDB Einträgen trainieren</button>';
            });
        }
    ).catch(
        error => console.log('Error writing to MongoDB model:', error)
    );
}
function trainModel() {
    fetch('/trainModel', {
        method: 'POST',
        headers: {}
    }).then(response => {
        response.json().then(function (data) {
            // Daten aus dem JSON-Objekt extrahieren
            const modelCoefficients = JSON.parse(data.model);
    
            // Diagramm erstellen
            const plotData = [{
                x: ['temperatureMax', 'humidity', 'uvIndex', 'wind', 'wintryMix'],
                y: modelCoefficients,
                type: 'bar'
            }];
    
            const layout = {
                title: 'Model Coefficients',
                xaxis: {
                    title: 'Feature'
                },
                yaxis: {
                    title: 'Coefficient Value'
                }
            };
    
            buttonContainer.innerHTML = 'Berechnungen durchgeführt:';
            answer.style.display = "none";
            title.style.display = "none";
            Plotly.newPlot('plot', plotData, layout);
        });
    }).catch(error => console.log('Error fetching model:', error));    
}
function getPrediction(predictionDate) {
    if (!predictionDate || predictionDate == "") {
        answer.innerHTML = 'Bitte Datum angeben';
        answerPart.style.visibility = "visible";
        return
    }
    // Get Sentiment
    fetch('/predictWeatherData?' + new URLSearchParams({
        predictionDate: predictionDate,
    }), {
        method: 'GET',
        headers: {}
    }).then(
        response => {
            response.text().then(function (data) {
                console.log(data);
            });
        }
    ).catch(
        error => console.log(error)
    );
}
function parseJSONToObj(data) {
    console.log(data);
    try {
        var obj = JSON.parse(data);
    } catch (error) {
        console.error('Error parsing JSON:', error);
        return {}; // Gib ein leeres Objekt zurück, wenn das Parsen fehlschlägt
    }
    return obj;
}

function generateTableHTML(data) {
    // Überprüfe, ob data ein gültiger JSON-String ist
    try {
        var content = parseJSONToObj(data);
    } catch (error) {
        console.error('Error parsing JSON:', error);
        return ''; // Gib einen leeren String zurück, wenn das Parsen fehlschlägt
    }

    let html = '<table class="table mt-4">';
    // Annahme: Die erste Zeile des Datenobjekts enthält die Spaltenüberschriften
    if (Object.keys(content).length > 0) {
        html += '<thead><tr>';
        for (let key in content[0]) {
            html += '<th>' + key + '</th>';
        }
        html += '</tr></thead>';
        // Datenzeile hinzufügen
        for (let key in content) {
            html += '<tbody><tr>';
            for (const [keyy, value] of Object.entries(content[key])) {
                html += '<td>' + value + '</td>';
              }
              html += '</tr></tbody>';
        }
    }
    html += '</table>';
    return html;
}
