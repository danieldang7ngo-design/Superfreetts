"""This module contains functions to list all available voices and a class to find the
correct voice based on their attributes."""

import json
import logging
import ssl
from typing import Any, List, Optional

import aiohttp
import certifi
from typing_extensions import Unpack

from .constants import SEC_MS_GEC_VERSION, VOICE_HEADERS, VOICE_LIST
from .drm import DRM
from .typing import Voice, VoicesManagerFind, VoicesManagerVoice

_SSL_CTX = ssl.create_default_context(cafile=certifi.where())

logger = logging.getLogger(__name__)


async def __list_voices(
    session: aiohttp.ClientSession, ssl_ctx: ssl.SSLContext, proxy: Optional[str]
) -> List[Voice]:
    """
    Private function that makes the request to the voice list URL and parses the
    JSON response. This function is used by list_voices() and makes it easier to
    handle client response errors related to clock skew.

    Args:
        session (aiohttp.ClientSession): The aiohttp session to use for the request.
        ssl_ctx (ssl.SSLContext): The SSL context to use for the request.
        proxy (Optional[str]): The proxy to use for the request.

    Returns:
        List[Voice]: A list of voices and their attributes.
    """
    async with session.get(
        f"{VOICE_LIST}&Sec-MS-GEC={DRM.generate_sec_ms_gec()}"
        f"&Sec-MS-GEC-Version={SEC_MS_GEC_VERSION}",
        headers=DRM.headers_with_muid(VOICE_HEADERS),
        proxy=proxy,
        ssl=ssl_ctx,
        raise_for_status=True,
    ) as url:
        data: List[Any] = json.loads(await url.text())

    for voice in data:
        if "VoiceTag" not in voice:
            voice["VoiceTag"] = {}

        if "ContentCategories" not in voice["VoiceTag"]:
            voice["VoiceTag"]["ContentCategories"] = []

        if "VoicePersonalities" not in voice["VoiceTag"]:
            voice["VoiceTag"]["VoicePersonalities"] = []

    return data


async def list_voices(
    *, connector: Optional[aiohttp.BaseConnector] = None, proxy: Optional[str] = None
) -> List[Voice]:
    """
    List all available voices and their attributes.

    This pulls data from the URL used by Microsoft Edge to return a list of
    all available voices.

    Args:
        connector (Optional[aiohttp.BaseConnector]): The connector to use for the request.
        proxy (Optional[str]): The proxy to use for the request.

    Returns:
        List[Voice]: A list of voices and their attributes.
    """
    async with aiohttp.ClientSession(connector=connector, trust_env=True) as session:
        try:
            data = await __list_voices(session, _SSL_CTX, proxy)
        except aiohttp.ClientResponseError as e:
            if e.status == 403:
                # 403 doubles as the clock-skew signal, so try the skew path
                # conditionally: retry only when the Date header proves
                # significant skew, otherwise re-raise the original error so
                # a real rejection is never masked by SkewAdjustmentError.
                if not DRM.adjust_skew_if_significant(e):
                    logger.error(
                        "EdgeTTS voice-list request failed: HTTP %s: %s (headers=%s)",
                        e.status,
                        e.message,
                        dict(e.headers) if e.headers else None,
                    )
                    raise
                logger.info(
                    "EdgeTTS clock skew adjusted to %.1fs; retrying voice list once",
                    DRM.clock_skew_seconds,
                )
                try:
                    data = await __list_voices(session, _SSL_CTX, proxy)
                except aiohttp.ClientResponseError as retry_e:
                    logger.error(
                        "EdgeTTS voice-list retry failed: HTTP %s: %s (headers=%s)",
                        retry_e.status,
                        retry_e.message,
                        dict(retry_e.headers) if retry_e.headers else None,
                    )
                    raise
            elif e.status is not None and 400 <= e.status < 500:
                # Other 4xx are real rejections, not clock-skew issues:
                # surface them with their real status.
                logger.error(
                    "EdgeTTS voice-list request failed: HTTP %s: %s (headers=%s)",
                    e.status,
                    e.message,
                    dict(e.headers) if e.headers else None,
                )
                raise
            else:
                DRM.handle_client_response_error(e)
                data = await __list_voices(session, _SSL_CTX, proxy)
    return data


class VoicesManager:
    """
    A class to find the correct voice based on their attributes.
    """

    def __init__(self) -> None:
        self.voices: List[VoicesManagerVoice] = []
        self.called_create: bool = False

    @classmethod
    async def create(
        cls, custom_voices: Optional[List[Voice]] = None
    ) -> "VoicesManager":
        """
        Creates a VoicesManager object and populates it with all available voices.
        """
        self = VoicesManager()
        voices = await list_voices() if custom_voices is None else custom_voices
        self.voices = [
            {**voice, "Language": voice["Locale"].split("-")[0]} for voice in voices
        ]
        self.called_create = True
        return self

    def find(self, **kwargs: Unpack[VoicesManagerFind]) -> List[VoicesManagerVoice]:
        """
        Finds all matching voices based on the provided attributes.
        """
        if not self.called_create:
            raise RuntimeError(
                "VoicesManager.find() called before VoicesManager.create()"
            )

        matching_voices = [
            voice for voice in self.voices if kwargs.items() <= voice.items()
        ]
        return matching_voices
