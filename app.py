from flask import Flask, request, render_template_string
import datetime
import requests
import logging
import json

app = Flask(__name__)
PORT = 5000
AUTHOR = "Sebastian Żurawski"

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
logging.info(f"Start aplikacji: {datetime.datetime.now()}, Autor: {AUTHOR}, Port: {PORT}")

# Predefiniowane kraje i miasta
cities = {
    "Polska": ["Warszawa", "Kraków", "Gdańsk"],
    "USA": ["New York", "Los Angeles", "Chicago"],
    "Niemcy": ["Berlin", "Monachium", "Hamburg"]
}

# Funkcja pobierająca pogodę
def get_weather(city):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    geo = requests.get(url).json()
    if geo.get('results'):
        lat = geo['results'][0]['latitude']
        lon = geo['results'][0]['longitude']
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        weather = requests.get(weather_url).json()
        return weather.get('current_weather', {})
    return {}

# Strona główna
@app.route("/", methods=["GET", "POST"])
def index():
    selected_country = "Polska"
    selected_city = None
    weather = None

    if request.method == "POST":
        selected_country = request.form.get("country")
        selected_city = request.form.get("city")
        if selected_city:
            weather = get_weather(selected_city)

    country_options = ''.join([
        f'<option value="{country}" {"selected" if country == selected_country else ""}>{country}</option>'
        for country in cities.keys()
    ])

    city_options = ''.join([
        f'<option value="{city}" {"selected" if city == selected_city else ""}>{city}</option>'
        for city in cities.get(selected_country, [])
    ])

    weather_info = ""
    if weather:
        weather_info = f"""
        <h2>Aktualna pogoda dla {selected_city}:</h2>
        <ul>
            <li>Temperatura: {weather.get('temperature', '?')} °C</li>
            <li>Wiatr: {weather.get('windspeed', '?')} km/h</li>
            <li>Kierunek wiatru: {weather.get('winddirection', '?')}°</li>
        </ul>
        """

    return render_template_string('''
    <h1>Aplikacja Pogodowa</h1>
    <form method="POST">
        <label for="country">Wybierz kraj:</label><br>
        <select name="country" id="country" onchange="updateCities()">
            {{ country_options|safe }}
        </select><br><br>

        <label for="city">Wybierz miasto:</label><br>
        <select name="city" id="city">
            {{ city_options|safe }}
        </select><br><br>

        <button type="submit">Sprawdź pogodę</button>
    </form>

    {{ weather_info|safe }}

    <script>
    const cities = {{ cities|tojson }};
    function updateCities() {
        const country = document.getElementById('country').value;
        const citySelect = document.getElementById('city');
        citySelect.innerHTML = "";
        cities[country].forEach(function(city) {
            let option = document.createElement('option');
            option.value = city;
            option.text = city;
            citySelect.appendChild(option);
        });
    }
    </script>
    ''', country_options=country_options, city_options=city_options, weather_info=weather_info, cities=cities)

# Uruchomienie aplikacji
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
