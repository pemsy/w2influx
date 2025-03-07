import requests
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import os
import time

# Konfiguracja OpenWeather API
API_KEY = os.getenv("OPENWEATHER_API_KEY", "TWOJ_KLUCZ_API")
CITY = os.getenv("CITY", "Warsaw")
URL = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid={API key}&units=metric"


# Konfiguracja InfluxDB
INFLUX_URL = os.getenv("INFLUX_URL", "http://influxdb:8086")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "my-token")
INFLUX_ORG = os.getenv("INFLUX_ORG", "myorg")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "weather")

client = influxdb_client.InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

def get_weather():
    """ Pobiera dane pogodowe z OpenWeather API """
    response = requests.get(URL)
    if response.status_code == 200:
        data = response.json()
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        return temp, humidity, pressure
    else:
        print("Błąd pobierania danych pogodowych:", response.status_code)
        return None

def write_to_influx(temp, humidity, pressure):
    """ Wpisuje dane do InfluxDB """
    point = influxdb_client.Point("weather").tag("city", CITY) \
        .field("temperature", temp) \
        .field("humidity", humidity) \
        .field("pressure", pressure)
    
    write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
    print(f"✅ Dane zapisane: Temp={temp}°C, Humidity={humidity}%, Pressure={pressure} hPa")

if __name__ == "__main__":
    while True:
        temp, humidity, pressure = get_weather()
        if temp is not None:
            write_to_influx(temp, humidity, pressure)
        time.sleep(600)  # Czekaj 10 minut
