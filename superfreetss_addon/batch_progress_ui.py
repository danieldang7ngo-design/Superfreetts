"""
Enhanced batch processing progress UI with phase indicators, color transitions, and real-time ETA.
Provides visual feedback for batch operations with intuitive phase stages and timing information.
"""

import aqt.qt
from typing import Optional, Callable
from datetime import datetime, timedelta
import math


class BatchProgressPhase:
    """Enumeration of batch processing phases."""
    LOADING = "Loading Voices"
    PREPARING = "Preparing Notes"
    DEDUPLICATING = "Analyzing Duplicates"
    GENERATING = "Generating Audio"
    SAVING = "Saving to Collection"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class BatchProgressWidget(aqt.qt.QWidget):
    """
    Enhanced progress widget with phase indicators, color transitions, ETA, and keyboard shortcuts.
    
    Features:
    - Phase indicator bar showing current processing stage
    - Color transitions: blue (active) → green (completed) → done
    - Real-time ETA calculation based on processed items
    - Progress bar with percentage text
    - Phase-aware formatting and styling
    - Keyboard shortcuts: ESC=cancel, R=retry
    """
    
    def __init__(self, cancel_callback: Optional[Callable] = None):
        """
        Initialize enhanced progress widget.
        
        Args:
            cancel_callback: Function to call when cancel is requested (ESC key)
        """
        super().__init__()
        self.cancel_callback = cancel_callback
        self.current_phase = BatchProgressPhase.LOADING
        self.start_time = None
        self.completed_count = 0
        self.total_count = 0
        self.phase_start_times = {}  # Track when each phase started
        
        # Colors for different phases
        self.phase_colors = {
            BatchProgressPhase.LOADING: self._hex_to_rgb("#3498db"),      # Blue
            BatchProgressPhase.PREPARING: self._hex_to_rgb("#3498db"),    # Blue
            BatchProgressPhase.DEDUPLICATING: self._hex_to_rgb("#3498db"), # Blue
            BatchProgressPhase.GENERATING: self._hex_to_rgb("#3498db"),    # Blue
            BatchProgressPhase.SAVING: self._hex_to_rgb("#2ecc71"),        # Green
            BatchProgressPhase.COMPLETED: self._hex_to_rgb("#27ae60"),     # Dark green
            BatchProgressPhase.CANCELLED: self._hex_to_rgb("#e74c3c"),     # Red
        }
        
        self._setup_ui()
        self._setup_keyboard_shortcuts()
    
    def _setup_ui(self) -> None:
        """Setup the UI components."""
        layout = aqt.qt.QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # Phase indicator bar
        phase_layout = aqt.qt.QHBoxLayout()
        self.phase_labels = {}
        phases = [
            BatchProgressPhase.LOADING,
            BatchProgressPhase.PREPARING,
            BatchProgressPhase.DEDUPLICATING,
            BatchProgressPhase.GENERATING,
            BatchProgressPhase.SAVING,
        ]
        
        for i, phase in enumerate(phases):
            label = aqt.qt.QLabel(phase)
            label.setAlignment(aqt.qt.Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet(self._get_phase_label_style(phase, is_current=False))
            label.setMinimumHeight(30)
            self.phase_labels[phase] = label
            phase_layout.addWidget(label)
            
            # Add arrow between phases
            if i < len(phases) - 1:
                arrow = aqt.qt.QLabel("→")
                arrow.setAlignment(aqt.qt.Qt.AlignmentFlag.AlignCenter)
                arrow.setMinimumWidth(20)
                phase_layout.addWidget(arrow)
        
        layout.addLayout(phase_layout)
        
        # Separator
        separator = aqt.qt.QFrame()
        separator.setFrameShape(aqt.qt.QFrame.Shape.HLine)
        separator.setFrameShadow(aqt.qt.QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # Progress bar with percentage
        progress_label_layout = aqt.qt.QHBoxLayout()
        self.progress_label = aqt.qt.QLabel("0%")
        self.progress_label.setAlignment(aqt.qt.Qt.AlignmentFlag.AlignCenter)
        self.progress_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        progress_label_layout.addWidget(self.progress_label)
        layout.addLayout(progress_label_layout)
        
        self.progress_bar = aqt.qt.QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMinimumHeight(25)
        self.progress_bar.setStyleSheet(self._get_progress_bar_style())
        layout.addWidget(self.progress_bar)
        
        # Stats: Time, ETA, Speed
        stats_layout = aqt.qt.QHBoxLayout()
        self.elapsed_label = aqt.qt.QLabel("Elapsed: 0s")
        self.eta_label = aqt.qt.QLabel("ETA: --:--")
        self.speed_label = aqt.qt.QLabel("Speed: -- notes/min")
        
        for label in [self.elapsed_label, self.eta_label, self.speed_label]:
            label.setStyleSheet("font-size: 11px; color: #555;")
        
        stats_layout.addWidget(self.elapsed_label)
        stats_layout.addStretch()
        stats_layout.addWidget(self.eta_label)
        stats_layout.addStretch()
        stats_layout.addWidget(self.speed_label)
        layout.addLayout(stats_layout)
        
        # Current phase label
        self.current_phase_label = aqt.qt.QLabel(self.current_phase)
        self.current_phase_label.setAlignment(aqt.qt.Qt.AlignmentFlag.AlignCenter)
        self.current_phase_label.setStyleSheet("font-style: italic; color: #666; font-size: 12px;")
        layout.addWidget(self.current_phase_label)
        
        # Help text for keyboard shortcuts
        help_text = aqt.qt.QLabel("Press ESC to cancel")
        help_text.setAlignment(aqt.qt.Qt.AlignmentFlag.AlignCenter)
        help_text.setStyleSheet("font-size: 10px; color: #999;")
        layout.addWidget(help_text)
        
        self.setLayout(layout)
    
    def _setup_keyboard_shortcuts(self) -> None:
        """Setup keyboard shortcuts for cancellation and retry."""
        self.esc_shortcut = aqt.qt.QShortcut(aqt.qt.QKeySequence.StandardKey.Cancel, self)
        self.esc_shortcut.activated.connect(self._on_cancel_pressed)
    
    def _on_cancel_pressed(self) -> None:
        """Handle cancel key press (ESC)."""
        if self.cancel_callback:
            self.cancel_callback()
    
    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _get_phase_label_style(self, phase: str, is_current: bool) -> str:
        """Get stylesheet for phase label."""
        if is_current:
            color = "white"
            bg_color = "#3498db"
            weight = "bold"
        else:
            color = "#666"
            bg_color = "#ecf0f1"
            weight = "normal"
        
        return f"""
            background-color: {bg_color};
            color: {color};
            border-radius: 5px;
            border: 2px solid #bdc3c7;
            font-weight: {weight};
            padding: 5px;
        """
    
    def _get_progress_bar_style(self, color: str = "#3498db") -> str:
        """Get stylesheet for progress bar with dynamic color."""
        return f"""
            QProgressBar {{
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: #ecf0f1;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 3px;
            }}
        """
    
    def set_phase(self, phase: str) -> None:
        """
        Set current processing phase.
        
        Args:
            phase: One of BatchProgressPhase constants
        """
        # Update previous phase label to completed style
        if self.current_phase != phase:
            prev_label = self.phase_labels.get(self.current_phase)
            if prev_label and self.current_phase in self.phase_labels:
                prev_label.setStyleSheet(self._get_phase_label_style(self.current_phase, is_current=False))
        
        self.current_phase = phase
        self.phase_start_times[phase] = datetime.now()
        
        # Update current phase label
        current_label = self.phase_labels.get(phase)
        if current_label:
            current_label.setStyleSheet(self._get_phase_label_style(phase, is_current=True))
        
        # Update color based on phase
        color = self.phase_colors.get(phase, "#3498db")
        color_hex = "#{:02x}{:02x}{:02x}".format(*color)
        self.progress_bar.setStyleSheet(self._get_progress_bar_style(color_hex))
        
        # Update label
        self.current_phase_label.setText(f"Phase: {phase}")
    
    def update_progress(self, completed: int, total: int, start_time: datetime) -> None:
        """
        Update progress bar and statistics.
        
        Args:
            completed: Number of completed items
            total: Total number of items
            start_time: When the batch started
        """
        self.completed_count = completed
        self.total_count = total
        self.start_time = start_time
        
        # Update progress bar
        if total > 0:
            percentage = int((completed / total) * 100)
            self.progress_bar.setValue(percentage)
            self.progress_label.setText(f"{percentage}% ({completed}/{total})")
        
        # Update statistics
        if start_time:
            elapsed = datetime.now() - start_time
            self.elapsed_label.setText(self._format_time_delta("Elapsed: ", elapsed))
            
            # Calculate ETA
            if completed > 0 and total > completed:
                time_per_item = elapsed.total_seconds() / completed
                remaining_items = total - completed
                eta_seconds = time_per_item * remaining_items
                eta_time = datetime.now() + timedelta(seconds=eta_seconds)
                self.eta_label.setText(self._format_time_delta("ETA: ", timedelta(seconds=eta_seconds)))
                
                # Calculate speed (items per minute)
                if elapsed.total_seconds() > 0:
                    speed = (completed / elapsed.total_seconds()) * 60
                    self.speed_label.setText(f"Speed: {speed:.1f} notes/min")

    def set_status_text(self, status_text: Optional[str]) -> None:
        """Show a translated status message under the progress stats."""
        self.current_phase_label.setText(status_text or self.current_phase)

    def reset(self) -> None:
        """Reset progress UI to its initial idle state."""
        self.current_phase = BatchProgressPhase.LOADING
        self.start_time = None
        self.completed_count = 0
        self.total_count = 0
        self.phase_start_times.clear()
        for phase, label in self.phase_labels.items():
            label.setStyleSheet(self._get_phase_label_style(phase, is_current=False))
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet(self._get_progress_bar_style())
        self.progress_label.setText("0%")
        self.elapsed_label.setText("Elapsed: 0s")
        self.eta_label.setText("ETA: --:--")
        self.speed_label.setText("Speed: -- notes/min")
        self.current_phase_label.setText(self.current_phase)
    
    def _format_time_delta(self, prefix: str, delta: timedelta) -> str:
        """Format a timedelta as human-readable time."""
        total_seconds = int(delta.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{prefix}{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{prefix}{minutes}m {seconds}s"
        else:
            return f"{prefix}{seconds}s"
    
    def set_completed(self) -> None:
        """Mark processing as completed."""
        self.set_phase(BatchProgressPhase.COMPLETED)
        self.progress_bar.setValue(100)
        self.progress_label.setText("100%")
    
    def set_cancelled(self) -> None:
        """Mark processing as cancelled."""
        self.set_phase(BatchProgressPhase.CANCELLED)
        for label in self.phase_labels.values():
            label.setStyleSheet("background-color: #ecf0f1; color: #666; border: 1px solid #bdc3c7;")
