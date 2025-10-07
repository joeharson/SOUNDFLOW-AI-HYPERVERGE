from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
from new import process_audio
from flask_cors import CORS
import logging
import traceback
import torch
import sys
from werkzeug.serving import WSGIRequestHandler

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add version check
torch_version = torch.__version__
if not torch_version.startswith('1.10.0'):
    logger.warning(f"Warning: Model was trained with torch 1.10.0, but you're using {torch_version}. "
                  "This may cause compatibility issues.")

# Initialize Flask app and CORS support
app = Flask(__name__)
CORS(app)

# Set up file upload configurations
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a'}

# Function to check if the file type is valid
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_audio():
    try:
        if 'file' not in request.files:
            logger.error("No file part in request")
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            logger.error("No selected file")
            return jsonify({'error': 'No selected file'}), 400

        # Save the uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, "audio.wav")
        
        logger.info(f"Attempting to save file to: {file_path}")
        file.save(file_path)
        logger.info(f"File saved successfully at {file_path}")

        # Process the audio file
        logger.info("Starting audio processing")
        result = process_audio(file_path)
        logger.info(f"Processing result: {result}")

        # Check for errors in processing
        if isinstance(result, dict) and "error" in result:
            logger.error(f"Error in processing: {result['error']}")
            return jsonify({'error': result["error"]}), 500

        # Ensure result has the correct structure
        response_data = {
            'message': 'File processed successfully',
            'filename': filename,
            'transcription': {
                'segments': result.get('segments', []),
                'language': result.get('language', 'unknown'),
                'status': result.get('status', 'success')
            }
        }
        
        logger.info(f"Sending response: {response_data}")
        return jsonify(response_data)

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        return jsonify({'error': str(e)}), 500

@app.route('/process-audio', methods=['POST'])
def process_audio_file():
    logger.debug("=== Starting process_audio_file endpoint ===")
    logger.debug(f"Request files: {request.files}")
    
    if 'audio' not in request.files:
        logger.error("No 'audio' field in request files")
        return jsonify({'error': 'No audio file provided'}), 400
    
    file = request.files['audio']
    logger.debug(f"Received file: {file.filename}, type: {file.content_type}")
    
    if file.filename == '':
        logger.error("Empty filename received")
        return jsonify({'error': 'No selected file'}), 400

    try:
        # Save the uploaded file
        file_path = os.path.join(UPLOAD_FOLDER, 'audio.wav')
        logger.debug(f"Attempting to save file to: {file_path}")
        file.save(file_path)
        logger.debug(f"File saved successfully. Size: {os.path.getsize(file_path)} bytes")
        
        # Process the audio file
        logger.debug("Starting audio processing with process_audio function")
        result = process_audio(file_path)
        logger.debug(f"Processing completed. Result: {result}")
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error in process_audio_file: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500
    finally:
        logger.debug("=== Ending process_audio_file endpoint ===")

if __name__ == "__main__":
    # Disable reloader for specific paths
    WSGIRequestHandler.log_request = lambda *args, **kwargs: None
    
    # Run the Flask app with minimal configuration
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True,
        use_reloader=False
    )
