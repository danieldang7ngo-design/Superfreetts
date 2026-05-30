import os
import sys
import traceback

addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, addon_dir)
sys.path.insert(0, os.path.join(addon_dir, "external"))

from tests import mock_anki

mock_anki.mock_all()


def print_result(name, ok, detail=""):
    status = "PASS" if ok else "FAIL"
    line = f"[{status}] {name}"
    if detail:
        line += f": {detail}"
    print(line)


def check_import_module():
    try:
        from superfreetts_addon.services import service_edgetts  # noqa: F401
        print_result("Import service_edgetts", True)
        return True
    except Exception:
        print_result("Import service_edgetts", False)
        traceback.print_exc()
        return False


def check_import_class():
    try:
        from superfreetts_addon.services.service_edgetts import EdgeTTS  # noqa: F401
        print_result("Import EdgeTTS class", True)
        return True
    except Exception:
        print_result("Import EdgeTTS class", False)
        traceback.print_exc()
        return False


def build_service_manager():
    import superfreetts_addon.servicemanager as servicemanager

    services_dir = os.path.join(addon_dir, "superfreetts_addon", "services")
    sm = servicemanager.ServiceManager(services_dir, "superfreetts_addon.services", False)
    sm.init_services()
    return sm


def check_discovery():
    try:
        sm = build_service_manager()
        sm.instantiate_all_services(instantiate_expensive=True)
        ok = "EdgeTTS" in sm.services
        print_result("Discover EdgeTTS", ok, f"services={sorted(sm.services.keys())}")
        return ok
    except Exception:
        print_result("Discover EdgeTTS", False)
        traceback.print_exc()
        return False


def check_voice_list():
    try:
        sm = build_service_manager()
        sm.instantiate_service_lazy("EdgeTTS")
        edge_service = sm.services.get("EdgeTTS")
        if not edge_service:
            print_result("Fetch voices", False, "EdgeTTS service not instantiated")
            return False

        voices = edge_service.voice_list()
        ok = len(voices) > 0
        first_voice = voices[0].voice_key if ok else "NONE"
        print_result("Fetch voices", ok, f"count={len(voices)}, first={first_voice}")
        return ok
    except Exception:
        print_result("Fetch voices", False)
        traceback.print_exc()
        return False


def check_audio_generation():
    try:
        from superfreetts_addon import constants
        from superfreetts_addon import languages
        from superfreetts_addon import voice
        from superfreetts_addon.services.service_edgetts import EdgeTTS

        svc = EdgeTTS()
        svc.configure({
            "concurrency_workers": 3,
            "initial_delay_min_ms": 0,
            "initial_delay_max_ms": 100,
            "wave_start_stagger_ms": 50,
        })
        test_voice = voice.build_voice_v3(
            name="Test",
            gender=constants.Gender.Female,
            language=languages.AudioLanguage.en_US,
            service=svc,
            voice_key="en-US-AriaNeural",
            options={},
        )
        results = svc.get_tts_audio_batch(
            ["hello world", "Ti\u1ebfng Vi\u1ec7t c\u00f3 d\u1ea5u", "hej varlden"],
            test_voice,
            {"speed": 0, "pitch": 0, "volume": 0},
        )
        audio_lengths = [len(result) if result else 0 for result in results]
        ok = len(audio_lengths) == 3 and all(length > 0 for length in audio_lengths)
        print_result("Generate audio wave", ok, f"bytes={audio_lengths}")
        return ok
    except Exception:
        print_result("Generate audio", False)
        traceback.print_exc()
        return False


def check_sequence_selection():
    try:
        from superfreetts_addon import config_models
        from superfreetts_addon import constants
        from superfreetts_addon import voice
        from superfreetts_addon.superfreetts import SuperFreeTTS

        selection = config_models.VoiceSelectionSequence()
        expected_keys = ["voice-1", "voice-2", "voice-3", "voice-1", "voice-2"]
        for voice_key in ["voice-1", "voice-2", "voice-3"]:
            selection.add_voice(
                config_models.VoiceWithOptionsSequence(
                    voice.TtsVoiceId_v3(voice_key=voice_key, service="EdgeTTS"),
                    {},
                )
            )

        hypertts = SuperFreeTTS.__new__(SuperFreeTTS)
        chosen_keys = [
            hypertts.choose_voice(selection, None, idx).voice_id.voice_key
            for idx in range(len(expected_keys))
        ]
        ok = selection.selection_mode == constants.VoiceSelectionMode.sequence and chosen_keys == expected_keys
        print_result("Sequence voice order", ok, f"order={chosen_keys}")
        return ok
    except Exception:
        print_result("Sequence voice order", False)
        traceback.print_exc()
        return False


def main():
    checks = [
        check_import_module,
        check_import_class,
        check_discovery,
        check_voice_list,
        check_sequence_selection,
        check_audio_generation,
    ]

    results = [check() for check in checks]
    passed = sum(1 for ok in results if ok)
    total = len(results)
    print("")
    print(f"Summary: {passed}/{total} checks passed")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
