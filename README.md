# w2influx
# Integracja OpenWeather API z InfluxDB w Dockerze

## Wprowadzenie

Ten projekt pobiera dane pogodowe z **OpenWeather API** co 10 minut i zapisuje je do **InfluxDB** w kontenerze Dockerowym.

---

## Struktura projektu

```
weather-influx/
│── Dockerfile
│── weather_to_influx.py
│── requirements.txt
│── docker-compose.yml
```

---

## 1. Skrypt `weather_to_influx.py`

```python
import requests
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import os
import time

# Konfiguracja OpenWeather API
API_KEY = os.getenv("OPENWEATHER_API_KEY", "TWOJ_KLUCZ_API")
CITY = os.getenv("CITY", "Warsaw")
URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

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
```

---

## 2. `requirements.txt`

```txt
requests
influxdb-client
```

---

## 3. `Dockerfile`

```dockerfile
# Używamy obrazu z Pythonem
FROM python:3.9-slim

# Ustawiamy katalog roboczy
WORKDIR /app

# Kopiujemy pliki projektu
COPY weather_to_influx.py requirements.txt ./

# Instalujemy zależności
RUN pip install --no-cache-dir -r requirements.txt

# Ustawiamy zmienne środowiskowe
ENV OPENWEATHER_API_KEY=your_api_key
ENV CITY=Warsaw
ENV INFLUX_URL=http://influxdb:8086
ENV INFLUX_TOKEN=my-token
ENV INFLUX_ORG=myorg
ENV INFLUX_BUCKET=weather

# Uruchamiamy skrypt
CMD ["python", "weather_to_influx.py"]
```

---

## 4. `docker-compose.yml`

```yaml
version: "3.8"

services:
  influxdb:
    image: influxdb:2.7
    container_name: influxdb
    ports:
      - "8086:8086"
    environment:
      - DOCKER_INFLUXDB_INIT_MODE=setup
      - DOCKER_INFLUXDB_INIT_USERNAME=admin
      - DOCKER_INFLUXDB_INIT_PASSWORD=admin
      - DOCKER_INFLUXDB_INIT_ORG=myorg
      - DOCKER_INFLUXDB_INIT_BUCKET=weather
      - DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=my-token
    volumes:
      - influxdb_data:/var/lib/influxdb2

  weather:
    build: .
    container_name: weather
    environment:
      - OPENWEATHER_API_KEY=your_api_key
      - CITY=Warsaw
      - INFLUX_URL=http://influxdb:8086
      - INFLUX_TOKEN=my-token
      - INFLUX_ORG=myorg
      - INFLUX_BUCKET=weather
    depends_on:
      - influxdb

volumes:
  influxdb_data:
```

---

## Budowanie i uruchamianie kontenerów

1. **Zbuduj obraz**:
   ```bash
   docker-compose build
   ```
2. **Uruchom kontenery**:
   ```bash
   docker-compose up -d
   ```
3. **Sprawdź logi**:
   ```bash
   docker logs -f weather
   ```

Teraz co 10 minut dane pogodowe będą zapisywane do InfluxDB! 🚀


