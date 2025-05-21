import cv2
import asyncio
import websockets
import json

CAM_INDEX = 0
ROW_HEIGHT = 3  # Anzahl der horizontalen Pixelreihen
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

async def send_frames(websocket):
    cap = cv2.VideoCapture(CAM_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
    cap.set(cv2.CAP_PROP_FOCUS, 0)  # Fix auf manuell z. B. ganz nah

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # Extrahiere mittlere horizontale(n) Reihe(n)
        start_row = FRAME_HEIGHT // 2 - ROW_HEIGHT // 2
        end_row = start_row + ROW_HEIGHT
        strip = frame[start_row:end_row, :, :]

        # Downsample für geringere Bandbreite
        resized_strip = cv2.resize(strip, (FRAME_WIDTH, ROW_HEIGHT))
        _, buffer = cv2.imencode('.jpg', resized_strip)
        await websocket.send(buffer.tobytes())

        await asyncio.sleep(0.02)  # 50 FPS

async def main():
    async with websockets.serve(send_frames, "0.0.0.0", 8765):
        print("open server..")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
