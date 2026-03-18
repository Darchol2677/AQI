from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Open-Meteo APIs (Free, no API key required)
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
AQI_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

def get_aqi_category(aqi):
    """Returns category, health advice, and color code based on US AQI standard."""
    if aqi <= 50:
        return "Good", "Air quality is satisfactory. Air pollution poses little or no risk.", "#00e400"
    elif aqi <= 100:
        return "Moderate", "Air quality is acceptable. However, there may be a risk for some people, particularly those who are unusually sensitive to air pollution.", "#ffff00"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups", "Members of sensitive groups may experience health effects. The general public is less likely to be affected.", "#ff7e00"
    elif aqi <= 200:
        return "Unhealthy", "Some members of the general public may experience health effects; members of sensitive groups may experience more serious health effects.", "#ff0000"
    elif aqi <= 300:
        return "Very Unhealthy", "Health alert: The risk of health effects is increased for everyone.", "#8f3f97"
    else:
        return "Hazardous", "Health warning of emergency conditions: everyone is more likely to be affected.", "#7e0023"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/result')
def result():
    city = request.args.get('city')
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    
    try:
        city_name = city
        # If city name is provided, use Geocoding API to get coordinates
        if city:
            geo_response = requests.get(f"{GEOCODING_URL}?name={city}&count=1&language=en&format=json")
            geo_data = geo_response.json()
            
            if not geo_data.get("results"):
                return render_template('result.html', error=f"City '{city}' not found. Please try another search.")
            
            location = geo_data["results"][0]
            lat = location["latitude"]
            lon = location["longitude"]
            country = location.get("country", "")
            city_name = f"{location['name']}, {country}" if country else location['name']
        
        # If auto-detect location was used (lat/lon provided directly)
        elif lat and lon:
            lat = round(float(lat), 4)
            lon = round(float(lon), 4)
            city_name = f"Your Location ({lat}, {lon})"
            
        else:
            return render_template('result.html', error="Please provide a city name or use location auto-detect.")
            
        # Fetch AQI data using coordinates
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "us_aqi,pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone",
            "hourly": "us_aqi",
            "timezone": "auto"
        }
        
        aqi_response = requests.get(AQI_URL, params=params)
        aqi_response.raise_for_status() # Raise exception for bad status codes
        aqi_data = aqi_response.json()
        
        current_data = aqi_data.get("current", {})
        hourly_data = aqi_data.get("hourly", {})
        
        if "us_aqi" not in current_data or current_data["us_aqi"] is None:
            return render_template('result.html', error="AQI data is currently unavailable for this specific location.")
            
        aqi_val = current_data["us_aqi"]
        category, advice, color = get_aqi_category(aqi_val)
        
        # Format pollutants data
        pollutants = {
            "PM2.5": {"value": current_data.get("pm2_5"), "unit": "μg/m³"},
            "PM10": {"value": current_data.get("pm10"), "unit": "μg/m³"},
            "Carbon Monoxide (CO)": {"value": current_data.get("carbon_monoxide"), "unit": "μg/m³"},
            "Nitrogen Dioxide (NO2)": {"value": current_data.get("nitrogen_dioxide"), "unit": "μg/m³"},
            "Sulphur Dioxide (SO2)": {"value": current_data.get("sulphur_dioxide"), "unit": "μg/m³"},
            "Ozone (O3)": {"value": current_data.get("ozone"), "unit": "μg/m³"}
        }
        
        # Format graph data (next 24 hours of forecast)
        graph_data = {
            "time": hourly_data.get("time", [])[:24],
            "aqi": hourly_data.get("us_aqi", [])[:24]
        }
        
        return render_template('result.html', 
                             city=city_name,
                             aqi=aqi_val, 
                             category=category, 
                             advice=advice, 
                             color=color,
                             pollutants=pollutants,
                             graph_data=graph_data)
                             
    except requests.exceptions.RequestException as e:
        return render_template('result.html', error="Failed to connect to the weather service. Please try again later.")
    except Exception as e:
        return render_template('result.html', error=f"An unexpected error occurred: {str(e)}")

if __name__ == '__main__':
    # Run the application
    app.run(debug=True, port=5000)
