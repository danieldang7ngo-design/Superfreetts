import os
import sys
import time
import concurrent.futures

addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, addon_dir)
sys.path.insert(0, os.path.join(addon_dir, 'external'))

from tests import mock_anki
mock_anki.mock_all()

from superfreetts_addon.services.service_edgetts import EdgeTTS
from superfreetts_addon import constants
from superfreetts_addon import languages
from superfreetts_addon import voice
from superfreetts_addon import batch_constants

VI_BASES = [
    "Xin chào",
    "Cảm ơn bạn",
    "Tôi là sinh viên",
    "Hôm nay trời đẹp",
    "Bạn có khỏe không",
    "Tôi đi học",
    "Cô ấy đang đọc sách",
    "Chúng tôi đi chơi",
    "Anh ấy là bác sĩ",
    "Mẹ tôi nấu ăn ngon",
    "Con mèo đang ngủ",
    "Ngôi nhà màu xanh",
    "Bông hoa rất đẹp",
    "Trời mưa to quá",
    "Em bé đang khóc",
    "Xe đạp của tôi",
    "Cửa hàng sách",
    "Trường học lớn",
    "Bữa tối ngon",
    "Chúc ngủ ngon",
    "Tôi yêu bạn",
    "Mặt trời mọc",
    "Biển xanh cát trắng",
    "Cây cao vút",
    "Chim hót líu lo",
    "Dòng sông chảy",
    "Núi non hùng vĩ",
    "Rừng già xanh thẳm",
    "Thành phố náo nhiệt",
    "Làng quê yên bình",
    "Đồi chè bát ngát",
    "Vườn hoa rực rỡ",
    "Hồ nước trong veo",
    "Bầu trời sao lấp lánh",
    "Cánh đồng lúa chín",
    "Con đường quanh co",
    "Bãi biển đông người",
    "Khu phố cổ kính",
    "Chợ quê tấp nập",
    "Đền chùa linh thiêng",
    "Cơm tấm bì sườn",
    "Phở bò tái chín",
    "Bún chả Hà Nội",
    "Bánh mì thịt nướng",
    "Cà phê sữa đá",
    "Trà đá vỉa hè",
    "Nước dừa tươi",
    "Bánh tráng trộn",
    "Chè đậu xanh",
    "Cháo lòng",
    "Mì quảng",
    "Hủ tiếu nam vang",
    "Lẩu thái chua cay",
    "Bánh xèo giòn",
    "Nem rán",
    "Gỏi cuốn tôm thịt",
    "Bún bò huế",
    "Cơm niêu",
]

SPECIAL_CHARS = [
    "",
    ".",
    ",",
    "!",
    "?",
    ";",
    ":",
    "-",
    "—",
    "...",
    "()",
    "[]",
    "{}",
    "<>",
    "&",
    "%",
    "/",
    "\\",
    "#",
    "@",
    "*",
    "+",
    "=",
    "~",
    "^",
    "_",
    "|",
    "`",
    "$",
    "\"",
    "'",
]

def build_texts(count):
    texts = []
    for i in range(count):
        base = VI_BASES[i % len(VI_BASES)]
        sc = SPECIAL_CHARS[i % len(SPECIAL_CHARS)]
        if i % 4 == 0:
            texts.append(f"{base} {sc}")
        elif i % 4 == 1:
            texts.append(f"{sc} {base} {sc}")
        elif i % 4 == 2:
            texts.append(f"{base}, {sc} {base}")
        else:
            texts.append(f"<b>{base}</b> {sc} <i>{base}</i>")
    return texts

svc = EdgeTTS()
svc.configure({
    "concurrency_workers": batch_constants.EDGETTS_MAX_WORKERS,
    "initial_delay_min_ms": 0,
    "initial_delay_max_ms": 250,
    "wave_start_stagger_ms": 150,
    "max_retries": 3,
    "retry_backoff_seconds": 3,
    "debug_logging": False,
})

voice_key = "vi-VN-HoaiMyNeural"
test_voice = voice.build_voice_v3(
    name="HoaiMyNeural",
    gender=constants.Gender.Female,
    language=languages.AudioLanguage.vi_VN,
    service=svc,
    voice_key=voice_key,
    options={},
)

TOTAL = 1000
BATCH_SIZE = 3

texts = build_texts(TOTAL)
chunks = [texts[i:i+BATCH_SIZE] for i in range(0, len(texts), BATCH_SIZE)]

print(f"EdgeTTS Vietnamese stress test: {len(texts)} texts")
print(f"  concurrency_workers: {batch_constants.EDGETTS_MAX_WORKERS}")
print(f"  batch_size: {BATCH_SIZE} ({len(chunks)} chunks)")
print(f"  max_retries: 3")
print(f"  voice: {voice_key}")
print(f"  special chars: {len(SPECIAL_CHARS)} patterns")
print(f"  html mixed: yes")
print()

start = time.time()

def process_chunk(chunk_idx, chunk_texts):
    results = svc.get_tts_audio_batch(chunk_texts, test_voice, {"speed": 0, "pitch": 0, "volume": 0})
    return chunk_idx, results

all_results = [None] * len(texts)
with concurrent.futures.ThreadPoolExecutor(max_workers=batch_constants.EDGETTS_MAX_WORKERS) as pool:
    futures = {pool.submit(process_chunk, i, c): i for i, c in enumerate(chunks)}
    for future in concurrent.futures.as_completed(futures):
        chunk_idx, chunk_results = future.result()
        for j, r in enumerate(chunk_results):
            text_idx = chunk_idx * BATCH_SIZE + j
            all_results[text_idx] = r

elapsed = time.time() - start

succeeded = sum(1 for r in all_results if r is not None)
failed = sum(1 for r in all_results if r is None)

print()
print(f"Total: {len(all_results)}, Succeeded: {succeeded}, Failed: {failed}")
print(f"Success rate: {succeeded}/{len(all_results)} ({100 * succeeded / len(all_results):.1f}%)")
print(f"Time: {elapsed:.2f}s ({elapsed/len(all_results):.2f}s per text)")

if failed > 0:
    print(f"FAILED: {failed} texts failed after retries")
    for i, r in enumerate(all_results):
        if r is None:
            print(f"  FAIL text[{i}]: {texts[i][:80]}")
    sys.exit(1)
else:
    print("PASSED: all texts generated successfully")
    sys.exit(0)
