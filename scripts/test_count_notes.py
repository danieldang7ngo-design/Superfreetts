from tools.notes_db import count_notes, apply_index
import sys

if __name__ == '__main__':
    # optional: apply index then print count
    try:
        apply_index()
    except Exception as e:
        print('apply_index failed:', e)
    try:
        print(count_notes())
    except Exception as e:
        print('count_notes failed:', e)
        sys.exit(1)
