import os
import sqlite3
from typing import List, Any

ROOT = os.path.dirname(os.path.dirname(__file__))
DEFAULT_DB = os.path.join(ROOT, 'notes.db')
DEFAULT_USER_FILES_DIR = os.path.join(ROOT, 'user_files')


def _expand_path(path: str) -> str:
    if not path:
        return path
    return os.path.expandvars(os.path.expanduser(path))


def get_collection_path() -> str:
    env_path = os.environ.get('NOTES_DB_PATH')
    if env_path:
        return _expand_path(env_path)

    try:
        from aqt import mw
        if getattr(getattr(mw, 'col', None), 'path', None):
            return _expand_path(mw.col.path)
    except Exception:
        pass

    return _expand_path(DEFAULT_DB)


def get_addon_user_files_dir() -> str:
    user_files_dir = _expand_path(DEFAULT_USER_FILES_DIR)
    os.makedirs(user_files_dir, exist_ok=True)
    return user_files_dir


def _get_conn():
    return sqlite3.connect(get_collection_path())

def apply_index():
    sql = 'CREATE INDEX IF NOT EXISTS idx_notes_lookup ON notes(deck_id, mod);'
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
    finally:
        conn.close()

def fetch_notes(limit: int = 100, offset: int = 0) -> List[Any]:
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute('SELECT * FROM notes LIMIT ? OFFSET ?', (limit, offset))
        rows = cur.fetchall()
        return rows
    finally:
        conn.close()

def count_notes() -> int:
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM notes')
        row = cur.fetchone()
        return int(row[0]) if row else 0
    finally:
        conn.close()

if __name__ == '__main__':
    # quick test CLI
    print(count_notes())
