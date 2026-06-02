import os
import requests
from dotenv import load_dotenv

# Load variables from the root .env file
load_dotenv()

API_KEY = os.environ.get("OPENWEATHER_API_KEY")
CITY = os.environ.get("TARGET_LOCATION") or "Lagos"

# We use the 5-day / 3-hour forecast API endpoint (available on the free tier)
url = f"https://api.openweathermap.org/data/2.5/forecast?q={CITY}&appid={API_KEY}&units=metric"

print(f"Fetching weather forecast for: {CITY}...")

try:
    response = requests.get(url)
    data = response.json()
    
    if response.status_code == 200:
        print("\n--- WEATHER CONNECTION SUCCESSFUL ---")
        print(f"City: {data['city']['name']}, {data['city']['country']}")
        
        # Pull the upcoming forecast entry from the list
        first_forecast = data['list'][0]
        time = first_forecast['dt_txt']
        temp = first_forecast['main']['temp']
        desc = first_forecast['weather'][0]['description']
        
        print(f"Expected Time: {time}")
        print(f"Temperature: {temp}°C")
        print(f"Condition: {desc.capitalize()}")
        print("--------------------------------------\n")
    else:
        print(f"\nAPI Error {response.status_code}: {data.get('message', 'Unknown error')}")
        if response.status_code == 401:
            print("💡 Tip: If your account is brand new, wait a few minutes for the API key to activate.")
            
except Exception as e:
    print(f"An error occurred: {e}")