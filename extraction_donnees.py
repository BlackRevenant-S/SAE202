import json
import folium
from folium.plugins import MarkerCluster
import numpy as np
from scipy.spatial import Delaunay
from scipy.spatial.distance import cdist

# Lire les données des stations depuis un fichier JSON
json_file = "station_information.json"
with open(json_file, 'r', encoding='UTF-8') as file:
    velib = json.load(file)
# Extraire de la structure JSON les informations des stations
stations_data = velib['data']['stations']

# Créer une carte centrée sur Paris
m = folium.Map(location=[48.8566, 2.3522], zoom_start=11)
# Ajouter des marqueurs pour chaque station
for station in stations_data:
    folium.CircleMarker(
    location=[station['lat'], station['lon']],
    radius=station['capacity']//4,
    color='blue',
    weight=1,
    fill=True,
    fill_color='blue'
    ).add_to(m)
# Sauvegarder la carte dans un fichier HTML
m.save('velib_stations_map.html')