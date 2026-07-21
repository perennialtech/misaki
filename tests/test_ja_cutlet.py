import re

from misaki.ja import JAG2P
from misaki.ja.cutlet import HEPBURN, Cutlet, Katakana_Phonetic_Extensions
from misaki.ja.num2kana import Convert


def test_hepburn_table_invariants():
    kana_keys = {
        key
        for key in HEPBURN
        if all(
            12353 <= ord(char) <= 12438 or 12535 <= ord(char) <= 12538 for char in key
        )
    }
    assert len(kana_keys) == 164
    assert all(
        codepoint in {12387, 12435} or chr(codepoint) in HEPBURN
        for codepoint in range(12353, 12439)
    )
    assert all(chr(codepoint) in HEPBURN for codepoint in range(12535, 12539))

    for key in kana_keys:
        if len(key) == 2:
            assert key[0] in HEPBURN
            assert key[1] in HEPBURN

    assert set(Katakana_Phonetic_Extensions) == {
        chr(codepoint) for codepoint in range(12784, 12800)
    }
    for small, full_size in Katakana_Phonetic_Extensions.items():
        assert len(small) == len(full_size) == 1
        assert 12784 <= ord(small) < 12800
        assert full_size in "クシストヌハヒフヘホムラリルレロ"


def test_long_number_is_spelled_in_japanese():
    result = Convert("12345678901")

    assert "Number" not in result
    assert not re.search(r"[A-Za-z]", result)


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
