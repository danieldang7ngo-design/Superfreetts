# Remaining Fix Plan — Low-capability AI agent friendly

## Instructions

Each fix is independent. Process top to bottom. Each entry specifies: file, exact line(s), old code, new code, and verification step.

---

## P0 — Bare `except:` catches KeyboardInterrupt

### Fix 1: `services/service_macos.py:551`

**Old:**
```python
        except:
            pass
```

**New:**
```python
        except Exception:
            pass
```

**Verify:** Search for `except:` (bare) in file. Should be 0 matches.

---

### Fix 2: `system_utils.py:22,39`

**Locations:** `get_cpu_threads()` (line 22) and `get_total_cpu_count()` (line 39)

**Old (both lines):**
```python
    except:
        return 1
```

**New (both lines):**
```python
    except Exception:
        return 1
```

**Verify:** Search for `except:` (bare) in file. Should be 0 matches.

---

## P1 — Resource leaks (file handles not in context manager)

### Fix 3: `downloader.py:64-98` — File handle leak on PermissionError retry path

**Background:** The `_download_chunk` method has a retry loop for PermissionError (file lock). The file handle `f` is opened with `f = open(part_file, 'wb')` and closed in a `finally` block. If PermissionError strikes after the file is opened but before the read loop starts, the handle is not cleaned up by the retry loop wrapper.

**Strategy:** Keep the retry loop structure for PermissionError, but once a handle is successfully obtained, wrap the read loop in a `with f:` context manager.

**Old (lines 64-98):**
```python
                    # Handle WinError 32: Process cannot access file
                    f = None
                    file_retries = 5
                    while file_retries > 0:
                        try:
                            f = open(part_file, 'wb')
                            break
                        except PermissionError as e: # Catch WinError 32
                            if e.errno == 13 or (hasattr(e, 'winerror') and e.winerror == 32):
                                self.log_debug(f"File lock detected on {part_file}, retrying in 1s...")
                                time.sleep(1)
                                file_retries -= 1
                            else:
                                raise

                    if not f:
                        raise Exception(f"Could not open part file {part_file} after retries")

                    try:
                        while not self._stop_event.is_set():
                            chunk = resp.read(1024 * 64) # Balanced buffer
                            if not chunk:
                                break
                            f.write(chunk)
                            with self.lock:
                                self.downloaded_bytes += len(chunk)
                                self.last_bytes.append((time.time(), len(chunk)))
                                now = time.time()
                                while self.last_bytes and now - self.last_bytes[0][0] > 2.0:
                                    self.last_bytes.pop(0)

                        if not self._stop_event.is_set():
                            self._report_progress()
                            return # Success
                    finally:
                        f.close()
```

**New:**
```python
                    # Handle WinError 32: Process cannot access file
                    f = None
                    file_retries = 5
                    while file_retries > 0:
                        try:
                            f = open(part_file, 'wb')
                            break
                        except PermissionError as e:
                            if e.errno == 13 or (hasattr(e, 'winerror') and e.winerror == 32):
                                self.log_debug(f"File lock detected on {part_file}, retrying in 1s...")
                                time.sleep(1)
                                file_retries -= 1
                            else:
                                raise

                    if not f:
                        raise Exception(f"Could not open part file {part_file} after retries")

                    try:
                        while not self._stop_event.is_set():
                            chunk = resp.read(1024 * 64)
                            if not chunk:
                                break
                            f.write(chunk)
                            with self.lock:
                                self.downloaded_bytes += len(chunk)
                                self.last_bytes.append((time.time(), len(chunk)))
                                now = time.time()
                                while self.last_bytes and now - self.last_bytes[0][0] > 2.0:
                                    self.last_bytes.pop(0)

                        if not self._stop_event.is_set():
                            self._report_progress()
                            return
                    finally:
                        f.close()
```

**Verify:** Check that indentation is consistent. Lines 66-97 should maintain original indentation level.

---

### Fix 4: `services/service_windows.py:350-352`

**Old:**
```python
        f = open(full_path_mp3, 'rb')
        content = f.read()
        f.close()
```

**New:**
```python
        with open(full_path_mp3, 'rb') as f:
            content = f.read()
```

**Verify:** Search for `f = open(` in file. Should be 0 matches.

---

### Fix 5: `services/service_espeakng.py:160` (approx)

**Old (find `f = open(mp3_temp_file_name, 'rb')`):**
```python
        f = open(mp3_temp_file_name, 'rb')
        audio_data = f.read()
        f.close()
```

**New:**
```python
        with open(mp3_temp_file_name, 'rb') as f:
            audio_data = f.read()
```

**Verify:** Search for `f = open(` in file. Should be 0 matches.

---

## P1 — Corrupt JSON written to Anki config

### Fix 6: `config_store.py:72-74`

**Old:**
```python
        try:
            safe_config = _sanitize_for_json(self.config)
            self.anki_utils.write_config(safe_config)
        except Exception:
            # Fallback: attempt to write raw config (will raise in upper layer)
            self.anki_utils.write_config(self.config)
```

**New:**
```python
        safe_config = _sanitize_for_json(self.config)
        self.anki_utils.write_config(safe_config)
```

**Verify:** Only 1 call to `write_config` in `_write()` method.

---

## P1 — Orphaned futures on stall cancel

### Fix 7: `batch_orchestrator.py:706`

**Old:**
```python
                    try:
                        pending_future.cancel()
                    except Exception:
                        pass
```

**New:**
```python
                    try:
                        pending_future.cancel()
                    except Exception as e:
                        logger.error(f"Failed to cancel pending future during stall: {e}")
```

**Verify:** `pass` should not appear at same indentation after `except Exception`.

---

## P1 — Module-level bare except hides import errors

### Fix 8: `batch_constants.py:8`

**Read the file first to find exact context. Add logging:**

**Old:**
```python
except Exception:
    pass
```

**New:**
```python
except Exception as e:
    logger.debug(f"No _local_override or failed to load: {e}")
```

Note: You may need to add `import logging` and `logger = logging.getLogger(__name__)` at the top of the file if they don't exist. Check first.

---

## P2 — Duplicate dict key (harmless)

### Fix 9: `services/service_espeakng.py:28`

**Old (two identical lines 27-28):**
```python
    'en-029': languages.AudioLanguage.en_CB,
    'en-029': languages.AudioLanguage.en_CB,
```

**New:**
```python
    'en-029': languages.AudioLanguage.en_CB,
```

**Verify:** Search for `en-029` in file. Should be 1 match.

---

## P2 — `except Exception: pass` in deserialization shim

### Fix 10: `voice.py:6,17,26,205`

**Step 1:** Add logger at top of file (after existing imports, before `try`):
```python
import logging
logger = logging.getLogger(__name__)
```

**Step 2:** Change each `except Exception: pass` to log at debug level.

**Line 6** — initial import fallback:
```python
except Exception:
    logger.debug("databind not available, using fallback shim")
```

**Line 17** — json dump fallback:
```python
                except Exception:
                    pass
```
→ Keep pass, log is not useful here for JSON serialization of fallback.

Actually for line 17: this is inside a dataclass detection — low value to log. Skip.

**Line 26** — json load fallback:
```python
                except Exception:
                    pass
```
→ Keep pass. Low value.

**Line 205** — voice_id parsing:
```python
        except Exception:
            pass
```
→ Add logging: `logger.debug(f"Failed to parse voice_id: {voice_id}")`

---

## P2 — Silent error hiding in service_kokoro.py and service_piper.py

### Fix 11: `services/service_kokoro.py`

Search for all `except: pass` or `except Exception: pass` in the file.
Change each to `except Exception: logger.warning(f"...: {e}")`.

Specific locations to check: around lines 129, 223, 255, 327.

Read the file and add descriptive messages like:
- `logger.warning(f"Kokoro warmup failed: {e}")`
- `logger.warning(f"Debug logging setup failed: {e}")`

---

### Fix 12: `services/service_piper.py`

Search for all `except Exception: pass` in the file.
Change each to `except Exception: logger.warning(f"...: {e}")`.

Specific locations to check: around lines 294, 354, 482.

Read the file and add descriptive messages.

---

## Summary

| # | File | Change type | Effort |
|---|------|-------------|--------|
| 1 | `service_macos.py` | `except:` → `except Exception:` | 30s |
| 2 | `system_utils.py` | `except:` → `except Exception:` (2x) | 30s |
| 3 | `downloader.py` | restructure retry loop | 3min |
| 4 | `service_windows.py` | `with` context manager | 1min |
| 5 | `service_espeakng.py` | `with` context manager | 1min |
| 6 | `config_store.py` | remove fallback branch | 1min |
| 7 | `batch_orchestrator.py` | add logging | 30s |
| 8 | `batch_constants.py` | add logging | 1min |
| 9 | `service_espeakng.py` | delete duplicate line | 10s |
| 10 | `voice.py` | add logger + debug logging | 2min |
| 11 | `service_kokoro.py` | add logging (4 sites) | 3min |
| 12 | `service_piper.py` | add logging (3 sites) | 2min |

**Total estimated time: 15 minutes.**
