from flask import Flask, request, jsonify
from flask_cors import CORS  # Mengaktifkan CORS
import yt_dlp
import os
import unicodedata  # Untuk normalisasi nama file
import re  # Untuk membersihkan karakter khusus dari nama file

# Update yt-dlp ke versi terbaru setiap kali aplikasi dijalankan
os.system("pip install --upgrade yt-dlp")

app = Flask(__name__)
CORS(app, origins=["*"])  # Mengaktifkan CORS untuk semua domain

# Folder tempat menyimpan file yang diunduh
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
            'socket_timeout': 30,  # Timeout jika video lambat
            'verbose': True,  # Tambahkan log lebih detail
        }

        # Proses download video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            file_name = ydl.prepare_filename(info)

            # Normalisasi nama file agar aman
            base_name = os.path.basename(file_name)
            normalized_name = normalize_filename(base_name)
            normalized_path = os.path.join(DOWNLOAD_FOLDER, normalized_name)

            if os.path.exists(file_name):
                os.rename(file_name, normalized_path)
            else:
                return jsonify({"error": "File not found after download."}), 500

        return jsonify({"file": normalized_name, "message": "Download successful!"}), 200

    except yt_dlp.DownloadError as e:
        return jsonify({"error": f"Download failed: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Tangkap semua error lainnya

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
