import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import folium
from streamlit_folium import folium_static

# WeatherAPI configuration
API_KEY = "0ffc69e3906042c689d71736252602"  # Replace with your WeatherAPI key
BASE_URL = "http://api.weatherapi.com/v1"

# Page configuration
st.set_page_config(
    page_title="Weather Dashboard",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        width: 100%;
    }
    .dark-mode {
        background-color: #1a1a1a;
        color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")
    
    # City selection
    city = st.text_input("Enter City", "London")
    
    # Temperature unit toggle
    temp_unit = st.radio("Temperature Unit", ["Celsius", "Fahrenheit"])
    
    # Dark mode toggle
    dark_mode = st.toggle("Dark Mode")
    
    # Date range selection
    date_range = st.slider(
        "Forecast Range (days)",
        min_value=1,
        max_value=5,
        value=3
    )

def get_weather_data(city):
    """Fetch weather data from WeatherAPI"""
    try:
        # Current weather and forecast in one call
        response = requests.get(
            f"{BASE_URL}/forecast.json",
            params={
                "key": API_KEY,
                "q": city,
                "days": 5,
                "aqi": "yes"
            }
        )
        response.raise_for_status()
        data = response.json()
        
        # Validate response
        if 'current' not in data or 'forecast' not in data:
            st.error("Invalid response from weather API")
            return None
            
        return data
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching weather data: {str(e)}")
        return None
    except ValueError as e:
        st.error(f"Error parsing API response: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return None

def celsius_to_fahrenheit(temp):
    """Convert Celsius to Fahrenheit"""
    return (temp * 9/5) + 32

# Main content
st.title("🌤️ Weather Dashboard")

# Fetch weather data
weather_data = get_weather_data(city)

if weather_data:
    current = weather_data['current']
    forecast = weather_data['forecast']
    
    # Current weather display
    col1, col2, col3 = st.columns(3)
    
    with col1:
        temp = current['temp_c'] if temp_unit == "Celsius" else current['temp_f']
        feels_like = current['feelslike_c'] if temp_unit == "Celsius" else current['feelslike_f']
        st.metric(
            "Temperature",
            f"{temp:.1f}°{'F' if temp_unit == 'Fahrenheit' else 'C'}",
            f"Feels like: {feels_like:.1f}°"
        )
    
    with col2:
        st.metric("Humidity", f"{current['humidity']}%")
    
    with col3:
        st.metric("Wind Speed", f"{current['wind_kph']} km/h")

    # Temperature trend chart
    st.subheader("Temperature Trend")
    forecast_temps = []
    forecast_times = []
    
    for day in forecast['forecastday'][:date_range]:
        for hour in day['hour']:
            temp = hour['temp_c'] if temp_unit == "Celsius" else hour['temp_f']
            forecast_temps.append(temp)
            forecast_times.append(datetime.fromtimestamp(hour['time_epoch']))
    
    temp_df = pd.DataFrame({
        'Time': forecast_times,
        'Temperature': forecast_temps
    })
    
    fig = px.line(
        temp_df,
        x='Time',
        y='Temperature',
        title=f"Temperature Forecast for {city}",
        labels={'Temperature': f'Temperature (°{"F" if temp_unit == "Fahrenheit" else "C"})'}
    )
    st.plotly_chart(fig, use_container_width=True)

    # Precipitation chart
    st.subheader("Precipitation Forecast")
    precipitation_data = []
    
    for day in forecast['forecastday'][:date_range]:
        for hour in day['hour']:
            precipitation_data.append(hour['precip_mm'])
    
    precip_df = pd.DataFrame({
        'Time': forecast_times,
        'Precipitation': precipitation_data
    })
    
    fig_precip = px.bar(
        precip_df,
        x='Time',
        y='Precipitation',
        title=f"Precipitation Forecast for {city}",
        labels={'Precipitation': 'Precipitation (mm)'}
    )
    st.plotly_chart(fig_precip, use_container_width=True)

    # Weather map
    st.subheader("Weather Map")
    location = weather_data['location']
    m = folium.Map(
        location=[location['lat'], location['lon']],
        zoom_start=10
    )
    
    folium.Marker(
        [location['lat'], location['lon']],
        popup=f"Temperature: {temp:.1f}°{'F' if temp_unit == 'Fahrenheit' else 'C'}\n"
              f"Weather: {current['condition']['text']}"
    ).add_to(m)
    
    folium_static(m)

else:
    st.error("Unable to fetch weather data. Please check the city name and try again.")

# Apply dark mode if enabled
if dark_mode:
    st.markdown("""
        <style>
        .main {
            background-color: #1a1a1a;
            color: #ffffff;
        }
        </style>
        """, unsafe_allow_html=True)
