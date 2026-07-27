import os
from dotenv import load_dotenv
import requests

load_dotenv()
MAPPLS_ACCESS_TOKEN = os.getenv("MAPPLS_ACCESS_TOKEN")

base_lat = 12.9716
base_lng = 77.5946

start_lat, start_lng = base_lat - 0.005, base_lng - 0.005
end_lat, end_lng = base_lat + 0.005, base_lng + 0.005

url = f"https://apis.mappls.com/advancedmaps/v1/{MAPPLS_ACCESS_TOKEN}/route_adv/driving/{start_lng},{start_lat};{end_lng},{end_lat}?geometries=geojson"
r = requests.get(url)
print("Status Code:", r.status_code)
if r.status_code == 200:
    data = r.json()
    if "routes" in data and len(data["routes"]) > 0:
        coords = data["routes"][0]["geometry"]["coordinates"]
        print(f"Got {len(coords)} coordinates from API")
        print("First coordinate:", coords[0])
    else:
        print("No routes found")
else:
    print("Error:", r.text)
