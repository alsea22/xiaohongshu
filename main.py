from flask import Flask, request, jsonify
from flask_cors import CORS  # Tambahkan Flask-CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app)  # Izinkan semua domain mengakses backend

DOWNLOAD_FOLDER = 'downloads/'

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def index():
    return "Backend for Xiaohongshu Video Downloader is running."

@app.route('/download', methods=['POST'])
def download_video():
    data = request.get_json()
    video_url = data.get('video_url')

    if not video_url:
        return jsonify({"error": "No URL provided."}), 400

    try:
        ydl_opts = {
            'outtmpl': DOWNLOAD_FOLDER + '%(title)s.%(ext)s',
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            file_name = ydl.prepare_filename(info)

        return jsonify({"file": file_name, "message": "Download successful!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
