from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import traceback

# Inisialisasi Flask app
app = Flask(__name__)
CORS(app, supports_credentials=True)  # Aktifkan CORS untuk semua route dan semua origin

@app.after_request
def after_request(response):
    """
    Tambahkan header CORS ke semua respons.
    """
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return response

@app.route('/')
def index():
    return "Backend for Xiaohongshu Video Downloader is running."

@app.route('/download', methods=['POST'])
def download_video():
    try:
        # Ambil URL video dari request JSON
        data = request.get_json()
        video_url = data.get('video_url')

        # Validasi input URL
        if not video_url:
            return jsonify({"error": "No URL provided. Please include a valid video URL."}), 400

        # API tujuan (contoh endpoint API pihak ketiga)
        api_url = "https://shuiyinla.com/api/xiaohongshu"
        payload = {"url": video_url}
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://shuiyinla.com/",
            "Origin": "https://shuiyinla.com/"
        }

        # Kirim permintaan ke API pihak ketiga
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)

        # Jika API tidak memberikan respons yang valid
        if response.status_code != 200:
            return jsonify({
                "error": "Failed to fetch video data from API.",
                "status_code": response.status_code,
                "response": response.text
            }), 500

        # Parsing respons JSON dari API
        try:
            api_response = response.json()
        except ValueError:
            return jsonify({"error": "Failed to parse API response as JSON."}), 500

        # Ambil link download dari respons API
        download_url = api_response.get("download_url")
        if not download_url:
            return jsonify({"error": "No download link found in API response."}), 500

        # Kirim kembali link download ke frontend
        return jsonify({
            "download_url": download_url,
            "message": "Video link retrieved successfully!"
        }), 200

    except Exception as e:
        print("Error:", traceback.format_exc())
        return jsonify({
            "error": "An unexpected error occurred.",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 8080))  # Membaca PORT dari environment variable
    app.run(host='0.0.0.0', port=port)
