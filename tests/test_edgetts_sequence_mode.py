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
from superfreetts_addon import config_models
VI_TEXTS = [
    "Xin chào", "Cảm ơn bạn", "Tôi là sinh viên", "Hôm nay trời đẹp",
    "Bạn có khỏe không", "Tôi đi học", "Cô ấy đang đọc sách", "Chúng tôi đi chơi",
    "Anh ấy là bác sĩ", "Mẹ tôi nấu ăn ngon", "Con mèo đang ngủ", "Ngôi nhà màu xanh",
    "Bông hoa rất đẹp", "Trời mưa to quá", "Em bé đang khóc", "Xe đạp của tôi",
    "Cửa hàng sách", "Trường học lớn", "Bữa tối ngon", "Chúc ngủ ngon",
    "Tôi yêu bạn", "Mặt trời mọc", "Biển xanh cát trắng", "Cây cao vút",
    "Chim hót líu lo", "Dòng sông chảy", "Núi non hùng vĩ", "Rừng già xanh thẳm",
    "Thành phố náo nhiệt", "Làng quê yên bình", "Đồi chè bát ngát", "Vườn hoa rực rỡ",
    "Hồ nước trong veo", "Bầu trời sao lấp lánh", "Cánh đồng lúa chín", "Con đường quanh co",
    "Bãi biển đông người", "Khu phố cổ kính", "Chợ quê tấp nập", "Đền chùa linh thiêng",
    "Cơm tấm bì sườn", "Phở bò tái", "Bún chả Hà Nội", "Bánh mì thịt nướng",
    "Cà phê sữa đá", "Trà đá vỉa hè", "Nước dừa tươi", "Bánh tráng trộn",
    "Chè đậu xanh", "Cháo lòng", "Mì quảng", "Hủ tiếu nam vang",
    "Lẩu thái chua cay", "Bánh xèo giòn", "Nem rán", "Gỏi cuốn tôm thịt",
    "Bún bò huế", "Cơm niêu", "Vịt quay", "Cua rang me",
]

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

v1 = voice.build_voice_v3(name="HoaiMyNeural", gender=constants.Gender.Female,
    language=languages.AudioLanguage.vi_VN, service=svc,
    voice_key="vi-VN-HoaiMyNeural", options={})
v2 = voice.build_voice_v3(name="NamMinhNeural", gender=constants.Gender.Male,
    language=languages.AudioLanguage.vi_VN, service=svc,
    voice_key="vi-VN-NamMinhNeural", options={})

voice_map = {"vi-VN-HoaiMyNeural": v1, "vi-VN-NamMinhNeural": v2}

seq = config_models.VoiceSelectionSequence()
seq.add_voice(config_models.VoiceWithOptionsSequence(v1.voice_id, {}))
seq.add_voice(config_models.VoiceWithOptionsSequence(v2.voice_id, {}))

TOTAL = 100
texts = [f"{VI_TEXTS[i % len(VI_TEXTS)]} [{i}]" for i in range(TOTAL)]

# Simulate batch_orchestrator: choose_voice with sequence_index
tasks = []
for i, text in enumerate(texts):
    chosen_seq_voice = seq.voice_list[i % len(seq.voice_list)]
    actual_voice = voice_map[chosen_seq_voice.voice_id.voice_key]
    tasks.append((i, text, actual_voice))

print(f"EdgeTTS sequence + batch: {TOTAL} texts, 2 voices")
print(f"  workers: {batch_constants.EDGETTS_MAX_WORKERS}, batch_size: 3")
print()

BATCH_SIZE = 3
batches = [tasks[i:i+BATCH_SIZE] for i in range(0, len(tasks), BATCH_SIZE)]

def process_batch(batch):
    return [(i, t, svc.get_tts_audio_batch([t], v, {"speed":0,"pitch":0,"volume":0})[0]) for i, t, v in batch]

start = time.time()
all_results = []
with concurrent.futures.ThreadPoolExecutor(max_workers=batch_constants.EDGETTS_MAX_WORKERS) as pool:
    futures = {pool.submit(process_batch, b): b[0][0] for b in batches}
    for future in concurrent.futures.as_completed(futures):
        all_results.extend(future.result())

elapsed = time.time() - start

all_results.sort(key=lambda x: x[0])
ok = sum(1 for _, _, r in all_results if r is not None)
fail = sum(1 for _, _, r in all_results if r is None)

for i, txt, r in all_results:
    vk = tasks[i][2].voice_key
    print(f"  [{'OK' if r else 'FAIL'}] text[{i:3d}] {vk[:15]:15s} {len(r) if r else 0:>6d}b")

print()
print(f"Total: {TOTAL}, OK: {ok}, FAIL: {fail}")
print(f"Success: {100*ok/TOTAL:.1f}%")
print(f"Time: {elapsed:.2f}s")

v1_ok = sum(1 for i, _, r in all_results if tasks[i][2].voice_key == v1.voice_key and r)
v1_tot = sum(1 for i, _, _ in all_results if tasks[i][2].voice_key == v1.voice_key)
v2_ok = sum(1 for i, _, r in all_results if tasks[i][2].voice_key == v2.voice_key and r)
v2_tot = sum(1 for i, _, _ in all_results if tasks[i][2].voice_key == v2.voice_key)

print(f"  HoaiMyNeural: {v1_ok}/{v1_tot} ({100*v1_ok/v1_tot:.0f}%)")
print(f"  NamMinhNeural: {v2_ok}/{v2_tot} ({100*v2_ok/v2_tot:.0f}%)")

sys.exit(0 if fail == 0 else 1)
