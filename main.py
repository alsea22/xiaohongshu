from flask import Flask, request, jsonify
from flask_cors import CORS
import requests  # Untuk mengirim permintaan HTTP ke API pihak ketiga
import traceback

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Aktifkan CORS untuk semua domain

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
            return jsonify({"error": "No URL provided."}), 400

        # Endpoint API dlpanda.com
        api_url = "https://dlpanda.com/id/xiaohongshu"  # Gantilah jika ada endpoint khusus
        payload = {"url": video_url}  # Kirim URL video ke API
        headers = {"Content-Type": "application/json"}

        # Kirim request ke API dlpanda.com
        response = requests.post(api_url, json=payload, headers=headers)

        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch video data from API.", "status_code": response.status_code}), 500

        # Parse respons dari API
        api_response = response.json()

        # Cek apakah API mengembalikan link download
        if "download_url" not in api_response:
            return jsonify({"error": "No download link found in API response."}), 500

        # Respons berhasil
        download_url = api_response["download_url"]
        return jsonify({"download_url": download_url, "message": "Video link retrieved successfully!"}), 200

    except Exception as e:
        print("Error:", traceback.format_exc())  # Cetak error detail ke log
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
