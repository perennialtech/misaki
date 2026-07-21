import pytest

from misaki.token import MToken
from misaki.zh import ZHG2P
from misaki.zh.frontend import ZH_MAP, ZHFrontend


def test_zh_map_passthrough_symbols():
    assert ZH_MAP["a"] == "ㄚ"
    for symbol in ';:,.!?/—…"()“” 12345R':
        assert ZH_MAP[symbol] == symbol


def test_zh_frontend_smoke():
    phonemes, tokens = ZHFrontend()("你好.")

    assert isinstance(phonemes, str)
    assert phonemes
    assert phonemes.endswith(".")
    assert isinstance(tokens, list)
    assert tokens
    assert all(isinstance(token, MToken) for token in tokens)


def test_zhg2p_smoke():
    with pytest.warns(UserWarning):
        g2p = ZHG2P()

    phonemes, tokens = g2p("你好。")

    assert phonemes
    assert tokens is None


def test_zhg2p_interleaved_english():
    phonemes, tokens = ZHG2P(en_callable=lambda text: "EN")("你好 hello 世界。")

    assert "EN" in phonemes
    assert tokens is None

    with pytest.warns(UserWarning):
        g2p = ZHG2P(unk="UNKNOWN")
    phonemes, tokens = g2p("你好 hello 世界。")

    assert "UNKNOWN" in phonemes
    assert tokens is None
