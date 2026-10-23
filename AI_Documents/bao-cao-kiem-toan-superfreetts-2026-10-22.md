# Báo cáo kiểm toán quản lý tài nguyên và hiệu năng TTS — Super Free TTS

- **Ngày:** 2026-10-22
- **Mã nguồn:** `ee2c2f5d356abc3063f1f7161e38a13cd470da1f` (`ee2c2f5`), nhánh `fix/resource-management`
- **Phiên bản:** `26.10.2`
- **Phạm vi:** quản lý vòng đời process, RAM/concurrency, batch, realtime, cache/file âm thanh, checkpoint và các đường dự phòng
- **Cách làm:** chỉ đọc mã nguồn + kiểm chứng benchmark thật; **không sửa mã sản phẩm**, không đổi default
- **Môi trường đo:** Linux 7.2.9 (CachyOS), 16 logical CPU, 15.358 MB RAM, Python 3.14.8

> Báo cáo này thay thế bản nháp trong hội thoại. Các số liệu benchmark đã được đối chiếu lại với JSON/CSV gốc; các kết luận suy ra từ mã nguồn được ghi rõ là **rủi ro**, không gộp với số đo thực nghiệm.

---

## 1. Tóm tắt điều hành

### 1.1. Kết luận chính

1. **Vòng đời process đã được cải thiện và kiểm chứng tốt.** Idle cleanup, `stop_all()`, mở lại profile và chạy tiếp 5 request đều đạt cho cả bốn engine; không còn process mồ côi sau benchmark. Đây là điểm mạnh thực sự, không phải suy đoán.
2. **Benchmark 4 engine đạt chất lượng dữ liệu tốt:** 500/500 item mỗi engine và mỗi mode, 4.000 file WAV, 0 lỗi, mỗi engine/mode có 500/500 hash âm thanh khác nhau, tổng khoảng 2,1 GB.
3. **Không thể coi cấu hình mặc định là an toàn.** Cùng một host, bộ cấp phát hiện tại có thể cấp **6 worker Kokoro** khi chỉ bật Kokoro; thực đo Kokoro ngốn **3.933 MB cho 1 runner** và **4.662 MB cho 2 runner**. Nếu lấy peak 1 runner làm worst-case, 6 worker có thể lên tới ~23 GB; nếu lấy mức trung bình của batch 2 runner, 6 worker ~14 GB. Cả hai đều cao hơn nhiều so với 3 GB ước tính, và worst-case vượt 15,4 GB RAM của máy. Đây là **P0**.
4. **Hợp đồng định dạng âm thanh đang bị vi phạm ở cả bốn engine local, cộng thêm EdgeTTS ở chiều ngược lại.** `AudioFileStore` đặt tên file theo preference (`mp3`/`wav`/`ogg`) nhưng không bảo đảm byte bên trong đúng định dạng. Mặc định `mp3` + MMS/Kokoro/Supertonic tạo ra **WAV nằm trong file `.mp3`**; Piper batch cũng vậy. OGG chưa từng được encode nhưng vẫn có trong UI. Đây là **P1** về tính đúng đắn.
5. **Các rủi ro treo/khó phục hồi còn nguyên:** IPC `stdout.readline()` của MMS/Kokoro/Supertonic không có timeout; semaphore cấp process cũng chờ vô hạn. Một runner bị treo có thể giữ worker và làm cạn pool. Batch chỉ có stall detector toàn cục 180 giây, không xử lý được một worker đơn lẻ bị treo. Đây là **P1**.
6. **Checkpoint hiện tại gần như không dùng được để phục hồi:** đường batch đang chạy chỉ lưu checkpoint **sau khi đã cập nhật xong toàn bộ note**, không lưu khi hủy/lỗi. Đoạn `O(n²)` nằm trong các hàm `execute()` không được gọi, không phải đường đang chạy. Đây là điểm cần đính chính so với bản nháp trước.
7. **Batch chỉ tăng tốc 10,7–18,4% ở cấu hình 2 worker**, đổi lại RAM tăng đáng kể. Vì vậy không nên tăng worker mặc định chỉ dựa vào benchmark này; cần đo ma trận worker × thread trước.

### 1.2. Bảng ưu tiên

| Mức | Vấn đề | Tác động | Trạng thái bằng chứng |
|---|---|---|---|
| **P0** | Kokoro ước tính 500 MB/worker nhưng thực đo 3,9–4,7 GB cho 1–2 runner; auto có thể cấp 6–8 worker | OOM/swap, treo hoặc crash Anki trên máy 16 GB | Đã tái lập phân bổ; đã đo RAM; **chưa cố tình chạy 6 worker để gây OOM** |
| **P1** | Định dạng file không khớp phần mở rộng; OGG không được encode | File `.mp3` chứa WAV, file `.ogg` không hợp lệ; playback/media lỗi | Đã kiểm tra code tất cả service; chưa chạy Anki end-to-end |
| **P1** | IPC local engine không có timeout; semaphore chờ vô hạn | Một runner treo giữ worker/pool; batch hoặc realtime đứng | Đã kiểm tra code; chưa tạo sự cố treo trong benchmark |
| **P1** | Checkpoint chỉ lưu cuối batch; resume trộn index gốc/đã lọc | Mất toàn bộ tiến độ khi crash/hủy; resume có thể sai note | Đã kiểm tra luồng active và code executor |
| **P1** | Cleanup xóa **mọi file cấp 1** trong `user_files` cũ hơn retention, gồm log/usage | Mất `usage_log.json`, log; chạy đồng bộ lúc khởi động | Đã kiểm tra code; chưa đo thời gian khởi động |
| **P2** | Piper spawn binary mỗi request, nạp lại model 63 MB | Tăng latency/CPU; tiềm năng tối ưu nhưng chưa đo mức trần | Đã kiểm tra code; chưa đo persistent mode |
| **P2** | MMS batch rò temp WAV khi lỗi/retry | Tích tụ file rác trong `/tmp` | Đã kiểm tra code; benchmark 0 lỗi nên chưa quan sát |
| **P2** | EdgeTTS cộng bytes bằng `data += chunk` | Có thể O(n²) với text dài, thường nhỏ | Đã kiểm tra code; chưa đo |
| **P2** | `fsync` từng file cache; benchmark không tính | Batch 500 file có thêm chi phí I/O | Đã kiểm tra code; chưa đo |
| **P2** | Code executor/resource cũ không dùng, dễ gây hiểu nhầm | Bảo trì, test sai đường | Đã kiểm tra bằng tìm kiếm tham chiếu |

---

## 2. Phạm vi, kiến trúc và cách đo

### 2.1. Luồng chính

```
UI / batch dialog / realtime tag
        │
        ▼
SuperFreeTTS (facade, vòng đời add-on)
        ├── BatchOrchestrator ──► MultiEngineExecutor (thread pool theo engine)
        ├── AudioGenerator ────► AudioFileStore (cache, tên file, ghi atomic)
        └── TTSPlayer / realtime
                    │
                    ▼
             ServiceManager
                    │
      ┌─────────────┼──────────────┬──────────────┐
      ▼             ▼              ▼              ▼
   Piper          MMS           Kokoro        Supertonic / EdgeTTS
   pool           pool           pool             pool / async
      │             │              │              │
      ▼             ▼              ▼              ▼
  runner        runner         runner          runner
  (spawn         (persistent)   (persistent)    (persistent)
   piper
   mỗi request)
```

- Process pool dùng chung lớp `SherpaProcessPool`; idle timeout **180 giây**, timer dọn dẹp **15 giây** (`superfreetts_addon/services/service_mms.py:40-60`).
- Pool được auto-scale theo `engine_config`; `build_engine_config()` lấy số worker từ bộ cấp phát RAM dùng chung (`tts_orchestrator.py:148-154`, `:225-250`).
- Batch chia chunk mặc định 5 item (EdgeTTS 3), gửi lên thread pool riêng của từng engine (`batch_orchestrator.py:616-627`), không chạy tuần tự toàn bộ.
- Cache key gồm processed text, voice, voice options và **định dạng được yêu cầu**; file được ghi qua temp + `fsync` + `os.replace()` (`audio_file_store.py:75-129`).
- Khi đóng profile: executor shutdown, bốn pool `stop_all()`, realtime player shutdown (`superfreetts.py:578-620`, `gui.py:406-416`). Khi mở lại: tạo lại executor và restart player (`gui.py:418-431`, `superfreetts.py:622-638`).

### 2.2. Những điểm đã được kiểm chứng là tốt

- **Idle cleanup thực tế:** tree RSS giảm từ 65,32 → 46,02 MB (Piper), 448,75 → 42,09 MB (MMS), 3.933,39 → 47,53 MB (Kokoro), 687,14 → 54,35 MB (Supertonic); số runner về 0.
- **`stop_all()`:** cả bốn engine không còn child process; mở lại và chạy 5 request đều 5/5 thành công; cleanup timer sống lại sau `stop_all()` (`service_mms.py:62-70`).
- **Không rò process sau benchmark:** trạng thái cuối 0 runner, 0 engine child, tree RSS 47–58 MB.
- **Tính toàn vẹn dữ liệu benchmark:** 4.000 WAV, 0 WAV lỗi; 500/500 hash khác nhau ở từng engine/mode.
- **Realtime có giới hạn:** timeout 20 giây và tối đa 4 generation đang bay (`ttsplayer.py:49`, `:56`, `:190-208`). Đây là giới hạn tài nguyên, không phải hủy process đang chạy.

---

## 3. Kết quả benchmark và kiểm chứng lại số liệu

### 3.1. Bảng kết quả

Nguồn: `superfreetts_data/benchmark/BENCHMARK_SUMMARY.md`, đối chiếu `*_results.json`, `*_items.csv`, `*_chunks.csv`.

| Engine | Mode | Wall | Items/s | Mean/item | P95 | RTF | Peak tree RSS |
|---|---|---:|---:|---:|---:|---:|---:|
| Piper | single | 519,9 s | 0,962 | 1,039 s | 1,358 s | 0,112 | 327 MB |
| Piper | batch 2 worker | 424,2 s | 1,179 | 0,849 s | 10,526 s/chunk | 0,091 | 384 MB (probe) |
| MMS | single | 612,8 s | 0,816 | 1,225 s | 1,614 s | 0,127 | 450 MB |
| MMS | batch 2 worker | 543,0 s | 0,921 | 1,086 s | 12,339 s/chunk | 0,113 | ~827 MB (ước tính) |
| Kokoro | single | **1.242,1 s** | 0,403 | **2,484 s** | 3,566 s | 0,265 | **3.933 MB** |
| Kokoro | batch 2 worker | **1.109,2 s** | 0,451 | **2,218 s** | 26,188 s/chunk | 0,237 | **4.662 MB** |
| Supertonic | single | 1.398,6 s | 0,358 | **2,796 s** | 3,757 s | 0,249 | 687 MB |
| Supertonic | batch 2 worker | 1.144,7 s | 0,437 | **2,289 s** | 29,869 s/chunk | 0,204 | 1.376 MB |

**Mức giảm thời gian/item khi batch 2 worker:**

- Piper: **18,4%**
- MMS: **11,4%**
- Kokoro: **10,7%**
- Supertonic: **18,1%**

Đây là tăng thông lượng, **không phải giảm latency từng chunk**. P95 mỗi chunk batch là 10,5–29,9 giây; giao diện batch phải chờ cả chunk. Không dùng bảng này để hứa “batch nhanh hơn 18%” cho mọi cấu hình.

### 3.2. Kiểm chứng số liệu và các đính chính

Đã đối chiếu lại với raw JSON/CSV; các điểm sau phải được ghi đúng:

1. **Kokoro single 1.242,1 giây là thời gian đã trừ suspend.** Bản raw ban đầu cộng 5.016 giây system suspend (19:05:23–20:28:59). Không dùng wall time thô để tính throughput.
2. **Piper batch 298 MB là số đo sai do sampler cũ.** Sampler chỉ đọc children của leader thread, bỏ sót runner/Piper do `ThreadPoolExecutor` tạo. Probe 20 item sửa đúng cho **384,39 MB**, 2 runner + 2 Piper child + 5 process. Không dùng 298 MB làm peak batch.
3. **MMS ~827 MB là ước tính từ tổng RSS runner + parent**, không phải một mẫu peak duy nhất của cả cây. Probe 20 item đo trực tiếp **645,63 MB**; runner tăng thêm khi chạy đủ 500 item. Ghi rõ đây là ước tính.
4. **Kokoro 4.662 MB là peak của 2 runner**, không phải “RAM mỗi process”. Một runner đơn đã đạt 3.933 MB; marginal khi thêm runner thứ hai thấp hơn do chia tải và đo tree RSS. Khi lập ngân sách phải dùng **peak 1 runner** làm worst-case, không chia đôi 4.662 MB.
5. **Benchmark dùng 2 worker, không phải default của add-on.** Piper/MMS/Kokoro/Supertonic được đo với `2` worker; MMS/Kokoro/Supertonic dùng **8 thread**, Piper 1 thread. Default của service là `num_threads=1` (`service_kokoro.py:197-198`, `service_mms.py:387-388`, `service_piper.py:107-108`), còn số worker do bộ cấp phát RAM quyết định. Vì vậy mean 1,039–2,796 giây **không phải latency mặc định** của người dùng.
6. **Benchmark dùng WAV và gọi service trực tiếp.** Không đi qua `AudioFileStore`, không `fsync`, không chuyển MP3/OGG, không import media vào Anki, không `update_notes`, không thử lỗi/timeout. Đây là benchmark **generation**, không phải benchmark end-to-end.
7. **Checkpoint `O(n²)` chỉ nằm trong đường không dùng.** Đường active `process_batch_audio()` gọi `_execute_unique_tasks_unified()` (`batch_orchestrator.py:472`), không gọi `UnifiedBatchExecutor.execute()`/`MultiEngineExecutor.execute()`. Hai hàm `execute()` có lưu checkpoint sau từng item và tạo list `note_id` trong mỗi vòng lặp (`batch_executor.py:386-401`), nhưng không được gọi. Đường active chỉ lưu **một lần sau khi apply xong** (`batch_orchestrator.py:544-550`).
8. **Tuyên bố “2 worker khớp cấu hình Piper shipped” trong docstring benchmark không đúng như một bảo đảm.** `bench_piper.py` chọn 2 worker cố định; add-on có thể cấp tới 8 worker Piper khi chỉ bật Piper và đủ RAM. Docstring chỉ đúng cho kịch bản benchmark, không đúng cho mọi default.

---

## 4. Phát hiện chi tiết

### P0-1 — Ngân sách RAM Kokoro không phản ánh thực tế, có thể cấp 6–8 worker

**Bằng chứng**

- Bảng ước tính đặt Kokoro = **500 MB/worker** (`superfreetts_addon/tts_orchestrator.py:26-31`). Comment ngay trên bảng tự ghi đây là số do người dùng báo cáo, **chưa đo bằng psutil với model thật**.
- Bộ cấp phát dùng **50% RAM khả dụng** làm ngân sách chung (`system_utils.py:231-237`, `:324`) và cấp thêm worker theo vòng lặp (`system_utils.py:336-354`).
- `build_engine_config()` dùng kết quả cấp phát làm `engine_config`, rồi gọi `auto_scale_pool()` để đổi `max_processes` thực tế của pool (`tts_orchestrator.py:225-250`). `MultiEngineExecutor` tạo thread pool đúng bằng số này (`batch_executor.py:509-521`).
- Tái lập trên host hiện tại: available **6.851 MB**, budget **3.425 MB**, chỉ bật Kokoro → **Kokoro 6 worker**, ước tính 3.000 MB.
- Thực đo benchmark: Kokoro **3.933 MB** cho 1 runner; **4.662 MB** cho 2 runner. Đây là **phong bì**, không phải dự báo tuyến tính: nếu mỗi worker chạm peak 1 runner 3,9 GB thì 6 worker ≈ **23,4 GB**; nếu dùng mức trung bình 4,662/2 = 2,33 GB thì 6 worker ≈ **14,0 GB**. Cả hai đều cao hơn nhiều so với 3.000 MB ước tính; worst-case vượt **15,36 GB** của máy. Manual 8 worker có thể lên **18,6–31,4 GB** theo cùng hai cách tính.
- Đây không phải lỗi “ước tính hơi thấp”: peak 1 runner cao hơn 500 MB **7,9 lần**; ngay cả mức trung bình 2 runner cũng cao hơn **4,7 lần**. Điều chắc chắn là **ngân sách 3.000 MB cho 6 worker không có cơ sở**; việc 6 worker có OOM hay không còn phụ thuộc mức chia sẻ bộ nhớ và tải thực tế.
- Các engine khác cũng lệch nhưng mức tuyệt đối thấp hơn: Piper 327 MB (ước tính 200), MMS 450 MB (500, tạm an toàn), Supertonic 687 MB (500). Vẫn cần cập nhật theo ma trận, nhưng Kokoro là mức P0.

**Tác động**

- OOM killer hoặc swap nặng khi người dùng bật Kokoro batch; Anki có thể bị kill, mất dữ liệu chưa lưu.
- Rủi ro tăng khi Anki/collection đang dùng 1–2 GB, hoặc khi bật thêm engine khác.
- Các test hiện tại không bắt được vì benchmark chỉ chạy 2 worker và không đi qua allocator production.

**Đề xuất**

1. **Chặn auto-scale Kokoro ở 2 worker** trên máy 16 GB, trước khi có ma trận đo mới. Không dựa vào 500 MB.
2. Đặt lại estimate theo số đo: tối thiểu **2.400 MB/worker** cho batch marginal; dùng **4.000 MB/worker** nếu muốn an toàn với peak 1 runner. Sau đó đo lại 3–4 worker để chọn con số chính thức.
3. Ghép ngân sách thread: bảo đảm `workers × num_threads ≤ get_total_cpu_count()` (16 logical CPU trên host này), không dùng nhầm `get_cpu_threads()` (đang trả 8 như một policy cap). Ví dụ Kokoro 2 × 8 = 16 thread là vừa 16 CPU; 2 × 8 không nên đi với 6–8 worker. Nếu ưu tiên RAM, 1 worker × 8 thread chỉ dùng ~3,9 GB và chỉ chậm hơn batch 2 worker khoảng 10,7%.
4. Kiểm tra lại available RAM trước khi tăng pool, không chỉ một lần lúc khởi động; ghi log `peak_tree_rss` thực tế cạnh `estimated_mb`.
5. Giữ manual override nhưng hiển thị cảnh báo rõ nếu vượt budget; hiện cảnh báo chỉ ghi log (`tts_orchestrator.py:218-223`).

**Đánh đổi**

- Hạ Kokoro xuống 1–2 worker làm batch chậm hơn 10,7% so với 2 worker, nhưng tránh được nguy cơ OOM. Đây là đánh đổi đúng cho mặc định.
- Nếu cần batch Kokoro nhanh trên máy 32 GB, có thể mở manual 4 worker sau khi đo; không nên tự động.

**Cách kiểm chứng**

- Chạy 500 item với Kokoro ở 1/2/4/6 worker, đo peak tree RSS và OOM; kiểm tra `estimated_mb` so với peak thực.
- Chạy cùng lúc Piper + Kokoro + Anki collection 1 GB để thấy áp lực thực tế.

---

### P1-1 — File âm thanh không được bảo đảm đúng định dạng; OGG chưa hề được encode

**Bằng chứng**

- `AudioFileStore.resolve_audio_format()` mặc định **MP3**, map `wav`/`ogg` theo preference (`audio_file_store.py:62-73`); tên file lấy extension từ định dạng yêu cầu (`:84-91`); ghi nguyên byte vào file, không kiểm tra/không chuyển mã (`:109-129`).
- `AudioRequestKey` có trường `audio_format` theo **yêu cầu**, không phải định dạng thực tế của byte (`:20-31`, `:75-82`).
- **MMS:** batch ghi WAV ra temp `.wav`, đọc byte trả về (`service_mms.py:581-620`); single cũng dùng temp WAV. Không có nhánh MP3/OGG.
- **Kokoro:** runner tạo WAV trong bộ nhớ bằng `soundfile` (`kokoro_runner.py:108-120`); service trả base64 đã decode (`service_kokoro.py:289-293`). Không có chuyển mã.
- **Supertonic:** runner trả WAV (`supertonic_runner.py:83-110`); service trả byte WAV. Không có chuyển mã.
- **Piper:** single chỉ chuyển WAV→MP3 khi preference là `mp3` (`service_piper.py:371-392`); batch trả thẳng WAV (`:412-492`). Piper không xử lý OGG.
- **EdgeTTS:** luôn trả MP3 từ `edge_tts.Communicate` (`service_edgetts.py:345-355`), không nhận format đầu ra.
- Không có đường encode OGG nào trong các service; UI vẫn cho chọn `"ogg"` (`component_preferences.py:159-160`).

**Kết luận:** với default `mp3`, MMS/Kokoro/Supertonic (single và batch) tạo **WAV trong file `.mp3`**; Piper batch cũng vậy. Nếu người dùng chọn `wav`, EdgeTTS tạo **MP3 trong file `.wav`**. Nếu chọn `ogg`, tất cả đều tạo file `.ogg` không hợp lệ. Đây là lỗi hợp đồng dữ liệu, không chỉ là “đặt tên file xấu”.

**Tác động**

- Playback có thể lỗi hoặc phụ thuộc vào khả năng “sniff” nội dung của Anki/OS; file không hợp lệ khi kiểm tra bằng ffprobe/trình phát khác.
- Media đã import có thể không phát được trên một số nền tảng; lỗi chỉ xuất hiện với một số engine/format, dễ bị bỏ qua trong test.
- Cache lưu theo format yêu cầu nên lỗi tồn tại lâu, không tự sửa khi đổi preference.

**Đề xuất**

1. Chọn **một biên duy nhất** chịu trách nhiệm format: `AudioFileStore` hoặc `ServiceManager`. Service trả về `(bytes, actual_format)`; biên này hoặc transcode sang format yêu cầu, hoặc từ chối với lỗi rõ ràng.
2. Nếu chưa muốn transcode: đặt default local engine là `wav`, ẩn/disable OGG cho đến khi có encoder, và ghi rõ format thực tế trong tên file/cache.
3. Thêm test magic bytes: `RIFF` cho WAV, `ID3`/frame sync cho MP3, `OggS` cho OGG; test cả single và batch cho 5 engine.
4. Nếu dùng MP3: encode một lần sau khi sinh, không encode trong từng worker; đo chi phí encode 500 file trước khi bật default.

**Đánh đổi**

- Transcode MP3/OGG tốn CPU, thời gian và có thể cần temp file; batch 500 file sẽ chậm hơn benchmark hiện tại.
- Giữ WAV thì dung lượng lớn hơn (benchmark 500 item ~150–225 MB/engine/mode) nhưng an toàn và không tốn encoder. Cần đo dung lượng media thực tế trước khi chọn default.

---

### P1-2 — IPC tới runner không có timeout; semaphore có thể chờ vĩnh viễn

**Bằng chứng**

- `SherpaProcessPool.get_process()` gọi `self._semaphore.acquire()` **không timeout** (`service_mms.py:109-112`); `DynamicSemaphore.acquire()` chờ trên `Condition` vô hạn (`:17-29`).
- Các lời gọi `process.stdout.readline()` không có timeout:
  - MMS single/batch: `service_mms.py:517`, `:608`
  - Kokoro single/batch: `service_kokoro.py:279`, `:347`
  - Supertonic single/batch: `service_supertonic.py:346`, `:383`
- Piper có timeout **bên trong** cho binary `piper` (30 giây, `piper_runner.py:160-172`) nhưng `response_line` từ runner vẫn không timeout (`service_piper.py:346`, `:474`).
- EdgeTTS có `asyncio.wait_for` cho task (`service_edgetts.py:357-360`), nên không nằm trong nhóm này.
- Batch stall detector chỉ kiểm tra “không có future nào xong” trong 180 giây (`batch_orchestrator.py:731-753`). Nếu một trong 6 worker bị treo, các future khác vẫn xong nên detector không kích hoạt; future đang chạy không thể `cancel()`.
- Realtime timeout 20 giây chỉ bỏ future và giữ slot cho tới khi call thật sự kết thúc (`ttsplayer.py:197-208`), không kill runner.

**Tác động**

- Một runner bị treo (model lỗi, ONNX deadlock, pipe đầy, process con không thoát) giữ một worker + một semaphore permit. Nếu lặp lại đủ lần, toàn bộ pool bị khóa; batch treo vô hạn dù stall detector báo lỗi.
- Khi profile đóng, `stop_all()` có thể dọn process, nhưng trong phiên làm việc người dùng không có cách phục hồi ngoài restart Anki.
- Đây là **rủi ro**, chưa xảy ra trong 4.000 request benchmark (0 lỗi).

**Đề xuất**

1. Thêm deadline theo request: khởi điểm **60 giây** cho single, **120 giây** cho chunk batch (P95 hiện tại 1,6–29,9 giây; cold start Kokoro/Supertonic khoảng 10 giây cho 3 request). Đo lại trên máy chậm trước khi chốt.
2. Dùng watchdog/reader thread + queue để chờ có timeout; khi hết hạn, **kill và reap runner**, đánh dấu unhealthy, release permit, rồi retry một lần với process mới.
3. Thêm `acquire(timeout=...)` cho semaphore; nếu hết hạn, trả lỗi “engine busy” thay vì treo.
4. Với batch, timeout theo chunk và ghi lỗi cho đúng các note trong chunk; không chỉ dựa vào stall toàn cục.
5. Ghi metric: thời gian chờ process, số lần timeout, số lần restart runner.

**Đánh đổi**

- Timeout quá thấp sẽ giết request hợp lệ khi model cold start hoặc máy yếu. Nên tách “first request sau idle” khỏi steady-state, hoặc dùng 2 mức deadline.
- Kill process làm mất cache model trong RAM; request sau chậm hơn. Nhưng treo vô hạn tệ hơn.

---

### P1-3 — Checkpoint không phục hồi được batch; `O(n²)` nằm ở đường chết

**Bằng chứng**

- Đường active `process_batch_audio()` gọi `_execute_unique_tasks_unified()` (`batch_orchestrator.py:472`), rồi apply toàn bộ note, rồi mới lưu checkpoint trong nhánh `if notes_to_update and batch_status.must_continue` (`:544-550`).
- Không có lưu checkpoint trong `except`, `finally`, khi hủy, hoặc sau từng chunk. Vì vậy crash/hủy trước khi apply xong **không có checkpoint**; nếu app chết ngay sau khi lưu thì checkpoint đã gần như hoàn tất và bị xóa ngay sau đó (`:562-563`).
- Hai hàm `execute()` của `UnifiedBatchExecutor`/`MultiEngineExecutor` có lưu sau từng item (`batch_executor.py:386-401`), tạo `[t['note_id'] for t in tasks]` trong mỗi vòng lặp, và serialize toàn bộ `completed_indices`/`note_id_list` mỗi lần (`:261-274`) → `O(n²)` cả CPU và I/O. Nhưng `rg` không thấy lời gọi `.execute(` ngoài định nghĩa; đường active không dùng.
- Resume trộn index: `completed_indices` là index của danh sách gốc; sau khi lọc, `note_id_list` chỉ còn pending (`batch_orchestrator.py:342-355`), nhưng lúc lưu lại duyệt `range(len(results))` và append index của danh sách đã lọc (`:546-550`). Danh sách `note_id_list` lưu kèm vẫn là danh sách gốc. Khi resume lần hai, tập note bị lệch.
- Nếu checkpoint đã đánh dấu hoàn tất toàn bộ, code xóa checkpoint nhưng **không return**, tiếp tục chạy lại toàn bộ batch (`:346-355`) — hành vi không rõ ràng, có thể regenerate và apply lại.

**Tác động**

- Batch 10.000 note bị crash/hủy gần cuối mất gần như toàn bộ tiến độ; người dùng phải chạy lại.
- Nếu resume trong trường hợp hiếm, có thể bỏ sót hoặc cập nhật nhầm note.
- Không có bằng chứng `O(n²)` ảnh hưởng batch thật vì đường đó không chạy; đừng đưa nó vào phần “chi phí batch hiện tại”.

**Đề xuất**

1. Lưu checkpoint **theo chunk** hoặc mỗi 50 note, sau khi generation và trước/sau apply; lưu cả trạng thái “generated” và “applied” nếu cần exactly-once.
2. Chỉ lưu **tập note ID đã hoàn tất** + lỗi, không lưu hai list index; dùng `set`/JSONL append hoặc file nhỏ atomic. Sửa resume theo note ID ổn định, không theo vị trí.
3. Lưu trước khi apply, xóa sau khi apply + `update_notes` thành công; nếu crash giữa apply, resume phải idempotent (kiểm tra note đã có sound tag).
4. Xóa hoặc sửa các `execute()` chết để không ai vô tình dùng lại mô hình `O(n²)`.

**Đánh đổi**

- Ghi checkpoint thường xuyên tốn I/O; mỗi 50 note là cân bằng. Với 10.000 note, 200 lần ghi nhỏ thay vì 1 lần ghi lớn.
- Exactly-once phức tạp hơn at-least-once; nếu chọn đơn giản, phải chấp nhận regenerate một số ít và ghi rõ.

---

### P1-4 — Cleanup xóa cả log/usage, không chỉ cache âm thanh

**Bằng chứng**

- `cleanup_user_files()` quét **mọi entry là file** ở cấp 1 của `user_files`, xóa nếu `mtime` cũ hơn retention (`superfreetts.py:121-165`). Không lọc tên, không loại trừ metadata.
- `user_files` là nơi chứa:
  - audio cache `superfreetts-<hash>.<ext>` (`audio_file_store.py:84-91`)
  - `usage_log.json` (`constants.py:165`, `usage_tracker.py:36-38`)
  - `superfreetts.log` (`logging_utils.py:17`, `__init__.py:53`)
- `UsageTracker` được khởi tạo **trước** cleanup (`superfreetts.py:90-94`, `:119`). Trên Linux, file log đang mở có thể bị unlink; usage data cũ bị xóa khỏi đĩa.
- Cleanup chạy đồng bộ trong `__init__` trên main thread; comment tự ghi “runs quickly” nhưng chưa có số đo với thư mục lớn (`:125-128`).

**Tác động**

- Mất lịch sử `usage_log.json` và log sau retention; user không biết vì sao dashboard reset.
- Khởi động Anki có thể bị chậm nếu `user_files` có hàng chục nghìn file; chưa đo nên chỉ là rủi ro.
- Xóa file đang được dùng bởi batch/realtime là rủi ro race (dù tên cache thường đã cũ).
- Audio đã import vào `collection.media` **không** bị cleanup này xóa; đây là cache nguồn trong `user_files`. Vì vậy hệ quả chính là mất log/usage và phải regenerate, không phải mất audio đã gắn vào note.

**Đề xuất**

1. Chỉ xóa file khớp pattern cache: `superfreetts-<sha224>.(mp3|wav|ogg)`; loại trừ `usage_log.json`, `*.log`, checkpoint, config, file tạm.
2. Chạy cleanup trong background sau khi profile mở, có lock với lần ghi cache; không chặn main thread.
3. Chỉ xóa file không được tham chiếu gần đây; có thể touch/atime khi cache hit, hoặc dùng tuổi tối thiểu lớn hơn.
4. Log rõ “deleted N cache files”, không log như cleanup chung.

**Đánh đổi**

- Background cleanup phức tạp hơn, có thể tranh chấp với generation; cần lock theo file hoặc chỉ xóa file cũ hơn 24 giờ.
- Giữ log/usage lâu hơn tốn ít dung lượng; không đáng để mất dữ liệu.

---

### P1-5 — Benchmark không đại diện cho default; worker và thread chưa được ghép

**Bằng chứng**

- `get_cpu_threads()` trả `min(ideal, 8)` (`system_utils.py:104-115`); trên host 16 CPU là 8. `get_max_workers()` trả 16 (`:119-125`).
- Chỉ bật Kokoro, auto (không manual) → 6 worker như đã tái lập. Chỉ bật Piper → có thể 8 worker. Cả bốn engine → 2 mỗi engine.
- `engine_config` này là `max_workers` của `BoundedThreadPoolExecutor` (`batch_executor.py:509-521`), nên batch production có thể chạy 6–8 worker, không phải 2.
- Service default `num_threads=1`; benchmark MMS/Kokoro/Supertonic dùng 8. Nếu người dùng đặt 8 thread và allocator cấp 8 worker, tổng là **64 thread** trên 16 CPU — oversubscription, latency/CPU tăng.
- Benchmark không đo cấu hình 8 worker × 1 thread, cũng không đo 2 worker × 8 thread cho tất cả engine (Piper 1 thread). Vì vậy không thể kết luận default nhanh/chậm từ bảng.

**Tác động**

- Quyết định default dựa trên benchmark 2 worker có thể gây OOM (Kokoro) hoặc oversubscription (nếu tăng thread).
- Người dùng có thể thấy latency khác xa số công bố.

**Đề xuất**

1. Định nghĩa **ngân sách song song** `total_threads = Σ workers × threads` và bảo đảm ≤ số logical CPU thực (`get_total_cpu_count()`, 16 trên host này), trừ khi người dùng override có cảnh báo. Không dùng `get_cpu_threads()` (8) làm tổng ngân sách thread vì đó là policy cap cho số worker mặc định.
2. Chọn default theo profile RAM/CPU, ví dụ 16 GB/16 CPU: Kokoro 1×8 (ưu tiên RAM) hoặc 2×8 (chỉ khi đo thấy đủ RAM); Piper 4×1; MMS/Supertonic 2×4; sau đó đo lại.
3. Chạy ma trận tối thiểu: mỗi engine × worker {1,2,4,8} × thread {1,4,8}, 100–500 item, đo mean/P95/peak RSS.
4. Chỉ công bố “batch nhanh hơn X%” kèm cấu hình worker/thread và mức RAM.

**Đánh đổi**

- Nhiều worker tăng throughput nhưng RAM tăng gần tuyến tính; nhiều thread tăng CPU contention. Không có một default tối ưu cho mọi máy.
- Giới hạn thread có thể làm batch chậm trên CPU nhiều core nhưng RAM ít; đúng với mục tiêu ổn định.

---

### P2 — Tối ưu và vệ sinh tài nguyên

| Vấn đề | Bằng chứng | Tác động | Đề xuất / đánh đổi |
|---|---|---|---|
| **Piper spawn binary mỗi request** | `piper_runner.py:145-158` gọi `subprocess.Popen` cho từng task; model 63,2 MB được nạp lại. Runner Python thì persistent nhưng binary thì không. | Mean 1,039 s/item; 4.637 s audio / 500 item. Có thể có fixed cost lớn, nhưng **chưa đo**. | Đo persistent Piper/in-process ONNX; chỉ đổi nếu binary hỗ trợ. Đánh đổi: giữ process/model trong RAM, phức tạp timeout và vệ sinh. Không hứa mức tăng khi chưa đo. |
| **MMS batch rò temp WAV** | Tạo `tempfile.mkstemp(suffix='.wav')` ở `service_mms.py:581-587`; cleanup chỉ sau khi đọc kết quả thành công (`:627-632`), không có `finally`. Retry/lỗi JSON/readline bỏ qua cleanup. | Mỗi chunk lỗi có thể để lại tối đa 5 file; batch lớn lỗi nhiều lần làm đầy `/tmp`. | Đưa cleanup vào `finally`, hoặc dùng `TemporaryDirectory` cho cả chunk. Đánh đổi: gần như không có. |
| **EdgeTTS cộng bytes O(n²)** | `data += chunk["data"]` (`service_edgetts.py:350-355`). | Với text dài/nhiều chunk, cấp phát lại; thường audio nhỏ nên tác động thấp. | Dùng `bytearray` hoặc list + `b"".join()`. Đánh đổi: không đáng kể. |
| **`fsync` từng file cache** | `os.fsync(f.fileno())` trước `os.replace()` (`audio_file_store.py:118-123`). Benchmark ghi WAV trực tiếp, không fsync. | 500 fsync khi batch; trên HDD có thể thêm vài trăm ms đến vài giây; trên SSD nhỏ. Chưa đo. | Đo batch 500 file có/không fsync. Với cache có thể tái sinh, cân nhắc bỏ fsync (atomic rename vẫn bảo vệ phần lớn); đánh đổi: mất file cache nếu mất điện, nhưng có thể regenerate. |
| **Code/executor cũ** | `batch_state_manager.py` không được dùng runtime; `resource_manager` chủ yếu còn helper RSS; `UnifiedBatchExecutor.execute()`/`MultiEngineExecutor.execute()` (`batch_executor.py:552-670`) không được gọi; `_execute_single_task` trả `None` (`:423-443`, `:665-669`). | Người đọc dễ tưởng checkpoint/executor cũ là đường chính; test dễ bảo vệ hành vi chết. | Xóa hoặc đánh dấu deprecated, thêm test import; giữ helper RSS. Đánh đổi: xóa có thể ảnh hưởng test/API nội bộ, cần làm sau khi chốt. |
| **Cold start sau idle** | Pool idle 180 s (`service_mms.py:50`), cleanup 15 s; warmup Kokoro chỉ spawn process/import lib, không load model (`service_kokoro.py:142-162`); warmup 3 request: Piper 3,416 s, MMS 4,145 s, Kokoro 10,437 s, Supertonic 10,028 s. | Request đầu sau 3 phút idle có thể chậm; realtime timeout 20 s có thể bỏ audio trên máy chậm. Chưa đo riêng model load. | Đo first-request sau 180 s; nếu realtime hay dùng, tăng idle TTL hoặc prewarm model có kiểm soát. Đánh đổi: giữ 3,9 GB Kokoro thường trực. |

---

## 5. Đề xuất thứ tự thực hiện

### Cổng 0 — Trước khi coi bản build là an toàn để release

Không đổi default hàng loạt; chỉ chặn các lỗi có thể gây mất dữ liệu/OOM:

1. **Chặn Kokoro auto >2 worker** và sửa estimate theo số đo; thêm test allocator.
2. **Sửa hợp đồng format** hoặc tạm đặt local default `wav`, ẩn OGG; thêm test magic bytes.
3. **Giới hạn cleanup** chỉ vào cache audio; loại trừ usage/log/checkpoint.
4. **Đưa cleanup temp MMS vào `finally`**.

### Cổng 1 — Ổn định batch/realtime

5. Thêm deadline + kill/restart runner cho MMS/Kokoro/Supertonic; timeout cho `acquire`.
6. Sửa checkpoint theo chunk/note ID; bỏ đường `execute()` chết.
7. Chạy ma trận worker × thread; chốt default theo profile RAM.

### Cổng 2 — Tối ưu có đo lường

8. Đo Piper persistent; chỉ triển khai nếu tiết kiệm ≥15–20% mean mà không tăng rủi ro treo.
9. Đo fsync và EdgeTTS bytearray; tối ưu nếu có lợi.
10. Dọn code chết, cập nhật tài liệu benchmark/handoff.

---

## 6. Ma trận kiểm chứng đề xuất

| Test | Cách chạy | Tiêu chí đạt |
|---|---|---|
| **RAM Kokoro** | 1/2/4/6 worker, 100 và 500 item, đo peak tree RSS, có Anki collection 1 GB | Không OOM/swap; peak cây ≤ 70% RAM khả dụng; 6 worker bị chặn hoặc cảnh báo rõ; estimate sai ≤ 25% so với peak |
| **Format** | 5 engine × {mp3,wav,ogg} × {single,batch}; đọc magic bytes và extension | 100% file đúng format hoặc trả lỗi “unsupported”; OGG không còn nếu chưa encode |
| **Timeout IPC** | `SIGSTOP` runner giữa request; đo thời gian trả lỗi; kiểm tra process/permit | Request kết thúc trong deadline; runner bị kill/replace; không rò semaphore; batch tiếp tục |
| **Checkpoint** | Kill tiến trình ở 25/50/75%; resume | Không mất note; không apply trùng; đúng tập note ID; thời gian resume hợp lý |
| **Cleanup** | Tạo file audio cũ, `usage_log.json`, log, checkpoint cũ; khởi động | Chỉ audio cache bị xóa; usage/log còn; startup không chặn UI |
| **End-to-end** | 500 note trên máy 8 GB và 16 GB; batch + realtime; đóng/mở profile | 0 OOM, 0 process mồ côi, 0 note thiếu audio, playback OK |
| **Hiệu năng** | 1/2/4 worker × 1/4/8 thread, 100–500 item | Có bảng mean/P95/RSS; chọn default có bằng chứng, không suy đoán |

---

## 7. Hạn chế của báo cáo

- **Môi trường:** chỉ Linux x86_64, 16 CPU, 15,4 GB; chưa có macOS/Windows, chưa có GPU, chưa có Anki collection thật.
- **Benchmark:** chỉ WAV, 2 worker; MMS/Kokoro/Supertonic 8 thread; gọi service trực tiếp, không qua `AudioFileStore`, không MP3/OGG, không `fsync`, không import media, không `update_notes`.
- **Không đo:** cold start sau 180 s idle, lỗi/retry, timeout, hủy batch, profile switch giữa batch, máy 8 GB, CPU thấp, ổ HDD.
- **RAM:** peak tree RSS có thể cộng shared page nhiều lần; số Kokoro 3,9 GB là worst-case quan sát được, không phải toàn bộ không gian địa chỉ. Vì vậy càng phải thận trọng, không dùng 500 MB.
- **Tính suy ra:** kết luận OOM ở 6 worker là **suy ra từ phân bổ + số đo**, chưa cố tình chạy 6 worker. Kết luận playback lỗi do sai format là **suy ra từ code**, chưa chạy Anki end-to-end.
- **Phạm vi mã:** chưa rà soát đầy đủ `component_batch.py`, `component_services.py`, các engine manager, service ngoài Linux và `external/`.
- **Không sửa mã, không đổi default, không push/release/AnkiWeb.**

---

## 8. Tệp và lệnh tham chiếu

### 8.1. Tệp chính

| Nội dung | Tệp |
|---|---|
| Ước tính RAM, allocator, auto-scale | `superfreetts_addon/tts_orchestrator.py`, `superfreetts_addon/system_utils.py` |
| Process pool, IPC, temp MMS | `superfreetts_addon/services/service_mms.py` |
| Kokoro pool, warmup, IPC | `superfreetts_addon/services/service_kokoro.py` |
| Supertonic pool, IPC | `superfreetts_addon/services/service_supertonic.py` |
| Piper single/batch, spawn binary | `superfreetts_addon/services/service_piper.py`, `piper_runner.py` |
| Format, cache, atomic write | `superfreetts_addon/audio_file_store.py` |
| Batch, chunk, checkpoint active | `superfreetts_addon/batch_orchestrator.py` |
| Executor/checkpoint cũ | `superfreetts_addon/batch_executor.py`, `batch_state_manager.py` |
| Cleanup, shutdown, reopen | `superfreetts_addon/superfreetts.py`, `gui.py` |
| Realtime timeout/cap | `superfreetts_addon/ttsplayer.py` |
| Benchmark | `superfreetts_data/benchmark/BENCHMARK_SUMMARY.md` và `*_results.json` |

### 8.2. Lệnh tái lập benchmark

```bash
git rev-parse HEAD   # ee2c2f5d356abc3063f1f7161e38a13cd470da1f
.venv/bin/python superfreetts_data/benchmark/bench_piper.py
```

Các engine khác dùng cùng harness; xem `superfreetts_data/benchmark/README.md` cho biến môi trường `KOKORO_PYTHON`, `MMS_PYTHON`, `SUPERTONIC_PYTHON` và model tương ứng.

### 8.3. Lệnh kiểm tra nhanh phân bổ (không cần Anki)

```bash
python3 - <<'PY'
import importlib.util
spec = importlib.util.spec_from_file_location('su', 'superfreetts_addon/system_utils.py')
su = importlib.util.module_from_spec(spec)
spec.loader.exec_module(su)
avail = su.get_available_ram_mb()
print('available_mb =', avail)
print(su.allocate_local_engine_workers(
    cpu_caps={p: su.get_cpu_threads() for p in ['Piper','Kokoro','MMS','Supertonic']},
    ram_per_process_mb={'Piper':200,'Kokoro':500,'MMS':500,'Supertonic':500},
    enabled_engines={'Kokoro'},
    available_ram_mb=avail,
))
PY
```

Kết quả trên host hiện tại: `available_mb = 6851`, `Kokoro = 6`, `budget_mb = 3425`, `estimated_mb = 3000`.

---

## 9. Kết luận

Bản build đã tiến bộ rõ ở vòng đời process và đã có dữ liệu benchmark thật, đủ tốt để ra quyết định kỹ thuật. Tuy nhiên **chưa đủ điều kiện để coi là an toàn tài nguyên**:

- **Kokoro** có thể vượt RAM gấp nhiều lần ngân sách ước tính và có nguy cơ OOM.
- **Định dạng file** đang sai ở default `mp3` cho ba engine local, và OGG chưa được hỗ trợ dù có trong UI.
- **IPC không timeout** và **checkpoint không phục hồi được** là hai lỗ hổng vận hành lớn khi batch dài.
- **Benchmark 2 worker/8 thread/WAV** không đại diện cho default; không nên dùng nó để tuyên bố hiệu năng mặc định.

Nếu chỉ được sửa ba việc trước release, nên chọn: **(1) chặn Kokoro auto >2 worker**, **(2) sửa hợp đồng format hoặc tạm default WAV + ẩn OGG**, **(3) thêm timeout/kill runner cho MMS/Kokoro/Supertonic**. Các việc còn lại có thể theo cổng 1–2 sau khi đo ma trận worker × thread.
