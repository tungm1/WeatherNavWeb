import requests
import polyline # may need pip install polyline
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

coordinates = [] # Every coordinate in coordinates is in one hour intervals along the route
cachedCities = {} # cachedCities checks to see that don't need to call the Google APIs again
places = [] # places is the physical locations of all items in coordinates
weatherOfPlace = [] # weatherOfPlace stores the weather for each place

def assignment(points, totalTime):
    num_points = len(coordinates)
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
        "result_type": "sublocality"
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
    # route = data['routes'][0]['legs'][0]
    # print("Route Summary:")
    # print(f"Start Address: {route['start_address']}")
    # print(f"End Address: {route['end_address']}")
    # print(f"Duration: {route['duration']['text']}")
    # print(f"Distance: {route['distance']['text']}")
    # print("\nStep-by-step directions:")

    # for step in route['steps']:
    #     instruction = step['html_instructions']
    #     instruction_clean = instruction.replace('<b>', '').replace('</b>', '').replace('<div style="font-size:0.9em">', ' ').replace('</div>', '')
    #     print(f"- {instruction_clean} ({step['distance']['text']})")
    route = data['routes'][0]['legs'][0]
    startEndCity = route['start_address'] + " " + route['end_address']
    if startEndCity in cachedCities:
        places = cachedCities[startEndCity]
    else:
        routePolyline = data['routes'][0]['overview_polyline']['points'] # Should be "points" in "overview_polyline"
        total_duration_seconds = route['duration']['value']
    
        coordinates = decodePolyline(routePolyline, total_duration_seconds)
    
        for i, coordinate in enumerate(coordinates):
            places.append([reverseGeocoding(coordinate), i])
        
        cachedCities[startEndCity] = places

    for place in places:
        weatherOfPlace.append(weatherAPICall(place[0], place[1]))

    for item in weatherOfPlace:
        print(item)
else:
    print(f"Error with API request: {data['status']}")
