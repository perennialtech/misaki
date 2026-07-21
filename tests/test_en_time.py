import pytest

from misaki import en
from misaki.en._lexicon import Lexicon, apply_stress
from misaki.en._tokenization import retokenize
from misaki.token import MToken


class _UnexpectedFallback:
    def __call__(self, token):
        raise AssertionError(f"Unexpected fallback for {token.text!r}")


@pytest.fixture(scope="module")
def lexicon():
    return Lexicon(british=False)


@pytest.fixture(scope="module")
def g2p():
    return en.G2P(british=False, fallback=_UnexpectedFallback())


def spoken(lexicon, *words):
    return " ".join(lexicon.lookup(word, None, None, None)[0] for word in words)


def plural(lexicon, unit):
    return lexicon.stem_s(unit + "s", None, None, None)[0]


def test_clock_times(lexicon):
    assert lexicon.get_time("2:30") == (spoken(lexicon, "two", "thirty"), 4)
    assert lexicon.get_time("14:45") == (
        spoken(lexicon, "fourteen", "forty", "five"),
        4,
    )

    oh = apply_stress(
        lexicon.lookup("O", None, None, None)[0],
        -2,
    )
    assert lexicon.get_time("2:05") == (
        f"{spoken(lexicon, 'two')} {oh} {spoken(lexicon, 'five')}",
        4,
    )
    assert lexicon.get_time("2:00") == (
        spoken(lexicon, "two", "o'clock"),
        4,
    )
    assert lexicon.get_time("14:00") == (
        spoken(lexicon, "fourteen", "hundred"),
        4,
    )
    assert lexicon.get_time("00:00") == (
        spoken(lexicon, "zero", "hundred"),
        4,
    )


def test_clock_meridiems(lexicon):
    pm = lexicon.get_NNP("pm")[0]
    am = lexicon.get_NNP("am")[0]
    oh = apply_stress(
        lexicon.lookup("O", None, None, None)[0],
        -2,
    )

    assert lexicon.get_time("2:30pm") == (
        f"{spoken(lexicon, 'two', 'thirty')} {pm}",
        3,
    )
    assert lexicon.get_time("2:00PM") == (
        f"{spoken(lexicon, 'two')} {pm}",
        3,
    )
    assert lexicon.get_time("2am") == (
        f"{spoken(lexicon, 'two')} {am}",
        3,
    )
    assert lexicon.get_time("2:30:15pm") == (
        f"{spoken(lexicon, 'two', 'thirty', 'fifteen')} {pm}",
        3,
    )
    assert lexicon.get_time("2:00:05am") == (
        f"{spoken(lexicon, 'two')} {oh} {oh} {oh} {spoken(lexicon, 'five')} {am}",
        3,
    )


@pytest.mark.parametrize(
    "word",
    [
        "2",
        "45:99",
        "2:5",
        "2:60",
        "24:00",
        "0am",
        "00:30pm",
        "13pm",
        "14:45PM",
        "23:30am",
        "14:30:15pm",
    ],
)
def test_time_rejections(lexicon, word):
    assert lexicon.get_time(word) == (None, None)


@pytest.mark.parametrize("word", ["0:00:00", "1:00:30", "2:30:15", "23:59:59"])
def test_ambiguous_hms_forms_are_not_normalized(lexicon, word):
    assert lexicon.get_time(word) == (None, None)


def test_unambiguous_hms_durations(lexicon):
    assert lexicon.get_time("24:30:15") == (
        " ".join(
            [
                spoken(lexicon, "twenty", "four"),
                plural(lexicon, "hour"),
                spoken(lexicon, "thirty"),
                plural(lexicon, "minute"),
                spoken(lexicon, "and", "fifteen"),
                plural(lexicon, "second"),
            ]
        ),
        4,
    )
    assert lexicon.get_time("25:00:30") == (
        " ".join(
            [
                spoken(lexicon, "twenty", "five"),
                plural(lexicon, "hour"),
                spoken(lexicon, "and", "thirty"),
                plural(lexicon, "second"),
            ]
        ),
        4,
    )
    assert lexicon.get_time("24:00:00") == (
        " ".join(
            [
                spoken(lexicon, "twenty", "four"),
                plural(lexicon, "hour"),
            ]
        ),
        4,
    )


def test_attached_duration_units(lexicon):
    hours = plural(lexicon, "hour")
    minutes = plural(lexicon, "minute")
    seconds = plural(lexicon, "second")

    assert lexicon.get_number("2h", None, True, "") == (
        f"{spoken(lexicon, 'two')} {hours}",
        4,
    )
    assert lexicon.get_number("1h", None, True, "") == (
        spoken(lexicon, "one", "hour"),
        4,
    )

    point = apply_stress(
        lexicon.lookup("point", None, None, None)[0],
        -2,
    )
    assert lexicon.get_number("1.5h", None, True, "") == (
        f"{spoken(lexicon, 'one')} {point} {spoken(lexicon, 'five')} {hours}",
        4,
    )

    assert lexicon.get_number("2hrs", None, True, "") == (
        f"{spoken(lexicon, 'two')} {hours}",
        4,
    )
    assert lexicon.get_number("2hr", None, True, "") == (
        f"{spoken(lexicon, 'two')} {hours}",
        4,
    )
    assert lexicon.get_number("3min", None, True, "") == (
        f"{spoken(lexicon, 'three')} {minutes}",
        4,
    )
    assert lexicon.get_number("1min", None, True, "") == (
        spoken(lexicon, "one", "minute"),
        4,
    )
    assert lexicon.get_number("45sec", None, True, "") == (
        f"{spoken(lexicon, 'forty', 'five')} {seconds}",
        4,
    )
    assert lexicon.get_number("10secs", None, True, "") == (
        f"{spoken(lexicon, 'ten')} {seconds}",
        4,
    )
    assert lexicon.get_number("2000h", None, True, "") == (
        f"{spoken(lexicon, 'two', 'thousand')} {hours}",
        4,
    )
    assert lexicon.get_number("1,000h", None, True, "") == (
        f"{spoken(lexicon, 'one', 'thousand')} {hours}",
        4,
    )
    assert lexicon.get_number("-1h", None, True, "") == (
        spoken(lexicon, "minus", "one", "hour"),
        4,
    )
    assert lexicon.get_number("-2h", None, True, "") == (
        f"{spoken(lexicon, 'minus', 'two')} {hours}",
        4,
    )

    for malformed in ("1,h", "1,,2h", "12,34h", "1,2,3h", "2.3.4h"):
        assert lexicon.get_number(malformed, None, True, "") == (None, None)

    assert Lexicon.is_number("2h", True) is True
    assert Lexicon.is_number("2:30", True) is False


@pytest.mark.parametrize(
    ("number", "unit"),
    [
        ("2", "h"),
        ("1", "h"),
        ("-2", "hrs"),
        ("1,000", "min"),
    ],
)
def test_retokenize_spaced_units(number, unit):
    groups = retokenize(
        [
            MToken(number, "CD", " "),
            MToken(unit, "NN", ""),
        ]
    )

    assert len(groups) == 1
    assert "".join(token.text for token in groups[0]) == number + unit
    assert groups[0][-1].features.is_head is False
    assert all(token.features.alias is None for token in groups[0])


def test_retokenize_preserves_numeric_text_tagged_as_punctuation():
    groups = retokenize(
        [
            MToken("-2", "NFP", " "),
            MToken("h", "NN", ""),
        ]
    )

    assert len(groups) == 1
    assert "".join(token.text for token in groups[0]) == "-2h"
    assert groups[0][-1].features.is_head is False
    assert all(token.phonemes is None for token in groups[0])


@pytest.mark.parametrize("time", ["2:30", "2", "2:30:15"])
def test_retokenize_spaced_meridiems(time):
    groups = retokenize(
        [
            MToken(time, "CD", " "),
            MToken("pm", "NN", ""),
        ]
    )

    assert len(groups) == 1
    assert "".join(token.text for token in groups[0]) == time + "pm"
    assert groups[0][-1].features.is_head is False
    assert all(token.features.alias is None for token in groups[0])


@pytest.mark.parametrize(
    "token",
    [
        MToken("h", "NN", ""),
        MToken("pm", "NN", ""),
    ],
)
def test_retokenize_does_not_alias_without_time_context(token):
    groups = retokenize(
        [
            MToken("The", "DT", " "),
            token,
        ]
    )

    assert groups[-1][0].features.alias is None


@pytest.mark.parametrize("text", ["2h", "2am"])
def test_retokenize_leaves_attached_forms_merged(text):
    groups = retokenize([MToken(text, "CD", "")])

    assert len(groups) == 1
    assert len(groups[0]) > 1
    assert all(token.features.alias is None for token in groups[0])


@pytest.mark.parametrize("number", ["1,", "1,,2", "12,34", "1,2,3"])
def test_retokenize_rejects_malformed_spaced_duration_numbers(number):
    groups = retokenize(
        [
            MToken(number, "CD", " "),
            MToken("h", "NN", ""),
        ]
    )

    assert all(
        "".join(token.text for token in group) != number + "h" for group in groups
    )


def test_retokenize_closes_split_group_at_trailing_whitespace():
    groups = retokenize(
        [
            MToken("2h", "CD", " "),
            MToken("later", "RB", ""),
        ]
    )

    assert ["".join(token.text for token in group) for group in groups] == [
        "2h",
        "later",
    ]


def test_end_to_end_time_equalities(g2p):
    assert g2p("2h")[0] == g2p("2 h")[0] == g2p("2 hours")[0]
    assert g2p("1h")[0] == g2p("1 hour")[0]
    assert g2p("-2h")[0] == g2p("-2 h")[0] == g2p("-2 hours")[0]
    assert g2p("-1h")[0] == g2p("-1 h")[0] == g2p("-1 hour")[0]
    assert g2p("1,000h")[0] == g2p("1,000 h")[0]
    assert g2p("2:30")[0] == g2p("two thirty")[0]
    assert g2p("2:30 pm")[0] == g2p("2:30pm")[0]
    assert g2p("2:30:15 pm")[0] == g2p("2:30:15pm")[0]
    assert g2p("2 am")[0] == g2p("2am")[0]
    assert g2p("3 min")[0] == g2p("3 minutes")[0]


@pytest.mark.parametrize("text", ["It's 2:30.", "It took 24:30:15."])
def test_end_to_end_times_do_not_fall_back(g2p, text):
    phonemes, _ = g2p(text)

    assert "❓" not in phonemes


def test_time_alias_guards(g2p):
    hours = g2p.lexicon.stem_s("hours", None, None, None)[0]
    am_letters = g2p.lexicon.get_NNP("am")[0]

    assert hours not in g2p("The h is silent.")[0]
    assert am_letters not in g2p("I am here.")[0]


def test_version_two_time_passthrough():
    phonemes, _ = en.G2P(version="2.0", fallback=None)("2:30")

    assert "❓" not in phonemes
