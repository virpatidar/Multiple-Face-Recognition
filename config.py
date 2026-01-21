import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE = os.path.join(BASE_DIR, "face_attendance.db")

UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "assets", "faces")

FACE_MATCH_THRESHOLD = 0.6   # configurable

CAMERA_DURATION_SECONDS = 60
