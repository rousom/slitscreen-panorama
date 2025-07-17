from flask import Flask, request
from flask_cors import CORS
from escpos.printer import Usb
from PIL import Image
from PIL import ImageEnhance
import numpy as np

from werkzeug.utils import secure_filename
import os

import logging
logging.getLogger('escpos').setLevel(logging.ERROR)


app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ESC/POS printer IDs
VENDOR_ID = 0x04b8
PRODUCT_ID = 0x0202
INTERFACE = 0
MAX_WIDTH = 512  # pixels

from threading import Lock
printer_lock = Lock()

def print_image(filepath):
    with printer_lock: # lock thread to prevent multiple request
        print("Opening image...")
        img = Image.open(filepath)

        # Rotate image so canvas height maps to printer width
        img = img.rotate(90, expand=True)
        print('img h')
        print(img.height)
        print('img w')
        print(img.width)
        # Resize to fit printer width (512px)
        # if img.height != MAX_WIDTH:
        #     print("rescaling")
        #     scale = MAX_WIDTH / float(img.height)
        #     new_width = int(float(img.width) * scale)
        #     img = img.resize((new_width, MAX_WIDTH), Image.LANCZOS)

        # Enhance brightness
        brightness_enhancer = ImageEnhance.Brightness(img)
        img = brightness_enhancer.enhance(1.2)  # 1.0 = original, <1 = darker, >1 = brighter

        # Enhance contrast
        contrast_enhancer = ImageEnhance.Contrast(img)
        img = contrast_enhancer.enhance(1.5)  # 1.0 = original, >1 = more contrast

        print("Converting to 1-bit B/W...")
        img = img.convert('L')
        # img = img.convert('1')
        img = img.convert("1", dither=Image.FLOYDSTEINBERG)

        threshold = 120  # Lower = darker print
        img = img.point(lambda x: 0 if x < threshold else 255, '1')

        try:
            # Print via USB
            printer = Usb(VENDOR_ID, PRODUCT_ID, INTERFACE)
            printer.image(img)
            # printer.text("\n\n")
            # printer.cut()
            print("Printed and rotated successfully.")
        finally:
            printer.close()
            print("Printer closed.")

# def print_image(filepath):
#     print("Opening image...")
#     img = Image.open(filepath)

#     if img.width > MAX_WIDTH:
#         w_percent = MAX_WIDTH / float(img.size[0])
#         h_size = int((float(img.size[1]) * float(w_percent)))
#         img = img.resize((MAX_WIDTH, h_size), Image.LANCZOS)

#     print("Converting image...")
#     img = img.convert('L')  # Grayscale
#     img = img.convert('1')  # 1-bit

#     print("Sending to printer...")
#     printer = Usb(VENDOR_ID, PRODUCT_ID, INTERFACE)
#     printer.image(img)
#     printer.text("\n\n")
#     printer.cut()
#     print("Printed uploaded image.")

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return 'No image file part', 400

    file = request.files['image']
    if file.filename == '':
        return 'No selected file', 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    # return f'Image saved as {filename}', 200

    # # Optional: resize or pad image to width supported by your printer (e.g., 512 px)
    # file = file.resize((512, 100))
    
    try:
        print_image(filepath)
        return f'Image printed: {filename}', 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f'Failed to print: {str(e)}', 500

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(port=5051)

# @app.route("/print-buffer", methods=["POST"])
# def print_buffer():
#     data = request.get_json()
#     w = data.get("width")
#     h = data.get("height")
#     pixels = data.get("pixels")

#     if not pixels or len(pixels) != w * h:
#         return "Invalid pixel data", 400

#     import numpy as np
#     from PIL import Image

#     array = np.array(pixels, dtype=np.uint8).reshape((h, w))
#     img = Image.fromarray(array).convert("1")

#     try:
#         printer = Usb(0x04b8, 0x0202)
#         printer.image(img)
#         # printer.cut()
#     finally:
#         printer.close()

#     return "Printed OK", 200


# @app.route('/print_array', methods=['POST'])
# def print_array():
#     try:
#         # data = request.json
        
#         # print(data)
#         # pixels = np.array(data['pixels'], dtype=np.uint8) * 255  # Convert 0/1 → 0/255
#         # print("DEBUG")
#         # print("PIX: " + pixels)
#         # img = Image.fromarray(pixels, mode='L').convert('1')     # Convert to 1-bit B/W

#         # # Optional: Pad width to printer's width (e.g., 512 px)
#         # padded = Image.new('1', (512, img.height), color=1)  # white background
#         # padded.paste(img, (0, 0))

#         # printer = Usb(0x04b8, 0x0202)
#         # printer.image(img)
#         # # printer.cut()

#         # # === 1. Define Your Pixel Array ===
#         width = 512
#         height = 1

#         pixels = np.random.randint(0, 2, size=(height, width), dtype=np.uint8)


#         # === 2. Convert Pixel Array to Image ===
#         def pixel_array_to_image(pixels):
#             array = np.array(pixels, dtype=np.uint8) * 255  # 0 → black, 1 → white
#             img = Image.fromarray(array, mode='L')          # grayscale
#             img = img.convert('1')                          # convert to B/W
#             return img

#         image = pixel_array_to_image(pixels)

#         # Optional: resize or pad image to width supported by your printer (e.g., 512 px)
#         image = image.resize((512, 100))

#         # === 3. Send to USB Thermal Printer ===

#         # Find your printer's Vendor ID and Product ID using `lsusb`
#         VENDOR_ID = 0x04b8  # Example: Epson
#         PRODUCT_ID = 0x0202  # Example: TM-T88IV
#         INTERFACE = 0       # Usually 0

#         try:
#             printer = Usb(VENDOR_ID, PRODUCT_ID, interface=INTERFACE)
#             printer.image(image)
#             #printer.cut()
#             # printer.
#             print("Printed successfully.")
#             printer.close()
#         except Exception as e:
#             print(f"Error: {e}")
#         return "Printed strip", 200
#     except Exception as e:
#         return f"Error: {e}", 500





# if __name__ == '__main__':
#     app.run(port=5050)