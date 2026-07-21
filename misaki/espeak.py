import re

import espeakng_loader
import phonemizer
from phonemizer.backend.espeak.wrapper import EspeakWrapper

from .en_phonemes import english_from_espeak
from .token import G2PResult, PronunciationResult


def _configure_espeak():
    # Set espeak-ng library path and espeak-ng-data
    EspeakWrapper.set_library(espeakng_loader.get_library_path())
    # Change data_path as needed when editing espeak-ng phonemes
    EspeakWrapper.set_data_path(espeakng_loader.get_data_path())


# EspeakFallback is used as a last resort for English
class EspeakFallback:
    def __init__(self, british):
        _configure_espeak()
        self.british = british
        self.backend = phonemizer.backend.EspeakBackend(
            language=f"en-{'gb' if british else 'us'}",
            preserve_punctuation=True,
            with_stress=True,
            tie="^",
        )

    def __call__(self, token) -> PronunciationResult:
        ps = self.backend.phonemize([token.text])
        if not ps:
            return None, None
        ps = ps[0].strip()
        ps = english_from_espeak(ps, self.british)
        return ps, 2


# EspeakG2P used for most non-English/CJK languages
class EspeakG2P:
    def __init__(self, language, version=None):
        _configure_espeak()
        self.language = language
        self.version = version
        self.backend = phonemizer.backend.EspeakBackend(
            language=language,
            preserve_punctuation=True,
            with_stress=True,
            tie="^",
            language_switch="remove-flags",
        )
        self.e2m = {
            "a^ɪ": "I",
            "a^ʊ": "W",
            "d^z": "ʣ",
            "d^ʒ": "ʤ",
            "e^ɪ": "A",
            "o^ʊ": "O",
            "ə^ʊ": "Q",
            "s^s": "S",
            "t^s": "ʦ",
            "t^ʃ": "ʧ",
            "ɔ^ɪ": "Y",
        }
        if version == "2.0":
            self.e2m.update(
                {
                    "œ̃": "B",
                    "ɔ̃": "C",
                    "ɑ̃": "D",
                    "ɛ̃": "E",
                    "ʊ̃": "V",
                    "ũ": "U",
                    "õ": "X",
                    "ɐ̃": "Z",
                }
            )
        self.e2m = sorted(self.e2m.items())

    def __call__(self, text) -> G2PResult:
        # Angles to curly quotes
        text = text.replace("«", chr(8220)).replace("»", chr(8221))
        # Parentheses to angles
        text = text.replace("(", "«").replace(")", "»")
        ps = self.backend.phonemize([text])
        if not ps:
            return "", None
        ps = ps[0].strip()
        for old, new in self.e2m:
            ps = ps.replace(old, new)
        # Delete any remaining tie characters, hyphens (not sure what they mean)
        ps = ps.replace("^", "")
        if self.version == "2.0":
            ps = ps.replace(chr(809), "").replace(chr(810), "")
            ps = re.sub(r"(\S)\u0329", r"ᵊ\1", ps)
        else:
            ps = ps.replace("-", "")
        # Angles back to parentheses
        ps = ps.replace("«", "(").replace("»", ")")
        return ps, None
