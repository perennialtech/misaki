from misaki import en
from misaki.en._lexicon import Lexicon


def test_currency_classification():
    assert Lexicon.is_currency("1.000") is True
    assert Lexicon.is_currency("1.23") is True
    assert Lexicon.is_currency("1.234") is False
    assert Lexicon.is_currency("1.2.3") is False
    assert Lexicon.is_currency("100") is True


def test_currency_pipeline():
    phonemes, _ = en.G2P(fallback=None)("$1.50")

    assert phonemes
    assert "dˈɑləɹ" in phonemes
    assert "sˈɛnts" in phonemes
