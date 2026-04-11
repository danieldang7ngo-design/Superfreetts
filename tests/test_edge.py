import sys
import traceback

sys.path.insert(0, r'c:\Users\Administrator\AppData\Roaming\Anki2\addons21\Superfreetts\external')

try:
    import edge_tts
    print("SUCCESS: edge_tts imported!")
except Exception as e:
    print("FAILED to import edge_tts")
    traceback.print_exc()
