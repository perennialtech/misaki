import pytest
import spacy

from misaki.en import G2P, Lexicon, TokenContext, merge_tokens
from misaki.token import MToken


def test_mtoken_rating_field():
    tk = MToken(text="hi", tag="UH", whitespace=" ")
    assert tk.rating is None
    tk_rated = MToken(text="hello", tag="UH", whitespace="", rating=4)
    assert tk_rated.rating == 4


def test_merge_tokens_ratings():
    tk1 = MToken("a", "DT", " ", rating=4, _=MToken.Underscore(is_head=True))
    tk2 = MToken("b", "NN", "", rating=3, _=MToken.Underscore(is_head=False))
    merged = merge_tokens([tk1, tk2])
    assert merged.rating == 3

    tk3 = MToken("c", "NN", "", rating=None, _=MToken.Underscore(is_head=False))
    merged_none = merge_tokens([tk1, tk3])
    assert merged_none.rating is None


def test_lexicon_special_cases():
    lexicon = Lexicon(british=False)
    ctx = TokenContext(future_vowel=False)

    ps_a, _ = lexicon.get_special_case("a", "DT", 0, ctx)
    assert ps_a == "ɐ"

    ps_an, _ = lexicon.get_special_case("an", "DT", 0, ctx)
    assert ps_an == "ɐn"

    ps_am, _ = lexicon.get_special_case("am", "VBP", 0, ctx)
    assert ps_am == "ɐm"


class FakeFallback:
    def __init__(self, ps_return="fAk", rating_return=1):
        self.ps_return = ps_return
        self.rating_return = rating_return
        self.called = False

    def __call__(self, token):
        self.called = True
        return self.ps_return, self.rating_return

    def __bool__(self):
        return False


def test_g2p_no_fallback():
    g2p = G2P(fallback=None, unk="UNK")
    ph, tks = g2p("asdfghjkl")
    assert "UNK" in ph
    assert tks[0].phonemes == "UNK"


def test_g2p_explicit_fallback():
    fb = FakeFallback(ps_return="fAk", rating_return=1)
    g2p = G2P(fallback=fb)
    ph, tks = g2p("asdfghjkl")
    assert fb.called
    assert "fAk" in ph
    assert tks[0].phonemes == "fAk"
    assert tks[0].rating == 1


def test_g2p_falsey_fallback():
    fb = FakeFallback(ps_return="fOls", rating_return=2)
    assert not fb
    g2p = G2P(fallback=fb)
    ph, tks = g2p("asdfghjkl")
    assert fb.called
    assert "fOls" in ph


def test_g2p_lexical_rating():
    g2p = G2P(fallback=None)
    _, tks = g2p("hello")
    # hello is in dictionary so it should have a rating of 4 (gold) or 3 (silver)
    assert tks[0].rating in (3, 4)


def test_g2p_finalization_with_fake_fallback():
    fb = FakeFallback("ɾʔ", rating_return=1)

    legacy_g2p = G2P(version=None, fallback=fb)
    ph_leg, tks_leg = legacy_g2p("asdfghjkl")
    assert "Tt" in ph_leg
    assert tks_leg[0].phonemes == "Tt"

    v2_g2p = G2P(version="2.0", fallback=fb)
    ph_v2, tks_v2 = v2_g2p("asdfghjkl")
    assert "ɾʔ" in ph_v2
    assert tks_v2[0].phonemes == "ɾʔ"


def test_spacy_model_missing_raises(monkeypatch):
    def fake_is_package(name):
        return False

    def fake_download(name):
        raise AssertionError("Should not download spacy models in __init__")

    monkeypatch.setattr(spacy.util, "is_package", fake_is_package)
    monkeypatch.setattr(spacy.cli, "download", fake_download)

    with pytest.raises(RuntimeError, match="must be installed before constructing G2P"):
        G2P(fallback=None)
