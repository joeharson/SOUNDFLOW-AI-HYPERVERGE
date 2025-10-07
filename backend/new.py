import whisperx
import gc
import torch
import logging
import os
import traceback

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Set default file path
DEFAULT_FILE_PATH = os.path.join("uploads", "audio.wav")

def process_audio(file_path=DEFAULT_FILE_PATH):
    logger.info("=== Starting process_audio function ===")
    logger.info(f"Processing file: {file_path}")
    logger.info(f"File exists: {os.path.exists(file_path)}")
    logger.info(f"File size: {os.path.getsize(file_path) if os.path.exists(file_path) else 'N/A'} bytes")
    
    if not os.path.exists(file_path):
        logger.error("File not found at specified path")
        return {"error": "Please upload a valid audio file."}

    try:
        # Clear GPU memory if available
        logger.info("Clearing GPU memory")
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            logger.info("CUDA is available and cache cleared")
        else:
            logger.info("CUDA is not available, using CPU")

        # Determine device based on availability
        device = "cuda" if torch.cuda.is_available() else "cpu"
        compute_type = "float16" if torch.cuda.is_available() else "int8"
        batch_size = 4 if torch.cuda.is_available() else 1
        logger.info(f"Using device: {device}, compute_type: {compute_type}, batch_size: {batch_size}")

        # Load audio
        logger.info(f"Loading audio from {file_path}")
        try:
            audio = whisperx.load_audio(file_path)
            logger.info(f"Audio loaded successfully. Shape: {audio.shape}")
        except Exception as e:
            logger.error(f"Error loading audio: {str(e)}")
            raise

        # Load transcription model
        logger.info("Loading whisperx model...")
        try:
            model = whisperx.load_model(
                "large-v2", 
                device=device, 
                compute_type=compute_type
            )
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise

        # Transcribe the audio
        logger.info("Starting transcription...")
        try:
            result = model.transcribe(audio, batch_size=batch_size)
            logger.info(f"Transcription completed. Language detected: {result.get('language', 'unknown')}")
            logger.info(f"Number of segments: {len(result.get('segments', []))}")
        except Exception as e:
            logger.error(f"Error during transcription: {str(e)}")
            raise

        # Load alignment model
        logger.info("Loading alignment model...")
        try:
            model_a, metadata = whisperx.load_align_model(
                language_code=result["language"],
                device=device
            )
            logger.info("Alignment model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading alignment model: {str(e)}")
            raise

        # Align transcription
        logger.info("Aligning transcription with audio...")
        try:
            result = whisperx.align(
                result["segments"], 
                model_a, 
                metadata, 
                audio, 
                device,
                return_char_alignments=False
            )
            logger.info("Alignment completed successfully")
        except Exception as e:
            logger.error(f"Error during alignment: {str(e)}")
            raise

        # Clean up alignment models
        del model_a
        gc.collect()
        logger.info("Cleaned up alignment models")

        # Diarization process
        logger.info("Starting diarization...")
        try:
            diarize_model = whisperx.DiarizationPipeline(
                use_auth_token="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",
                device=device
            )
            logger.info("Diarization model loaded")

            diarize_segments = diarize_model(
                audio,
                min_speakers=2,
                max_speakers=4
            )
            logger.info("Diarization completed successfully")
        except Exception as e:
            logger.error(f"Error during diarization: {str(e)}")
            raise

        # Assign speakers to words
        logger.info("Assigning speakers to segments...")
        try:
            result = whisperx.assign_word_speakers(diarize_segments, result)
            logger.info("Speaker assignment completed")
        except Exception as e:
            logger.error(f"Error assigning speakers: {str(e)}")
            raise

        # Format output
        formatted_result = {
            "status": "success",
            "segments": [
                {
                    "speaker": segment.get("speaker", "Unknown"),
                    "start": round(float(segment["start"]), 2),
                    "end": round(float(segment["end"]), 2),
                    "text": segment["text"]
                }
                for segment in result["segments"]
            ],
            "language": result.get("language", "unknown")
        }

        logger.info(f"Final formatted result: {formatted_result}")
        logger.info("Processing complete!")
        return formatted_result

    except Exception as e:
        logger.error(f"Error in process_audio: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {"error": f"Error processing audio: {str(e)}"}

    finally:
        # Cleanup
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up file: {file_path}")
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                logger.info("Cleaned up GPU memory")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
        logger.info("=== Ending process_audio function ===")
