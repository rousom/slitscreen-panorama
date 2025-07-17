from escpos.printer import Usb
from PIL import Image
import numpy as np

# === 1. Define Your Pixel Array ===
# Example 8x8 checkerboard pattern
width = 512
height = 1

pixels = np.random.randint(0, 2, size=(height, width), dtype=np.uint8)


# === 2. Convert Pixel Array to Image ===
def pixel_array_to_image(pixels):
    array = np.array(pixels, dtype=np.uint8) * 255  # 0 → black, 1 → white
    img = Image.fromarray(array, mode='L')          # grayscale
    img = img.convert('1')                          # convert to B/W
    return img

image = pixel_array_to_image(pixels)

# Optional: resize or pad image to width supported by your printer (e.g., 512 px)
image = image.resize((512, 64))

# === 3. Send to USB Thermal Printer ===

# Find your printer's Vendor ID and Product ID using `lsusb`
VENDOR_ID = 0x04b8  # Example: Epson
PRODUCT_ID = 0x0202  # Example: TM-T88IV
INTERFACE = 0       # Usually 0

try:
    printer = Usb(VENDOR_ID, PRODUCT_ID, interface=INTERFACE)
    printer.image(image)
    #printer.cut()
    print("Printed successfully.")
except Exception as e:
    print(f"Error: {e}")