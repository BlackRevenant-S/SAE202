import json
import folium
from folium.plugins import MarkerCluster
import numpy as np
from scipy.spatial import Delaunay
from scipy.spatial.distance import cdist
from collections import defaultdict


# Lire les données des stations depuis un fichier JSON
json_file = "station_information.json"
with open(json_file, 'r', encoding='UTF-8') as file:
    velib = json.load(file)

# Extraire de la structure JSON les informations des stations
stations_data = velib['data']['stations']

# Trouver la capacite max pour normaliser les tailles
max_capacity = max(station['capacity'] for station in stations_data)

# Créer une carte centrée sur Paris
m = folium.Map(location=[48.8566, 2.3522], zoom_start=11)



# Obtention des coordonnées de chaque station (en liste)

coords = np.array([[s['lat'], s['lon']] for s in stations_data])


# Utilisation de Delaunay

tri = Delaunay(coords)


# Calculer le degré de chaque sommet (nombre d'arretes d'un sommet)
degrees = np.zeros(len(stations_data))
for simplex in tri.simplices:
    for vertex in simplex:
        degrees[vertex] += 1


# formule de l'indice de répartition 
# n_v : nombre de stations voisines
# c : capacité de la station
# a : facteur de ponderation (a appartient a [0,1] )

def indice_repartition(n_v,c,a):
    if n_v == 6:
        return 0
    else:
        return a * ((n_v - 6) / 6) + (1 - a) * ((max_capacity - c) / max_capacity)
    



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


# Tracement des lignes

for simplex in tri.simplices:
    triangle = coords[simplex]

    # On boucle pour fermer le triangle
    co = triangle.tolist() + [triangle[0].tolist()]
    folium.PolyLine(co, color="red", weight=2.5).add_to(m)


# Initialiser la liste d'adjacence
liste_adjacence = defaultdict(set)  # set pour enlever tout les doublons

# Traduit les indice utilisés dans tri.simplices en IDs de stations
index_to_id = [station['station_id'] for station in stations_data]

for simplex in tri.simplices:
    for i in range(3):
        for j in range(i + 1, 3):
            a, b = simplex[i], simplex[j]
            id_a = index_to_id[a]
            id_b = index_to_id[b]

            # Ajouter la connexion dans les deux sens (graphe non orienté)
            liste_adjacence[id_a].add(id_b)
            liste_adjacence[id_b].add(id_a)

# Convertir les ensembles en listes
liste_adjacence = {k: list(v) for k, v in liste_adjacence.items()}

# debugging # 
# print(liste_adjacence)




















# Sauvegarder la carte dans un fichier HTML
m.save('velib_stations_map.html')





# Legende qui sera ajouté a la fin du fichier html
legend = """
<html>
    <legend>

        <img src="img/trait rouge.png" alt="trait rouge" width="60" height="30">
        <p>
            : Trait Delaunay
        </p>
            <br>
        <img src="img/point bleu.png" alt="point bleu" width="36" height="30">

        <p>
            : Station Velib
        </p>

    

    </legend>

    <style>
        legend{
            position: fixed;
            bottom: 0px;
            left: 6px;
            width: 300px;
            background-color: white;
            z-index:999;
            border:solid;
            border-color: rgb(0, 0, 0);
            border-width: 3 px;   
        }

        img,p{
            display:inline;
            margin: 10px;
        }
            </style>

<html>
    """



# ajout de la legende !! TOUJOUR EN DERNIER
f = open("velib_stations_map.html", "a")
f.write(legend)
f.close()
