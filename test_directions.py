import requests
import polyline 
import math

# Replace this with your actual API key
API_KEY = ""

# Example start and end locations
start_location = "Nashville, TN"
end_location = "Atlanta, GA"

# Build the request URL
url = "https://maps.googleapis.com/maps/api/directions/json"
params = {
    "origin": start_location,
    "destination": end_location,
    "key": API_KEY
}

# Send the request
response = requests.get(url, params=params)
data = response.json()

coordinates = []
places = []
weatherOfPlace = []

def assignment(points, totalTime):
    num_points = len(points)
    print(num_points)
    points_per_second = num_points / totalTime
    points_per_hour = points_per_second * 3600
    points_per_hour = math.floor(points_per_hour)
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
    return None

# Check if the response is OK
if data['status'] == 'OK':
    routePolyline = data['routes'][0]['overview_polyline']['points']
    total_duration_seconds = data['routes'][0]['legs'][0]['duration']['value']

    coordinates = decodePolyline(routePolyline, total_duration_seconds)

    for i, coordinate in enumerate(coordinates):
        places.append([reverseGeocoding(coordinate), i])

    ## Uncomment line 80 and 84, and comment out 81 when working on weather portion
    for place in places:
        #weatherOfPlace.append(weatherAPICall(place[0], place[1]))
        print(place)

    #for item in weatherOfPlace:
    #    print(item)
else:
    print(f"Error with API request: {data['status']}")