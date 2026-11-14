# Đánh giá hiệu năng hiện tại — SuperFreeTTS 26.10.3

Ngày đo: 2026-10-24 · Máy: 16 CPU, 15,4 GB RAM, Linux 7.2.9 (CachyOS)
Repo: `superfreetts` · nhánh `fix/resource-management` · HEAD `55089d3` (release 26.10.3)

## Kết luận ngắn

Hiệu năng **không hồi quy** so với mốc 22/10. Phần add-on gần như không tốn thời gian
(tổng chi phí ngoài engine cho 2.000 note ≈ 0,27 s). Thời gian tạo audio nằm gần như
toàn bộ ở engine. Máy hôm nay chậm hơn lúc đo 22/10 khoảng 16–18% do trạng thái hệ
thống, không do code — đã kiểm chứng bằng A/B cùng máy.

## 1. A/B cùng máy, cùng dữ liệu (80 từ tiếng Anh, Piper en_US-lessac-medium)

| Bản | Đơn lẻ | Batch (chunk 5, 2 worker) | RAM đỉnh đơn lẻ | RAM đỉnh batch |
|---|---:|---:|---:|---:|
| `ee2c2f5` (mốc 22/10) | 1,208 s/từ | 1,021 s/từ | 365 MB | 573 MB |
| `55089d3` (hiện tại) | 1,230 s/từ | 1,019 s/từ | 250 MB | 465 MB |
| Chênh lệch | +1,8% | −0,2% | — | — |

Kết luận: chênh lệch nằm trong nhiễu đo. Code hiện tại không làm chậm engine.

Mốc 22/10 (500 từ) là 1,039 s/từ đơn lẻ và 0,849 s/từ batch — nhanh hơn ~16–18% so với
hôm nay. Nguyên nhân là điều kiện máy: desktop đang chạy (Brave + Hermes + KWin,
load average 1,6–3,7) và governor `powersave`; độ dài audio mỗi từ giống nhau
(9,26 s so với 9,28 s) nên không phải do khối lượng công việc khác.

## 2. Chi phí phần add-on (không tính engine), 2.000 note

| Công đoạn | Tổng | Mỗi note |
|---|---:|---:|
| Làm sạch text (HTML, ngoặc, cloze, ký tự đặc biệt) | 8,1 ms | 4,1 µs |
| Tạo khoá + gộp note trùng (25% trùng) | 16,6 ms | 8,3 µs |
| Ghi file cache (500 file thật, ~16 KB) | 53,7 ms | 0,107 ms |
| Đọc cache (500 lần trúng) | 8,1 ms | 16,3 µs |

Ước tính 2.000 note: ~0,27 s tổng, trong đó ghi cache là phần lớn. Chạy lại một batch
đã có cache: ~32 ms cho 2.000 note.

Thread pool (200 tác vụ giả 10 ms): overhead 1,3% với 1 luồng, 1,9% với 4 luồng,
2,6% với 8 luồng — gần như tuyến tính, không có nghẽn hàng đợi.

## 3. Khởi động và bộ kiểm thử

| Hạng mục | Kết quả |
|---|---|
| Import module lõi | 31 ms |
| Import facade `superfreetts` | +49 ms (tổng 79 ms) |
| RAM sau import | 36 MB |
| `pytest` toàn bộ | 474 passed, 1 skipped — 6,67 s |
| `ruff check` | pass — 0,04 s |
| `bandit -ll` | pass — 2,45 s (chỉ 2 warning `nosec` đã biết) |
| Gói cài `SuperFreeTTS.ankiaddon` | 2,2 MB |

## 4. Engine qua mạng — EdgeTTS (mạng thật, cap 3 luồng)

| Kiểu chạy | Kết quả |
|---|---|
| 1 câu ngắn, tuần tự | 0,40–0,58 s/câu |
| 3 câu, 1 luồng | 1,50 s (0,50 s/câu) |
| 3 câu, 3 luồng | 0,49–0,58 s (0,16–0,19 s/câu) → nhanh 2,6× |
| 6 câu tuần tự (lần đo đầu) | 15,85 s (2,64 s/câu) — bị bóp tốc độ |

Độ trễ phụ thuộc mạng và có lúc bị Microsoft giới hạn tốc độ; đây là rủi ro của dịch vụ,
không phải lỗi add-on. Cap 3 luồng vẫn giữ nguyên.

## 5. Điểm yếu còn lại (từ benchmark 500 từ ngày 22/10)

| Engine | Đơn lẻ | Batch 2 worker | RAM đỉnh đơn lẻ | RAM đỉnh batch |
|---|---:|---:|---:|---:|
| Piper | 1,039 s | 0,849 s | 327 MB | 384 MB |
| MMS | 1,225 s | 1,086 s | 450 MB | ~827 MB |
| Kokoro | 2,484 s | 2,218 s | 3.933 MB | 4.662 MB |
| Supertonic | 2,796 s | 2,289 s | 687 MB | 1.376 MB |

- Kokoro là engine nặng nhất: gấp ~2,4× thời gian Piper và ~4,7 GB RAM khi batch.
- P95 mỗi chunk batch là 10,5–29,9 s, có chunk chậm bất thường → thanh tiến trình có
  thể đứng vài chục giây dù batch vẫn chạy.
- Nhả bộ nhớ sau khi rảnh hoạt động đúng ở cả 4 engine (về 38–58 MB, 0 tiến trình con).

## 6. Khuyến nghị

1. Cấu hình nhanh nhất: Piper + batch 2 worker; EdgeTTS để 3 luồng như mặc định.
2. Kokoro/Supertonic: giữ 1 worker, cảnh báo nếu máy dưới 8 GB RAM.
3. Muốn số đo tuyệt đối: đo lại khi đóng ứng dụng khác — chênh lệch môi trường ~16–18%.
4. Việc P2 trong kế hoạch (ma trận worker × thread, Piper persistent) vẫn chưa làm;
   chỉ nên làm nếu cần tối ưu thêm, vì phần add-on hiện chỉ chiếm dưới 0,02% thời gian batch.

## Tệp sinh ra

- `superfreetts_data/benchmark_current/bench_layer.py` — đo phần add-on (không cần mạng).
- `superfreetts_data/benchmark_current/bench_piper.py` — bản sao harness Piper, chạy `--limit 80`.
- `superfreetts_data/benchmark_current/layer_results.json`, `piper_results.json`, `REPORT_PIPER.md`.
