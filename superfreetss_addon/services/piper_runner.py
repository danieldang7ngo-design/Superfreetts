
import sys
import json
import os
import time
import subprocess
import io
import base64
import wave

# Inject local libs path (still needed for soundfile or other dependencies if used, 
# but we'll try to use standard 'wave' module for zero-dependency WAV creation)
base_dir = os.path.dirname(os.path.dirname(__file__))
libs_path = os.path.join(base_dir, 'libs')
if os.path.exists(libs_path) and libs_path not in sys.path:
    sys.path.insert(0, libs_path)

def log(msg):
    sys.stderr.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
    sys.stderr.flush()

def pcm_to_wav(pcm_data, sample_rate=22050, channels=1, sampwidth=2):
    """Convert raw PCM data to WAV format in memory."""
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wav:
        wav.setnchannels(channels)
        wav.setsampwidth(sampwidth)
        wav.setframerate(sample_rate)
        wav.writeframes(pcm_data)
    return buf.getvalue()

def main():
    log("PIPER-STOCK RUNNER STARTED")
    
    # Resolve piper.exe path
    data_dir = os.environ.get('SUPERFREETSS_DATA_DIR')
    
    if data_dir:
        piper_exe = os.path.join(data_dir, 'piper_engine', 'piper', 'piper.exe')
    else:
        addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        piper_exe = os.path.join(addon_dir, 'data', 'piper_engine', 'piper', 'piper.exe')
    
    if not os.path.exists(piper_exe):
        log(f"ERROR: piper.exe not found at {piper_exe}")

    while True:
        try:
            line = sys.stdin.readline()
            if not line: break
            
            data = json.loads(line)
            action = data.get('action', 'generate')
            
            if action == 'init':
                # No-op for stock piper as it's spawned per-request or we just check paths here
                response = json.dumps({"status": "ok", "message": "ready"}) + "\n"
                sys.stdout.buffer.write(response.encode('utf-8'))
                sys.stdout.buffer.flush()
                continue
            
            # Batch Generation
            if action == 'generate_batch':
                tasks = data.get('tasks', [])
                num_threads = data.get('num_threads', 1)
                
                batch_results = []
                for task in tasks:
                    batch_results.append(generate_single(piper_exe, task, num_threads))
                
                response = json.dumps({"status": "ok", "results": batch_results}) + "\n"
                sys.stdout.buffer.write(response.encode('utf-8'))
                sys.stdout.buffer.flush()
                continue

            # Single Generation
            num_threads = data.get('num_threads', 1)
            res = generate_single(piper_exe, data, num_threads)
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

def generate_single(piper_exe, data, global_threads=1):
    try:
        text = data.get('text', '').strip()
        model_path = data.get('model_path')
        data_dir = data.get('data_dir') # espeak-ng-data
        speed = data.get('speed', 1.0)
        
        if not text or not model_path:
            return {"status": "error", "message": "Missing text or model_path"}

        if not os.path.exists(piper_exe):
            return {"status": "error", "message": f"piper.exe not found at {piper_exe} (SUPERFREETSS_DATA_DIR={data_dir})"}

        # Piper speed is controlled by length-scale (inverse of speed)
        # 1.0 = normal, 0.5 = 2x faster, 2.0 = 2x slower
        # But piper stock '-s/--length-scale' behaves this way.
        # If user provides 'speed' where 2.0 is faster, we invert it.
        # Wait, service_piper.py provides length_scale as speed?
        # Let's check: length_scale = options.get('length_scale', 1.0)
        # and in build_voice_v3: 'tooltip': '1.0 = normal, 0.5 = 2x faster, 2.0 = 2x slower'
        # So 'speed' in our JSON is already length_scale.
        length_scale = speed

        # Command for stock piper:
        # piper.exe -m model.onnx -c model.onnx.json --data_dir ... --length-scale ... --output_raw
        cmd = [
            piper_exe,
            "-m", model_path,
            "--data_dir", data_dir,
            "--length-scale", str(length_scale),
            "--output_raw"
        ]
        
        # Add threads if specified
        # Note: -t flag might not exist in all piper versions, but usually it does for multi-threaded phonemization.
        if global_threads > 1:
            cmd.extend(["-t", str(global_threads)])

        log(f"Running: {' '.join(cmd)}")
        start_time = time.time()
        
        # Spawn piper.exe
        # We use a startupinfo to hide the window on Windows
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            startupinfo=startupinfo
        )
        
        # Send text and close stdin
        stdout, stderr = process.communicate(input=text.encode('utf-8'))
        
        if process.returncode != 0:
            err_msg = stderr.decode('utf-8', errors='replace')
            log(f"Piper error: {err_msg}")
            return {"status": "error", "message": err_msg}

        if not stdout:
            return {"status": "error", "message": "No audio output from piper.exe"}

        # piper.exe outputs raw 16-bit mono PCM at 22050Hz (usually)
        # We need to get the sample rate from the .json config to be precise
        sample_rate = 22050
        try:
            config_path = model_path + ".json"
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    sample_rate = config.get('audio', {}).get('sample_rate', 22050)
        except: pass

        wav_data = pcm_to_wav(stdout, sample_rate=sample_rate)
        audio_b64 = base64.b64encode(wav_data).decode('utf-8')
        
        duration = time.time() - start_time
        log(f"Generated {len(stdout)} bytes in {duration:.2f}s (SR={sample_rate})")
        
        return {
            "status": "ok",
            "audio_b64": audio_b64,
            "duration": duration
        }
        
    except Exception as e:
        log(f"Exception in generate_single: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
