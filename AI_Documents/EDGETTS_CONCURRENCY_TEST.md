# EdgeTTS Concurrency — Test thực tế & Khuyến nghị

> Ngày test: 2026-08-09. Môi trường: Windows, Python 3.12.10, `edge_tts 7.2.7` (bundled trong `external/`).
> Mục đích: tìm mức concurrency tối ưu cho máy dev (dev dùng full speed; users vẫn nhận mặc định an toàn = 3).

---

## 1. Kiến trúc giới hạn EdgeTTS (3 lớp chồng lên nhau)

| Lớp | Vị trí | Giới hạn |
|---|---|---|
| Thread pool | `tts_orchestrator.py:78` (`max_cap = EDGETTS_MAX_WORKERS`) | pool = min(concurrency_workers, EDGETTS_MAX_WORKERS) |
| Gate HTTP toàn cục | `service_edgetts.py:89-96, 313` | tổng request đồng thời ≤ concurrency_workers (BoundedSemaphore) |
| Clamp cứng | `batch_constants.py:44` (`EDGETTS_MAX_WORKERS`) + `service_edgetts.py:164` (UI max) | không bao giờ vượt EDGETTS_MAX_WORKERS |

- **Không có phép nhân** (vd "20 thread × 10 request = 200"): semaphore toàn cục chặn — tổng request EdgeTTS đồng thời luôn ≤ `concurrency_workers`, không phụ thuộc pool size.
- **Lưu ý:** committed source có `EDGETTS_MAX_WORKERS = 3`. Dù `config.json` để `concurrency_workers: 20`, runtime vẫn clamp về **3** trừ khi nâng `EDGETTS_MAX_WORKERS` qua `_local_override.py`.

## 2. Phương pháp test

- Gửi `N` request song song bằng `asyncio.gather(N)`, mỗi request = 1 luồng WebSocket tới Microsoft Edge TTS (đúng code path của `service_edgetts.get_tts_audio_batch`).
- Tăng N dần trong **1 process duy nhất** (không chạy nhiều subagent song song — cùng 1 IP nên load cộng dồn, không gán được lỗi cho mức nào).
- Phân loại lỗi: 429/403 (rate-limit), 503, timeout, no-audio.

## 3. Kết quả test

### 3.1 Text ngắn (~40 ký tự, voice `vi-VN-HoaiMyNeural`)

| Mức | Wall time | Tỉ lệ thành công | Throughput | avg / p90 / p99 latency |
|---|---|---|---|---|
| 1 | 1.33s | 100% | 0.75 req/s | 1.3 / 1.3 / 1.3s |
| 3 | 2.67s | 100% | 1.12 req/s | 2.0 / 2.6 / 2.6s |
| 5 | 4.07s | 100% | 1.23 req/s | 2.8 / 4.0 / 4.0s |
| 10 | 6.51s | 100% | 1.54 req/s | 3.9 / 6.4 / 6.4s |
| 15 | 9.60s | 100% | 1.56 req/s | 5.8 / 9.0 / 9.0s |
| 20 | 13.64s | 100% | 1.47 req/s | 7.8 / 13.1 / 13.1s |
| 30 | 33.19s | 100% | 0.90 req/s | 12.0 / 21.0 / 21.0s |
| 50 | 30.57s | 100% | 1.64 req/s | 16.4 / 26.7 / 26.7s |
| 60 | 33.9s | 100% | 1.77 req/s | 18.0 / 30.5 / 33.2s |
| 80 | 43.3s | 100% | 1.85 req/s | 23.2 / 39.0 / 42.8s |
| **100** | **53.5s** | **100%** | **1.87 req/s** | **29.0 / 48.5 / 53.1s** |
| 150 | 81.3s | 100% | 1.84 req/s | 41.6 / 69.4 / 78.6s |
| 200 | 109.1s | 100% | 1.83 req/s | 57.2 / 98.1 / 107.1s |
| 300 | 188.6s | **89%** (268/300, 32 timeout) | 1.42 req/s | 113.2 / 161.2 / 173.1s |

### 3.2 Text dài (~200 ký tự, tiếng Việt có dấu)

| Mức | Wall time | Tỉ lệ thành công | Throughput | avg / p90 / p99 latency |
|---|---|---|---|---|
| 20 | 65.1s | 100% | 0.31 req/s | 45.5 / 58.7 / 60.3s |
| 50 | 103.3s | 100% | 0.48 req/s | 42.7 / 77.8 / 92.1s |
| **100** | **141.7s** | **100%** | **0.71 req/s** | **70.4 / 106.7 / 126.5s** |

## 4. Phân tích

1. **Microsoft không rate-limit (không 429/403)** kể cả ở 300 concurrent — nhưng **serialize theo IP**: càng nhiều request song song, mỗi request chờ càng lâu; throughput bão hòa ~1.8 req/s (text ngắn).
2. **Điểm vỡ là timeout 180s** (`EDGETTS_TASK_TIMEOUT_SECONDS` trong addon), không phải rate-limit. Ở 300: p99 = 173s chạm trần → 32/300 fail. Ở 200: p99 = 107s → an toàn.
3. **Đỉnh hiệu quả = 100 concurrent**:
   - Text ngắn: throughput cao nhất 1.87 req/s.
   - Text dài: vẫn đang tăng (0.71 req/s) nhưng p99 = 126.5s — dưới 180s, còn dư địa.
   - Từ 100 → 200: throughput KHÔNG tăng (bão hòa), chỉ latency tệ hơn.

## 5. Cấu hình đã áp dụng (dev machine)

- `superfreetts_addon/_local_override.py` (mới, **gitignored** — không ship trong `.ankiaddon`):
  ```python
  EDGETTS_MAX_WORKERS = 100
  ```
- `config.json`: `configuration.service_config.EdgeTTS.concurrency_workers = 100` (trước là 20).
- **Verify:** cả 3 lớp clamp đều ra 100 (pool `engine_config['EdgeTTS']` = 100, service gate = 100).

### Cách đổi mức
- Muốn an toàn hơn: sửa `_local_override.py` → `EDGETTS_MAX_WORKERS = 50` (+ set `config.json` = 50).
- Muốn về mặc định: xóa `_local_override.py`, set `config.json` = 3.
- **KHÔNG dùng 2 script `set_edge_workers_20.py` / `set_edge_workers_3.py`** — chúng sửa trực tiếp `batch_constants.py` (làm dirty source). `_local_override.py` là cơ chế chuẩn (đã có sẵn trong `batch_constants.py:45-46`).

## 6. Khuyến nghị cho batch 2800 items

- **Chọn mức 100** (đang cấu hình): throughput đỉnh, 100% thành công, p99 vẫn dưới timeout 180s.
- Ước tính thời gian:
  - Toàn bộ text ngắn (~40 ký tự): 2800 ÷ 1.87 ≈ **25 phút**.
  - Toàn bộ text dài (~200 ký tự): 2800 ÷ 0.71 ≈ **66 phút**.
  - Hỗn hợp thực tế (flashcard): **~30-45 phút**.
- Tăng lên 200 KHÔNG nhanh hơn (bão hòa), chỉ tăng rủi ro latency. 300 là không nên (timeout).
- Nếu text chủ yếu dài >150 ký tự, có thể cân nhắc 60-80 để giữ p99 an toàn hơn; nhưng 100 vẫn hợp lệ vì đã có retry (mặc định 3 lần, backoff 5s).

## 7. Rủi ro

- Chạy 100+ concurrent đồng nghĩa chấp nhận rủi ro bị Microsoft giới hạn/ban IP nếu burst kéo dài — đây là lý do committed source giữ mặc định 3 cho users.
- `build_share.py` khi build `.ankiaddon` sẽ tự reset `config.json` về defaults và không đóng gói `_local_override.py` (gitignored) → users luôn nhận mức an toàn.
