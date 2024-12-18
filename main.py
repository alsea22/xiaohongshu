from flask import Flask, request, jsonify
from flask_cors import CORS  # Mengaktifkan CORS untuk semua domain
import requests  # Untuk mengirim request HTTP ke API pihak ketiga
import traceback  # Untuk mencetak log error yang detail

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Aktifkan CORS agar backend bisa diakses dari frontend

@app.route('/')
def index():
    return "Backend for Xiaohongshu Video Downloader using dlpanda.com API is running."

@app.route('/download', methods=['POST'])
def download_video():
    try:
        # Ambil URL video dari body request
        data = request.get_json()
        video_url = data.get('video_url')

        if not video_url:
            return jsonify({"error": "No URL provided. Please include a valid video URL."}), 400

        # Endpoint API pihak ketiga
        api_url = "https://dlpanda.com/id/xiaohongshu"  # Ganti URL jika API membutuhkan endpoint khusus
        payload = {"url": video_url}  # Kirim URL video dalam request
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        # Kirim request ke API pihak ketiga
        response = requests.post(api_url, json=payload, headers=headers)

        # Debug respons API (untuk Railway Logs)
        print("API Status Code:", response.status_code)
        print("API Response:", response.text)

        # Jika respons bukan 200 OK
        if response.status_code != 200:
            return jsonify({
                "error": "Failed to fetch video data from API.",
                "status_code": response.status_code,
                "response": response.text
            }), 500

        # Parse respons API
        api_response = response.json()

        # Pastikan respons API memiliki link download
        if "download_url" not in api_response:
            return jsonify({"error": "No download link found in API response."}), 500

        # Ambil link download dari API
        download_url = api_response["download_url"]

        # Kirim link download ke frontend
        return jsonify({
            "download_url": download_url,
            "message": "Video link retrieved successfully!"
        }), 200

    except Exception as e:
        # Tangani error dan cetak log error detail ke Railway
        print("Error:", traceback.format_exc())
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 8080))  # Membaca PORT dari environment variable
    app.run(host='0.0.0.0', port=port)
