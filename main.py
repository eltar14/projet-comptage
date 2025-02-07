from ultralytics import YOLO
import cv2

from flask import Flask, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS
from threading import Thread

from VehicleCounter import VehicleCounter

counter_counts = {}  # objets détectés

app = Flask(__name__)
api = Api(app)
CORS(app)


class CountsAPI(Resource):
    def get(self):
        return jsonify({"data": counter_counts})


api.add_resource(CountsAPI, "/counts")



# pour mettre à jour les comptages dans un thread séparé
def count_loop(video_path):
    objects_list = [  # liste des classes COCO qui sert d'entraînement à YOLOv11
        "person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
        "trafficlight", "firehydrant", "streetsign", "stopsign", "parkingmeter", "bench", "bird",
        "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "hat",
        "backpack", "umbrella", "shoe", "eyeglasses", "handbag", "tie", "suitcase", "frisbee",
        "skis", "snowboard", "sportsball", "kite", "baseballbat", "baseballglove", "skateboard",
        "surfboard", "tennisracket", "bottle", "plate", "wineglass", "cup", "fork", "knife",
        "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli", "carrot", "hotdog",
        "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed", "mirror", "diningtable",
        "window", "desk", "toilet", "door", "tvmonitor", "laptop", "mouse", "remote", "keyboard",
        "cellphone", "microwave", "oven", "toaster", "sink", "refrigerator", "blender", "book",
        "clock", "vase", "scissors", "teddybear", "hairdrier", "toothbrush", "hairbrush"
    ]

    ids_to_keep_list = [i for i in range(1, 9)] # "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck"

    cap = cv2.VideoCapture(video_path)  # chemin vers la vidéo

    while cap.isOpened():  # pour chaque frame
        ret, frame = cap.read()
        if not ret:
            break

        # détection des véhicules
        results = model.predict(frame, conf=0.65, iou=0.3, save=False, verbose=False, classes=ids_to_keep_list)

        # maj des suivis et afficher les résultats
        frame = counter.update_tracks(results, frame, objects_list=objects_list)

        counter_counts.update(counter.counts)

        cv2.imshow("Video - press Q to quit", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# flask dans un thread séparé
def start_flask():
    app.run(debug=True, use_reloader=False, host="localhost", port=5000)


if __name__ == "__main__":
    # flask dans un thread séparé
    flask_thread = Thread(target=start_flask)
    flask_thread.start()

    # boucle de mise à jour des compteurs

    model = YOLO("yolo11m.pt")

    line_points = (0, 330, 640, 160)  # x1 y1 x2 y2 de la ligne de threshold "videos/30 Minutes of Cars Driving By in 2009.mp4"
    #line_points = (0, 250, 640, 250)  # x1 y1 x2 y2 de la ligne de threshold "videos/Road traffic video for object recognition.mp4"
    counter = VehicleCounter(line_points)

    video_path = "videos/30 Minutes of Cars Driving By in 2009.mp4"
    #video_path = "videos/Road traffic video for object recognition.mp4"
    #video_path = "videos/4K Road traffic video for object detection and tracking - free download now!.mp4"
    count_loop(video_path=video_path)
