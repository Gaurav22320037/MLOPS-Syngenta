import requests
import streamlit as st
import pandas as pd

# OpenWeatherMap API credentials and parameters
API_KEY = "661e31209c95328976a7cdc51aebf03f"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
CURRENT_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
GEOCODE_URL = "https://api.openweathermap.org/data/2.5/weather"
LAT = None
LON = None

# Function to fetch the coordinates (latitude and longitude) for a location
def fetch_coordinates(city_name, api_key):
    params = {"q": city_name, "appid": api_key}
    response = requests.get(GEOCODE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        return data["coord"]["lat"], data["coord"]["lon"]
    else:
        st.error("Failed to fetch coordinates for the given location.")
        return None, None

# Function to fetch 5-day forecast weather data
def fetch_5_day_forecast(lat, lon, api_key):
    params = {"lat": lat, "lon": lon, "appid": api_key, "units": "metric"}
    response = requests.get(FORECAST_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch weather data.")
        return None

# Function to fetch current weather data
def fetch_current_weather(lat, lon, api_key):
    params = {"lat": lat, "lon": lon, "appid": api_key, "units": "metric"}
    response = requests.get(CURRENT_WEATHER_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch current weather data.")
        return None

# Function to process forecast data
def process_forecast_data(data):
    daily_data = {}
    
    for forecast in data["list"]:
        date = forecast["dt_txt"].split(" ")[0]  # Extract date only
        temp = forecast["main"]["temp"]
        humidity = forecast["main"]["humidity"]
        rainfall = forecast.get("rain", {}).get("3h", 0)
        
        # Aggregate data by date
        if date not in daily_data:
            daily_data[date] = {"temp_sum": 0, "temp_count": 0, "humidity_sum": 0, "humidity_count": 0, "rainfall": 0}
        
        daily_data[date]["temp_sum"] += temp
        daily_data[date]["temp_count"] += 1
        daily_data[date]["humidity_sum"] += humidity
        daily_data[date]["humidity_count"] += 1
        daily_data[date]["rainfall"] += rainfall

    # Calculate daily averages and totals
    processed_data = []
    for date, values in daily_data.items():
        processed_data.append({
            "Date": date,
            "Avg Temperature (°C)": round(values["temp_sum"] / values["temp_count"], 2),
            "Avg Humidity (%)": round(values["humidity_sum"] / values["humidity_count"], 2),
            "Total Rainfall (mm)": round(values["rainfall"], 2),
        })
    
    return processed_data

# Streamlit UI
st.title("Weather Forecast and Current Weather")
st.write("Enter a city name to fetch the weather data:")

# User input for city
city_name = st.text_input("City Name")

# Check if the user has entered a city name
if city_name:
    # Fetch latitude and longitude for the given city
    LAT, LON = fetch_coordinates(city_name, API_KEY)
    
    if LAT and LON:
        st.write(f"Weather data for {city_name} (Latitude: {LAT}, Longitude: {LON})")

        # Fetch and display the current weather
        if st.button("Fetch Current Weather"):
            current_data = fetch_current_weather(LAT, LON, API_KEY)
            if current_data:
                current_temp = current_data["main"]["temp"]
                current_humidity = current_data["main"]["humidity"]
                current_wind_speed = current_data["wind"]["speed"]
                current_description = current_data["weather"][0]["description"]
                current_pressure = current_data["main"]["pressure"]
                current_visibility = current_data["visibility"] / 1000  # Convert meters to kilometers

                # Display current weather data
                st.write(f"**Current Temperature**: {current_temp}°C")
                st.write(f"**Humidity**: {current_humidity}%")
                st.write(f"**Wind Speed**: {current_wind_speed} m/s")
                st.write(f"**Weather Description**: {current_description.capitalize()}")
                st.write(f"**Pressure**: {current_pressure} hPa")
                st.write(f"**Visibility**: {current_visibility} km")

        # Fetch and display the 5-day forecast
        if st.button("Fetch 5-Day Forecast"):
            data = fetch_5_day_forecast(LAT, LON, API_KEY)
            if data:
                # Process the forecast data
                forecast_data = process_forecast_data(data)
                forecast_df = pd.DataFrame(forecast_data).head(5)
                
                # Display results
                st.subheader("5-Day Weather Forecast (Averages)")
                st.dataframe(forecast_df)

                # Optionally: Add charts
                st.write("### Temperature Trends")
                st.line_chart(forecast_df.set_index("Date")["Avg Temperature (°C)"])

                st.write("### Humidity Trends")
                st.line_chart(forecast_df.set_index("Date")["Avg Humidity (%)"])

                st.write("### Rainfall Trends")
                st.bar_chart(forecast_df.set_index("Date")["Total Rainfall (mm)"])
    else:
        st.error("Could not find location coordinates. Please check the city name and try again.")
