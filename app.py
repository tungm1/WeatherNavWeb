from flask import Flask, request, render_template
import requests
import polyline  # may need pip install polyline
import math

app = Flask(__name__)

# Replace this with your actual API key
API_KEY = "AIzaSyA04jUJc3adR32G_iZ17GYYkEObdOcYb1s"

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
        "key": API_KEY,
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

def weatherAPICall(place, time):
    # Placeholder: this function will be used to query weather at a given location and hour
    # Your friend can plug in OpenWeatherMap (or similar) here
    return None

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
            "key": API_KEY
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

            for place in places:
                #weatherOfPlace.append(weatherAPICall(place[0], place[1]))
                print(place)

            #for item in weatherOfPlace:
            #    print(item)

            return f"Processed {len(weatherOfPlace)} weather points. Check terminal output."

        else:
            return f"Google API error: {data['status']}"

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)