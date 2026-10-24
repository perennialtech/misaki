"""Regression coverage for output-preserving multilingual fast paths."""

import random

import pytest

from misaki.multilingual import MultilingualG2P, normalize_multilingual_punctuation


def _legacy_route(router, text):
    """Reference implementation: examine each character in order."""
    text = normalize_multilingual_punctuation(text)
    spans = []
    english_start = position = 0
    while position < len(text):
        candidate = router._candidate_at(text, position)
        if candidate is None:
            position += 1
            continue
        end, _, language = candidate
        if english_start < position:
            spans.append(("en", text[english_start:position]))
        spans.append(
            (
                router.default_han_language if language == "han" else language,
                text[position:end],
            )
        )
        english_start = position = end
    if english_start < len(text):
        spans.append(("en", text[english_start:]))
    return spans


@pytest.mark.parametrize("default", ["zh", "ja"])
def test_router_matches_character_by_character_reference(default):
    router = object.__new__(MultilingualG2P)
    router.default_han_language = default
    inputs = [
        "",
        "Plain English 2026, 3.5hr!",
        "Déjà vu: café naïve.",
        "Hello 世界 今日もいい天気ですね。",
        "2026년 이후",
        "𠀋",
        "ひらがな 한글 漢字",
        "👩‍👩‍👧‍👦 💻",
        "ಕನ್ನಡ १२३４५",
        "１２３カナ",
        "々〆ヶー・ヽヾゝゞ",
        "Hello " * 1000 + "세계!",
        "こん にちは Hello ٥٥ 😂 한국어",
    ]
    rng = random.Random(841)
    characters = (
        "abc.,!? 09\n你好世界漢字あかなカタカナ한국어한글𠀋々〆ヶー・ヽヾゝゞ०１２３👩é"
    )
    inputs.extend(
        "".join(rng.choices(characters, k=rng.randrange(0, 110))) for _ in range(3000)
    )
    for text in inputs:
        assert router._route_spans(text) == _legacy_route(router, text), repr(text)


@pytest.mark.parametrize("punctuation", list(".,!?:;—…()“”"))
@pytest.mark.parametrize("before,after", [("", ""), (" \t", "\n ")])
def test_standalone_punctuation_does_not_invoke_english_model(
    punctuation, before, after
):
    router = object.__new__(MultilingualG2P)
    router.en = lambda _: pytest.fail("The English neural pipeline should not run")
    text = before + punctuation + after
    assert router._english(text) == text


@pytest.mark.parametrize(
    "text", ["-", "'", '"', "!?", "……", ".……", "...", "a", "  a  "]
)
def test_other_english_spans_still_run_english_g2p(text):
    router = object.__new__(MultilingualG2P)
    requests = []

    def phonemize(source):
        requests.append(source)
        return "PHONEMES", None

    router.en = phonemize
    assert (
        router._english(text)
        == text[: len(text) - len(text.lstrip())]
        + "PHONEMES"
        + text[len(text.rstrip()) :]
    )
    assert requests == [text.strip()]


def test_whitespace_only_spans_do_not_invoke_english_g2p():
    router = object.__new__(MultilingualG2P)
    router.en = lambda _: pytest.fail("Whitespace does not need G2P")
    assert router._english("  \n\t  ") == "  \n\t  "
