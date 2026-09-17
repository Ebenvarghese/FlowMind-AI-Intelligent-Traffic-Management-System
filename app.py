"""
app.py — Flask + SocketIO Master Backend
Serves both YOLO and Simulation sections.
"""

import os
import sys
import threading
import time
import json
import random
from pathlib import Path

from flask import (
    Flask,
    render_template,
    Response,
    request,
    jsonify,
    redirect,
    url_for,
    session,
)

from flask_socketio import SocketIO, emit
from flask_cors import CORS

print("[APP] Loading engines...")
sys.stdout.flush()

from sim_engine import SimEngine
from yolo_engine import YoloEngine

print("[APP] Engines imported")
sys.stdout.flush()

# ------------------------------------------------------------------
# App Setup
# ------------------------------------------------------------------

app = Flask(__name__)
app.config["SECRET_KEY"] = "traffic-secret-key-2024"

USERS_FILE = "users.json"


def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"admin": "admin123"}


def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)


CORS(app)

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading",
    ping_timeout=60,
    ping_interval=25,
    logger=False,
    engineio_logger=False,
)

SAMPLE_VIDEO_DIR = os.path.join(os.path.dirname(__file__), "sample_videos")

# Use local model
YOLO_MODEL_PATH = os.path.join(os.path.dirname(__file__), "yolov8n.pt")

if not os.path.exists(YOLO_MODEL_PATH):
    YOLO_MODEL_PATH = None

# ------------------------------------------------------------------
# Engine Instances
# ------------------------------------------------------------------

sim = SimEngine(socketio)
yolo_eng = YoloEngine(socketio, model_path=YOLO_MODEL_PATH)

VIDEO_EXTENSIONS = (".mp4", ".avi", ".mkv", ".mov")


def get_random_sample_video():
    if not os.path.exists(SAMPLE_VIDEO_DIR):
        return None

    videos = [
        f
        for f in os.listdir(SAMPLE_VIDEO_DIR)
        if f.lower().endswith(VIDEO_EXTENSIONS)
    ]

    if videos:
        return os.path.join(SAMPLE_VIDEO_DIR, random.choice(videos))

    fallback_path = os.path.join(SAMPLE_VIDEO_DIR, "traffic_sample.mp4")

    if not os.path.exists(fallback_path):
        _download_sample_video(fallback_path)

    return fallback_path if os.path.exists(fallback_path) else None


# ------------------------------------------------------------------
# Authentication Routes
# ------------------------------------------------------------------

@app.route("/", methods=["GET", "POST"])
def login():

    # Always show the login page on GET requests.
    if request.method == "GET":
        return render_template("login.html")

    # POST = user clicked Login
    users = load_users()

    username = request.form["username"].strip()
    password = request.form["password"].strip()

    if username in users and users[username] == password:
        session.clear()          # remove any old session
        session["user"] = username
        return redirect(url_for("dashboard"))

    return render_template("login.html", error="Invalid username or password")


@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        users = load_users()

        username = request.form["username"].strip()
        password = request.form["password"].strip()
        confirm = request.form["confirm_password"].strip()

        if username in users:
            return render_template(
                "signup.html",
                error="Username already exists",
            )

        if password != confirm:
            return render_template(
                "signup.html",
                error="Passwords do not match",
            )

        users[username] = password
        save_users(users)

        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("index.html", username=session["user"])

@app.route("/logout")
def logout():
    session.clear()
    session.modified = True
    return redirect(url_for("login"))


# ------------------------------------------------------------------
# Original Project Routes
# ------------------------------------------------------------------

@app.route("/video_feed")
def video_feed():

    def generate():

        while True:

            with yolo_eng.lock:
                frame_bytes = yolo_eng.current_frame

            if frame_bytes:
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n"
                    + frame_bytes
                    + b"\r\n"
                )
            else:
                time.sleep(0.05)

    return Response(
        generate(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


@app.route("/upload_video/<int:lane_idx>", methods=["POST"])
def upload_video(lane_idx):

    if "video" not in request.files:
        return jsonify({"error": "No file"}), 400

    f = request.files["video"]

    if f.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    os.makedirs(SAMPLE_VIDEO_DIR, exist_ok=True)

    save_path = os.path.join(
        SAMPLE_VIDEO_DIR,
        f"lane_{lane_idx}_uploaded.mp4",
    )

    f.save(save_path)

    yolo_eng.set_lane_video(lane_idx, save_path)

    return jsonify({"status": "ok", "lane": lane_idx})


@app.route("/use_sample/<int:lane_idx>")
def use_sample(lane_idx):

    sample_path = get_random_sample_video()

    if sample_path:
        yolo_eng.set_lane_video(lane_idx, sample_path)

        return jsonify(
            {
                "status": "ok",
                "lane": lane_idx,
                "file_mounted": os.path.basename(sample_path),
            }
        )

    return jsonify(
        {"error": "No sample videos available."},
        404,
    )


@app.route("/use_sample_all")
def use_sample_all():

    if yolo_eng.n_lanes <= 0:
        return jsonify({"error": "No lanes initialized."}), 400

    for i in range(yolo_eng.n_lanes):

        sample_path = get_random_sample_video()

        if sample_path:
            yolo_eng.set_lane_video(i, sample_path)
        else:
            return jsonify(
                {"error": "Sample video failed."},
                404,
            )

    return jsonify({"status": "ok"})


@app.route("/clear_lane/<int:lane_idx>")
def clear_lane(lane_idx):

    yolo_eng.clear_lane_video(lane_idx)

    return jsonify({"status": "ok", "lane": lane_idx})


def _download_sample_video(save_path):

    try:
        import requests as req_lib

        url = "https://www.pexels.com/download/video/855282/"

        r = req_lib.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=15,
            stream=True,
        )

        if r.status_code == 200:

            with open(save_path, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)

            print(f"[APP] Downloaded sample video.")

    except Exception as e:
        print(f"[APP] Download failed: {e}")


@app.route("/set_quads/<int:n>")
def set_quads(n):

    yolo_eng.set_n_lanes(n)

    return jsonify({"status": "ok", "n_lanes": n})


# ------------------------------------------------------------------
# Socket Events
# ------------------------------------------------------------------

@socketio.on("connect")
def on_connect():
    print(f"[SOCKET] Connected: {request.sid}")


@socketio.on("disconnect")
def on_disconnect():
    print(f"[SOCKET] Disconnected: {request.sid}")


@socketio.on("toggle_emergency")
def on_toggle_emergency(data=None):

    lane = None

    if isinstance(data, dict):
        lane = data.get("lane")
    elif isinstance(data, str):
        lane = data

    sim.trigger_emergency(lane=lane)

    emit("sim_state", sim.tick(), broadcast=True)


@socketio.on("cancel_emergency")
def on_cancel_emergency():

    sim.cancel_emergency()

    emit("sim_state", sim.tick(), broadcast=True)


@socketio.on("yolo_set_quads")
def on_yolo_set_quads(data):

    yolo_eng.set_n_lanes(data.get("n", 4))


@socketio.on("yolo_emergency_override")
def on_yolo_emergency():

    yolo_eng.emergency = True
    yolo_eng._cycle_timer = 15


# ------------------------------------------------------------------
# Background Thread
# ------------------------------------------------------------------

def start_sim_loop():

    time.sleep(1)

    sim.run_loop()


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print(" AI Traffic Management System")
    print(" http://127.0.0.1:5000")
    print("=" * 60)

    sim_thread = threading.Thread(
        target=start_sim_loop,
        daemon=True,
    )
    sim_thread.start()

    yolo_eng.start()

    print("\n===== REGISTERED ROUTES =====")

    for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
        print(f"{rule.rule:25} -> {rule.endpoint}")

    print("=============================\n")

    print("[APP] Starting Flask server...")

    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=True,
        allow_unsafe_werkzeug=True,
    )