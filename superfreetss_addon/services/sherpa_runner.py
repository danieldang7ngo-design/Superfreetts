import os
import sys
import json
import time

# Robust path detection for embedded Python
base_dir = os.path.dirname(sys.executable)
site_packages = os.path.join(base_dir, 'Lib', 'site-packages')
if os.path.exists(site_packages) and site_packages not in sys.path:
    sys.path.append(site_packages)
# Also check for root site-packages (some setups)
site_packages_root = os.path.join(base_dir, 'site-packages')
if os.path.exists(site_packages_root) and site_packages_root not in sys.path:
    sys.path.append(site_packages_root)

def log(msg):
    # Log to stderr for Anki's logger
    sys.stderr.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
    sys.stderr.flush()
    # Also log to a file in data dir for deep debugging
    # Log to stderr for Anki's logger
    sys.stderr.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
    sys.stderr.flush()
    # Also log to a file in user_files for deep debugging
    try:
        appdata = os.environ.get('APPDATA')
        if appdata:
            log_dir = os.path.join(appdata, 'Anki2', 'addons21', 'Superfreetts', 'user_files')
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, 'sherpa_debug.log')
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception as e:
        sys.stderr.write(f"Log file error: {e}\n")

log("SHERPA RUNNER STARTED HELLO WORLD")
log("Runner script started. Importing dependencies...")

try:
    import sherpa_onnx
    log("sherpa_onnx imported.")
    import numpy as np
    log("numpy imported.")
    import soundfile as sf
    log("soundfile imported.")
except ImportError as e:
    log(f"Import Error: {e}")
    sys.exit(1)
except Exception as e:
    log(f"Startup Exception: {e}")
    sys.exit(1)

def main():
    log("Initializing Sherpa-ONNX Runner for MMS...")
    
    # Cache for models to avoid reloading
    models = {}
    model_order = []
    MAX_MODELS = 5

    while True:
        try:
            # ... existing input reading ...
            line_bytes = sys.stdin.buffer.readline()
            if not line_bytes:
                break
            line = line_bytes.decode('utf-8').strip()
            if not line:
                continue
            
            data = json.loads(line)
            text = data.get('text', '').strip()
            lang_code = data.get('lang_code')
            model_dir = data.get('model_dir')
            output_file = data.get('output_file')
            
            if not text or not model_dir or not output_file:
                continue

            # Load model if not in cache
            if model_dir not in models:
                # LRU: If too many models, remove the oldest one
                if len(model_order) >= MAX_MODELS:
                    oldest_dir = model_order.pop(0)
                    log(f"Cache full, unloading oldest model: {oldest_dir}")
                    if oldest_dir in models:
                        del models[oldest_dir]
                
                log(f"Loading Model from {model_dir}")
                # ... existing model config logic ...
                model_path = data.get('model_path') or os.path.join(model_dir, "model.onnx")
                tokens_path = data.get('tokens_path') or os.path.join(model_dir, "tokens.txt")
                lexicon_path = data.get('lexicon_path') or ""
                
                vits_config = sherpa_onnx.OfflineTtsVitsModelConfig(
                    model=model_path,
                    tokens=tokens_path,
                    lexicon=lexicon_path,
                    data_dir=data.get('data_dir', ""),
                    noise_scale=data.get('noise_scale', 0.667),
                    noise_scale_w=data.get('noise_scale_w', 0.8),
                    length_scale=data.get('length_scale', 1.0)
                )
                
                model_config = sherpa_onnx.OfflineTtsModelConfig(
                    vits=vits_config,
                    num_threads=data.get('num_threads', 1),
                    debug=False,
                    provider=data.get('provider', "cpu")
                )
                
                rule_fsts = data.get('rule_fsts', "")
                
                tts_config = sherpa_onnx.OfflineTtsConfig(
                    model=model_config,
                    rule_fsts=rule_fsts,
                    max_num_sentences=1
                )
                
                try:
                    models[model_dir] = sherpa_onnx.OfflineTts(tts_config)
                    model_order.append(model_dir)
                    log("Model Loaded successfully.")
                except Exception as ex:
                    log(f"CRITICAL: Failed to initialize OfflineTts: {ex}")
                    raise
            else:
                # Update LRU order: move used model to the end
                if model_dir in model_order:
                    model_order.remove(model_dir)
                model_order.append(model_dir)

            tts = models[model_dir]
            
            start_time = time.time()
            # Generate audio
            audio = tts.generate(text)
            duration = time.time() - start_time
            
            # Save audio
            sf.write(output_file, audio.samples, audio.sample_rate)
            log(f"MMS Generated in {duration:.2f}s")
            
            # Response
            response = json.dumps({"status": "ok", "file": output_file}) + "\n"
            sys.stdout.buffer.write(response.encode('utf-8'))
            sys.stdout.buffer.flush()

        except Exception as e:
            log(f"MMS Error: {e}")
            try:
                err_resp = json.dumps({"status": "error", "message": str(e)}) + "\n"
                sys.stdout.buffer.write(err_resp.encode('utf-8'))
                sys.stdout.buffer.flush()
            except: pass

if __name__ == "__main__":
    main()
