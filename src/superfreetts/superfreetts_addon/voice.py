import sys
import abc
import dataclasses
import logging

logger = logging.getLogger(__name__)
try:
    import databind
except Exception:
    logger.debug("databind not available, using fallback shim")
    import json as _json

    class _DataBindShim:
        class json:
            @staticmethod
            def dump(obj, schema=None):
                try:
                    if dataclasses.is_dataclass(obj):
                        return _json.dumps(dataclasses.asdict(obj))
                except Exception:
                    pass
                return _json.dumps(obj)

            @staticmethod
            def load(s, schema=None):
                try:
                    if isinstance(s, (str, bytes)):
                        return _json.loads(s)
                except Exception:
                    pass
                return s

    databind = _DataBindShim()
import functools
from typing import Dict, Any, List, Union

from . import constants
from . import languages
from . import i18n

class VoiceBase(abc.ABC):
    """
    abstract base class which defines all the mandatory properties
    """

    @property
    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def gender(self) -> constants.Gender:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def language(self) -> languages.AudioLanguage:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def service(self):
        """Service instance that provides this voice (type opaque to avoid cycles)"""
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def voice_key(self) -> Union[Dict[str, Any], str]:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def options(self) -> Dict[str, Dict[str, Any]]:
        raise NotImplementedError()

    def serialize(self):
        return {
            'name': self.name,
            'gender': self.gender.name,
            'language': self.language.name,
            'service': self.service.name,
            'voice_key': self.voice_key
        }

    def __str__(self):
        return f'{self.language.audio_lang_name}, {self.gender.name}, {self.name}, {self.service.name}'

    def __eq__(self, other):
        return self.service.name == other.service.name and self.voice_key == other.voice_key


class Voice(VoiceBase):
    """
    this basic implementation can be used by services which don't have a particular requirement
    """

    def __init__(self, name, gender, language, service, voice_key, options):
        self._name = name
        self._gender = gender
        self._language = language
        self._service = service
        self._voice_key = voice_key
        self._options = options

    def _get_name(self):
        return self._name

    def _get_gender(self):
        return self._gender

    def _get_language(self):
        return self._language

    def _get_service(self):
        return self._service
    
    def _get_voice_key(self):
        return self._voice_key

    def _get_options(self):
        return self._options

    def __repr__(self):
        return f'{self.service} {self.name}, {self.language}'

    name = property(fget=_get_name)
    gender = property(fget=_get_gender)
    language = property(fget=_get_language)
    service = property(fget=_get_service)
    voice_key = property(fget=_get_voice_key)
    options = property(fget=_get_options)

# these classes are used with API version 3
# support for multilingual voices

# voice identification only
@dataclasses.dataclass
class TtsVoiceId_v3:
    voice_key: Union[Dict[str, Any], str]
    service: str

    def __eq__(self, other):
        if not isinstance(other, TtsVoiceId_v3):
            return NotImplemented
        return self.voice_key == other.voice_key and self.service == other.service

    def __hash__(self):
        if isinstance(self.voice_key, str):
            # voice_key is a string
            return hash((self.voice_key, self.service))
        else:
            # voice_key is a dict
            return hash((frozenset(self.voice_key.items()), self.service))


# full voice information (to display in the GUI)
@dataclasses.dataclass
class TtsVoice_v3:
    name: str
    voice_key: Dict[str, Any]
    options: Dict[str, Dict[str, Any]]
    service: str
    gender: constants.Gender
    audio_languages: List[languages.AudioLanguage]
    service_fee: constants.ServiceFee

    @property
    def voice_id(self) -> TtsVoiceId_v3:
        return self.get_voice_id()

    def get_voice_id(self) -> TtsVoiceId_v3:
        return TtsVoiceId_v3(voice_key=self.voice_key, service=self.service)

    # languages that this voide provides
    def get_languages(self) -> List[languages.Language]:
        return list(set(audio_language.lang for audio_language in self.audio_languages))

    @functools.cached_property
    def languages(self) -> List[languages.Language]:
        return self.get_languages()
    

    def __str__(self):
        return voice_str(self)

    def __repr__(self):
            return (f"TtsVoice_v3(name={self.name!r}, voice_key={self.voice_key!r}, options={self.options!r}, "
                    f"service={self.service!r}, gender={self.gender!r}, audio_languages={self.audio_languages!r}, "
                    f"service_fee={self.service_fee!r}, voice_id={self.voice_id!r})")

def serialize_voice_id_v3(voice_id: TtsVoiceId_v3) -> str:
    return databind.json.dump(voice_id, TtsVoiceId_v3)

def deserialize_voice_id_v3(voice_id: Union[str, Dict[str, Any]]) -> TtsVoiceId_v3:
    if isinstance(voice_id, TtsVoiceId_v3):
        return voice_id
    if isinstance(voice_id, str):
        try:
            import json
            parsed = json.loads(voice_id)
            if isinstance(parsed, dict) or isinstance(parsed, str):
                voice_id = parsed
        except Exception:
            logger.debug(f"Failed to parse voice_id: {voice_id}")
    if isinstance(voice_id, dict):
        vk = voice_id.get('voice_key')
        if isinstance(vk, dict):
            vkey = vk
        elif isinstance(vk, str):
            vkey = vk
        else:
            vkey = ""

        svc = voice_id.get('service')
        svc_str = str(svc) if svc is not None else ""

        return TtsVoiceId_v3(
            voice_key=vkey,
            service=svc_str
        )
    return databind.json.load(voice_id, TtsVoiceId_v3)

def build_voice_v3(name, gender, language, service, voice_key, options) -> TtsVoice_v3:
    return TtsVoice_v3(
        name=name,
        voice_key=voice_key,
        options=options,
        service=service.name,
        gender=gender,
        audio_languages=[language],
        service_fee=service.service_fee
    )


def voice_str(voice: TtsVoice_v3, lang: str = "en") -> str:
    if len(voice.audio_languages) == 1:
        language_str = voice.audio_languages[0].audio_lang_name
    else:
        language_str = i18n.get_text("voice_multilingual", lang)

    gender_key = f"voice_gender_{voice.gender.name.lower()}"
    gender_str = i18n.get_text(gender_key, lang)
    
    return f"{language_str}, {gender_str}, {voice.name} ({voice.service})"

def generate_voice_with_options_str(voice: TtsVoice_v3, options, lang: str = "en") -> str:
    result = ''

    result += f"{voice_str(voice, lang)}"

    options_array = []
    for key, value in options.items():
        if value != voice.options[key]['default']:
            options_array.append(f'{key}: {value}')
    if len(options_array) > 0:
        result += ' (' + ', '.join(options_array) + ')'

    return result

def get_audio_language_for_voice(voice: TtsVoice_v3) -> languages.AudioLanguage:
    if len(voice.audio_languages) == 1:
        return voice.audio_languages[0]
    # otherwise, we are dealing with a multilingual voice. default to en_US for now
    return languages.AudioLanguage.en_US
