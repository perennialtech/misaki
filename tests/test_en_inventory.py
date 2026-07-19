from misaki.en_phonemes import (ENGLISH_OUTPUT_PUNCTUATION, ENGLISH_UNION, GB,
                                GB_ONLY, SHARED_ENGLISH_OUTPUT,
                                US_DEFAULT_OR_LEGACY,
                                US_DEFAULT_OR_LEGACY_ONLY, US_V2, US_V2_ONLY,
                                english_from_espeak, finalize_english_phonemes)


def test_inventory_counts():
    assert len(SHARED_ENGLISH_OUTPUT) == 42
    assert len(US_DEFAULT_OR_LEGACY) == 46
    assert len(US_V2) == 47
    assert len(GB) == 46
    assert len(ENGLISH_UNION) == 52


def test_english_output_punctuation():
    assert ENGLISH_OUTPUT_PUNCTUATION == frozenset(';:,.!?—…"“”()')


def test_inventory_differences():
    assert US_DEFAULT_OR_LEGACY - SHARED_ENGLISH_OUTPUT == US_DEFAULT_OR_LEGACY_ONLY
    assert US_V2 - SHARED_ENGLISH_OUTPUT == US_V2_ONLY
    assert GB - SHARED_ENGLISH_OUTPUT == GB_ONLY


def test_shared_contains_weak_a():
    assert "ɐ" in SHARED_ENGLISH_OUTPUT
    assert "ɐ" in US_V2
    assert "ɐ" in GB


def test_finalize_english_phonemes():
    assert finalize_english_phonemes("ɾʔ", None) == "Tt"
    assert finalize_english_phonemes("ɾʔ", "2.0") == "ɾʔ"
    assert finalize_english_phonemes("hello! ɾʔ world", None) == "hello! Tt world"
    assert finalize_english_phonemes("hello! ɾʔ world", "2.0") == "hello! ɾʔ world"


def test_english_from_espeak():
    espeak_ps = "mˈɜːt^ʃəntʃˌɪp"
    assert english_from_espeak(espeak_ps, british=False) == "mˈɜɹʧəntʃˌɪp"
    assert english_from_espeak(espeak_ps, british=True) == "mˈɜːʧəntʃˌɪp"

    # Representative merged diphthong and affricate mappings
    assert english_from_espeak("e^ɪ", british=False) == "A"
    assert english_from_espeak("a^ɪ", british=False) == "I"
    assert english_from_espeak("t^ʃ", british=False) == "ʧ"

    # eSpeak ɐ maps to Misaki ə
    assert english_from_espeak("ɐ", british=False) == "ə"

    # Tie characters absent from result
    assert english_from_espeak("a^ɪ^b", british=False) == "Ib"
