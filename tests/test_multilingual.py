import subprocess
import sys
import tomllib
import unicodedata
from pathlib import Path

import pytest

import misaki
from misaki.en_phonemes import ENGLISH_OUTPUT_PUNCTUATION, US_DEFAULT_OR_LEGACY
from misaki.multilingual import (
    MultilingualG2P,
    normalize_multilingual_punctuation,
    project_japanese,
    project_korean,
    project_mandarin,
    validate_multilingual_output,
)


def _router(default):
    router = object.__new__(MultilingualG2P)
    router.default_han_language = default
    return router


@pytest.mark.parametrize(
    ("text", "default", "expected"),
    [
        ("hello世界", "zh", [("en", "hello"), ("zh", "世界")]),
        ("hello世界", "ja", [("en", "hello"), ("ja", "世界")]),
        ("世界かな", "zh", [("ja", "世界かな")]),
        ("かな世界", "zh", [("ja", "かな世界")]),
        ("한글世界", "zh", [("ko", "한글"), ("zh", "世界")]),
        ("한글世界", "ja", [("ko", "한글"), ("ja", "世界")]),
        ("2026年", "zh", [("zh", "2026年")]),
        ("2026年", "ja", [("ja", "2026年")]),
        ("2026년", "zh", [("ko", "2026년")]),
        ("2026년", "ja", [("ko", "2026년")]),
        ("2026かな", "zh", [("ja", "2026かな")]),
        ("2026かな", "ja", [("ja", "2026かな")]),
        ("2026", "zh", [("en", "2026")]),
        ("2026", "ja", [("en", "2026")]),
    ],
)
def test_routing(text, default, expected):
    assert _router(default)._route_spans(text) == expected


def test_punctuation_normalization():
    source = "、，。．！？：；«《「『【»》」』】（）～〜–"
    assert normalize_multilingual_punctuation(source) == ",,..!?:;“““““”””””()———"


def test_constructor_boundaries():
    with pytest.raises(TypeError):
        MultilingualG2P()
    for value in ("ko", "en", "anything", None):
        with pytest.raises(ValueError, match="exactly 'zh' or 'ja'"):
            MultilingualG2P(value)
    for marker in ("", None, 1):
        with pytest.raises(ValueError, match="nonempty string"):
            MultilingualG2P("zh", unk=marker)


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("kʲi", "ki"),
        ("kʲɨ", "kju"),
        ("ɲi", "ni"),
        ("ɾ", "T"),
        ("ʔkɑ", "kkɑ"),
        ("ʔʨi", "ʧʧi"),
        ("oː", "OO"),
        ("Oː", "OO"),
        ("ɕi", "ʃi"),
        ("ʣ", "dz"),
        ("«test»", "“tɛst”"),
    ],
)
def test_japanese_projection(source, expected):
    result = project_japanese(source)
    assert result == expected
    validate_multilingual_output(result)
    assert not set("ɾʔː") & set(result)


def test_japanese_projection_unknown_and_timing_boundaries():
    assert project_japanese("x") == "❓"
    assert project_japanese("ʔ") == "t"
    assert project_japanese("ː") == "❓"


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("한글", "hɑnɡʊl"),
        ("랄", "ɹɑl"),
        ("까따빠싸", "kkɑttɑppɑssɑ"),
        ("차카타파", "ʧhɑkhɑthɑphɑ"),
        ("시", "ʃi"),
        ("사", "sɑ"),
    ],
)
def test_korean_projection(source, expected):
    result = project_korean(source)
    assert result == expected
    validate_multilingual_output(result)


def test_composed_and_decomposed_korean_match():
    composed = "한글"
    decomposed = unicodedata.normalize("NFD", composed)
    assert project_korean(composed) == project_korean(decomposed) == "hɑnɡʊl"


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("ㄓ十4", "ʤɜɹ"),
        ("ㄗㄭ3", "dzᵊ"),
        ("ㄐㄩ1", "ʤu"),
        ("ㄩ1", "ju"),
        ("ㄑ月2", "ʧwɛ"),
        ("月2", "jwɛ"),
        ("ㄍ我2", "ɡwO"),
        ("a/R", "❓ ɹ"),
    ],
)
def test_mandarin_projection(source, expected):
    result = project_mandarin(source)
    assert result == expected
    validate_multilingual_output(result)
    assert not any(symbol in result for symbol in "012345ㄅㄓㄩ月我")


def test_validator_contract():
    validate_multilingual_output("həlˈO, “wˈɜɹld” (Tt) ❓")
    validate_multilingual_output("ɑUNKNOWNɑ", "UNKNOWN")
    with pytest.raises(ValueError, match="'x'"):
        validate_multilingual_output("ɑx")
    with pytest.raises(ValueError, match="'x'"):
        validate_multilingual_output("UNKNOWNx", "UNKNOWN")
    with pytest.raises(ValueError, match="'ɾ'"):
        validate_multilingual_output("ɾʔ")


def test_projection_outputs_use_only_the_final_contract():
    results = [
        project_japanese("kʲɨ ʔʨi oː"),
        project_korean("한글 시"),
        project_mandarin("ㄓ十4/ㄐㄩ1"),
    ]
    for result in results:
        index = 0
        while index < len(result):
            if result.startswith("❓", index):
                index += 1
                continue
            symbol = result[index]
            assert (
                symbol in US_DEFAULT_OR_LEGACY
                or symbol in ENGLISH_OUTPUT_PUNCTUATION
                or symbol.isspace()
            )
            index += 1


def test_kog2p_rejects_latin_before_backend():
    from misaki.ko import KOG2P

    class Backend:
        def __init__(self):
            self.calls = []

        def __call__(self, text):
            self.calls.append(text)
            return text

    backend = Backend()
    g2p = object.__new__(KOG2P)
    g2p.g2pk = backend

    with pytest.raises(
        ValueError,
        match="KOG2P accepts Korean text only.*MultilingualG2P",
    ):
        g2p("한국어 and English")
    assert backend.calls == []

    assert g2p("한글") == ("한글", None)
    assert backend.calls == ["한글"]


def test_public_facade_is_lazy():
    assert misaki.MultilingualG2P is MultilingualG2P

    code = """
import sys
import misaki
assert misaki.MultilingualG2P
for name in (
    "spacy",
    "misaki.en",
    "misaki.ja.cutlet",
    "misaki.ko",
    "misaki.zh.frontend",
    "cn2an",
):
    assert name not in sys.modules, name
"""
    subprocess.run([sys.executable, "-c", code], check=True)


def test_language_frontend_imports_are_lazy():
    code = """
import sys
import misaki.ja.cutlet
import misaki.zh.frontend
assert "misaki.zh.transcription" not in sys.modules
assert "ordered_set" not in sys.modules
"""
    subprocess.run([sys.executable, "-c", code], check=True)


def test_multilingual_integration():
    g2p = MultilingualG2P(default_han_language="zh", trf=False)
    samples = [
        "English.",
        "中文。",
        "日本語。",
        "한국어.",
        "English, 中文, 日本語, 한국어.",
    ]
    for sample in samples:
        phonemes, tokens = g2p(sample)
        assert phonemes
        assert tokens is None
        validate_multilingual_output(phonemes)

    mixed, _ = g2p("English，中文。日本語！한국어？")
    punctuation = [symbol for symbol in mixed if symbol in ",.!?"]
    assert punctuation == [",", ".", "!", "?"]

    japanese = MultilingualG2P(default_han_language="ja", trf=False)
    zh_phonemes, _ = g2p("世界")
    ja_phonemes, _ = japanese("世界")
    assert zh_phonemes
    assert ja_phonemes
    assert zh_phonemes != ja_phonemes
