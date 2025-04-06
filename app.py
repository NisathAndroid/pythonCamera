import os
import base64
import logging
from datetime import datetime
from flask import Flask, render_template, request, send_from_directory, jsonify
from flask_socketio import SocketIO, emit

# Configurations
UPLOAD_FOLDER = "uploads"
HOST = "0.0.0.0"
PORT = 5000

# Setup
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
logging.basicConfig(level=logging.INFO)

# Flask App & SocketIO Setup
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
socketio = SocketIO(app, cors_allowed_origins="*")  # Allow cross-origin for ngrok

# Routes
@app.route("/")
def home():
    logging.info("Loading laptop.html from '/' route")
    return render_template("laptop.html")

@app.route("/android")
def android_page():
    logging.info("Loading android.html from '/android' route")
    return render_template("android.html")

@app.route("/upload", methods=["POST"])
def upload_image():
    try:
        logging.info("Received image upload request (web)")
        image_data = request.json.get("image")
        filename = save_base64_image(image_data, prefix="image")
        socketio.emit("image_saved", {"filename": filename})
        logging.info(f"Image uploaded and saved as {filename}")
        return {"status": "success", "filename": filename}
    except Exception as e:
        logging.error(f"Upload failed: {e}")
        return {"status": "error", "message": str(e)}

@app.route("/downloads")
def list_uploaded_files():
    files = os.listdir(UPLOAD_FOLDER)
    logging.info(f"Listing {len(files)} uploaded files")
    return jsonify(files)

@app.route("/download/<filename>")
def download_file(filename):
    logging.info(f"Download requested: {filename}")
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

# SocketIO Events
@socketio.on("trigger_capture")
def handle_camera_trigger():
    logging.info("Received 'trigger_capture' event, broadcasting 'take_picture'")
    emit("take_picture", broadcast=True)

@socketio.on("send_image")
def handle_android_image(data):
    try:
        logging.info("Received image from Android device via WebSocket")
        image_data = data.get("image")
        filename = save_base64_image(image_data, prefix="android_image")
        emit("image_saved", {"filename": filename}, broadcast=True)
        logging.info(f"Android image saved and broadcasted as {filename}")
    except Exception as e:
        logging.error(f"Failed to save Android image: {e}")

# Utility Function
def save_base64_image(image_data, prefix="image"):
    """Decodes base64 image and saves it to disk with a timestamped filename."""
    img_bytes = base64.b64decode(image_data.split(",")[1])
    filename = f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    with open(filepath, "wb") as f:
        f.write(img_bytes)
    return filename

# Start Server (without SSL for ngrok)
if __name__ == "__main__":
    logging.info(f"Starting Flask-SocketIO server on http://{HOST}:{PORT}")
    socketio.run(app, host=HOST, port=PORT)





# import os
# import ssl
# import base64
# import logging
# from datetime import datetime
# from flask import Flask, render_template, request, send_from_directory, jsonify
# from flask_socketio import SocketIO, emit
#
# # Configurations
# UPLOAD_FOLDER = "uploads"
# CERT_FILE = "cert/cert.pem"
# KEY_FILE = "cert/key.pem"
# HOST = "192.168.169.27"
# PORT = 5000
#
# # Setup
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# logging.basicConfig(level=logging.INFO)
#
# # Flask App & SocketIO Setup
# app = Flask(__name__)
# app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
# socketio = SocketIO(app, async_mode="gevent")
#
# # Routes
# @app.route("/")
# def home():
#     logging.info("Loading laptop.html from '/' route")
#     return render_template("laptop.html")
#
# @app.route("/android")
# def android_page():
#     logging.info("Loading android.html from '/android' route")
#     return render_template("android.html")
#
# @app.route("/upload", methods=["POST"])
# def upload_image():
#     try:
#         logging.info("Received image upload request (web)")
#         image_data = request.json.get("image")
#         filename = save_base64_image(image_data, prefix="image")
#         socketio.emit("image_saved", {"filename": filename})
#         logging.info(f"Image uploaded and saved as {filename}")
#         return {"status": "success", "filename": filename}
#     except Exception as e:
#         logging.error(f"Upload failed: {e}")
#         return {"status": "error", "message": str(e)}
#
# @app.route("/downloads")
# def list_uploaded_files():
#     files = os.listdir(UPLOAD_FOLDER)
#     logging.info(f"Listing {len(files)} uploaded files")
#     return jsonify(files)
#
# @app.route("/download/<filename>")
# def download_file(filename):
#     logging.info(f"Download requested: {filename}")
#     return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
#
# # SocketIO Events
# @socketio.on("trigger_camera")
# def handle_camera_trigger():
#     logging.info("Received 'trigger_camera' event, broadcasting 'capture_image'")
#     emit("capture_image", broadcast=True)
#
# @socketio.on("send_image")
# def handle_android_image(data):
#     try:
#         logging.info("Received image from Android device via WebSocket")
#         image_data = data.get("image")
#         filename = save_base64_image(image_data, prefix="android_image")
#         emit("image_saved", {"filename": filename}, broadcast=True)
#         logging.info(f"Android image saved and broadcasted as {filename}")
#     except Exception as e:
#         logging.error(f"Failed to save Android image: {e}")
#
# # Utility Function
# def save_base64_image(image_data, prefix="image"):
#     """Decodes base64 image and saves it to disk with a timestamped filename."""
#     img_bytes = base64.b64decode(image_data.split(",")[1])
#     filename = f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
#     filepath = os.path.join(UPLOAD_FOLDER, filename)
#     with open(filepath, "wb") as f:
#         f.write(img_bytes)
#     return filename
#
# # Start Server
# if __name__ == "__main__":
#     logging.info(f"Starting Flask-SocketIO server on https://{HOST}:{PORT}")
#     ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
#     ssl_context.load_cert_chain(CERT_FILE, KEY_FILE)
#
#     socketio.run(app, host=HOST, port=PORT, ssl_context=ssl_context)
#
#     # Optional fallback HTTP run (commented out)
#     # socketio.run(app, host="0.0.0.0", port=5001)
