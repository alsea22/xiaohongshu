from flask import Flask, request, jsonify
from flask_cors import CORS
import requests  # Untuk request HTTP ke API pihak ketiga
import traceback  # Untuk mencetak log error secara detail

# Inisialisasi Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Mengaktifkan CORS agar backend bisa diakses dari frontend

@app.route('/')
def index():
    return "Backend for Xiaohongshu Video Downloader using dlpanda.com API is running."

@app.route('/download', methods=['POST'])
def download_video():
    try:
        # Ambil URL video dari body request
        data = request.get_json()
        video_url = data.get('video_url')

        # Validasi input URL
        if not video_url:
            return jsonify({"error": "No URL provided. Please include a valid video URL."}), 400

        # Endpoint API pihak ketiga
        api_url = "https://dlpanda.com/id/xiaohongshu"  # API tujuan
        payload = {"url": video_url}  # Payload yang dikirim
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://dlpanda.com/",  # Header Referer agar sesuai dengan asal domain
            "Origin": "https://dlpanda.com/",  # Header Origin
            "Accept": "application/json"
        }

        # Menggunakan sesi request
        session = requests.Session()
        response = session.post(api_url, json=payload, headers=headers)

        # Log respons untuk debugging
        print("API Status Code:", response.status_code)
        print("API Response:", response.text)

        # Jika respons bukan 200 OK
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

        # Validasi apakah respons API memiliki download_url
        download_url = api_response.get("download_url")
        if not download_url:
            return jsonify({"error": "No download link found in API response."}), 500

        # Kirim kembali link download ke frontend
        return jsonify({
            "download_url": download_url,
            "message": "Video link retrieved successfully!"
        }), 200

    except Exception as e:
        # Menangkap error dan mencetak ke log untuk debugging
        print("Error:", traceback.format_exc())
        return jsonify({
            "error": "An unexpected error occurred.",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 8080))  # Membaca PORT dari environment variable
    app.run(host='0.0.0.0', port=port)
