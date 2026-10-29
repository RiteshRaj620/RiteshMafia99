CR-REMOVER WORKING PROJECT
==========================

WHAT IT DOES
- Upload a video through the web UI.
- Preview it in the browser.
- Use FFmpeg on the server to export a YouTube-friendly H.264 MP4 at 720p or 1080p.
- Keep original audio, mute it, or replace it with an audio file you own or are licensed to use.
- Download the processed output.

IMPORTANT
This is a video conversion/editing tool, NOT a copyright-claim remover. It does not defeat YouTube Content ID, remove ownership metadata to evade detection, or guarantee a video is copyright-free. Use only content you own or have permission/licensing to publish.

REQUIREMENTS
- Python 3.10+
- FFmpeg installed and available as `ffmpeg` in PATH.

INSTALL
1. Install Python.
2. Install FFmpeg:
   - Windows: install FFmpeg and add its bin folder to PATH.
   - Ubuntu/Debian: sudo apt update && sudo apt install ffmpeg
   - Termux: pkg update && pkg install python ffmpeg
3. Open terminal in this project folder.
4. Install Python packages:
   python -m pip install -r requirements.txt
5. Start server:
   python app.py
6. On the same device open http://127.0.0.1:5000
   On another device on the same Wi-Fi, use http://YOUR_COMPUTER_LAN_IP:5000

TERMUX NOTES
- Extract the ZIP in Termux-accessible storage.
- `cd` into the extracted project directory.
- Run the install and start commands above.
- Keep the terminal/server running while using the web app.
- This is a local development server. Do not expose it publicly without authentication, upload limits, cleanup policies, and production deployment hardening.

OUTPUT
Processed MP4 files are saved under outputs/. Uploaded source files are removed after processing. Generated output files remain until you delete them.
