from flask import Flask, request, jsonify
from flask_cors import CORS  # Mengaktifkan CORS
import yt_dlp
import os
import unicodedata  # Untuk normalisasi nama file
import re  # Untuk membersihkan karakter khusus dari nama file

app = Flask(__name__)
CORS(app, origins=["*"], supports_credentials=True)  # Izinkan semua origin untuk akses CORS

# Folder tempat menyimpan file yang diunduh
DOWNLOAD_FOLDER = 'downloads/'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Fungsi untuk membersihkan nama file
def normalize_filename(name):
    # Menghilangkan karakter non-ASCII
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')
    # Hapus simbol aneh kecuali huruf, angka, titik, garis bawah, dan spasi
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

        # Konfigurasi yt
