from flask import Flask, render_template, jsonify
import cv2
import time
import base64
from datetime import datetime
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import re
import os

app = Flask(__name__)

def capture_images(interval, duration):
    camera = cv2.VideoCapture('rtsp://192.168.1.44:554/11')  # Nueva conexión a la cámara
    start_time = time.time()
    images = []
    while time.time() - start_time < duration:
        success, frame = camera.read()
        if success:
            _, buffer = cv2.imencode('.jpg', frame)
            image_base64 = base64.b64encode(buffer).decode('utf-8')
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            images.append({'image': image_base64, 'timestamp': timestamp})
            time.sleep(interval)

    camera.release()  # Cierra la conexión a la cámara al finalizar la captura
    return images

def create_folder(drive, folder_name):
    folder = drive.CreateFile({'title': folder_name, 'mimeType': 'application/vnd.google-apps.folder'})
    folder.Upload()
    return folder

def upload_to_drive(images):
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)

    # Crear una carpeta con el timestamp actual
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    folder_name = f"dataset_{timestamp}"
    folder = create_folder(drive, folder_name)

    for idx, image in enumerate(images):
        image_data = base64.b64decode(image['image'])
        
        # Reemplazar caracteres no permitidos en nombres de archivos de Windows
        timestamp = re.sub(r'[:]', '-', image['timestamp'])
        file_name = f"image_{idx}_{timestamp}.jpg"

        with open(file_name, 'wb') as file:
            file.write(image_data)

        # Subir la imagen a la carpeta en Google Drive
        file_drive = drive.CreateFile({'title': file_name, 'parents': [{'id': folder['id']}]})
        file_drive.SetContentFile(file_name)
        file_drive.Upload()

        file_drive.content.close()

        os.remove(file_name)

    print(f"Images uploaded to Google Drive folder: {folder_name}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_images/<int:interval>/<int:duration>', methods=['GET'])
def get_images(interval, duration):
    try:
        images = capture_images(interval, duration)
        upload_to_drive(images)
        return jsonify({'images': images})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
