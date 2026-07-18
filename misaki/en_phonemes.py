SHARED_ENGLISH_OUTPUT = frozenset("AIWYbdfhijklmnpstuvwzðŋɑɔəɛɜɡɪɹʃʊʌʒʤʧˈˌθᵊɐ")

US_DEFAULT_OR_LEGACY_ONLY = frozenset("æOᵻT")
US_V2_ONLY = frozenset("æOᵻɾʔ")
GB_ONLY = frozenset("aQɒː")

US_DEFAULT_OR_LEGACY = SHARED_ENGLISH_OUTPUT | US_DEFAULT_OR_LEGACY_ONLY
US_V2 = SHARED_ENGLISH_OUTPUT | US_V2_ONLY
GB = SHARED_ENGLISH_OUTPUT | GB_ONLY
ENGLISH_UNION = SHARED_ENGLISH_OUTPUT | US_DEFAULT_OR_LEGACY_ONLY | US_V2_ONLY | GB_ONLY


def finalize_english_phonemes(ps, version):
    if version == "2.0":
        return ps
    return ps.replace("ɾ", "T").replace("ʔ", "t")
