"""Legacy HyperTTS voice list.

SuperFreeTTS only ships free services; every entry in the historical
HyperTTS voice list was a paid service and no bundled service calls
``basic_voice_list()``.  Keeping 46k lines of unused data forced Anki to
compile a 2.5 MB module on every startup, so the list is intentionally
empty now.  The public names are preserved for backwards compatibility.
"""

_VOICE_LIST = []
VOICE_LIST = _VOICE_LIST


def get_voice_list():
    return _VOICE_LIST
