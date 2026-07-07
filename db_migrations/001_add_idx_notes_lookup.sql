-- Migration: add index for faster lookup by deck_id and mod
CREATE INDEX IF NOT EXISTS idx_notes_lookup ON notes(deck_id, mod);
