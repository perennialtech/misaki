import pytest

from misaki.en import G2P


class _UnexpectedFallback:
    def __call__(self, token):
        raise AssertionError(f"Unexpected fallback for {token.text!r}")


@pytest.fixture(scope="module")
def g2p_us():
    return G2P(british=False, fallback=_UnexpectedFallback())


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("o/o/o/", "ˈO slˈæʃ ˈO slˈæʃ ˈO slˈæʃ"),
        ("it could be hello/world", "ɪt kʊd bi həlˈO slˈæʃ wˈɜɹld"),
    ],
)
def test_us_compact_slash_regressions(g2p_us, text, expected):
    phonemes, _ = g2p_us(text)

    assert phonemes == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("/", "slˈæʃ"),
        ("hello / world", "həlˈO slˈæʃ wˈɜɹld"),
    ],
)
def test_us_standalone_and_spaced_slash_regressions(g2p_us, text, expected):
    phonemes, _ = g2p_us(text)

    assert phonemes == expected


@pytest.mark.parametrize("text", ["and/or", "1/2"])
def test_us_compound_slash_is_explicitly_spoken(g2p_us, text):
    phonemes, _ = g2p_us(text)

    assert phonemes.split().count("slˈæʃ") == 1
