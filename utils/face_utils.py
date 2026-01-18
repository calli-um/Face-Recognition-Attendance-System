# utils/face_utils.py
import cv2
from ultralytics import YOLO
from keras_facenet import FaceNet
from numpy.linalg import norm

yolo = YOLO("model.pt")
embedder = FaceNet()

THRESHOLD = 0.8  # Balanced threshold for group photos (0.6 too strict, 1.0 too permissive)


def preprocess_face(face):
    face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
    face = cv2.resize(face, (160, 160))
    return face.astype("uint8")


def extract_embedding(img):
    results = yolo(img, verbose=False)
    if results[0].boxes is None:
        return None

    box = results[0].boxes[0]
    x1, y1, x2, y2 = map(int, box.xyxy[0])
    face = img[y1:y2, x1:x2]

    if face.size == 0:
        return None

    face = preprocess_face(face)
    return embedder.embeddings([face])[0]


def recognize_face(embedding, face_db, verbose=False):
    best_name = "Unknown"
    best_dist = float("inf")
    all_distances = {}

    for name, embeddings in face_db.items():
        min_dist_for_name = float("inf")
        for db_emb in embeddings:
            dist = norm(embedding - db_emb)
            if dist < min_dist_for_name:
                min_dist_for_name = dist
            if dist < best_dist:
                best_dist = dist
                best_name = name
        all_distances[name] = min_dist_for_name

    if verbose:
        print(f"    All distances: {all_distances}")
        print(f"    Best match: {best_name} with distance {best_dist:.4f}")
        print(f"    Threshold: {THRESHOLD}")

    if best_dist <= THRESHOLD:
        return best_name, best_dist

    return "Unknown", best_dist
