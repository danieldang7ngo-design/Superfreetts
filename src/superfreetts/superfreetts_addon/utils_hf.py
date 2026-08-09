import os
import requests
import logging
from aqt import mw
from .downloader import TurboDownloader

logger = logging.getLogger(__name__)

def download_file(url, dest_path, progress_callback=None):
    """Downloads a file using TurboDownloader with progress reporting."""
    try:
        debug_mode = False
        if hasattr(mw, 'hyper_tts'):
            debug_mode = mw.hyper_tts.get_preferences().error_handling.debug_mode
            
        def on_progress(data):
            if progress_callback:
                progress_callback(data['downloaded'], data['total'])
        
        downloader = TurboDownloader(url, dest_path, progress_callback=on_progress, debug_mode=debug_mode)
        downloader.start()
        return True
    except Exception as e:
        logger.error(f"Failed to download {url}: {e}")
        return False

def get_hf_model_files(repo_id, folder_path=""):
    """
    Returns a list of files in a HuggingFace repo folder.
    Uses the HF API: https://huggingface.co/api/models/{repo_id}
    """
    api_url = f"https://huggingface.co/api/models/{repo_id}"
    try:
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        files = []
        for file_info in data.get('siblings', []):
            rpath = file_info.get('rpath', '')
            if not folder_path or rpath.startswith(folder_path):
                files.append(rpath)
        return files
    except Exception as e:
        logger.error(f"Failed to fetch HF repo info for {repo_id}: {e}")
        return []

def get_download_url(repo_id, filename):
    return f"https://huggingface.co/{repo_id}/resolve/main/{filename}"
