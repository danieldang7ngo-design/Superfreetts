import json

from . import config_models
from . import constants
from . import errors
from . import i18n
from . import text_utils


def get_field_values(note):
    return {field_name: note[field_name] for field_name in list(note.keys())}


def expand_simple_template(note, source_template):
    try:
        return source_template.format_map(get_field_values(note))
    except Exception as e:
        raise errors.TemplateExpansionError(e)


def expand_advanced_template(note, source_template, ui_language):
    raise errors.SuperFreeTTSError(i18n.get_text("error_advanced_template_lite", ui_language))


def get_source_text(note, batch_source, text_override, ui_language="en"):
    if text_override is not None:
        return text_override

    if batch_source.mode == constants.BatchMode.simple:
        if batch_source.source_field not in note:
            raise errors.SourceFieldNotFoundError(batch_source.source_field)
        return note[batch_source.source_field]
    if batch_source.mode == constants.BatchMode.template:
        return expand_simple_template(note, batch_source.source_template)
    if batch_source.mode == constants.BatchMode.advanced_template:
        return expand_advanced_template(note, batch_source.source_template, ui_language)
    raise errors.SourceTextEmpty()


def _coerce_text_processing_model(text_processing_model):
    if text_processing_model is None:
        return config_models.TextProcessing()
    return text_processing_model


def text_processing_cache_key(source_text, text_processing_model):
    text_processing_model = _coerce_text_processing_model(text_processing_model)
    serialized = None
    if text_processing_model is not None:
        serialized = text_processing_model.serialize()
    return json.dumps(
        {
            "source_text": source_text,
            "text_processing": serialized,
        },
        sort_keys=True,
        ensure_ascii=True,
        default=str,
    )


def process_text(source_text, text_processing_model):
    processed_text = text_utils.process_text(source_text, text_processing_model)
    if len(processed_text) == 0:
        raise errors.SourceTextEmpty()
    return processed_text

