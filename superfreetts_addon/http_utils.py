"""Small, shared HTTP helpers.

Every outbound request in the add-on should go through this module.  Having a
single default timeout prevents a dictionary site or model host from freezing
Anki forever, and the audio helper translates transport failures into the same
user-facing ``AudioNotFoundError`` used for a missing pronunciation.
"""

from __future__ import annotations

import requests

from . import errors
from . import logging_utils

logger = logging_utils.get_child_logger(__name__)

# (connect, read) seconds.  A page that cannot start within 5 seconds or send
# any data for 20 seconds is not useful for an interactive dictionary lookup.
DEFAULT_TIMEOUT = (5, 20)


def get(url: str, **kwargs) -> requests.Response:
    """Perform a GET with a timeout, defaulting to ``DEFAULT_TIMEOUT``."""
    kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
    # Timeout is injected immediately above and cannot be omitted here.
    return requests.get(url, **kwargs)  # nosec B113


def get_audio(url: str, source_text: str, voice, **kwargs) -> requests.Response:
    """GET an audio URL, converting network errors to ``AudioNotFoundError``.

    Dictionary services should use this for every request that is part of an
    audio lookup.  Keeping the conversion here avoids leaking
    ``requests.exceptions.*`` into the batch pipeline, where it would be
    reported as an internal error instead of a missing pronunciation.
    """
    try:
        return get(url, **kwargs)
    except requests.exceptions.RequestException as exc:
        logger.error("HTTP request failed for %r: %s", url, exc)
        raise errors.AudioNotFoundError(source_text, voice) from exc
