import pytest

from misaki.en._lexicon import Lexicon, apply_stress


@pytest.fixture(scope="module")
def lexicon():
    return Lexicon(british=False)


def spoken(lexicon, *words):
    return " ".join(lexicon.lookup(word, None, None, None)[0] for word in words)


def test_number_reading_strategies(lexicon):
    assert lexicon.get_number("2000", None, True, "")[0] == spoken(
        lexicon, "two", "thousand"
    )
    assert lexicon.get_number("1st", None, True, "")[0] == spoken(lexicon, "first")
    assert lexicon.get_number("-5", None, True, "")[0] == spoken(
        lexicon, "minus", "five"
    )

    point = apply_stress(
        lexicon.lookup("point", None, None, None)[0],
        -2,
    )
    assert point in lexicon.get_number("3.5", None, True, "")[0]


def test_number_suffixes(lexicon):
    five = spoken(lexicon, "five")
    assert lexicon.get_number("5s", None, True, "")[0] == lexicon._s(five)
    assert lexicon.get_number("5ed", None, True, "")[0] == lexicon._ed(five)
    assert lexicon.get_number("5ing", None, True, "")[0] == lexicon._ing(five)


def test_non_head_number_reads_digits(lexicon):
    assert lexicon.get_number("0123", None, False, "")[0] == spoken(
        lexicon, "zero", "one", "two", "three"
    )


def test_number_flags(lexicon):
    with_a = lexicon.get_number("100", None, True, "a")[0]
    without_a = lexicon.get_number("100", None, True, "")[0]

    assert with_a.startswith("ə ")
    assert without_a.startswith(spoken(lexicon, "one"))
