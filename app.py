from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import base64
import io
from PIL import Image

app = Flask(__name__)

def b64_to_cv2_img(b64_data):
    header, data = b64_data.split(',', 1) if ',' in b64_data else (None, b64_data)
    img_data = base64.b64decode(data)
    img = Image.open(io.BytesIO(img_data)).convert("RGB")
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    img_b64 = data.get("image_b64")
    p1 = np.array(data.get("point1"), dtype=float)
    p2 = np.array(data.get("point2"), dtype=float)
    coin_mm = float(data.get("coin_diameter_mm", 25.0))
    density = float(data.get("density", 40.0))

    img = b64_to_cv2_img(img_b64)
    coin_px = np.linalg.norm(p1 - p2)
    mm_per_px = coin_mm / coin_px

    # Simple bald area detection (placeholder)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (11, 11), 0)
    _, mask = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY)

    bald_px = int(np.sum(mask > 0))
    bald_mm2 = bald_px * (mm_per_px ** 2)
    bald_cm2 = bald_mm2 / 100.0
    estimated_grafts = bald_cm2 * density

    # Overlay for preview
    overlay = cv2.addWeighted(img, 0.7, cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR), 0.3, 0)
    _, buf = cv2.imencode('.jpg', overlay)
    overlay_b64 = "data:image/jpeg;base64," + base64.b64encode(buf).decode('utf-8')

    return jsonify({
        "coin_px": round(float(coin_px), 2),
        "bald_cm2": round(float(bald_cm2), 2),
        "estimated_grafts": int(round(float(estimated_grafts))),
        "overlay_b64": overlay_b64
    })

if __name__ == "__main__":
    app.run(debug=True)
