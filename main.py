from flask import Flask, request, jsonify
from flask_cors import CORS  # Mengaktifkan CORS
import yt_dlp
import os
import unicodedata  # Untuk normalisasi nama file
import re  # Untuk membersihkan karakter khusus dari nama file

app = Flask(__name__)
CORS(app, origins=["*"])  # Mengaktifkan CORS untuk semua domain

DOWNLOAD_FOLDER = 'downloads/'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Fungsi untuk membersihkan nama file
def normalize_filename(name):
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')
    name = re.sub(r'[^\w\s.-]', '', name)
    return name

@app.route('/')
def index():
    return "Backend for Xiaohongshu Video Downloader is running."

@app.route('/download', methods=['POST'])
def download_video():
    try:
        # Ambil URL dari permintaan pengguna
        data = request.get_json()
        video_url = data.get('video_url')

        if not video_url:
            return jsonify({"error": "No URL provided."}), 400

        # Konfigurasi yt-dlp untuk download video
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'socket_timeout': 30,  # Tambahkan timeout jika video lambat
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            file_name = ydl.prepare_filename(info)

            # Normalisasi nama file agar tidak error
            base_name = os.path.basename(file_name)
            normalized_name = normalize_filename(base_name)
            normalized_path = os.path.join(DOWNLOAD_FOLDER, normalized_name)

            if os.path.exists(file_name):
                os.rename(file_name, normalized_path)

        return jsonify({"file": normalized_name, "message": "Download successful!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Tangkap semua error di sini

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
