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
                buttonContainer.innerHTML = '<p>Daten gefunden!</p><button class="form-control btn-primary my-5" onclick="writeToDB()">Daten in MongoDB integrieren</button>';
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
                buttonContainer.innerHTML = '<p>Die Daten wurden erfolgreich in die MongoDB geschrieben.</p><button class="form-control btn-primary my-5" onclick="trainModel()">Model anzeigen</button>';
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
            const jsonObject = JSON.parse(data.model);
            const modelCoefficients = jsonObject.coefficients;
            const mae = jsonObject.MAE;
            const mse = jsonObject.MSE;
            const r2 = jsonObject.R2;

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

            title.innerHTML = 'Metriken:';
            buttonContainer.style.display = "none"
            answer.style.display = "block";
            title.style.display = "block";
            Plotly.newPlot('plot', plotData, layout);

            // Anzeigen der Metriken
            answer.innerHTML = `<p>Mean Absolute Error (MAE): ${mae}</p>
                                <p>Mean Squared Error (MSE): ${mse}</p>
                                <p>R² (Bestimmtheitsmass): ${r2}</p>`;
        });
    }).catch(error => console.log('Error fetching model:', error));    
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

function validatePredictionForm(event) {
    event.preventDefault(); // Verhindert das Absenden des Formulars, wenn Bedingungen nicht erfüllt sind
    
    error = false;
    // Temperatur validieren
    var minTemp = parseInt(document.getElementById('minTempInput').value);
    if (minTemp < -10 || minTemp > 35 || minTemp === '' || minTemp == NaN) {
        error = true;
        $('#minTempInputError').html("Die Temperatur muss zwischen -10 und 35 liegen").show();
    } else {
        $('#minTempInputError').html("").hide();
    }

    // Datum validieren
    var predictionDate = new Date(document.getElementById('dateInput').value);
    var currentDate = new Date();

    if (predictionDate <= currentDate) {
        error = true;
        $('#dateInputError').html("Das Datum muss in der Zukunft liegen").show();
    } else {
        $('#dateInputError').html("").hide();
    }

    // Wenn alles in Ordnung ist, kann das Formular abgesendet werden
    if (!error) {
        // Datum parsen
        var date = new Date(predictionDate);

        // Jahr, Monat und Tag extrahieren
        var year = date.getFullYear();
        var month = ("0" + (date.getMonth() + 1)).slice(-2); // Monat von 0-11, daher +1 und führende Nullen hinzufügen
        var day = ("0" + date.getDate()).slice(-2); // Führende Nullen hinzufügen

        // Datum im Format "YYYY-MM-DD" erstellen
        var formattedDate = year + "-" + month + "-" + day;
        // Hier AJAX Aufruf ans Backend        
        fetch('/api/predict?' + new URLSearchParams({
            minTemp: minTemp,
            predictionDate: formattedDate,
        }), {
            method: 'GET',
            headers: {}
        }).then(
            response => {
                response.text().then(function (data) {
                    const jsonObject = JSON.parse(data);
                    answer.innerHTML = 'vorhergesagte Maximaltemperatur: ' + jsonObject.max_temperature_prediction;
                    answerPart.style.visibility = "visible";
                });
            }
        ).catch(
            error => console.log(error)
        );
    }
    return false;
}