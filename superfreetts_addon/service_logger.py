"""
Centralized Service Logger for TTS services.
Provides per-service install and runtime log files with consistent formatting.

Log files are stored in: superfreetts_addon/user_files/log/
Each service gets two files:
    - {service}_install.log  (always writes — installation events)
    - {service}_runtime.log  (controlled by debug_logging config — TTS events)
"""

import os
import time
import threading

# Log directory (relative to this file's location)
_ADDON_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(_ADDON_DIR, 'user_files', 'log')

# Maximum log file size before rotation (5 MB)
_MAX_LOG_SIZE = 5 * 1024 * 1024

# Thread lock for file writes
_write_lock = threading.Lock()


def _ensure_log_dir():
    """Create log directory if it doesn't exist."""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR, exist_ok=True)


def _rotate_if_needed(filepath):
    """Rotate log file if it exceeds _MAX_LOG_SIZE."""
    try:
        if os.path.exists(filepath) and os.path.getsize(filepath) > _MAX_LOG_SIZE:
            backup = filepath + '.old'
            if os.path.exists(backup):
                os.remove(backup)
            os.rename(filepath, backup)
    except Exception:
        pass


def _get_log_path(service_name, log_type):
    """Get the log file path for a service.
    
    Args:
        service_name: e.g. 'mms', 'edgetts', 'piper', 'kokoro'
        log_type: 'install' or 'runtime'
    """
    return os.path.join(LOG_DIR, f'{service_name}_{log_type}.log')


def write_log(service_name, log_type, level, message, details=None):
    """Write a formatted log entry to the appropriate service log file.
    
    Args:
        service_name: e.g. 'mms', 'edgetts', 'piper', 'kokoro'
        log_type: 'install' or 'runtime'
        level: 'INFO', 'OK', 'WARN', 'ERROR'
        message: Main log message
        details: Optional dict of key-value pairs to include
    """
    try:
        _ensure_log_dir()
        filepath = _get_log_path(service_name, log_type)
        _rotate_if_needed(filepath)

        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        
        lines = []
        lines.append(f'[{timestamp}] [{level}] {message}')
        
        if details:
            for key, value in details.items():
                lines.append(f'    {key}: {value}')
        
        lines.append('')  # Empty line for spacing between entries
        
        entry = '\n'.join(lines) + '\n'
        
        with _write_lock:
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(entry)
    except Exception:
        pass  # Never crash the addon due to logging


def write_install_separator(service_name, command_text):
    """Write a separator block for install commands (matches existing MMS format).
    
    Args:
        service_name: e.g. 'mms', 'piper', 'kokoro'
        command_text: The command being run
    """
    try:
        _ensure_log_dir()
        filepath = _get_log_path(service_name, 'install')
        _rotate_if_needed(filepath)

        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        
        block = (
            f'\n{"=" * 60}\n'
            f'[{timestamp}] Command: {command_text}\n'
        )
        
        with _write_lock:
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(block)
    except Exception:
        pass


def write_install_result(service_name, exit_code, stdout=None, stderr=None):
    """Write command result to install log.
    
    Args:
        service_name: e.g. 'mms', 'piper', 'kokoro'
        exit_code: Process return code
        stdout: Standard output text
        stderr: Standard error text
    """
    try:
        filepath = _get_log_path(service_name, 'install')
        
        lines = [f'Exit code: {exit_code}']
        if stdout:
            lines.append(f'--- STDOUT ---\n{stdout}')
        if stderr:
            lines.append(f'--- STDERR ---\n{stderr}')
        lines.append('')
        
        with _write_lock:
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write('\n'.join(lines) + '\n')
    except Exception:
        pass


def get_log_dir():
    """Return the log directory path (for UI 'Open Log Folder' buttons)."""
    _ensure_log_dir()
    return LOG_DIR
