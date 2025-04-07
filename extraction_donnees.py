import json
import folium
from folium.plugins import MarkerCluster
import numpy as np
from scipy.spatial import Delaunay,Voronoi
from scipy.spatial.distance import cdist
from collections import defaultdict

maximum_indice = 0.7017543859649122 
minimum_indice = -0.07017543859649122

indice_total = 0.77192982456

# -------------------------
# Collecte des données
# -------------------------

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


# -------------------------
# Graphe des stations avec Delaunay
# -------------------------



# formule de l'indice de répartition 
# n_v : nombre de stations voisines
# c : capacité de la station
# a : facteur de ponderation (a appartient a [0,1] )
    

def indice_repartition(n_v,c,a):
    if n_v == 6:
        return 0
    else:
        return a * ((n_v - 6) / 6) + (1 - a) * ((max_capacity - c) / max_capacity)

coords = np.array([[s['lat'], s['lon']] for s in stations_data])

tri = Delaunay(coords)
for simplex in tri.simplices:
    triangle = coords[simplex]
    # On boucle pour fermer le triangle
    co = triangle.tolist() + [triangle[0].tolist()]
    folium.PolyLine(co, color="red", weight=2.5).add_to(m)

# Calculer le degré de chaque sommet (nombre d'arretes d'un sommet)
degrees = np.zeros(len(stations_data))
for simplex in tri.simplices:
    for vertex in simplex:
        degrees[vertex] += 1

# Ajouter des marqueurs pour chaque station avec un rayon proportionnel à la capacité

for i, station in enumerate(stations_data):
    indice = indice_repartition(degrees[i], station['capacity'], 0.5)

    h = 0
    red = 255
    green = 120

    if indice < 0:
            red = 255
            green = 0


    else: 
        while indice > h:
            h = h + indice_total/(510 - 120)
        
            if green == 255:
           
                red = red -1

            else:
                green = green +1
        

    couleur = 'rgb('+str(red)+','+str(green)+',0)'

    folium.CircleMarker(
        location=[station['lat'], station['lon']],
        radius=station['capacity'] // 4,
        weight=1,
        color='black',
        fill=True,
        fill_color= couleur,
        fill_opacity=1,
        popup=f"Indice: {indice:.2f}"
    ).add_to(m)

# -------------------------
# Liste adjacente
# -------------------------

# Initialiser la liste d'adjacence avec distances
liste_adjacence = defaultdict(dict)  # dict pour stocker les distances associées à chaque voisin

# Associer les indices à leurs coordonnées et IDs
index_to_id = [station['station_id'] for station in stations_data]
index_to_coord = [ (station['lat'], station['lon']) for station in stations_data ]

# Calculer les distances et remplir la liste d’adjacence
for simplex in tri.simplices:
    for i in range(3):
        for j in range(i + 1, 3):
            a, b = simplex[i], simplex[j]
            id_a = index_to_id[a]
            id_b = index_to_id[b]

            # Calculer la distance géographique (euclidienne pour simplifier ici)
            coord_a = index_to_coord[a]
            coord_b = index_to_coord[b]
            distance = np.linalg.norm(np.array(coord_a) - np.array(coord_b))

            # Ajouter la connexion avec distance dans les deux sens (graphe non orienté)
            liste_adjacence[id_a][id_b] = distance
            liste_adjacence[id_b][id_a] = distance

# test
for station, voisins in list(liste_adjacence.items())[:5]:
    print(f"{station} :")
    for voisin, distance in voisins.items():
        print(f"    -> {voisin} ({distance:.4f})")


# -------------------------
# Algorithme de Kruskal
# -------------------------

# Étape 1 : Créer une liste d’arêtes avec les coûts (ici = distances)
edges = []
for station, voisins in liste_adjacence.items():
    for voisin, distance in voisins.items():
        if station < voisin:  # éviter les doublons (graphe non orienté)
            cost = distance  # ou cost = distance ** 2 si souhaité
            edges.append((cost, station, voisin))

# Étape 2 : Union-Find pour gérer les composantes connexes
parent = {}

def find(x):
    if parent[x] != x:
        parent[x] = find(parent[x])
    return parent[x]

def union(x, y):
    root_x = find(x)
    root_y = find(y)
    if root_x != root_y:
        parent[root_y] = root_x
        return True
    return False

# Initialisation des parents
nodes = liste_adjacence.keys()
for node in nodes:
    parent[node] = node

# Étape 3 : Appliquer Kruskal
edges.sort()  # tri croissant par coût
mst_edges = []

for cost, u, v in edges:
    if union(u, v):
        mst_edges.append((u, v, cost))

# Étape 4 : Visualisation sur la carte
id_to_coord = {station['station_id']: (station['lat'], station['lon']) for station in stations_data}
for u, v, _ in mst_edges:
    folium.PolyLine([id_to_coord[u], id_to_coord[v]], color="green", weight=3).add_to(m)

# Afficher le coût total
total_cost = sum(edge[2] for edge in mst_edges)
print(f"Coût total de l’arbre couvrant minimal : {total_cost:.4f}")


# -------------------------
# Graphe Voronoï
# -------------------------

# On utilise les coordonnées dans l'ordre (lon, lat), car Folium utilise cet ordre
points = np.array([[s['lon'], s['lat']] for s in stations_data])
vor = Voronoi(points)

# Dessiner les cellules de Voronoï
for ridge_vertices in vor.ridge_vertices:
    if -1 not in ridge_vertices:  # on ignore les arêtes infinies
        points = [vor.vertices[i] for i in ridge_vertices]
        # Repasser les coordonnées en (lat, lon) pour Folium
        points_latlon = [[lat, lon] for lon, lat in points]
        folium.PolyLine(points_latlon, color="orange", weight=1.5, opacity=0.7).add_to(m)


# -------------------------
# Visualisation
# -------------------------

# Sauvegarder la carte dans un fichier HTML
m.save('velib_stations_map.html')
    
# Legende qui sera ajouté a la fin du fichier html
legend = """
<html>
    <legend>

        <img src="img/station.png" alt="cercle noir" width="45" height="45">
        <p>
            : Station velib
        </p>
        <br>
    
        <section>
        <img src="img/spectre.png" alt="spectre" width="100" height="30">

    
            <p>
                : Vert = station en surdistribution 
            </p>
            <p id="lineup">
                Rouge = station en sous distribution
            </p>
            <br>
            

        </section>
            
        <img src="img/trait rouge.png" alt="trait rouge" width="60" height="30">
        <p>
            : Trait de la fonction Delaunay
        </p>
        <br>


        

    

    </legend>

    <style>
        legend{
            position: fixed;
            bottom: 0px;
            left: 6px;
            width: 400px;
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

        #lineup{
            position:relative;
            left:120px;
        }

     </style>

<html>
    """



# ajout de la legende !! TOUJOUR EN DERNIER
f = open("velib_stations_map.html", "a")
f.write(legend)
f.close()
