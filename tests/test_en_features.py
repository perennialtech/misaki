import pytest
import spacy

from misaki import en
from misaki.en._g2p import merge_tokens
from misaki.en._lexicon import Lexicon, TokenContext, _validate_lexicon_resource
from misaki.en._tokenization import TokenGroup, retokenize
from misaki.token import MToken, MTokenFeatures


def test_public_facade():
    import misaki

    assert hasattr(misaki.en, "G2P")
    assert hasattr(misaki.en, "FallbackNetwork")


def test_mtoken_features_defaults():
    tk = MToken(text="test", tag="NN", whitespace="")
    assert isinstance(tk.features, MTokenFeatures)
    assert tk.features.is_head is True
    assert tk.features.alias is None
    assert tk.features.stress is None
    assert tk.features.currency is None
    assert tk.features.num_flags == ""
    assert tk.features.prespace is False


def test_mtoken_rating_field():
    tk = MToken(text="hi", tag="UH", whitespace=" ")
    assert tk.rating is None
    tk_rated = MToken(text="hello", tag="UH", whitespace="", rating=4)
    assert tk_rated.rating == 4


def test_merge_tokens_ratings():
    tk1 = MToken("a", "DT", " ", rating=4)  # Default is_head is True
    tk2 = MToken("b", "NN", "", rating=3, features=MTokenFeatures(is_head=False))
    merged = merge_tokens([tk1, tk2])
    assert merged.rating == 3

    tk3 = MToken("c", "NN", "", rating=None, features=MTokenFeatures(is_head=False))
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


def test_lexicon_validation_failures():
    # valid string
    _validate_lexicon_resource({"word": "æ"}, "test", frozenset(["æ"]))
    # valid dict
    _validate_lexicon_resource({"word": {"DEFAULT": "æ"}}, "test", frozenset(["æ"]))
    # None variant
    _validate_lexicon_resource(
        {"word": {"DEFAULT": "æ", "VB": None}}, "test", frozenset(["æ"])
    )

    with pytest.raises(ValueError, match="Must be str or dict"):
        _validate_lexicon_resource({"word": 123}, "test", frozenset(["æ"]))
    with pytest.raises(ValueError, match="Missing 'DEFAULT' in named variant"):
        _validate_lexicon_resource({"word": {"VB": "æ"}}, "test", frozenset(["æ"]))
    with pytest.raises(ValueError, match="Invalid symbol '❓' in plain pronunciation"):
        _validate_lexicon_resource({"word": "❓"}, "test", frozenset(["æ"]))
    with pytest.raises(ValueError, match="Invalid symbol '❓' in variant 'DEFAULT'"):
        _validate_lexicon_resource({"word": {"DEFAULT": "❓"}}, "test", frozenset(["æ"]))


def test_retokenize_groups():
    t1 = MToken("hello", "NN", " ")
    t2 = MToken("world", "NN", "")
    t3 = MToken(".", ".", "")

    out = retokenize([t1, t2])
    assert all(isinstance(g, TokenGroup) for g in out)
    assert len(out) == 2


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


def test_unsupported_version():
    with pytest.raises(ValueError, match="Unsupported output version"):
        en.G2P(version="2")
    with pytest.raises(ValueError, match="Unsupported output version"):
        en.G2P(version="legacy")


def test_g2p_no_fallback():
    g2p = en.G2P(fallback=None, unk="UNK")
    ph, tks = g2p("asdfghjkl")
    assert "UNK" in ph
    assert tks[0].phonemes == "UNK"


def test_g2p_explicit_fallback():
    fb = FakeFallback(ps_return="fAk", rating_return=1)
    g2p = en.G2P(fallback=fb)
    ph, tks = g2p("asdfghjkl")
    assert fb.called
    assert "fAk" in ph
    assert tks[0].phonemes == "fAk"
    assert tks[0].rating == 1


def test_g2p_falsey_fallback():
    fb = FakeFallback(ps_return="fOls", rating_return=2)
    assert not fb
    g2p = en.G2P(fallback=fb)
    ph, tks = g2p("asdfghjkl")
    assert fb.called
    assert "fOls" in ph


def test_g2p_lexical_rating():
    g2p = en.G2P(fallback=None)
    _, tks = g2p("hello")
    # hello is in dictionary so it should have a rating of 4 (gold) or 3 (silver)
    assert tks[0].rating in (3, 4)


def test_g2p_finalization_with_fake_fallback():
    fb = FakeFallback("ɾʔ", rating_return=1)

    legacy_g2p = en.G2P(version=None, fallback=fb)
    ph_leg, tks_leg = legacy_g2p("asdfghjkl")
    assert "Tt" in ph_leg
    assert tks_leg[0].phonemes == "Tt"

    v2_g2p = en.G2P(version="2.0", fallback=fb)
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
        en.G2P(fallback=None)


def test_e2e_regressions():
    g2p = en.G2P(fallback=None)

    # 1. Normal lexical word
    ph, _ = g2p("hello")
    assert ph == "həlˈO"

    # 2. Context-sensitive weak form
    ph, _ = g2p("to today")  # "to" before consonant
    assert "tə" in ph
    ph, _ = g2p("to apple")  # "to" before vowel
    assert "tʊ" in ph

    # 3. Explicit phoneme override
    ph, _ = g2p("this is a [override](/OˈvɹId/)")
    assert "OˈvɹId" in ph

    # 4. Unresolved word with no fallback
    ph, _ = g2p("xyzab")
    assert "❓" in ph

    # 5. Whole compound resolved through fallback
    class MockFallback:
        def __call__(self, text):
            return "mˈɑk", 1

    g2p_mock = en.G2P(fallback=MockFallback())
    ph, _ = g2p_mock("xyzab-def")  # compound unresolved
    assert "mˈɑk" in ph

    # 6. Punctuation and whitespace preservation
    ph, _ = g2p("hi, there!")
    assert ph == "hˈI, ðˈɛɹ!"
