import re

import pytest

from misaki.ja import JAG2P
from misaki.ja.cutlet import (HEPBURN, KATAKANA_PHONETIC_EXTENSIONS, SYMBOLS,
                              Cutlet)
from misaki.ja.num2kana import number_to_hiragana


def test_hepburn_table_invariants():
    assert len(HEPBURN) == 164
    assert all(
        all(
            ord(char) in range(12353, 12439) or ord(char) in range(12535, 12539)
            for char in key
        )
        for key in HEPBURN
    )
    assert set(SYMBOLS).isdisjoint(HEPBURN)
    assert all(
        codepoint in {12387, 12435} or chr(codepoint) in HEPBURN
        for codepoint in range(12353, 12439)
    )
    assert all(chr(codepoint) in HEPBURN for codepoint in range(12535, 12539))

    for key in HEPBURN:
        if len(key) == 2:
            assert key[0] in HEPBURN
            assert key[1] in HEPBURN

    assert set(KATAKANA_PHONETIC_EXTENSIONS) == {
        chr(codepoint) for codepoint in range(12784, 12800)
    }
    for small, full_size in KATAKANA_PHONETIC_EXTENSIONS.items():
        assert len(small) == len(full_size) == 1
        assert 12784 <= ord(small) < 12800
        assert full_size in "クシストヌハヒフヘホムラリルレロ"


def test_long_number_is_spelled_in_japanese():
    result = number_to_hiragana("12345678901")

    assert "Number" not in result
    assert not re.search(r"[A-Za-z]", result)


@pytest.mark.parametrize(
    ("digits", "expected"),
    [
        ("0", "ゼロ"),
        ("7", "なな"),
        ("13", "じゅうさん"),
        ("20", "にじゅう"),
        ("58", "ごじゅうはち"),
        ("100", "ひゃく"),
        ("305", "さんびゃくご"),
        ("999", "きゅうひゃくきゅうじゅうきゅう"),
        ("1000", "せん"),
        ("1999", "せんきゅうひゃくきゅうじゅうきゅう"),
        ("8000", "はっせん"),
        ("10000", "いちまん"),
        ("21000", "にまんいっせん"),
        ("007", "なな"),
        (
            "123456789",
            "いちおくにせんさんびゃくよんじゅうごまん"
            "ろくせんななひゃくはちじゅうきゅう",
        ),
        ("12345678901", "いちにさんよんごろくななはちきゅうゼロいち"),
    ],
)
def test_number_to_hiragana_regressions(digits, expected):
    assert number_to_hiragana(digits) == expected


def test_cutlet_long_number_has_no_digit_output():
    phonemes, tokens = Cutlet()("12345678901")

    assert phonemes
    assert not re.search(r"\d", phonemes)
    assert tokens is None


def test_cutlet_smoke():
    phonemes, tokens = Cutlet()("こんにちは。")

    assert phonemes
    assert phonemes.endswith(".")
    assert tokens is None


def test_jag2p_smoke():
    phonemes, tokens = JAG2P()("こんにちは。")

    assert phonemes
    assert tokens is None
