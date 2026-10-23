# Test tay crash-resume Preview — 2026-10-23

Môi trường ghi nhận: Anki <ghi version>, OS <ghi OS>, SuperFreeTTS 26.10.2, nhánh fix/resource-management.

## Oracle
- Không mất note nào.
- Không trùng `[sound:]` trong field đích.
- Resume đúng note đã applied, chỉ apply phần còn lại.

## Các mốc checkpoint
1. Sau prepare: tạo key `preview-...` (preview_checkpoint_key).
2. Sau commit QueryOp: `mark_applied` các note trong chunk.
3. Khi xong: `remove()` checkpoint.
4. Khi hủy/lỗi: `flush()` checkpoint.

## Kịch bản kill -9 (200 note)
1. Mở Anki, chọn deck/batch 200 note, mở Preview.
2. Tạo audio (Prepare + Generate) xong, bắt đầu Áp (apply).
3. Khi apply đạt ~50-100 note, kill Anki: `kill -9 <pid>` (hoặc Task Manager).
4. Mở lại Anki, mở lại cùng batch/preset, Tạo audio tiếp (resume).
5. Kiểm tra: số note đã applied trước kill được bỏ qua; chỉ apply phần còn lại.
6. Sau hoàn tất, kiểm tra 200 note: mỗi field đích có đúng 1 `[sound:...]`, không trùng.
7. Ghi log: thời gian kill, số note applied trước kill, số note apply sau resume, kết quả.

## Dọn checkpoint kẹt
- Nếu checkpoint còn sau khi batch xong: xóa file `superfreetts_addon/user_files/batch_state/preview-*.checkpoint.json`.
- Hoặc gọi `batch_checkpoint.remove()` trong flow hủy.
