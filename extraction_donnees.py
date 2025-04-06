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

# Ajouter des marqueurs pour chaque station avec un rayon proportionnel à la capacité
for station in stations_data:
    folium.CircleMarker(
        location=[station['lat'], station['lon']],
        radius=station['capacity'] // 4,
        color='blue',
        weight=1,
        fill=True,
        fill_color='blue',
        fill_opacity=0.6
    ).add_to(m)

#

coords = np.array([[s['lat'], s['lon']] for s in stations_data])

# Utilisation de Delaunay

tri = Delaunay(coords)

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

print(liste_adjacence)


# Sauvegarder la carte dans un fichier HTML
m.save('velib_stations_map.html')


# ajout de la legende

f = open("velib_stations_map.html", "a")
f.write(legend)
f.close()




# !!! IMPORTANT !!!
#
# Pour le reseau electrique (donc l'arbre de poid minimum)
# regarder la page 17 de SAE2.02-Présentation.pdf