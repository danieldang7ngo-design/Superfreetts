import sys
import traceback

sys.path.insert(0, r'c:\Users\Administrator\AppData\Roaming\Anki2\addons21\Superfreetts\external')

try:
    print("SUCCESS: edge_tts imported!")
except Exception:
    print("FAILED to import edge_tts")
    traceback.print_exc()
