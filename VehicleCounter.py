from collections import defaultdict
import cv2


class VehicleCounter:
    def __init__(self, line_points):
        self.line_points = line_points  # [(x1, y1), (x2, y2)]
        self.tracks = {}
        self.counts = defaultdict(int)

        x1, y1, x2, y2 = line_points  # coefficients pour y = ax + b
        self.a = (y2 - y1) / (x2 - x1) if x2 != x1 else float('inf')  # Pente
        self.b = y1 - self.a * x1  # Intercept

        self.next_id = 1  # Compteur pour generer de nouveaux IDs

    def get_side(self, x, y):
        """
        Détermine de quel côté de la ligne se trouve un point (x, y).
        :param x: x
        :param y: y
        :return: closest_id, positif si au dessus de la ligne, négatif si en dessous, 0 (peu probable) si sur la ligne
        """
        return y - (self.a * x + self.b)

    def get_closest_track(self, cx, cy, max_distance=50):
        """
        Retourne l'id de la détection la plus proche, pour pas que les objets perdent leur id entre les frames
        :param cx: x centre
        :param cy: y centre
        :param max_distance: rayon de recherche, en pixels
        :return: id de la détection la plus proche sinon None
        """
        closest_id = None
        min_distance = float('inf')

        for obj_id, track_data in self.tracks.items():
            prev_cx, prev_cy = track_data["center"]
            distance = ((cx - prev_cx) ** 2 + (cy - prev_cy) ** 2) ** 0.5
            if distance < min_distance and distance < max_distance:
                closest_id = obj_id
                min_distance = distance

        return closest_id

    def update_tracks(self, detections, frame, objects_list):
        """
        Met à jour les chemins des objets détectés et dessine les bounding box, leur centre etc. sur l'image ainsi que la ligne de threshold
        :param objects_list:
        :param detections: toutes les détections actuelles
        :param frame: l'image actuelle
        :return: la frame avec les infos supplémentaires
        """
        current_tracks = {}
        for result in detections:  # pour chaque objet precedemment détecté
            for box, cls in zip(result.boxes.xyxy.cpu().numpy(), result.boxes.cls.cpu().numpy()):
                x1, y1, x2, y2 = box.astype(int)
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2  # centres

                # associer ou créer un nouvel ID
                closest_id = self.get_closest_track(cx, cy)
                if closest_id:  # si l'objet était déjà présent dans la frame d'avant, on fait suivre l'id
                    current_tracks[closest_id] = {"center": (cx, cy), "side": self.get_side(cx, cy), "class": int(cls)}
                else:  # si c'est nouveau on assigne un nouvel id
                    current_tracks[self.next_id] = {"center": (cx, cy), "side": self.get_side(cx, cy),
                                                    "class": int(cls)}
                    closest_id = self.next_id
                    self.next_id += 1

                # dessine les bounding boxes et ids sur la frame
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)
                cv2.putText(frame, f"ID: {closest_id}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)


        # ======== IMPORTANT =======
        # vérifie les traversées de la ligne rouge
        for obj_id, data in current_tracks.items():  # pour toutes les détections sur la frame actuelle
            if obj_id in self.tracks:  # si l'objet est déjà suivi
                prev_side = self.tracks[obj_id]["side"]
                curr_side = data["side"]
                if prev_side * curr_side < 0:  # traversée détectée
                    direction = "up" if curr_side < 0 else "down"
                    class_number = data["class"]
                    self.counts[f"{objects_list[class_number]}_{direction}"] += 1

            self.tracks[obj_id] = data  # met à jour les tracks

        self.tracks = {key: value for key, value in self.tracks.items() if key in current_tracks} # on clean les tracks perdues

        # afficher les compteurs dans un coin
        for idx, (key, value) in enumerate(self.counts.items()):
            cv2.putText(frame, f"{key}: {value}", (10, 30 + idx * 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        x1, y1, x2, y2 = self.line_points
        cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)  # tracer la ligne de threshold

        return frame
