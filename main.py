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
            'format': 'mp4/bestvideo+bestaudio/best',  # Coba format MP4, atau best yang tersedia
            'merge_output_format': 'mp4',
            'socket_timeout': 30,
            'verbose': True
        }

        # Proses download video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            file_name = ydl.prepare_filename(info)

            # Debug: Cek apakah file benar-benar ada
            if not os.path.exists(file_name):
                print("File not found:", file_name)
                return jsonify({"error": "Failed to download the video. File not created."}), 500

            # Debug: Baca isi file jika bukan MP4
            if not file_name.endswith(".mp4"):
                with open(file_name, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print("File Content Debug:", content[:500])  # Cetak sebagian isi file

            # Normalisasi nama file
            base_name = os.path.basename(file_name)
            normalized_name = normalize_filename(base_name)
            normalized_path = os.path.join(DOWNLOAD_FOLDER, normalized_name)

            # Rename file agar aman
            os.rename(file_name, normalized_path)

        return jsonify({"file": normalized_name, "message": "Download successful!"}), 200

    except yt_dlp.utils.DownloadError as e:
        print("Download Error:", str(e))  # Log error dari yt-dlp
        return jsonify({"error": "Failed to download video. The video format might not be available."}), 500
    except Exception as e:
        print("Error:", traceback.format_exc())  # Log error lainnya
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
