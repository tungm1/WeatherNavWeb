import requests

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

## TODO: decoding routePolyline
# Returns a list of coordinates that are x number of hours apart
def decodePolyline(polyline):
    return None

def reverseGeocoding(coordinate):
    return None

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

    routePolyline = routePolyline = data['routes'][0]['overview_polyline']['points'] # Should be "points" in "overview_polyline"

    coordinates = decodePolyline(routePolyline)

    for coordinate in coordinates:
        time = 1 # We are assuming that each coordinate is another hour gone by
        places.append([reverseGeocoding(coordinate), time])
        time = time + 1
    
    for place in places:
        weatherOfPlace.append(weatherAPICall(place[0], place[1]))

    for item in weatherOfPlace:
        print(item)
else:
    print(f"Error with API request: {data['status']}")