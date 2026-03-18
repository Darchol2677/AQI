from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Open-Meteo APIs (Free, no API key required)
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
AQI_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"


# ✅ FIXED INDENTATION HERE
def get_aqi_category(aqi):
    """Returns category, health advice, and color code based on US AQI standard."""
    if aqi <= 50:
        return "Good", "Air quality is satisfactory. Air pollution poses little or no risk.", "#00e400"
    elif aqi <= 100:
        return "Moderate", "Air quality is acceptable. Some people may be sensitive.", "#ffff00"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups", "Sensitive groups may experience health effects.", "#ff7e00"
    elif aqi <= 200:
        return "Unhealthy", "Everyone may begin to experience health effects.", "#ff0000"
    elif aqi <= 300:
        return "Very Unhealthy", "Health alert: everyone may experience serious effects.", "#8f3f97"
    else:
        return "Hazardous", "Emergency conditions: everyone is affected.", "#7e0023"


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

        # 🔹 If city is provided → get coordinates
        if city:
            geo_response = requests.get(
                f"{GEOCODING_URL}?name={city}&count=1&language=en&format=json"
            )
            geo_data = geo_response.json()

            if not geo_data.get("results"):
                return render_template('result.html', error=f"City '{city}' not found.")

            location = geo_data["results"][0]
            lat = location["latitude"]
            lon = location["longitude"]
            country = location.get("country", "")
            city_name = f"{location['name']}, {country}"

        # 🔹 If lat/lon provided (auto-detect)
        elif lat and lon:
            lat = float(lat)
            lon = float(lon)
            city_name = f"Your Location ({lat}, {lon})"

        else:
            return render_template('result.html', error="Enter city or allow location access.")

        # 🔹 Fetch AQI
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "us_aqi,pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone",
            "hourly": "us_aqi",
            "timezone": "auto"
        }

        aqi_response = requests.get(AQI_URL, params=params)
        aqi_response.raise_for_status()
        aqi_data = aqi_response.json()

        current_data = aqi_data.get("current", {})
        hourly_data = aqi_data.get("hourly", {})

        if "us_aqi" not in current_data or current_data["us_aqi"] is None:
            return render_template('result.html', error="AQI not available.")

        aqi_val = current_data["us_aqi"]
        category, advice, color = get_aqi_category(aqi_val)

        # 🔹 Pollutants
        pollutants = {
            "PM2.5": current_data.get("pm2_5"),
            "PM10": current_data.get("pm10"),
            "CO": current_data.get("carbon_monoxide"),
            "NO2": current_data.get("nitrogen_dioxide"),
            "SO2": current_data.get("sulphur_dioxide"),
            "O3": current_data.get("ozone")
        }

        # 🔹 Graph Data
        graph_data = {
            "time": hourly_data.get("time", [])[:24],
            "aqi": hourly_data.get("us_aqi", [])[:24]
        }

        return render_template(
            'result.html',
            city=city_name,
            aqi=aqi_val,
            category=category,
            advice=advice,
            color=color,
            pollutants=pollutants,
            graph_data=graph_data
        )

    except requests.exceptions.RequestException:
        return render_template('result.html', error="API connection failed.")
    except Exception as e:
        return render_template('result.html', error=str(e))


if __name__ == '__main__':
    app.run(debug=True)
