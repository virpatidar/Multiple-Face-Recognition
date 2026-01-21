import cv2
import numpy as np
from datetime import datetime
from database import get_db
from face_utils import extract_faces, get_embedding, match_face

# ================= CAMERA SETUP =================
camera = cv2.VideoCapture(0)

CAMERA_ACTIVE = False   # controlled by admin


# ================= FRAME GENERATOR =================
def generate_frames():
    global CAMERA_ACTIVE

    db = get_db()
    cur = db.cursor()

    # Load all stored embeddings once
    cur.execute("SELECT user_id, embedding FROM face_embeddings")
    stored = [
        (row["user_id"], np.frombuffer(row["embedding"], dtype=np.float32))
        for row in cur.fetchall()
    ]

    while True:
        if not CAMERA_ACTIVE:
            continue  # pause camera when admin stops it

        success, frame = camera.read()
        if not success:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = extract_faces(rgb)

        for face in faces:
            emb = get_embedding(face)
            user_id = match_face(emb, stored)

            if user_id:
                today = datetime.now().date().isoformat()
                time_now = datetime.now().strftime("%H:%M:%S")

                cur.execute(
                    "SELECT * FROM attendance WHERE user_id=? AND date=?",
                    (user_id, today)
                )

                if not cur.fetchone():
                    cur.execute(
                        "INSERT INTO attendance (user_id, date, time) VALUES (?, ?, ?)",
                        (user_id, today, time_now)
                    )
                    db.commit()

        # Encode frame
        ret, buffer = cv2.imencode(".jpg", frame)
        frame = buffer.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
        )
