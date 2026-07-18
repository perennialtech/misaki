from misaki.en_phonemes import (ENGLISH_UNION, GB, GB_ONLY,
                                SHARED_ENGLISH_OUTPUT, US_DEFAULT_OR_LEGACY,
                                US_DEFAULT_OR_LEGACY_ONLY, US_V2, US_V2_ONLY,
                                finalize_english_phonemes)


def test_inventory_counts():
    assert len(SHARED_ENGLISH_OUTPUT) == 42
    assert len(US_DEFAULT_OR_LEGACY) == 46
    assert len(US_V2) == 47
    assert len(GB) == 46
    assert len(ENGLISH_UNION) == 52


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
