# Vehicle Counting with YOLO11 and Flask Dashboard
## Description
Ce mini projet utilise le modèle YOLO11 pour détecter et compter les véhicules (voitures, camions, vélos, etc.) passant sur une vidéo, qu'elle soit en direct ou préenregistrée. Les statistiques issues de cette analyse sont ensuite affichées sur un dashboard interactif via une interface web développée avec Flask.
  
L'application différencie également :
- Le sens de passage des véhicules.
- Le type de véhicule détecté.

![image1.png](readme_imgs/image1.png)
<img src="readme_imgs/image2.png" alt="dashboard" width="800">

## Installation   
Cloner le repo :  
`git clone https://github.com/eltar14/projet-comptage.git`

Créer un venv :  
`python -m venv venvcomptage`
puis  
`source venvcomptage/bin/activate` (Linux/Mac)  
`.\venvcomptage\Scripts\activate` (Windows) 


Installer les dépendances  
`pip install -r requirements.txt`

Il vous faudra aussi télécharger une vidéo avec des voitures qui passent : 
[https://www.youtube.com/watch?v=e_WBuBqS9h8](https://www.youtube.com/watch?v=e_WBuBqS9h8)


## Lancer l'application 
`python main.py`  
L'application lancera deux processus en parallèle :

- L'API Flask (appel via [http://localhost:5000/counts](http://localhost:5000/counts)).
- La boucle de détection et de suivi des véhicules

Une fenêtre s'ouvrira pour afficher les détections en direct avec les bounding boxes et les trajectoires des véhicules détectés.  
Vous pouvez accéder aux statistiques via le dashboard à l'URL suivante :
[index.html](web/index.html) (dans web/).

Remarque : YOLO11n.pt a été inclus dans le repo en raison de son poids léger mais il est recommandé d'utiliser une version plus puissante comme yolo11m.pt

## Configuration avancée
### Ajuster la ligne de comptage  
La ligne de comptage des véhicules est définie par des coordonnées dans la variable *line_points*. Modifiez ces coordonnées pour l'adapter à votre vidéo :  
`line_points = (0, 330, 640, 160)  # x1, y1, x2, y2`

### Documentation des endpoints API
- `GET /counts`  
Renvoie les statistiques des véhicules comptés sous format JSON.
  
Exemple de réponse :  
```json
{
  "data": {
    "car_down": 40,
    "car_up": 21,
    "truck_down": 2
  }
}
```


## Choix techniques  
### YOLO11 pour la détection d'objets
Le choix de YOLO (You Only Look Once) repose sur ses performances en détection d'objets en temps réel.

- Pourquoi YOLO11 ? :  
YOLO11 offre un bon compromis entre rapidité et précision grâce à ses améliorations par rapport aux versions précédentes (meilleure gestion des petites détections, optimisations mémoire).

### OpenCV pour la manipulation vidéo
OpenCV permet une gestion efficace des flux vidéo en direct ou en différé :  
- Capture et décodage des frames vidéo.
- Manipulations diverses comme le redimensionnement, les masques ou l'annotation des images avec les bounding boxes des véhicules détectés.


### Flask pour l'interface web
Flask est un micro-framework léger et rapide, idéal pour une application web simple :  
- Serveur HTTP pour afficher le dashboard.
- Gestion des endpoints pour envoyer les données de détection et les statistiques au front-end.

### Plotly pour des graphiques  
Plotly permet de créer des graphiques interactifs directement dans le navigateur :
- Visualisation dynamique des types de véhicules détectés.
- Statistiques sur le sens de passage des véhicules.
- Et bien d'autres en fonction du besoin  

## Fonctionnalités

- Détection en temps réel ou sur des vidéos enregistrées.
- Affichage des statistiques sous forme de graphiques interactifs sur le dashboard.
- Différenciation des types de véhicules (camions, voitures, vélos).
- Calcul du trafic selon le sens de passage.

## Principal défi du projet : tracking des véhicules 

Le tracking des véhicules est le principal défi de ce projet. Il consiste à suivre chaque véhicule entre les frames d'une vidéo afin de détecter lorsqu'il traverse une ligne virtuelle et compter ces traversées selon leur direction.

### Principes Clés
- Identifiants uniques (IDs) : chaque véhicule détecté se voit attribuer un identifiant unique qui permet de le suivre entre les frames.
- Association des détections : pour chaque nouvelle détection, l'algorithme recherche la détection précédente la plus proche (en utilisant une distance maximale de 50 pixels) afin de maintenir la cohérence de l'identifiant attribué au véhicule.
- Vérification de traversée de ligne : une ligne de seuil est définie sur l'image. Si un véhicule passe d'un côté à l'autre de cette ligne, une traversée est enregistrée.
- Compteurs par type de véhicule et direction : les traversées sont catégorisées par type de véhicule (camion, voiture, vélo, etc.) et direction (haut/bas ou gauche/droite selon l'orientation de la ligne).



### Défis Techniques
Le tracking des véhicules constitue le principal défi de ce projet. L'objectif est de suivre chaque véhicule entre les frames d'une vidéo afin de détecter lorsqu'il traverse une ligne virtuelle et de compter ces traversées selon leur direction.

Pour y parvenir, plusieurs solutions ont été mises en place afin de répondre aux contraintes techniques liées au tracking en vision artificielle .


### Attribution d'identifiants uniques (IDs)
**Problème** :  
Lorsqu'un véhicule est détecté, il faut être capable de le reconnaître sur les frames suivantes pour savoir si c'est toujours le même objet.

**Solution** :  
Chaque détection reçoit un identifiant unique attribué lors de sa première apparition. Ce numéro permet de suivre ce même véhicule tout au long de sa trajectoire.

**Pourquoi cette solution** :
- Cela évite de compter plusieurs fois un même véhicule qui reste dans la scène.
- C'est essentiel pour vérifier si un véhicule a traversé la ligne virtuelle ou non.

### Association des détections (matching spatial)
**Problème** :  
Il est possible que la position d'un véhicule change légèrement d'une frame à l'autre (par exemple, en raison de son déplacement naturel). Il faut donc associer chaque nouvelle détection à une détection précédente.

**Solution** :  
Pour chaque nouvelle détection, l'algorithme calcule la distance entre le centre de la bounding box actuelle et le centre des bounding boxes des frames précédentes. Si la distance est inférieure à un seuil (50 pixels), la détection est associée à l'identifiant le plus proche.

**Pourquoi cette solution** :  
- Cette méthode minimise le risque de perdre l'identifiant d'un véhicule lorsqu'il se déplace rapidement ou que sa détection est légèrement décalée.
- L'utilisation d'une distance maximale permet de limiter les mauvaises associations (comme assigner un ID à un objet complètement différent).


### Vérification des traversées de ligne
**Problème** :  
Le simple suivi d'un véhicule ne suffit pas : il faut détecter quand il traverse une ligne virtuelle (par exemple, une ligne imaginaire sur la route).

**Solution** :  
La solution repose sur la position du centre du véhicule par rapport à une équation de droite `y = ax+b`. Si le signe de la distance entre le centre et la ligne change (de positif à négatif ou inversement), cela signifie que le véhicule a traversé la ligne.

**Pourquoi cette solution** :
- Cette approche mathématique simple fonctionne.
- En vérifiant uniquement le changement de signe, on capture des traversées sans avoir besoin d'une logique complexe de détection continue.

### Nettoyage des tracks perdus
**Problème** :  
Les véhicules qui sortent de la scène ou ne sont plus détectés doivent être supprimés pour éviter de maintenir inutilement des objets fantômes dans la mémoire.

**Solution** :  
Les objets non détectés durant un certain nombre de frames consécutives sont supprimés de la liste des tracks. 

**Pourquoi cette solution** :
- Cela maintient une gestion efficace de la mémoire.
- Éviter de suivre des objets fantômes réduit les erreurs de comptage.



Le tracking des véhicules repose sur une combinaison de méthodes simples mais efficaces : association spatiale des détections, suivi des IDs, détection des traversées et nettoyage dynamique des objets perdus. Ces solutions permettent une gestion robuste et précise des véhicules dans une scène dynamique, offrant ainsi une base solide pour des applications de comptage et d'analyse du trafic.


## Améliorations possibles
- Amélioration du tracking des véhicules (qui est actuellement rudimentaire)
- Ajout de prédictions avancées : détection d'événements anormaux dans le trafic (embouteillages, contre-sens).
- Exportation des données : ajouter la possibilité de sauvegarder les résultats au format CSV.