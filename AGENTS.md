# AGENTS.md — Super Free TTS

Hướng dẫn cho AI agent (Kiro, Claude Code, Copilot, Cursor, Codex, Aider…) khi
làm việc trên repo này. Đọc trước khi build `.ankiaddon`, `git add`, commit hay
push.

## 1. Bối cảnh repo

- Đây là addon Anki (Python), package name `superfreetts`, hiển thị là
  "Super Free TTS".
- Folder làm việc đồng thời là **chỗ Anki cài addon**:
  `C:\Users\ADMIN\AppData\Roaming\Anki2\addons21\351217314\`.
  Nghĩa là khi user chạy Anki, code ở đây load thẳng. Mọi file ở đây = dữ liệu
  thật đang chạy của user.
- Remote: `https://github.com/danieldang7ngo-design/Superfreetts`
  Nhánh chính: `main`. Còn có `master`, `test` (cũ).

## 2. EdgeTTS worker cap — quy tắc bất di bất dịch

User chia làm hai mức:

| Môi trường | Cap EdgeTTS | Lý do |
| --- | --- | --- |
| Local (máy user) | 20 worker | User rành tech, biết tự điều chỉnh. |
| Bản share / repo public / `.ankiaddon` | 3 worker | Tránh Microsoft rate-limit cho người dùng phổ thông. |

Source of truth nên đặt **cap 3 trong repo**, có cơ chế override local-only
(file `_local_override.py` đã gitignore) để bạn có thể bật 20 ở máy mình mà
không bao giờ ảnh hưởng commit.

Các điểm code liên quan tới cap (đụng vào thì phải nhớ cả 4):

- `superfreetts_addon/batch_constants.py` — định nghĩa hằng số worker.
- `superfreetts_addon/services/service_edgetts.py` — UI advanced, runtime
  clamp.
- `superfreetts_addon/superfreetts.py` — `__init__` và
  `reconfigure_service_manager` đều có `engine_config` cho EdgeTTS.
- `config.json` — `service_config.EdgeTTS.concurrency_workers` (default).

`MAX_WORKER_THREADS = 20` ở `batch_constants.py` là trần CHUNG cho mọi engine
local (Piper/Kokoro/MMS, CPU-bound). Đừng hạ nó xuống 3, nếu không Piper/Kokoro
cũng bị cap. Cap riêng EdgeTTS phải dùng `EDGETTS_MAX_WORKERS`.

## 3. NEVER commit / push những thứ này

User data và artifact runtime tuyệt đối không được lên git:

```
meta.json                          # uuid, install_time, presets cá nhân
user_files/                        # cache mp3, hàng nghìn file
superfreetts_addon/user_files/
superfreetts_addon/cache/          # generation cache
superfreetts-work.index            # Anki search index
__pycache__/  *.pyc  *.pyo
dist/                              # staging build
*.ankiaddon                        # output build
superfreetts-mirror.git/           # bare git mirror local
git-objects-tmp/                   # objects rời
EDGE_TTS_WORKER_20_REPORT.md       # note local
.idea/  .vscode/  *.log
```

Đã có `.gitignore` ở root cover các pattern này. Trước khi commit, chạy
`git status` và verify không có file thuộc các pattern trên trong "Changes to
be committed".

`meta.json` đặc biệt nguy hiểm: chứa `user_uuid`, install_time, toàn bộ presets
(có thể chứa text + voice setting cá nhân của user). Tuyệt đối không commit.

Lưu ý: commit cũ trên `origin/main` từng lỡ đẩy `meta.json`. Nếu user đồng ý,
có thể `git filter-repo` để xoá khỏi history, nhưng phải force-push và đổi
SHA.

## 4. Build `.ankiaddon` để chia sẻ

Script: `build_share.py` (chạy ở addon root: `python build_share.py`).

Nó sẽ:
1. Copy whitelist (`__init__.py`, `manifest.json`, `LICENSE`, `config.json`,
   `superfreetts_addon/`, `external/`, `graphics/`) sang `dist/staging/`.
2. Patch EdgeTTS cap từ 20 → 3 trong staging (giữ source local nguyên 20 nếu
   chưa migrate sang cơ chế `_local_override.py`).
3. Reset `config.json` về clean default (không kèm presets/uuid của user).
4. Zip thành `SuperFreeTTS.ankiaddon` ở addon root.

Khi user cài đè bằng file `.ankiaddon` mới, Anki **giữ nguyên**:
- `meta.json` (presets, settings, uuid) → vì Anki tự quản lý file này.
- `user_files/` (cache mp3) → Anki không đụng vào.

Nghĩa là user upgrade addon không mất data. Đây là hành vi mặc định của Anki
addon manager, không cần làm gì thêm.

Nếu sau này migrate sang cơ chế "source of truth = cap 3 + `_local_override`",
thì `build_share.py` không cần patch nữa, chỉ cần zip thuần là đủ.

## 5. Git workflow ở repo này

Cấu hình git:
- `user.name = Phuc`, `user.email = your@email.com` (placeholder, có thể nên
  set email thật).
- Nhánh mặc định: `main`. Push lên `origin/main`.

Tuần tự khi sửa code:

```cmd
git status                          # luôn check trước
git add <file_cụ_thể>               # tránh `git add -A` khi chưa hiểu repo state
git status                          # check lại staged area
git commit -m "..."
git push origin main
```

Tránh `git add .` hoặc `git add -A` khi:
- Có file mới chưa biết là user data hay code.
- Đang trong quá trình build (có `dist/` chưa kịp gitignore).

Không tự ý:
- Force push (`git push -f`) — chỉ làm khi user yêu cầu rõ.
- Rewrite history (`filter-repo`, `rebase -i` past published commits) — hỏi
  trước.
- Xoá branch remote.
- Sửa `.git/config` user identity.

Khi có conflict 20-vs-3 worker:
- KHÔNG `git stash` rồi `git stash pop` thủ công mỗi lần. Đó là dấu hiệu cần
  migrate sang cơ chế `_local_override.py` đã đề xuất ở mục 2.

## 6. Checklist nhanh trước khi commit/push

- [ ] `git status` không có `meta.json`, `user_files/`, `*.ankiaddon`,
      `dist/`, `__pycache__/`, `superfreetts-work.index`.
- [ ] Nếu sửa logic worker cap, đã đụng đủ 4 chỗ ở mục 2.
- [ ] Nếu thêm dependency mới vào `external/`, đã verify license tương thích
      và update `_EXTERNAL_LIBRARIES_EXPLAINED.md` nếu có.
- [ ] Commit message ngắn gọn, mô tả intent (vd: "Cap EdgeTTS at 3 for
      release", không phải "fix").
- [ ] Push lên đúng nhánh `main` (không phải `master` legacy hoặc `test`).

## 7. Checklist trước khi build `.ankiaddon` để share

- [ ] Verify code chạy OK ở Anki local (cap 20 hoặc 3 đều phải hoạt động).
- [ ] Bump `version.py` nếu phát hành.
- [ ] Update `CHANGELOG.md` nếu có thay đổi user-facing.
- [ ] Chạy `python build_share.py`, verify `SuperFreeTTS.ankiaddon` được tạo.
- [ ] Mở zip kiểm tra: không có `meta.json`, `user_files/`, `__pycache__/`,
      `cache/`. Có `manifest.json`, `__init__.py`, `superfreetts_addon/`,
      `external/`.
- [ ] Verify `service_edgetts.py` trong zip cap 3 (không phải 20).
- [ ] Verify `config.json` trong zip là default sạch (không có
      `user_uuid`, `presets` của bạn).

## 8. Cấu trúc thư mục tham khảo

```
351217314/                          (= addon root = repo root)
├── .git/                           (sau khi init, có thể chưa có)
├── .gitignore
├── AGENTS.md                       (file này)
├── README.md  CHANGELOG.md  _ROADMAP.md  _AI_SUMMARY.md ...
├── __init__.py                     (entry point Anki gọi)
├── manifest.json                   (package metadata)
├── config.json                     (default config, KHÔNG chứa user data)
├── meta.json                       (gitignored — Anki ghi user state)
├── LICENSE
├── build_share.py                  (build .ankiaddon)
├── superfreetts_addon/             (code chính)
│   ├── batch_constants.py
│   ├── batch_executor.py
│   ├── superfreetts.py
│   ├── services/
│   │   └── service_edgetts.py      (logic cap worker)
│   └── ...
├── external/                       (3rd party libs vendored)
├── graphics/
├── tests/                          (test suite)
├── user_files/                     (gitignored — cache mp3)
└── dist/                           (gitignored — build artifacts)
```

## 9. Quick reference paths

- Repo root: `c:\Users\ADMIN\AppData\Roaming\Anki2\addons21\351217314`
- Build output: `<repo_root>\SuperFreeTTS.ankiaddon`
- Build staging: `<repo_root>\dist\staging\`
- Remote: `https://github.com/danieldang7ngo-design/Superfreetts`
