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
    # Log to stderr (captured by Anki/Service)
    sys.stderr.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
    sys.stderr.flush()
    # Log to file if configured
    log_path = os.environ.get('SUPERFREETTS_LOG_FILE')
    if log_path:
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
        except Exception as e:
            sys.stderr.write(f"Log file error: {e}\n")

log("SHERPA RUNNER V2 STARTED")
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
    
    # Track current provider/threads to reload if changed
    current_config_hash = {} 

    while True:
        try:
            # Use binary stdin to avoid encoding issues on Windows
            line_bytes = sys.stdin.buffer.readline()
            if not line_bytes:
                break
            line = line_bytes.decode('utf-8').strip()
            if not line:
                continue
            
            log(f"Received request: {line[:100]}...")
            data = json.loads(line)
            text = data.get('text', '').strip()
            # lang_code = data.get('lang_code') # Not strictly used here, model_dir determines model
            model_dir = data.get('model_dir')
            output_file = data.get('output_file')
            
            if not text or not model_dir or not output_file:
                continue

            # Performance settings
            num_threads = data.get('num_threads', 1)
            provider = data.get('provider', "cpu")
            
            # Create a simple hash of config to detect changes
            config_key = f"{model_dir}_{num_threads}_{provider}"

            # Load model if not in cache or config changed
            if model_dir not in models or current_config_hash.get(model_dir) != config_key:
                log(f"Loading Model from {model_dir} (Threads={num_threads}, Provider={provider})")
                
                # Support both directory-based loading (MMS) and specific file paths
                model_path = data.get('model_path') or os.path.join(model_dir, "model.onnx")
                tokens_path = data.get('tokens_path') or os.path.join(model_dir, "tokens.txt")
                
                # Lexicon support (Critical for pronunciation fixes)
                lexicon_path = data.get('lexicon_path') or ""
                if not lexicon_path and os.path.exists(os.path.join(model_dir, "lexicon.txt")):
                    lexicon_path = os.path.join(model_dir, "lexicon.txt")
                
                if not os.path.exists(model_path):
                    log(f"Error: Model path {model_path} does not exist")
                    continue

                # Correct Config hierarchy for Sherpa-ONNX
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
                    num_threads=int(num_threads),
                    debug=False, # Disable internal debug to avoid potential deadlocks
                    provider=str(provider)
                )
                
                # Rule FSTs for Japanese/Korean processing if provided
                rule_fsts = data.get('rule_fsts') or ""
                
                log(f"Initializing Sherpa-ONNX engine with:")
                log(f"  Model: {model_path}")
                log(f"  Tokens: {tokens_path}")
                log(f"  Lexicon: {lexicon_path} (Exists: {os.path.exists(lexicon_path) if lexicon_path else 'N/A'})")
                log(f"  Threads: {num_threads}")
                log(f"  Provider: {provider}")
                
                tts_config = sherpa_onnx.OfflineTtsConfig(
                    model=model_config,
                    rule_fsts=str(rule_fsts),
                    max_num_sentences=1
                )
                
                try:
                    log("Creating OfflineTts instance...")
                    models[model_dir] = sherpa_onnx.OfflineTts(tts_config)
                    current_config_hash[model_dir] = config_key
                    log("Model Loaded successfully.")
                except Exception as ex:
                    log(f"CRITICAL: Failed to initialize OfflineTts: {ex}")
                    # Remove from cache if failed
                    if model_dir in models: del models[model_dir]
                    raise

            tts = models[model_dir]
            
            start_time = time.time()
            # Generate audio
            audio = tts.generate(text, sid=0, speed=1.0)
            duration = time.time() - start_time
            
            # Save audio
            sf.write(output_file, audio.samples, audio.sample_rate)
            log(f"Generated in {duration:.2f}s")
            
            # Response
            response = json.dumps({"status": "ok", "file": output_file}) + "\n"
            sys.stdout.buffer.write(response.encode('utf-8'))
            sys.stdout.buffer.flush()

        except Exception as e:
            log(f"Error: {e}")
            try:
                err_resp = json.dumps({"status": "error", "message": str(e)}) + "\n"
                sys.stdout.buffer.write(err_resp.encode('utf-8'))
                sys.stdout.buffer.flush()
            except: pass

if __name__ == "__main__":
    main()
