import importlib.resources
import json

from misaki.en import data
from misaki.en._lexicon import _validate_lexicon_resource
from misaki.en_phonemes import GB, US_V2


def test_bundled_lexicon_resources():
    for dialect, vocab in (("us", US_V2), ("gb", GB)):
        for tier in ("gold", "silver"):
            name = f"{dialect}_{tier}.json"
            with (importlib.resources.files(data) / name).open(
                "r", encoding="utf-8"
            ) as resource:
                dictionary = json.load(resource)
            _validate_lexicon_resource(dictionary, name, vocab)
