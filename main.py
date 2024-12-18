from flask import Flask, request, jsonify
from flask_cors import CORS  # Untuk mengaktifkan CORS
import yt_dlp  # yt-dlp untuk mengunduh video
import os
import unicodedata  # Untuk normalisasi nama file
import re  # Untuk membersihkan karakter khusus dari nama file

# Update yt-dlp ke versi terbaru setiap kali aplikasi berjalan
os.system("pip install --upgrade yt-dlp")

app = Flask(__name__)
CORS(app, origins=["*"])  # Izinkan semua domain untuk akses CORS

# Folder penyimpanan file hasil unduhan
DOWNLOAD_FOLDER = 'downloads/'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Fungsi untuk membersihkan nama file dari karakter aneh
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
        # Ambil URL video dari body request
        data = request.get_json()
        video_url = data.get('video_url')

        if not video_url:
            return jsonify({"error": "No URL provided."}), 400

        # Konfigurasi yt-dlp
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'socket_timeout': 30,  # Timeout jika proses download lambat
            'verbose': True  # Log lebih detail untuk debug
        }

        # Proses download video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            file_name = ydl.prepare_filename(info)

            # Normalisasi nama file agar aman
            base_name = os.path.basename(file_name)
            normalized_name = normalize_filename(base_name)
            normalized_path = os.path.join(DOWNLOAD_FOLDER, normalized_name)

            # Rename file jika berhasil diunduh
            if os.path.exists(file_name):
                os.rename(file_name, normalized_path)
            else:
                return jsonify({"error": "File not found after download."}), 500

        return jsonify({"file": normalized_name, "message": "Download successful!"}), 200

    except yt_dlp.utils.DownloadError as e:
        # Error khusus dari yt-dlp
        return jsonify({"error": f"Download failed: {str(e)}"}), 500
    except Exception as e:
        # Tangkap error lainnya
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
