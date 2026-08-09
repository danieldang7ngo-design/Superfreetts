import sys
import os

# add external modules to sys.path, for 3rd party modules
addon_dir = os.path.dirname(os.path.realpath(__file__))
external_dir = os.path.join(addon_dir, 'external')
sys.path.insert(0, external_dir)

# Add the current directory to sys.path
sys.path.insert(0, addon_dir)

# Set _pytest_mode if running under pytest
if 'pytest' in sys.modules or (len(sys.argv) > 0 and 'pytest' in sys.argv[0]):
    sys._pytest_mode = True

# Chỉ import package con; mọi gui_hooks (vd. profile_did_open cho welcome) phải đăng ký
# trong superfreetts_addon/__init__.py — không thêm append ở đây để tránh đăng ký hook hai lần.
if not hasattr(sys, '_pytest_mode'):
    from . import superfreetts_addon
