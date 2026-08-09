"""
Performance Tracking Module

This module provides utilities to track audio generation performance in debug mode.
It tracks generation speed (real-time) and computes average generation speed.
Only active when SILENT_LOGGING_MODE is False (debug mode enabled).
"""

import time
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from . import logging_utils

logger = logging_utils.get_child_logger(__name__)


@dataclass
class GenerationStats:
    """Statistics for a single audio generation"""
    text: str
    voice_name: str
    start_time: float
    end_time: float = 0.0
    duration: float = 0.0
    
    def finalize(self):
        """Calculate the duration after generation is complete"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time


class PerformanceTracker:
    """
    Tracks audio generation performance metrics in debug mode.
    
    Usage:
        tracker = PerformanceTracker()
        tracker.start_generation('hello world', 'en-US-AriaNeural')
        # ... generate audio ...
        tracker.end_generation()
        tracker.report()
    """
    
    def __init__(self):
        self._generations: List[GenerationStats] = []
        self._current_generation: Optional[GenerationStats] = None
        self._batch_stats: Dict[str, List[float]] = {}  # batch_id -> list of durations
        self._enabled = not logging_utils.SILENT_LOGGING_MODE
    
    def _is_debug_mode(self) -> bool:
        """Check if debug mode is enabled"""
        return not logging_utils.SILENT_LOGGING_MODE
    
    def start_generation(self, text: str, voice_name: str) -> None:
        """
        Start tracking a new audio generation.
        
        Args:
            text: Text being converted to speech
            voice_name: Name/ID of the voice being used
        """
        if not self._is_debug_mode():
            return
        
        if self._current_generation is not None:
            # Previous generation wasn't finalized
            logger.warning('[PERF] Previous generation not finalized before starting new one')
            self.end_generation()
        
        self._current_generation = GenerationStats(
            text=text[:50] if len(text) > 50 else text,  # Truncate for logging
            voice_name=voice_name,
            start_time=time.time()
        )
        logger.info(f'[PERF] Starting generation: text="{self._current_generation.text}...", voice={voice_name}')
    
    def end_generation(self) -> Optional[float]:
        """
        End tracking the current audio generation.
        
        Returns:
            Duration in seconds, or None if not in debug mode or no generation was started
        """
        if not self._is_debug_mode() or self._current_generation is None:
            return None
        
        self._current_generation.finalize()
        duration = self._current_generation.duration
        
        logger.info(f'[PERF] Generation completed in {duration:.2f}s: text="{self._current_generation.text}...", voice={self._current_generation.voice_name}')
        
        self._generations.append(self._current_generation)
        self._current_generation = None
        
        return duration
    
    def add_batch_duration(self, batch_id: str, duration: float) -> None:
        """
        Record a generation duration for a batch.
        
        Args:
            batch_id: Identifier for the batch
            duration: Duration in seconds
        """
        if not self._is_debug_mode():
            return
        
        if batch_id not in self._batch_stats:
            self._batch_stats[batch_id] = []
        
        self._batch_stats[batch_id].append(duration)
    
    def get_average_duration(self) -> float:
        """Get average generation duration across all tracked generations"""
        if not self._generations or len(self._generations) == 0:
            return 0.0
        
        total = sum(g.duration for g in self._generations)
        return total / len(self._generations)
    
    def get_total_duration(self) -> float:
        """Get total time spent generating audio"""
        return sum(g.duration for g in self._generations)
    
    def get_generation_count(self) -> int:
        """Get number of audio generations tracked"""
        return len(self._generations)
    
    def report(self, batch_id: Optional[str] = None) -> str:
        """
        Generate a performance report.
        
        Args:
            batch_id: If provided, report only for this batch
        
        Returns:
            Human-readable performance report
        """
        if not self._is_debug_mode():
            return ""
        
        if batch_id and batch_id in self._batch_stats:
            durations = self._batch_stats[batch_id]
            if not durations:
                return ""
            
            total = sum(durations)
            avg = total / len(durations)
            min_dur = min(durations)
            max_dur = max(durations)
            
            report = (
                f"\n{'='*60}\n"
                f"[PERF] BATCH GENERATION REPORT: {batch_id}\n"
                f"{'='*60}\n"
                f"  Total generations:    {len(durations)}\n"
                f"  Total time:           {total:.2f}s\n"
                f"  Average time/card:    {avg:.2f}s\n"
                f"  Min time:             {min_dur:.2f}s\n"
                f"  Max time:             {max_dur:.2f}s\n"
                f"{'='*60}\n"
            )
        else:
            # Report all generations
            if not self._generations:
                return "[PERF] No audio generations tracked"
            
            avg_duration = self.get_average_duration()
            total_duration = self.get_total_duration()
            count = self.get_generation_count()
            
            report = (
                f"\n{'='*60}\n"
                f"[PERF] AUDIO GENERATION PERFORMANCE REPORT\n"
                f"{'='*60}\n"
                f"  Total generations:    {count}\n"
                f"  Total time:           {total_duration:.2f}s\n"
                f"  Average time/card:    {avg_duration:.2f}s\n"
                f"  Min time:             {min(g.duration for g in self._generations):.2f}s\n"
                f"  Max time:             {max(g.duration for g in self._generations):.2f}s\n"
                f"{'='*60}\n"
            )
        
        return report
    
    def print_report(self, batch_id: Optional[str] = None) -> None:
        """
        Print a performance report to logger.
        
        Args:
            batch_id: If provided, report only for this batch
        """
        if not self._is_debug_mode():
            return
        
        report = self.report(batch_id)
        if report:
            logger.info(report)
    
    def reset(self) -> None:
        """Reset all tracked data"""
        self._generations = []
        self._current_generation = None
        self._batch_stats = {}


# Global instance for convenience
_global_tracker = PerformanceTracker()


def get_performance_tracker() -> PerformanceTracker:
    """Get the global performance tracker instance"""
    return _global_tracker

