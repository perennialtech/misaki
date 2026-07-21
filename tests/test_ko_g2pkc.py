from jamo import h2j

from misaki.ko.g2pkc import G2p


def test_idiom_application():
    assert G2p()("mp3") == h2j("엠피쓰리")


def test_bound_noun_number_spelling():
    output = G2p()("3개")

    assert output.startswith(h2j("세"))
    assert h2j("세") in output


def test_preloaded_rules_are_instance_stable():
    first = G2p()
    second = G2p()

    assert first("한국어") == second("한국어")
    assert first("mp3") == second("mp3")
