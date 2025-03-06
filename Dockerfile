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
