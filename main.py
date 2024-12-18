from flask import Flask, request, jsonify
from flask_cors import CORS  # Import Flask-CORS
import yt_dlp
import os

app = Flask(__name__)
# Mengizinkan semua metode dan preflight OPTIONS request
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

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
            '
