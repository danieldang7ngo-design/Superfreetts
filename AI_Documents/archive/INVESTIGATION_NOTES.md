# Investigation Notes — Phase 1 (verified against commit ef57c69)

Ngày xác minh: theo phiên làm việc hiện tại. Repo tại commit `ef57c69` ("fix: apply button not lighting up after notes loaded"), working tree clean.

Tất cả 6 phát hiện dưới đây đã được `grep`/`view` lại trực tiếp trên code hiện tại — không có sai lệch số dòng đáng kể so với plan gốc.

| # | File | Vị trí xác nhận | Độ tin cậy |
|---|---|---|---|
| 2.1 | `superfreetts_addon/services/service_edgetts.py` | `def run_async_safe(coro):` — dòng 64 | Đã xác minh |
| 2.2 | `superfreetts_addon/ttsplayer.py` | `class AnkiSuperFreeTTSPlayer` dòng 24, `def _play` dòng 47. Không có tham chiếu `_terminate_flag` trong toàn file (grep rỗng). | Đã xác minh |
| 2.3 | `engine_manager.py`, `mms_engine_manager.py`, `component_kokoro_manager.py` | `python.exe` hardcode ở 15+ vị trí trong 3 file, không có nhánh `platform.system()` nào để chọn executable khác trên macOS/Linux | Đã xác minh |
| 2.4 | `superfreetts_addon/services/service_macos.py` | `get_tts_audio` dòng 527, `subprocess.check_call` dòng 543, `aqt.sound._encode_mp3` dòng 545. Không có semaphore/gate quanh 2 lời gọi này. | Đã xác minh |
| 2.6 | `superfreetts_addon/tts_orchestrator.py` | `build_engine_config` dòng 19, `cpu_default = max(2, system_utils.get_max_workers())` dòng 20, áp dụng cho `PiperTTS`/`KokoroTTS`/`MmsTTS`/`SupertonicTTS` dòng 22-26, `auto_scale_pool` dòng 49 gọi `update_max_processes` cho cả 4 pool (dòng 53/56/59/62) | Đã xác minh |
| system_utils | `superfreetts_addon/system_utils.py` | `get_max_workers()` dòng 25 | Đã xác minh |

Ghi chú thêm phát hiện lúc verify: `mms_engine_manager.py` dòng 25 có 1 dòng comment `# PYTHON_EXE = os.path.join(MMS_ENGINE_DIR, 'python.exe')` — code cũ bị comment out, không ảnh hưởng runtime, nhưng cho thấy đây từng là hardcode trực tiếp ở cấp module trước khi refactor thành factory method `get_python_exe()`. Không đổi kết luận.

Không phát hiện thay đổi nào yêu cầu phải cập nhật lại plan. Tiến hành Phase 2.
