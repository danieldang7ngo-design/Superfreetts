
import sys
import json
import os
import time
import soundfile as sf
import numpy as np

def log(msg):
    # Log to stderr (captured by Anki)
    sys.stderr.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
    sys.stderr.flush()
    # Log to file if configured
    log_path = os.environ.get('SUPERFREETTS_LOG_FILE')
    if log_path:
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
        except: pass

def main():
    log("KOKORO HIGH-FIDELITY RUNNER STARTED (v1.0-stable)")
    
    # Eagerly load heavy libraries to avoid lag on first request
    try:
        log("Eagerly loading onnxruntime and kokoro_onnx...")
        import onnxruntime as ort
        from kokoro_onnx import Kokoro
        log(f"Libraries loaded. ONNX Runtime v{ort.__version__}")
    except Exception as e:
        log(f"Warning: Failed to eagerly load libraries: {e}")

    # Directory Structure
    engine_dir = os.path.dirname(sys.executable)
    models_dir = os.path.join(engine_dir, "models")
    
    # Ensure dirs exist
    os.makedirs(models_dir, exist_ok=True)

    engines = {}

    def get_engine(device='cpu', threads=0):
        engine_key = f"D:{device}_T:{threads}"
        if engine_key in engines:
            return engines[engine_key]
        
        # Resolve Brain (Model)
        model_path = os.path.join(models_dir, "kokoro-v1.0.onnx")
        if not os.path.exists(model_path):
            # Legacy fallback
            model_path = os.path.join(engine_dir, "kokoro-v1.0.onnx")
            
        if not os.path.exists(model_path):
            log("Error: No valid Kokoro model (Brain) found!")
            return None

        # Resolve Voices (Standard Bundle)
        # We prioritize voices-v1.0.bin (Official)
        voices_path = None
        possible_voices = ["voices-v1.0.bin", "v1.0-global.bin", "voices.bin"]
        for v_name in possible_voices:
            p = os.path.join(models_dir, v_name) # Check models dir first
            if os.path.exists(p):
                voices_path = p
                break
            p = os.path.join(engine_dir, v_name) # Check root dir
            if os.path.exists(p):
                voices_path = p
                break
        
        if not voices_path:
            log("Error: No valid Kokoro voice bundle found!")
            return None
            
        try:
            log(f"Initializing Kokoro: [Brain={os.path.basename(model_path)}] [Voice={os.path.basename(voices_path)}] on {device}...")
            from kokoro_onnx import Kokoro
            import onnxruntime as ort
            
            providers = ['CPUExecutionProvider']
            if device == 'gpu':
                available_providers = ort.get_available_providers()
                if 'DmlExecutionProvider' in available_providers:
                    providers = ['DmlExecutionProvider', 'CPUExecutionProvider']
                elif 'CUDAExecutionProvider' in available_providers:
                    providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']

            sess_options = ort.SessionOptions()
            sess_options.intra_op_num_threads = threads if threads > 0 else 1
            sess_options.inter_op_num_threads = 1

            # Standard Stock Initialization
            try:
                engine = Kokoro(model_path, voices_path, sess_options=sess_options)
            except TypeError:
                engine = Kokoro(model_path, voices_path)
                engine.sess = ort.InferenceSession(model_path, sess_options=sess_options, providers=providers)
            
            engines[engine_key] = engine
            log("Engine initialized successfully.")
            return engine
        except Exception as e:
            log(f"Failed to load engine: {e}")
            return None

    # Voice to Lang mapping for Kokoro
    LANG_MAP = {
        'a': 'en-us', 'b': 'en-gb', 'j': 'ja', 'z': 'zh', 
        'k': 'ko', 'f': 'fr', 'e': 'es', 'p': 'pt', 
        'i': 'it', 's': 'sv'
    }

    while True:
        try:
            line = sys.stdin.readline()
            if not line: break
            
            data = json.loads(line)
            action = data.get('action', 'generate')
            
            if action == 'init':
                device = data.get('device', 'cpu')
                threads = data.get('threads', 0)
                get_engine(device, threads)
                response = json.dumps({"status": "ok", "message": "initialized"}) + "\n"
                sys.stdout.buffer.write(response.encode('utf-8'))
                sys.stdout.buffer.flush()
                continue

            text = data.get('text', '').strip()
            voice_name = data.get('voice', 'af_bella')
            speed = data.get('speed', 1.0)
            output_file = data.get('output_file')
            
            if not text or not output_file: continue
            
            # Determine Language
            prefix = voice_name[0].lower() if voice_name else 'a'
            lang_code = LANG_MAP.get(prefix, 'en-us')

            device = data.get('device', 'cpu')
            threads = data.get('threads', 0)
            
            kokoro = get_engine(device, threads)
            if not kokoro:
                log("Error: Engine not available.")
                continue

            # Standard Generation
            try:
                log(f"Generating: Voice={voice_name}, Lang={lang_code}, Text='{text[:30]}...'")
                samples, sample_rate = kokoro.create(text, voice=voice_name, speed=speed, lang=lang_code)
                
                if output_file == "MEMORY":
                    import io
                    import base64
                    buffer = io.BytesIO()
                    sf.write(buffer, samples, sample_rate, format='WAV')
                    audio_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                    response = json.dumps({"status": "ok", "audio_b64": audio_b64}) + "\n"
                else:
                    sf.write(output_file, samples, sample_rate)
                    response = json.dumps({"status": "ok", "file": output_file}) + "\n"
                
                sys.stdout.buffer.write(response.encode('utf-8'))
                sys.stdout.buffer.flush()

            except Exception as e:
                log(f"Generation error: {e}")
                error_dict = {"status": "error", "message": str(e)}
                sys.stdout.buffer.write((json.dumps(error_dict) + "\n").encode('utf-8'))
                sys.stdout.buffer.flush()

        except Exception as e:
            log(f"Runner loop error: {e}")

if __name__ == "__main__":
    main()
