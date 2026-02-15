import os
import requests
import logging

logger = logging.getLogger(__name__)

def download_file(url, dest_path, progress_callback=None):
    """Downloads a file with optional progress reporting."""
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    if progress_callback and total_size > 0:
                        progress_callback(downloaded_size, total_size)
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
