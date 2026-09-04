import json
from pathlib import Path
from typing import Dict

SUPPORTED_LANGUAGES = ["en", "vi", "ko", "zh-CN", "zh-TW", "ja", "sv"]

_LOCALE_DIR = Path(__file__).parent / "locales"


def _load_locale(lang: str) -> Dict[str, str]:
    locale_file = _LOCALE_DIR / f"{lang}.json"
    with locale_file.open("r", encoding="utf-8") as handle:
        return json.load(handle)


STRINGS: Dict[str, Dict[str, str]] = {
    lang: _load_locale(lang)
    for lang in SUPPORTED_LANGUAGES
}


def _normalize_language(lang: str) -> str:
    """Normalize the UI language code and fall back to English."""
    if lang not in SUPPORTED_LANGUAGES:
        return "en"
    return lang


def get_text(key: str, lang: str) -> str:
    """
    Return UI text by key and language.

    - Unknown languages fall back to English.
    - Missing keys in the selected language fall back to English.
    - Missing keys in English return the key itself to make debugging obvious.
    """
    lang = _normalize_language(lang)
    lang_dict = STRINGS.get(lang, STRINGS["en"])
    if key in lang_dict:
        return lang_dict[key]
    if key in STRINGS["en"]:
        return STRINGS["en"][key]
    return key
