import pytest

from misaki.zh.tone_sandhi import ToneSandhi


@pytest.fixture(scope="module")
def sandhi():
    return ToneSandhi()


def test_two_character_all_third_tone(sandhi):
    assert sandhi._three_sandhi("老虎", ["ao3", "u3"]) == ["ao2", "u3"]


def test_three_character_all_third_tone(sandhi):
    assert sandhi._three_sandhi("蒙古包", ["eng3", "u3", "ao3"]) == [
        "eng2",
        "u2",
        "ao3",
    ]


def test_four_character_third_tone_idiom(sandhi):
    assert sandhi._three_sandhi("哩哩啦啦", ["i3", "i3", "a3", "a3"]) == [
        "i2",
        "i3",
        "a2",
        "a3",
    ]


def test_mixed_three_character_tones(sandhi):
    assert sandhi._three_sandhi("所有人", ["uo3", "ou3", "en2"]) == [
        "uo2",
        "ou3",
        "en2",
    ]


def test_bu_and_yi_sandhi(sandhi):
    assert sandhi._bu_sandhi("不怕", ["u4", "a4"]) == ["u2", "a4"]
    assert sandhi._yi_sandhi("一天", ["i1", "ian1"]) == ["i4", "ian1"]
