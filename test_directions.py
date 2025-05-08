import requests

# Replace this with your actual API key
API_KEY = "AIzaSyA04jUJc3adR32G_iZ17GYYkEObdOcYb1s"

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

# Check if the response is OK
if data['status'] == 'OK':
    route = data['routes'][0]['legs'][0]
    print("Route Summary:")
    print(f"Start Address: {route['start_address']}")
    print(f"End Address: {route['end_address']}")
    print(f"Duration: {route['duration']['text']}")
    print(f"Distance: {route['distance']['text']}")
    print("\nStep-by-step directions:")

    for step in route['steps']:
        instruction = step['html_instructions']
        instruction_clean = instruction.replace('<b>', '').replace('</b>', '').replace('<div style="font-size:0.9em">', ' ').replace('</div>', '')
        print(f"- {instruction_clean} ({step['distance']['text']})")

else:
    print(f"Error with API request: {data['status']}")
