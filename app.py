from flask import Flask, render_template, request, redirect, session, Response
from database import get_db
from camera import generate_frames
import camera   # ✅ IMPORTANT
import hashlib
import os
import numpy as np
from PIL import Image
from face_utils import extract_faces, get_embedding
from config import UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

TEMP_EMBEDDINGS = []  # temporary store during registration

app = Flask(__name__)
app.secret_key = "secure-key"


# ================= HOME =================
@app.route("/")
def index():
    return render_template("index.html")


# ================= USER =================
@app.route("/user")
def user_portal():
    return render_template("user_portal.html")


@app.route("/user/register", methods=["GET"])
def user_register():
    return render_template("user_register.html")


@app.route("/capture_face", methods=["POST"])
def capture_face():
    file = request.files["image"]
    image = Image.open(file).convert("RGB")
    img_np = np.array(image)

    faces = extract_faces(img_np)
    if not faces:
        return {"status": "no_face"}

    face = faces[0]
    emb = get_embedding(face)

    TEMP_EMBEDDINGS.append(emb.tobytes())
    return {"status": "ok"}


@app.route("/user/login", methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        email = request.form["email"]
        password = hashlib.sha256(request.form["password"].encode()).hexdigest()

        db = get_db()
        cur = db.cursor()
        cur.execute("""
            SELECT u.id, u.name FROM users u
            JOIN user_auth a ON u.id = a.user_id
            WHERE u.email=? AND a.password=?
        """, (email, password))

        user = cur.fetchone()
        if user:
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            return redirect("/user/dashboard")

    return render_template("user_login.html")


@app.route("/user/dashboard")
def user_dashboard():
    if "user_id" not in session:
        return redirect("/user/login")
    return render_template("user_dashboard.html")


# ================= ADMIN =================
@app.route("/admin")
def admin_root():
    return redirect("/admin/login")


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = hashlib.sha256(request.form["password"].encode()).hexdigest()

        db = get_db()
        cur = db.cursor()
        cur.execute(
            "SELECT * FROM admin WHERE username=? AND password=?",
            (username, password)
        )

        if cur.fetchone():
            session["admin"] = True
            return redirect("/admin/dashboard")

    return render_template("admin_login.html")


@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin"):
        return redirect("/admin/login")
    return render_template("admin_dashboard.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect("/")


@app.route("/admin/video")
def admin_video():
    if not session.get("admin"):
        return redirect("/admin/login")

    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


# ================= CAMERA CONTROL =================
@app.route("/admin/camera/start")
def start_camera():
    if not session.get("admin"):
        return redirect("/admin/login")

    camera.CAMERA_ACTIVE = True   # ✅ CORRECT
    return redirect("/admin/dashboard")


@app.route("/admin/camera/stop")
def stop_camera():
    if not session.get("admin"):
        return redirect("/admin/login")

    camera.CAMERA_ACTIVE = False  # ✅ CORRECT
    return redirect("/admin/dashboard")


# ================= CAMERA (PUBLIC STREAM) =================
@app.route("/video")
def video():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
