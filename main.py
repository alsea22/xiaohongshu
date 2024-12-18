from flask import Flask, request, jsonify
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import traceback
import time
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Path ke ChromeDriver (sesuaikan path di server Anda)
CHROMEDRIVER_PATH = "./chromedriver"

@app.route('/')
def index():
    return "Backend for Xiaohongshu Video Downloader is running."

@app.route('/download', methods=['POST'])
def download_video():
    try:
        # Ambil URL video dari request
        data = request.get_json()
        video_url = data.get("video_url")

        if not video_url:
            return jsonify({"error": "No URL provided."}), 400

        # Konfigurasi Selenium Chrome
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Mode tanpa GUI
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Inisialisasi WebDriver
        service = Service(CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=chrome_options)

        try:
            # Buka URL Xiaohongshu
            driver.get(video_url)
            time.sleep(5)  # Tunggu halaman dimuat

            # Cari elemen video (ganti selector ini jika tidak cocok)
            video_element = driver.find_element(By.TAG_NAME, "video")
            video_src = video_element.get_attribute("src")

            if not video_src:
                return jsonify({"error": "Failed to extract video source URL."}), 500

            # Kirim link video kembali ke frontend
            return jsonify({
                "download_url": video_src,
                "message": "Video link extracted successfully!"
            }), 200

        except Exception as e:
            print("Scraping Error:", traceback.format_exc())
            return jsonify({"error": "Failed to scrape video URL.", "details": str(e)}), 500

        finally:
            driver.quit()

    except Exception as e:
        print("Error:", traceback.format_exc())
        return jsonify({"error": "An unexpected error occurred.", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
