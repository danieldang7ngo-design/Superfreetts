"""
Batch state management for crash recovery and progress resumption.
Enables auto-save of batch progress and resumption on crash.
"""

import json
import os
import threading
from typing import Optional, Dict, List, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BatchStateCheckpoint:
    """Represents a checkpoint of batch execution state"""
    
    def __init__(self, batch_name: str, note_id_list: List[int], completed_indices: List[int], errors: Dict[int, str]):
        self.batch_name = batch_name
        self.note_id_list = note_id_list
        self.completed_indices = completed_indices
        self.errors = errors
        self.timestamp = datetime.now().isoformat()
        self.version = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize checkpoint to dictionary"""
        return {
            'batch_name': self.batch_name,
            'note_id_list': self.note_id_list,
            'completed_indices': self.completed_indices,
            'errors': self.errors,
            'timestamp': self.timestamp,
            'version': self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BatchStateCheckpoint':
        """Deserialize checkpoint from dictionary"""
        checkpoint = cls(
            batch_name=data.get('batch_name', 'unknown'),
            note_id_list=data.get('note_id_list', []),
            completed_indices=data.get('completed_indices', []),
            errors=data.get('errors', {})
        )
        checkpoint.timestamp = data.get('timestamp', checkpoint.timestamp)
        checkpoint.version = data.get('version', 1)
        return checkpoint
    
    def get_pending_notes(self) -> List[int]:
        """Get list of notes still pending processing."""
        pending_indices = [i for i in range(len(self.note_id_list)) if i not in self.completed_indices]
        return [self.note_id_list[i] for i in pending_indices]


class BatchStateManager:
    """
    Manages batch execution state for crash recovery.
    
    Provides:
    - Auto-save progress after each note
    - Resume interrupted batches
    - Error tracking and recovery
    - Thread-safe checkpointing
    """
    
    def __init__(self, state_dir: Optional[str] = None):
        """
        Initialize batch state manager.
        
        Args:
            state_dir: Directory to store state files (defaults to addon user_files)
        """
        self.state_dir = state_dir or self._get_default_state_dir()
        self._lock = threading.Lock()
        self._ensure_state_dir()
    
    def _get_default_state_dir(self) -> str:
        """Get default state directory in addon user_files"""
        from . import logging_utils
        addon_dir = logging_utils.get_addon_dir() if hasattr(logging_utils, 'get_addon_dir') else os.path.dirname(__file__)
        return os.path.join(addon_dir, 'user_files', 'batch_state')
    
    def _ensure_state_dir(self) -> None:
        """Create state directory if it doesn't exist"""
        os.makedirs(self.state_dir, exist_ok=True)
    
    def _get_checkpoint_path(self, batch_name: str) -> str:
        """Get file path for batch checkpoint"""
        safe_name = "".join(c for c in batch_name if c.isalnum() or c in ('-', '_'))[:50]
        return os.path.join(self.state_dir, f"{safe_name}.checkpoint.json")
    
    def save_checkpoint(self, checkpoint: BatchStateCheckpoint) -> None:
        """
        Save batch checkpoint to disk.
        
        Args:
            checkpoint: Checkpoint to save
        """
        with self._lock:
            try:
                path = self._get_checkpoint_path(checkpoint.batch_name)
                with open(path, 'w') as f:
                    json.dump(checkpoint.to_dict(), f, indent=2)
                logger.debug(f"Batch checkpoint saved: {checkpoint.batch_name}")
            except Exception as e:
                logger.error(f"Failed to save batch checkpoint: {e}")
    
    def load_checkpoint(self, batch_name: str) -> Optional[BatchStateCheckpoint]:
        """
        Load batch checkpoint from disk.
        
        Args:
            batch_name: Name of batch to load
            
        Returns:
            Checkpoint if found and valid, else None
        """
        with self._lock:
            try:
                path = self._get_checkpoint_path(batch_name)
                if not os.path.exists(path):
                    return None
                
                with open(path, 'r') as f:
                    data = json.load(f)
                
                checkpoint = BatchStateCheckpoint.from_dict(data)
                logger.info(f"Batch checkpoint loaded: {batch_name} ({len(checkpoint.completed_indices)}/{len(checkpoint.note_id_list)} completed)")
                return checkpoint
            except Exception as e:
                logger.error(f"Failed to load batch checkpoint {batch_name}: {e}")
                return None
    
    def update_progress(self, batch_name: str, completed_index: int, error: Optional[str] = None) -> None:
        """
        Update batch progress (add to completed list).
        
        Args:
            batch_name: Name of batch
            completed_index: Index of completed task
            error: Error message if task failed
        """
        checkpoint = self.load_checkpoint(batch_name)
        if checkpoint:
            if completed_index not in checkpoint.completed_indices:
                checkpoint.completed_indices.append(completed_index)
            if error:
                checkpoint.errors[str(completed_index)] = error
            self.save_checkpoint(checkpoint)
    
    def mark_batch_complete(self, batch_name: str) -> None:
        """
        Mark batch as complete and remove checkpoint.
        
        Args:
            batch_name: Name of batch
        """
        with self._lock:
            try:
                path = self._get_checkpoint_path(batch_name)
                if os.path.exists(path):
                    os.remove(path)
                    logger.info(f"Batch checkpoint cleaned up: {batch_name}")
            except Exception as e:
                logger.error(f"Failed to clean up batch checkpoint: {e}")
    
    def get_pending_notes(self, batch_name: str, note_id_list: List[int]) -> List[int]:
        """
        Get list of notes that still need processing.
        
        Args:
            batch_name: Name of batch
            note_id_list: Full list of notes in batch
            
        Returns:
            List of note IDs that haven't been completed
        """
        checkpoint = self.load_checkpoint(batch_name)
        if not checkpoint:
            return note_id_list
        
        # Get pending indices
        pending_indices = [i for i in range(len(note_id_list)) if i not in checkpoint.completed_indices]
        pending_notes = [note_id_list[i] for i in pending_indices]
        return pending_notes
    
    def cleanup_old_state_files(self, max_age_days: int = 7) -> None:
        """
        Clean up old checkpoint files.
        
        Args:
            max_age_days: Remove checkpoints older than this
        """
        with self._lock:
            try:
                from datetime import datetime, timedelta
                cutoff = datetime.now() - timedelta(days=max_age_days)
                
                for filename in os.listdir(self.state_dir):
                    if filename.endswith('.checkpoint.json'):
                        filepath = os.path.join(self.state_dir, filename)
                        file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                        if file_mtime < cutoff:
                            os.remove(filepath)
                            logger.debug(f"Removed old checkpoint: {filename}")
            except Exception as e:
                logger.error(f"Error cleaning up old state files: {e}")


# Global state manager instance
_batch_state_manager: Optional[BatchStateManager] = None


def get_batch_state_manager() -> BatchStateManager:
    """Get or create global batch state manager"""
    global _batch_state_manager
    if _batch_state_manager is None:
        _batch_state_manager = BatchStateManager()
    return _batch_state_manager


def reset_batch_state_manager() -> None:
    """Reset global batch state manager (for testing)"""
    global _batch_state_manager
    _batch_state_manager = None
