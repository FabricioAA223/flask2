from flask import Flask, render_template, Response
import cv2

app = Flask(__name__)

# Función para capturar imágenes de la cámara
def generate_frames():
    camera = cv2.VideoCapture('rtsp://192.168.1.44:554/11')  # Reemplaza con la dirección RTSP de tu cámara

    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    camera.release()

# Ruta principal para renderizar la plantilla HTML
@app.route('/')
def index():
    return render_template('index2.html')

# Ruta para la transmisión de imágenes desde la cámara
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
