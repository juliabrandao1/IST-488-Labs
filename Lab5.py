import streamlit as st
import requests
import json
from openai import OpenAI

st.title("Lab 5: What to Wear Bot")

# Get API keys from secrets
OPENWEATHER_API_KEY = st.secrets["OPENWEATHER_API_KEY"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# Create OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

def get_current_weather(location, api_key, units='imperial'):
    """Fetches current weather data for a given location from OpenWeatherMap."""
    url = (
        f'https://api.openweathermap.org/data/2.5/weather'
        f'?q={location}&appid={api_key}&units={units}'
    )
    response = requests.get(url)

    if response.status_code == 401:
        raise Exception('Authentication failed: Invalid API key (401 Unauthorized)')
    if response.status_code == 404:
        error_message = response.json().get('message')
        raise Exception(f'404 error: {error_message}')

    data = response.json()
    temp = data['main']['temp']
    feels_like = data['main']['feels_like']
    temp_min = data['main']['temp_min']
    temp_max = data['main']['temp_max']
    humidity = data['main']['humidity']

    return {
        'location': location,
        'temperature': round(temp, 2),
        'feels_like': round(feels_like, 2),
        'temp_min': round(temp_min, 2),
        'temp_max': round(temp_max, 2),
        'humidity': round(humidity, 2)
    }

# Define the tool for OpenAI
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather for a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state/country, e.g. Syracuse, NY, US"
                    }
                },
                "required": ["location"]
            }
        }
    }
]

# User input
city = st.text_input("Enter a city to get weather-based clothing advice:", 
                      placeholder="e.g. Syracuse, NY, US")

if city:
    with st.spinner("Getting weather and generating suggestions..."):
        try:
            # Step 1: Send the user's request to OpenAI with the tool available
            messages = [
                {"role": "system", "content": "You are a helpful assistant that provides clothing suggestions and outdoor activity recommendations based on the current weather."},
                {"role": "user", "content": f"What should I wear today in {city}? Also suggest some outdoor activities."}
            ]

            response = client.chat.completions.create(
                model="gpt-4.1",
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )

            msg = response.choices[0].message

            # Step 2: Check if OpenAI wants to call the weather tool
            if msg.tool_calls:
                tool_call = msg.tool_calls[0]
                arguments = json.loads(tool_call.function.arguments)
                location = arguments.get("location", "Syracuse, NY, US")

                # Call the actual weather function
                weather_data = get_current_weather(location, OPENWEATHER_API_KEY)

                # Display the weather data
                st.subheader(f"Current Weather in {weather_data['location']}")
                st.write(f"Temperature: {weather_data['temperature']}°F")
                st.write(f"Feels Like: {weather_data['feels_like']}°F")
                st.write(f"High: {weather_data['temp_max']}°F | Low: {weather_data['temp_min']}°F")
                st.write(f"Humidity: {weather_data['humidity']}%")

                st.divider()

                # Step 3: Send the weather data back to OpenAI for suggestions
                messages.append(msg)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(weather_data)
                })

                second_response = client.chat.completions.create(
                    model="gpt-4.1",
                    messages=messages
                )

                # Display the suggestions
                st.subheader("What to Wear & Things to Do")
                st.write(second_response.choices[0].message.content)

        except Exception as e:
            st.error(f"Error: {e}")

            