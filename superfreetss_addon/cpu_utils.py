"""
CPU utilities for detecting available cores and validating concurrency settings.
Uses multiprocessing.cpu_count() which is built-in and doesn't require external dependencies.
"""

import multiprocessing
import logging

logger = logging.getLogger(__name__)


class CPUInfo:
    """Helper class to get CPU information and validate concurrency settings."""
    
    @staticmethod
    def get_cpu_info():
        """
        Get CPU information for the system.
        Uses multiprocessing.cpu_count() to get available CPU cores.
        
        Returns:
            dict: Contains 'physical_cores' and 'logical_cores'
        """
        try:
            # multiprocessing.cpu_count() returns logical cores (all available CPUs)
            # This is safe and works on all platforms without external dependencies
            cpu_count = multiprocessing.cpu_count() or 1
            
            return {
                'physical_cores': cpu_count,  # Use logical count as practical limit
                'logical_cores': cpu_count,
            }
        except Exception as e:
            logger.warning(f"[CPU] Failed to detect CPU cores: {e}, defaulting to 1 core")
            return {
                'physical_cores': 1,
                'logical_cores': 1,
            }
    
    @staticmethod
    def get_max_workers():
        """
        Get maximum recommended workers based on available CPU cores.
        Uses the total CPU count (logical cores) to prevent over-subscription.
        
        Returns:
            int: Number of available CPU cores (1 minimum)
        """
        cpu_info = CPUInfo.get_cpu_info()
        return max(1, cpu_info['physical_cores'])
    
    @staticmethod
    def validate_concurrency(requested_workers):
        """
        Validate if requested concurrency level is acceptable.
        
        Args:
            requested_workers (int): Requested number of concurrent workers
            
        Returns:
            dict: {
                'valid': bool,
                'max_allowed': int,
                'warning': str or None
            }
        """
        if requested_workers < 1:
            return {
                'valid': False,
                'max_allowed': 1,
                'warning': "Minimum 1 worker required"
            }
        
        max_allowed = CPUInfo.get_max_workers()
        
        if requested_workers > max_allowed:
            return {
                'valid': False,
                'max_allowed': max_allowed,
                'warning': f"Max {max_allowed} workers (available CPU cores)"
            }
        
        return {
            'valid': True,
            'max_allowed': requested_workers,
            'warning': None
        }


if __name__ == '__main__':
    # Test
    info = CPUInfo.get_cpu_info()
    print(f"CPU Info: {info}")
    print(f"Max Workers: {CPUInfo.get_max_workers()}")
    
    # Test validation
    for test_val in [1, 4, 16, 32]:
        result = CPUInfo.validate_concurrency(test_val)
        print(f"Validate {test_val}: {result}")
