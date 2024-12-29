import streamlit as st
import requests
import google.generativeai as genai
import matplotlib.pyplot as plt
import numpy as np
from dotenv import load_dotenv
import os

# Memuat variabel lingkungan dari file .env
load_dotenv()

# Konfigurasi Google Generative AI dengan API Key dari .env
google_api_key = os.getenv("API_KEY_GOOGLE_GENERATIVE_AI")
genai.configure(api_key=google_api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Fungsi untuk mendapatkan data cuaca dari OpenWeatherMap
def get_weather_data(city, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Fungsi untuk menampilkan data cuaca
def display_weather(city_data):
    st.write(f"### 🌤 Weather in {city_data['name']}, {city_data['sys']['country']}")
    st.write(f"**Temperature**: {city_data['main']['temp']} °C 🌡️")
    st.write(f"**Feels Like**: {city_data['main']['feels_like']} °C 😓")
    st.write(f"**Weather**: {city_data['weather'][0]['description']} ☁️")
    st.write(f"**Humidity**: {city_data['main']['humidity']} % 💧")
    st.write(f"**Wind Speed**: {city_data['wind']['speed']} m/s 🌬️")
    st.write(f"**Pressure**: {city_data['main']['pressure']} hPa 🌪️")
    st.markdown("---")

# Fungsi untuk mendapatkan jawaban dari Generative AI dengan data cuaca
def get_ai_insights_with_weather(prompt, city_data):
    weather_details = (
        f"Current weather in {city_data['name']} ({city_data['sys']['country']}): "
        f"Temperature: {city_data['main']['temp']} °C, "
        f"Feels Like: {city_data['main']['feels_like']} °C, "
        f"Weather: {city_data['weather'][0]['description']}, "
        f"Humidity: {city_data['main']['humidity']}%, "
        f"Wind Speed: {city_data['wind']['speed']} m/s, "
        f"Pressure: {city_data['main']['pressure']} hPa."
    )
    combined_prompt = f"{weather_details}\n\n{prompt}"
    response = model.generate_content(combined_prompt)
    return response.text

# Fungsi untuk memvisualisasikan grafik suhu
def plot_temperature_graph(cities_data):
    city_names = [city['name'] for city in cities_data]
    temperatures = [city['main']['temp'] for city in cities_data]

    average_temp = np.mean(temperatures)
    std_dev_temp = np.std(temperatures)

    plt.figure(figsize=(10, 6))
    plt.bar(city_names, temperatures, color='lightblue', edgecolor='blue')
    plt.axhline(average_temp, color='red', linestyle='--', label=f'Average Temp: {average_temp:.2f}°C')
    plt.fill_between(range(len(city_names)), average_temp - std_dev_temp, average_temp + std_dev_temp, color='yellow', alpha=0.2, label="±1 Std Dev")
    plt.xlabel('Cities')
    plt.ylabel('Temperature (°C)')
    plt.title('Temperature Comparison', fontsize=16)
    plt.xticks(range(len(city_names)), city_names, rotation=45)
    plt.legend()
    st.pyplot(plt)

# Main Streamlit app
def main():
    # API key untuk OpenWeatherMap diambil dari file .env
    api_key = os.getenv("API_KEY_OPENWEATHERMAP")

    st.set_page_config(page_title="Weather Tracker + AI 🌍", page_icon=":sunny:", layout="wide")
    st.title("🌦️ **Weather Tracker + AI** 🌦️")
    st.markdown(
        """
        **Welcome to the next-gen weather tracker!** 🌍
        Get real-time weather data for multiple cities around the globe 🌏. 
        Plus, ask our AI for insights or explanations about the weather! 🧠
        """
    )

    cities_input = st.text_area("Enter Cities (comma separated):", "")
    cities = [city.strip() for city in cities_input.split(',')]

    cities_data = []
    for city in cities:
        if city:
            st.write(f"🔄 Fetching weather for {city}...")
            city_data = get_weather_data(city, api_key)
            if city_data:
                cities_data.append(city_data)
                display_weather(city_data)
            else:
                st.error(f"❌ Could not retrieve data for **{city}**. Please check the city name.")

    if len(cities_data) > 1:
        plot_temperature_graph(cities_data)

    st.markdown("### 🧠 Ask the AI")
    user_query = st.text_input("Enter your question about weather:", "")
    selected_city = st.selectbox("Select a city for AI insights:", options=[city['name'] for city in cities_data])

    if st.button("Get AI Insights"):
        with st.spinner("Generating AI insights..."):
            city_data = next(city for city in cities_data if city['name'] == selected_city)
            ai_response = get_ai_insights_with_weather(user_query, city_data)
        st.markdown(f"**AI Insight:** {ai_response}")

if __name__ == "__main__":
    main()

st.markdown("---")
st.markdown("**Created by Dimyati**")
