import os
import uuid
import subprocess
from flask import Flask, render_template, request, send_from_directory, jsonify
from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024 * 1024  # 1 GB upload limit

VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v"}
AUDIO_EXTS = {".mp3", ".wav", ".m4a", ".aac", ".ogg"}

def has_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, check=True)
        return True
    except Exception:
        return False

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/process")
def process_video():
    if "video" not in request.files:
        return jsonify(error="Please select a video file."), 400

    video = request.files["video"]
    if not video.filename:
        return jsonify(error="Please select a video file."), 400

    ext = os.path.splitext(secure_filename(video.filename))[1].lower()
    if ext not in VIDEO_EXTS:
        return jsonify(error="Unsupported video format."), 400

    if not has_ffmpeg():
        return jsonify(error="FFmpeg is not installed or not on PATH. See README.txt."), 500

    job_id = uuid.uuid4().hex[:12]
    input_path = os.path.join(UPLOAD_DIR, job_id + "_input" + ext)
    output_name = job_id + "_youtube_ready.mp4"
    output_path = os.path.join(OUTPUT_DIR, output_name)
    video.save(input_path)

    resolution = request.form.get("resolution", "1080")
    if resolution not in {"720", "1080"}:
        resolution = "1080"

    audio_mode = request.form.get("audio_mode", "keep")
    audio_path = None
    audio_file = request.files.get("audio")

    if audio_mode == "replace":
        if not audio_file or not audio_file.filename:
            return jsonify(error="Choose an audio file you own or are licensed to use."), 400
        audio_ext = os.path.splitext(secure_filename(audio_file.filename))[1].lower()
        if audio_ext not in AUDIO_EXTS:
            return jsonify(error="Unsupported audio format."), 400
        audio_path = os.path.join(UPLOAD_DIR, job_id + "_replacement" + audio_ext)
        audio_file.save(audio_path)

    # Standard YouTube-friendly H.264/AAC MP4 export. This does not remove copyright claims.
    scale = f"scale=-2:{resolution}:force_original_aspect_ratio=decrease"
    cmd = ["ffmpeg", "-y", "-i", input_path]
    if audio_mode == "replace" and audio_path:
        cmd += ["-stream_loop", "-1", "-i", audio_path]
        cmd += ["-map", "0:v:0", "-map", "1:a:0", "-shortest"]
    elif audio_mode == "mute":
        cmd += ["-map", "0:v:0", "-an"]
    else:
        cmd += ["-map", "0:v:0", "-map", "0:a?"]

    cmd += [
        "-vf", scale,
        "-c:v", "libx264", "-preset", "medium", "-crf", "21",
        "-pix_fmt", "yuv420p",
    ]
    if audio_mode != "mute":
        cmd += ["-c:a", "aac", "-b:a", "192k"]
    cmd += ["-movflags", "+faststart", output_path]

    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=3600)
        if result.returncode != 0 or not os.path.exists(output_path):
            message = result.stderr[-1800:] if result.stderr else "FFmpeg processing failed."
            return jsonify(error="Video processing failed: " + message), 500
    except subprocess.TimeoutExpired:
        return jsonify(error="Processing timed out. Try a shorter or smaller video."), 500
    finally:
        for path in (input_path, audio_path):
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass

    return jsonify(
        message="Processing complete. Copyright status is not verified.",
        download_url=f"/download/{output_name}",
        filename=output_name
    )

@app.get("/download/<path:filename>")
def download(filename):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
