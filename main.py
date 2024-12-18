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

@app.route('/download', methods=['POST'])
def download_video():
    try:
        # Aktifkan CORS untuk route ini
        CORS(app, resources={r"/download": {"origins": "*"}})

        # Ambil URL video dari request JSON
        data = request.get_json()
        video_url = data.get('video_url')

        # Validasi input URL
        if not video_url:
            return jsonify({"error": "No URL provided. Please include a valid video URL."}), 400

        # Endpoint API shuiyinla.com
        api_url = "https://shuiyinla.com/api/xiaohongshu"  # Ganti jika ada dokumentasi resmi
        payload = {"url": video_url}
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://shuiyinla.com/",
            "Origin": "https://shuiyinla.com/"
        }

        # Kirim request dengan retry mekanisme
        response = fetch_api_with_retry(api_url, payload, headers)

        # Jika respons gagal
        if not response:
            return jsonify({
                "error": "Failed to fetch video data after multiple attempts.",
                "message": "API might be unavailable or rejecting the request."
            }), 500

        # Log respons untuk debugging
        print("API Response:", response.text)

        # Parsing respons JSON dari API
        try:
            api_response = response.json()
        except ValueError:
            return jsonify({"error": "Failed to parse API response as JSON."}), 500

        # Validasi apakah API memberikan download_url
        download_url = api_response.get("download_url")
        if not download_url:
            return jsonify({"error": "No download link found in API response."}), 500

        # Kirim kembali link download ke frontend
        return jsonify({
            "download_url": download_url,
            "message": "Video link retrieved successfully!"
        }), 200

    except Exception as e:
        # Tangani error dengan log lengkap
        print("Error:", traceback.format_exc())
        return jsonify({
            "error": "An unexpected error occurred.",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 8080))  # Membaca PORT dari environment variable
    app.run(host='0.0.0.0', port=port)
