"""Guard the committed EdgeTTS worker default."""

import json
from pathlib import Path

from superfreetts_addon import batch_constants


ROOT = Path(__file__).resolve().parent.parent


def test_committed_edge_workers_do_not_exceed_source_cap():
    config = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    workers = config["configuration"]["service_config"]["EdgeTTS"]["concurrency_workers"]
    assert workers <= batch_constants.EDGETTS_MAX_WORKERS
