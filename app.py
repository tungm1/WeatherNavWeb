from flask import Flask, request, render_template
import requests
import polyline  # may need pip install polyline
import math
from datetime import datetime, timedelta


app = Flask(__name__)

# Replace this with your actual API key
NAV_API_KEY = "AIzaSyA04jUJc3adR32G_iZ17GYYkEObdOcYb1s"
WEATHER_API_KEY = "1f33fe4e224a0b645d433ffcda45f5dd"
coordinates = []       # Every coordinate in coordinates is in one hour intervals along the route
places = []            # places is the physical locations of all items in coordinates
weatherOfPlace = []    # weatherOfPlace stores the weather for each place
cachedCities = {}      # cachedCities checks to avoid redundant Google API calls

def assignment(points, totalTime):
    num_points = len(points)
    points_per_second = num_points / totalTime
    points_per_hour = points_per_second * 3600
    points_per_hour = math.floor(points_per_hour)
    if points_per_hour == 0:
        points_per_hour = 1
    reducedPoints = []
    for i in range(0, len(points), points_per_hour):
        reducedPoints.append(points[i])
    return reducedPoints

# Returns a list of coordinates that are x number of hours apart
def decodePolyline(polyline_str, totalTime):
    points = polyline.decode(polyline_str)
    return assignment(points, totalTime)

def reverseGeocoding(coordinate):
    # Build the request URL
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "latlng": f"{coordinate[0]},{coordinate[1]}",
        "key": NAV_API_KEY,
    }

    # Send the request
    response = requests.get(url, params=params)
    data = response.json()

    if data['status'] != 'OK' or not data['results']:
        return "Unknown location"

    for component in data["results"][0]["address_components"]:
        if "locality" in component["types"] or "administrative_area_level_2" in component["types"]:
            return component["long_name"]

    return data["results"][0]["formatted_address"]

def weatherAPICall(coordinate, time, start_time_utc=None):
    if start_time_utc is None:
        start_time_utc = datetime.utcnow()

    # Target time = start of trip + N hours
    target_time_utc = start_time_utc + timedelta(hours=time)

    url = "https://api.openweathermap.org/data/3.0/onecall"
    params = {
        "lat": coordinate[0],
        "lon": coordinate[1],
        "appid": WEATHER_API_KEY,
        "units": "imperial",  # Or "metric" for Celsius
        "exclude": "minutely,daily,current,alerts"
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "hourly" not in data:
        return f"{coordinate}: No hourly forecast data available"

    timezone_offset = data.get("timezone_offset", 0)  # seconds

    # Find forecast closest to target_time_utc
    closest = None
    min_diff = float('inf')

    for forecast in data["hourly"]:
        forecast_time_utc = datetime.utcfromtimestamp(forecast["dt"])
        diff = abs((forecast_time_utc - target_time_utc).total_seconds())
        if diff < min_diff:
            min_diff = diff
            closest = forecast

    if not closest:
        return f"{coordinate}: No matching forecast found"

    temp = closest["temp"]
    desc = closest["weather"][0]["description"].capitalize()

    # Convert target_time_utc to local time using timezone_offset
    arrival_time_local = target_time_utc + timedelta(seconds=timezone_offset)
    arrival_str = arrival_time_local.strftime("%-I %p")  # e.g., "3 PM"

    return f"{arrival_str}: {round(temp)}°F, {desc}"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        start = request.form.get('start')
        end = request.form.get('end')
        print(f"Start: {start}")
        print(f"End: {end}")

        url = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            "origin": start,
            "destination": end,
            "key": NAV_API_KEY
        }

        response = requests.get(url, params=params)
        data = response.json()

        if data['status'] == 'OK':
            route = data['routes'][0]['legs'][0]
            startEndCity = route['start_address'] + " " + route['end_address']

            weatherOfPlace.clear()

            if startEndCity in cachedCities:
                places[:] = cachedCities[startEndCity]
                print("Used cached city list.")
            else:
                routePolyline = data['routes'][0]['overview_polyline']['points']
                total_duration_seconds = route['duration']['value']
                coordinates[:] = decodePolyline(routePolyline, total_duration_seconds)

                print(len(coordinates))  # For debugging: number of 1-hour interval points

                places.clear()
                for i, coordinate in enumerate(coordinates):
                    city = reverseGeocoding(coordinate)
                    print(city)  # Print city at each hourly interval
                    places.append([city, i])

                cachedCities[startEndCity] = places.copy()

                start_time_utc = datetime.utcnow()

                for i in range(len(coordinates)):
                    city, hour = places[i]
                    forecast_str = weatherAPICall(coordinates[i], hour, start_time_utc)
                    print(f"{city} (+{hour}h): {forecast_str}")

            return f"Processed {len(weatherOfPlace)} weather points. Check terminal output."

        else:
            return f"Google API error: {data['status']}"

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)