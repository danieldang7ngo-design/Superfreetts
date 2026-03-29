
import sys
import json
import os
import time
import soundfile as sf
import sherpa_onnx
import io
import base64

# Inject local libs path
base_dir = os.path.dirname(os.path.dirname(__file__))
libs_path = os.path.join(base_dir, 'libs')
if os.path.exists(libs_path) and libs_path not in sys.path:
    sys.path.insert(0, libs_path)

def log(msg):
    sys.stderr.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
    sys.stderr.flush()

def main():
    log("PIER-SHERPA RUNNER STARTED")
    
    engines = {}

    def get_engine(model_path, tokens_path, data_dir, device='cpu', threads=2):
        engine_key = f"{model_path}_{device}_{threads}"
        if engine_key in engines:
            return engines[engine_key]
        
        if not os.path.exists(model_path):
            log(f"Model not found: {model_path}")
            return None
            
        try:
            log(f"Loading Piper-Sherpa engine: {os.path.basename(model_path)} on {device}...")
            
            # Piper Configuration for Sherpa-ONNX
            vits_config = sherpa_onnx.OfflineTtsVitsModelConfig(
                model=model_path,
                lexicon="",
                tokens=tokens_path,
                data_dir=data_dir,
                noise_scale=0.667,
                noise_scale_w=0.8,
                length_scale=1.0
            )
            
            # Overall Configuration
            # threads = processes (8) * 2 = 16 saturation
            s_threads = threads if threads > 0 else 1
            
            model_config = sherpa_onnx.OfflineTtsModelConfig(
                vits=vits_config,
                num_threads=s_threads,
                debug=False,
                provider=device
            )
            
            tts_config = sherpa_onnx.OfflineTtsConfig(
                model=model_config,
                rule_fsts="",
                max_num_sentences=1
            )
            
            engine = sherpa_onnx.OfflineTts(tts_config)
            engines[engine_key] = engine
            log(f"Engine {os.path.basename(model_path)} initialized.")
            return engine
        except Exception as e:
            log(f"Failed to load engine: {e}")
            return None

    def generate_single(engine, text, sid, speed):
        try:
            log(f"Request: SID={sid}, Text='{text[:30]}...'")
            start_time = time.time()
            audio = engine.generate(text, sid=sid, speed=speed)
            duration = time.time() - start_time
            log(f"Generated in {duration:.2f}s")

            buffer = io.BytesIO()
            sf.write(buffer, audio.samples, audio.sample_rate, format='WAV')
            audio_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return {
                "status": "ok", 
                "audio_b64": audio_b64,
                "duration": duration
            }
        except Exception as e:
            log(f"Generation error: {e}")
            return {"status": "error", "message": str(e)}

    while True:
        try:
            line = sys.stdin.readline()
            if not line: break
            
            data = json.loads(line)
            action = data.get('action', 'generate')
            
            if action == 'init':
                model_path = data.get('model_path')
                tokens_path = data.get('tokens_path')
                data_dir = data.get('data_dir', os.path.dirname(model_path))
                if model_path and tokens_path:
                    get_engine(model_path, tokens_path, data_dir)
                
                response = json.dumps({"status": "ok", "message": "initialized"}) + "\n"
                sys.stdout.buffer.write(response.encode('utf-8'))
                sys.stdout.buffer.flush()
                continue

            # Batch Generation
            if action == 'generate_batch':
                tasks = data.get('tasks', [])
                # Use first task's model to resolve engine (assume batch is for same engine)
                # This is standard for our batching logic
                if not tasks: continue
                
                first = tasks[0]
                model_path = first.get('model_path')
                tokens_path = first.get('tokens_path')
                data_dir = first.get('data_dir', os.path.dirname(model_path))
                
                engine = get_engine(model_path, tokens_path, data_dir)
                if engine is None:
                    response = json.dumps({"status": "error", "message": "Engine failed to load"}) + "\n"
                    sys.stdout.buffer.write(response.encode('utf-8'))
                    sys.stdout.buffer.flush()
                    continue

                batch_results = []
                for task in tasks:
                    t_text = task.get('text', '').strip()
                    t_sid = task.get('sid', 0)
                    t_speed = task.get('speed', 1.0)
                    batch_results.append(generate_single(engine, t_text, t_sid, t_speed))
                
                response = json.dumps({"status": "ok", "results": batch_results}) + "\n"
                sys.stdout.buffer.write(response.encode('utf-8'))
                sys.stdout.buffer.flush()
                continue

            # Legacy Single Generation
            text = data.get('text', '').strip()
            model_path = data.get('model_path')
            tokens_path = data.get('tokens_path')
            data_dir = data.get('data_dir', os.path.dirname(model_path))
            sid = data.get('sid', 0)
            speed = data.get('speed', 1.0)
            
            if not text or not model_path: continue
            
            engine = get_engine(model_path, tokens_path, data_dir)
            if engine is None:
                continue

            res = generate_single(engine, text, sid, speed)
            response = json.dumps(res) + "\n"
            sys.stdout.buffer.write(response.encode('utf-8'))
            sys.stdout.buffer.flush()

        except Exception as e:
            log(f"Error in piper loop: {e}")
            try:
                err_resp = json.dumps({"status": "error", "message": str(e)}) + "\n"
                sys.stdout.buffer.write(err_resp.encode('utf-8'))
                sys.stdout.buffer.flush()
            except: pass

if __name__ == "__main__":
    main()
