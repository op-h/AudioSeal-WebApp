import os
import traceback
from flask import Flask, request, render_template, send_from_directory, jsonify
from werkzeug.utils import secure_filename

# Make sure all functions are imported correctly from your dsp_core file
from dsp_core import embed_lsb, detect_lsb

app = Flask(__name__)

# --- Configuration ---
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
# --- CHANGE: Increased upload limit from 100MB to 500MB ---
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024 # 500 MB max upload size

@app.route('/favicon.ico')
def favicon():
    """Handles browser's request for a favicon to prevent 404 errors."""
    return '', 204 # Return 'No Content'

@app.route('/')
def index():
    """Renders the main page."""
    return render_template('index.html')

@app.route('/embed', methods=['POST'])
def handle_embed():
    """Endpoint for embedding the watermark."""
    if 'audio' not in request.files or 'watermark' not in request.form:
        return jsonify({"error": "Missing audio file or watermark text"}), 400

    file = request.files['audio']
    watermark = request.form['watermark']

    if file.filename == '' or not watermark.strip():
        return jsonify({"error": "Audio file and watermark text cannot be empty"}), 400

    try:
        input_filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], input_filename)
        file.save(input_path)

        output_filename = "sealed_" + os.path.splitext(input_filename)[0] + '.wav'
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)

        # --- Call the DSP core function ---
        embed_lsb(input_path, watermark, output_path)

        return jsonify({"download_filename": output_filename})

    except Exception as e:
        # --- ENHANCEMENT: Detailed Error Logging ---
        # This will print the full error to your terminal for debugging.
        print(f"An error occurred during embedding:")
        traceback.print_exc()
        # Send a user-friendly error back to the frontend.
        return jsonify({"error": str(e)}), 500


@app.route('/detect', methods=['POST'])
def handle_detect():
    """Endpoint for detecting the watermark."""
    if 'audio' not in request.files:
        return jsonify({"error": "Missing audio file"}), 400

    file = request.files['audio']
    if file.filename == '':
        return jsonify({"error": "No audio file selected"}), 400

    try:
        input_filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], input_filename)
        file.save(input_path)

        # --- Call the DSP core function ---
        detected_text = detect_lsb(input_path)

        return jsonify({"watermark": detected_text})

    except Exception as e:
        # --- ENHANCEMENT: Detailed Error Logging ---
        print(f"An error occurred during detection:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/download/<filename>')
def download_file(filename):
    """Provides the sealed file for download."""
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)

