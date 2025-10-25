from flask import Flask, request, render_template
import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    result_img = None
    result_text = ""

    if request.method == 'POST':
        file = request.files['image']
        points = request.form.get('points')  # نقاط النقر من JS
        coin_diameter_mm = float(request.form.get('coin_diameter'))

        if file and points:
            # قراءة الصورة
            file_bytes = np.frombuffer(file.read(), np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

            # تحويل نقاط من string إلى قائمة من tuples
            points = points.split(';')
            points = [tuple(map(int, p.split(','))) for p in points]

            # رسم النقاط على الصورة
            for p in points:
                cv2.circle(img, p, 5, (0,0,255), -1)

            # حساب قطر العملة بالبكسل
            x1, y1 = points[0]
            x2, y2 = points[1]
            coin_px = np.sqrt((x2-x1)**2 + (y2-y1)**2)

            # مقياس mm لكل بكسل
            scale = coin_diameter_mm / coin_px

            result_text = f"Coin scale: {scale:.2f} mm/pixel"

            # تحويل الصورة للعرض على الويب
            _, buffer = cv2.imencode('.png', img)
            result_img = base64.b64encode(buffer).decode('utf-8')

    return render_template('index.html', result_img=result_img, result_text=result_text)

if __name__ == '__main__':
    app.run(debug=True)
