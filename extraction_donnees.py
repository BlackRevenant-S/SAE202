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

# Trouver la capacité max pour normaliser les tailles
max_capacity = max(station['capacity'] for station in stations_data)

# Créer une carte centrée sur Paris
m = folium.Map(location=[48.8566, 2.3522], zoom_start=11)

# Ajouter des marqueurs pour chaque station avec un rayon proportionnel à la capacité
for station in stations_data:
    normalized_radius = (station['capacity'] / max_capacity) * 10  # Rayon max = 10
    folium.CircleMarker(
        location=[station['lat'], station['lon']],
        radius=normalized_radius,
        color='blue',
        weight=1,
        fill=True,
        fill_color='blue',
        fill_opacity=0.6
    ).add_to(m)

# Sauvegarder la carte dans un fichier HTML
m.save('velib_stations_map.html')
