
import sys
import json
import io
import os
import time
import soundfile as sf
# import kokoro # This will be available in the portable environment
# from kokoro import KPipeline

# Mocking Kokoro for now until we have the real environment
# In reality, this script will import torch, kokoro, etc.

from kokoro_onnx import Kokoro

def main():
    # Force logs to stderr
    def log(msg):
        sys.stderr.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        sys.stderr.flush()

    engine_dir = os.path.dirname(sys.executable)
    # Prefer INT8 model for speed, fall back to standard
    model_path_int8 = os.path.join(engine_dir, "kokoro-v1.0.int8.onnx")
    model_path_std = os.path.join(engine_dir, "kokoro-v1.0.onnx")
    
    model_path = model_path_int8 if os.path.exists(model_path_int8) else model_path_std
    voices_path = os.path.join(engine_dir, "voices-v1.0.bin")

    log(f"Initializing Kokoro with model: {model_path}")
    
    kokoro = None
    if os.path.exists(model_path) and os.path.exists(voices_path):
        try:
            # Set phonemizer to avoid issues if espeak-ng is missing
            kokoro = Kokoro(model_path, voices_path)
            log(f"Kokoro Engine Loaded ({'INT8' if 'int8' in model_path else 'FP32'}).")
        except Exception as e:
            log(f"CRITICAL: Failed to initialize Kokoro: {e}")
    else:
        log("CRITICAL: Kokoro model or voices file not found.")

    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            data = json.loads(line)
            text = data.get('text', '').strip()
            voice_name = data.get('voice', 'af_bella')
            speed = data.get('speed', 1.0)
            output_file = data.get('output_file')
            
            if not text or not output_file:
                continue
                
            if kokoro is None:
                log("Error: Runner is not initialized.")
                continue

            log(f"Processing Request: '{text[:30]}...'")
            
            start_time = time.time()
            # Generate audio
            samples, sample_rate = kokoro.create(text, voice=voice_name, speed=speed)
            duration = time.time() - start_time
            
            log(f"Generation Complete ({duration:.2f}s). Saving to {output_file}")
            sf.write(output_file, samples, sample_rate)
            
            # Send success JSON back via stdout buffer to be clean
            response = json.dumps({"status": "ok", "file": output_file}) + "\n"
            sys.stdout.buffer.write(response.encode('utf-8'))
            sys.stdout.buffer.flush()

        except Exception as e:
            log(f"Error during processing: {e}")
            # Even on error, try to send a response so Anki doesn't hang
            try:
                err_resp = json.dumps({"status": "error", "message": str(e)}) + "\n"
                sys.stdout.buffer.write(err_resp.encode('utf-8'))
                sys.stdout.buffer.flush()
            except: pass

if __name__ == "__main__":
    main()
