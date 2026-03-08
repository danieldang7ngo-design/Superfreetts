#!/usr/bin/env python3
"""
Test script to verify the CPU-aware concurrency worker configuration implementation.
"""

import sys
import os

# Add superfreetss_addon to path
addon_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, addon_path)

def test_cpu_utils():
    """Test CPU detection module - check without importing full addon."""
    print("\n" + "="*60)
    print("TEST 1: CPU Utilities Module")
    print("="*60)
    
    # Read the cpu_utils.py file directly to verify implementation
    cpu_utils_path = os.path.join(addon_path, 'superfreetss_addon', 'cpu_utils.py')
    with open(cpu_utils_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Verify key methods exist
    required_methods = [
        'def get_cpu_info():',
        'def get_max_workers():',
        'def validate_concurrency('
    ]
    
    for method in required_methods:
        if method in content:
            print(f"✓ Method found: {method}")
        else:
            print(f"✗ Method missing: {method}")
            return False
    
    # Check psutil import
    if 'import psutil' in content:
        print("✗ psutil import found (should use multiprocessing)")
        return False
    
    # Check multiprocessing import
    if 'import multiprocessing' in content:
        print("✓ multiprocessing imported for CPU detection")
    else:
        print("✗ multiprocessing import missing")
        return False
    
    # Check that CPUInfo uses multiprocessing.cpu_count()
    if 'multiprocessing.cpu_count()' in content:
        print("✓ Using multiprocessing.cpu_count() (no external dependencies)")
    else:
        print("✗ Not using multiprocessing.cpu_count()")
        return False
    
    print("\n✅ CPU Utils Module: All checks passed!")
    return True

def test_service_configs():
    """Test that services have concurrency_workers in advanced options."""
    print("\n" + "="*60)
    print("TEST 2: Service Configuration Options")
    print("="*60)
    
    services_to_check = [
        ('service_piper.py', 'PiperTTS', 2),
        ('service_kokoro.py', 'KokoroTTS', 1),
        ('service_edgetts.py', 'EdgeTTS', 3),
        ('service_mms.py', 'MMS', 1),
    ]
    
    for service_file, service_name, expected_default in services_to_check:
        path = os.path.join(addon_path, 'superfreetss_addon', 'services', service_file)
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        if 'concurrency_workers' not in content:
            print(f"✗ {service_name}: concurrency_workers NOT found")
            return False
        
        if 'from .. import cpu_utils' not in content:
            print(f"✗ {service_name}: cpu_utils import NOT found")
            return False
        
        if 'cpu_utils.CPUInfo.get_max_workers()' not in content:
            print(f"✗ {service_name}: CPUInfo.get_max_workers() NOT called")
            return False
        
        print(f"✓ {service_name} (default: {expected_default})")
    
    print("\n✅ Service Configs: All checks passed!")
    return True

def test_integrations():
    """Test that cpu_utils is properly integrated."""
    print("\n" + "="*60)
    print("TEST 3: Integration Check")
    print("="*60)
    
    # Check that superfreetss.py imports cpu_utils
    with open(os.path.join(addon_path, 'superfreetss_addon', 'superfreetss.py'), 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        if 'from . import cpu_utils' in content:
            print("✓ cpu_utils imported in superfreetss.py")
        else:
            print("✗ cpu_utils NOT imported in superfreetss.py")
            return False
        
        if 'cpu_utils.CPUInfo.get_max_workers()' in content:
            print("✓ CPUInfo.get_max_workers() used in superfreetss.py")
        else:
            print("✗ CPUInfo.get_max_workers() NOT used in superfreetss.py")
            return False
    
    # Check that preferences no longer has worker spinboxes
    with open(os.path.join(addon_path, 'superfreetss_addon', 'component_preferences.py'), 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        if 'self.piper_workers_spinbox' in content:
            print("✗ piper_workers_spinbox still found in component_preferences.py")
            return False
        if 'self.kokoro_workers_spinbox' in content:
            print("✗ kokoro_workers_spinbox still found in component_preferences.py")
            return False
        print("✓ Worker spinboxes removed from Preferences")
    
    # Check that service files have concurrency_workers in advanced_configuration_options
    services_to_check = [
        ('service_piper.py', 'PiperTTS'),
        ('service_kokoro.py', 'KokoroTTS'),
        ('service_edgetts.py', 'EdgeTTS'),
        ('service_mms.py', 'MMS'),
    ]
    
    for service_file, service_name in services_to_check:
        path = os.path.join(addon_path, 'superfreetss_addon', 'services', service_file)
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if 'concurrency_workers' in content and 'advanced_configuration_options' in content:
                print(f"✓ {service_name} has concurrency_workers in advanced options")
            else:
                print(f"✗ {service_name} missing concurrency_workers in advanced options")
                return False
    
    print("\n✅ Integration: All tests passed!")
    return True

if __name__ == '__main__':
    try:
        all_pass = True
        all_pass = test_cpu_utils() and all_pass
        all_pass = test_service_configs() and all_pass
        all_pass = test_integrations() and all_pass
        
        if all_pass:
            print("\n" + "="*60)
            print("🎉 ALL TESTS PASSED!")
            print("="*60)
            sys.exit(0)
        else:
            print("\n" + "="*60)
            print("❌ SOME TESTS FAILED")
            print("="*60)
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
