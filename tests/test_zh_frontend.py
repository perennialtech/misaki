from misaki.token import MToken
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
