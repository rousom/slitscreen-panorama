from flask import Flask, request, Response
from flask_cors import CORS
from escpos.printer import Usb
from PIL import Image, ImageEnhance
from werkzeug.utils import secure_filename
import os
import logging
from threading import Lock, Thread

# ========== Config ==========
UPLOAD_FOLDER = './uploads'
VENDOR_ID = 0x04b8
PRODUCT_ID = 0x0202
INTERFACE = 0
MAX_WIDTH = 512  # pixels
printer_lock = Lock()

# ========== Setup ==========
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
CORS(app, resources={r"/*": {"origins": "*"}}, allow_headers=["Content-Type"])

logging.getLogger('escpos').setLevel(logging.ERROR)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ========== Print Function ==========
def print_image(filepath):
    with printer_lock:
        img = Image.open(filepath)

        # Rotate to match printer orientation
        img = img.rotate(90, expand=True)

        # Enhance brightness & contrast
        img = ImageEnhance.Brightness(img).enhance(1.2)
        img = ImageEnhance.Contrast(img).enhance(1.5)

        # Dither and convert to 1-bit
        img = img.convert('L')  # grayscale
        img = img.convert("1", dither=Image.FLOYDSTEINBERG)
        threshold = 120
        img = img.point(lambda x: 0 if x < threshold else 255, '1')

        # Print
        try:
            printer = Usb(VENDOR_ID, PRODUCT_ID, INTERFACE)
            printer.image(img)
            printer.cut()
            printer.close()
            print("Printed successfully.")
        except Exception as e:
            print("Printing failed:", str(e))
            raise

# ========== Upload Endpoint ==========
@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return Response('No image file part', status=400, mimetype='text/plain')

    file = request.files['image']
    if file.filename == '':
        return Response('No selected file', status=400, mimetype='text/plain')

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Print in background
    Thread(target=print_image, args=(filepath,)).start()

    return Response(f'Image upload received: {filename}', status=200, mimetype='text/plain')

# ========== Run ==========
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5052)


