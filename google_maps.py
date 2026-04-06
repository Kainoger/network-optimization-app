import requests

def geocode_address(address, api_key):
    """
    Geocodes an address string into (Latitude, Longitude) using Google Maps API.
    """
    if not address or not api_key:
        return None
    
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": api_key
    }
    
    try:
        response = requests.get(base_url, params=params)
        data = response.json()
        
        if data["status"] == "OK":
            location = data["results"][0]["geometry"]["location"]
            return location["lat"], location["lng"]
        else:
            return None
    except Exception as e:
        print(f"Error geocoding: {e}")
        return None