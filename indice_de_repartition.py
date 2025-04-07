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

def indice_repartition(n_v,c,a):
    if n_v == 6:
        return 0
    else:
        return a * ((n_v - 6) / 6) + (1 - a) * ((max_capacity - c) / max_capacity)

coords = np.array([[s['lat'], s['lon']] for s in stations_data])
tri = Delaunay(coords)
# Calculer le degré de chaque sommet
degrees = np.zeros(len(stations_data))
for simplex in tri.simplices:
    for vertex in simplex:
        degrees[vertex] += 1


# Créer une carte centrée sur Paris
m = folium.Map(location=[48.8566, 2.3522], zoom_start=11)

# Ajouter des marqueurs pour chaque station avec un rayon proportionnel à la capacité
for i, station in enumerate(stations_data):
    indice = indice_repartition(degrees[i], station['capacity'], 0.5)
    folium.CircleMarker(
        location=[station['lat'], station['lon']],
        radius=station['capacity'] // 4,
        color='blue',
        weight=1,
        fill=True,
        fill_color='blue',
        fill_opacity=0.6,
        popup=f"Indice: {indice:.2f}"
    ).add_to(m)

for simplex in tri.simplices:
    triangle = coords[simplex]
    # On boucle pour fermer le triangle
    co = triangle.tolist() + [triangle[0].tolist()]
    folium.PolyLine(co, color="red", weight=2.5).add_to(m)

# Sauvegarder la carte dans un fichier HTML
m.save('velib_stations_map_indices.html')
