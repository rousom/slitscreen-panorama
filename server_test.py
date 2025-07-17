import rtde_control
import rtde_receive
import time
import numpy as np
import math
from contextlib import contextmanager
from flask import Flask, request, Response
from flask_cors import CORS
from flask_socketio import SocketIO, emit


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins=["http://127.0.0.1:5501"])
CORS(app, resources={r"/*": {"origins": "*"}})
@app.route('/ping')
def hello():
    return "Server is running!"

@socketio.on('connect')
def handle_connect():
    print("🔌 Client connected")
    emit('message_from_server', {'msg': 'Hello from Flask WebSocket!'})

@socketio.on('message_from_client')
def handle_client_message(data):
    print("📩 Received from client:", data)
    emit('reply', {'msg': f"Echo: {data['msg']}"})

@app.route('/events')
def events():
    def stream():
        while True:
            time.sleep(1)
            yield f"data: Server time is {time.ctime()}\n\n"
    return Response(stream(), mimetype='text/event-stream')


if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5051)
