
import sys
import traceback
import json
import os
import time
import soundfile as sf
import numpy as np

# ponytail: force utf-8 on stdio streams, windows pipes are not safe
if os.name == 'nt' and hasattr(sys.stdin, 'reconfigure'):
    sys.stdin.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

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

def write_response(response):
    try:
        sys.stdout.buffer.write(response.encode('utf-8'))
        sys.stdout.buffer.flush()
        return True
    except (BrokenPipeError, OSError) as e:
        log(f"stdout closed while writing response: {e}")
        return False

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

    def generate_single(kokoro, text, voice_name, speed, lang_code, output_file):
        try:
            log(f"Generating: Voice={voice_name}, Lang={lang_code}, Text='{text[:30]}...'")
            samples, sample_rate = kokoro.create(text, voice=voice_name, speed=speed, lang=lang_code)
            
            if output_file == "MEMORY":
                import io
                import base64
                buffer = io.BytesIO()
                sf.write(buffer, samples, sample_rate, format='WAV')
                audio_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                return {"status": "ok", "audio_b64": audio_b64}
            else:
                sf.write(output_file, samples, sample_rate)
                return {"status": "ok", "file": output_file}
        except Exception as e:
            tb = traceback.format_exc()
            log(f"Generation error: {e}\n{tb}")
            return {"status": "error", "message": str(e), "traceback": tb}

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
                if not write_response(response):
                    break
                continue

            # Batch Generation (New High-Performance Action)
            if action == 'generate_batch':
                tasks = data.get('tasks', [])
                device = data.get('device', 'cpu')
                threads = data.get('threads', 0)
                kokoro = get_engine(device, threads)
                
                if not kokoro:
                    response = json.dumps({"status": "error", "message": "Engine not available for batch"}) + "\n"
                    if not write_response(response):
                        break
                    continue

                batch_results = []
                for task in tasks:
                    t_text = task.get('text', '').strip()
                    t_voice = task.get('voice', 'af_bella')
                    t_speed = task.get('speed', 1.0)
                    t_out = task.get('output_file', 'MEMORY')
                    
                    t_prefix = t_voice[0].lower() if t_voice else 'a'
                    t_lang = LANG_MAP.get(t_prefix, 'en-us')
                    
                    res = generate_single(kokoro, t_text, t_voice, t_speed, t_lang, t_out)
                    batch_results.append(res)
                
                response = json.dumps({"status": "ok", "results": batch_results}) + "\n"
                if not write_response(response):
                    break
                continue

            # Legacy Single Generation
            text = data.get('text', '').strip()
            voice_name = data.get('voice', 'af_bella')
            speed = data.get('speed', 1.0)
            output_file = data.get('output_file')
            device = data.get('device', 'cpu')
            threads = data.get('threads', 0)
            
            if not text or not output_file: 
                response = json.dumps({"status": "error", "message": "Missing text or output_file in legacy request"}) + "\n"
                if not write_response(response):
                    break
                continue
            
            kokoro = get_engine(device, threads)
            if not kokoro:
                log("Error: Engine not available.")
                response = json.dumps({"status": "error", "message": "Engine not available for legacy request"}) + "\n"
                if not write_response(response):
                    break
                continue

            prefix = voice_name[0].lower() if voice_name else 'a'
            lang_code = LANG_MAP.get(prefix, 'en-us')

            res = generate_single(kokoro, text, voice_name, speed, lang_code, output_file)
            response = json.dumps(res) + "\n"
            if not write_response(response):
                break

        except Exception as e:
            tb = traceback.format_exc()
            log(f"Runner loop error: {e}\n{tb}")
            err_resp = json.dumps({"status": "error", "message": str(e), "traceback": tb}) + "\n"
            if not write_response(err_resp):
                break

if __name__ == "__main__":
    main()
