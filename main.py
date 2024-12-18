from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import traceback
import time

# Inisialisasi Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)  # Mengaktifkan CORS global

# Fungsi untuk mencoba request API dengan retry mekanisme
def fetch_api_with_retry(api_url, payload, headers, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(api_url, json=payload, headers=headers, timeout=10)
            print(f"Attempt {attempt + 1}: API Status Code {response.status_code}")
            if response.status_code == 200:
                return response
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1}: Request failed with error: {str(e)}")
        time.sleep(2)  # Tunggu 2 detik sebelum mencoba lagi
    return None

@app.route('/')
def index():
    return "Backend for Xiaohongshu Video Downloader using shuiyinla.com API is running."

import logging

# Tambahkan konfigurasi logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/download', methods=['POST'])
def download_video():
    try:
        # Tambahkan log sebelum mengambil request JSON
        logging.debug("Request received: %s", request.data)

        data = request.get_json()
        video_url = data.get('video_url')

        # Tambahkan log URL yang diterima
        logging.debug("Video URL received: %s", video_url)

        if not video_url:
            return jsonify({"error": "No URL provided. Please include a valid video URL."}), 400

        # Log sebelum request API
        logging.debug("Sending request to shuiyinla.com API...")

        # Endpoint API
        api_url = "https://shuiyinla.com/api/xiaohongshu"
        payload = {"url": video_url}
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://shuiyinla.com/",
            "Origin": "https://shuiyinla.com/"
        }

        response = requests.post(api_url, json=payload, headers=headers, timeout=10)

        # Log response dari API
        logging.debug("API Response Status Code: %s", response.status_code)
        logging.debug("API Response: %s", response.text)

        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch video data from API."}), 500

        api_response = response.json()
        download_url = api_response.get("download_url")

        if not download_url:
            return jsonify({"error": "No download link found in API response."}), 500

        return jsonify({"download_url": download_url, "message": "Success"}), 200

    except Exception as e:
        logging.error("An unexpected error occurred: %s", str(e))
        logging.error(traceback.format_exc())
        return jsonify({"error": "An unexpected error occurred.", "details": str(e)}), 500
