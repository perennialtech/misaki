SHARED_ENGLISH_OUTPUT = frozenset("AIWYbdfhijklmnpstuvwzðŋɑɔəɛɜɡɪɹʃʊʌʒʤʧˈˌθᵊɐ")
ENGLISH_OUTPUT_PUNCTUATION = frozenset(';:,.!?—…"“”()')

US_DEFAULT_OR_LEGACY_ONLY = frozenset("æOᵻT")
US_V2_ONLY = frozenset("æOᵻɾʔ")
GB_ONLY = frozenset("aQɒː")

US_DEFAULT_OR_LEGACY = SHARED_ENGLISH_OUTPUT | US_DEFAULT_OR_LEGACY_ONLY
US_V2 = SHARED_ENGLISH_OUTPUT | US_V2_ONLY
GB = SHARED_ENGLISH_OUTPUT | GB_ONLY
ENGLISH_UNION = SHARED_ENGLISH_OUTPUT | US_DEFAULT_OR_LEGACY_ONLY | US_V2_ONLY | GB_ONLY


import re


def finalize_english_phonemes(ps, version):
    if version == "2.0":
        return ps
    return ps.replace("ɾ", "T").replace("ʔ", "t")


_E2M_ENGLISH = sorted(
    {
        "ʔˌn\u0329": "ʔn",
        "ʔn\u0329": "ʔn",
        "a^ɪ": "I",
        "a^ʊ": "W",
        "d^ʒ": "ʤ",
        "e^ɪ": "A",
        "e": "A",
        "t^ʃ": "ʧ",
        "ɔ^ɪ": "Y",
        "ə^l": "ᵊl",
        "ʲo": "jo",
        "ʲə": "jə",
        "ʲ": "",
        "ɚ": "əɹ",
        "r": "ɹ",
        "x": "k",
        "ç": "k",
        "ɐ": "ə",
        "ɬ": "l",
        "\u0303": "",
    }.items(),
    key=lambda kv: -len(kv[0]),
)


def english_from_espeak(ps: str, british: bool) -> str:
    for old, new in _E2M_ENGLISH:
        ps = ps.replace(old, new)
    ps = re.sub(r"(\S)\u0329", r"ᵊ\1", ps).replace(chr(809), "")
    if british:
        ps = ps.replace("e^ə", "ɛː")
        ps = ps.replace("iə", "ɪə")
        ps = ps.replace("ə^ʊ", "Q")
    else:
        ps = ps.replace("o^ʊ", "O")
        ps = ps.replace("ɜːɹ", "ɜɹ")
        ps = ps.replace("ɜː", "ɜɹ")
        ps = ps.replace("ɪə", "iə")
        ps = ps.replace("ː", "")
    ps = ps.replace("o", "ɔ")
    return ps.replace("^", "")
