import importlib.resources
import re

from jamo import h2j

from misaki.ko import g2pkc
from misaki.ko.g2pkc import G2p
from misaki.ko.g2pkc.utils import parse_table


def test_rule_table_integrity():
    with (importlib.resources.files(g2pkc) / "table.csv").open(
        "r", encoding="utf-8"
    ) as resource:
        rows = [line.split(",") for line in resource.read().splitlines()]

    assert len(rows[0]) == 20
    assert all(len(row) == 20 for row in rows[1:])

    cell_pattern = re.compile(r"^[\u1100-\u11FF]+(?:\\1)?(?:\(\d+(?:/\d+)*\))?$")
    for row in rows[1:]:
        assert all(not cell or cell_pattern.fullmatch(cell) for cell in row[1:])

    table = parse_table()
    assert ("ᆹᄏ", "ᆸᄏ") in table
    assert ("ᆲᄑ", "ᆯᄑ") in table
    assert all(len(rule) == 2 for rule in table)


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


def test_optimized_table_matches_original_regex_evaluation():
    """Literal and compiled substitutions must preserve sequential rule effects."""
    import random

    g2p = G2p()
    rules = parse_table()
    assert len(rules) == len(g2p.table) == 409
    assert sum(isinstance(pattern, re.Pattern) for pattern, _ in g2p.table) == 20

    samples = [
        "",
        "한국어",
        "ᆩᄀ",
        "ᆹᄏ",
        "ᇂᄒ",
        "ᇂ!",
        "ᇂ ",
        "ᇂ",
        "ᆫᄅ",
        "ᆩᄋ",
        "ᆩ!",
        "ᇂᄃᆩᄆᆯᄅ",
        "ᆬ/Pᄀ",
        "ᆿ\n",
        "오늘 날씨가 좋습니다.",
    ]
    rng = random.Random(422)
    alphabet = "ᄒᄀᄁᄂᄃᄄᄅᄆᄇᄈᄉᄊᄌᄍᄎᄏᄐᄑᆨᆩᆪᆬᆭᆰᆱᆲᆳᆴᆵᆶᆹᆺᆻᆽᆾᆿᇀᇁᇂᆯᆷᅡᅵᅳ/P!? "
    samples.extend(
        "".join(rng.choices(alphabet, k=rng.randrange(0, 80))) for _ in range(500)
    )
    for sample in samples:
        old, new = sample, sample
        for pattern, replacement in rules:
            old = re.sub(pattern, replacement, old)
        for pattern, replacement in g2p.table:
            new = (
                new.replace(pattern, replacement)
                if isinstance(pattern, str)
                else pattern.sub(replacement, new)
            )
        assert new == old, repr(sample)


def test_korean_phonemizer_matches_legacy_table_outputs():
    """The rule-table fast path must not alter the complete Korean pipeline."""
    g2p = G2p()
    optimized = g2p.table
    g2p.table = [
        (re.compile(pattern), replacement) for pattern, replacement in parse_table()
    ]
    examples = [
        "한국어",
        "mp3",
        "3개",
        "안녕하세요 여러분",
        "오늘 날씨가 정말 좋습니다",
        "밟고 읽고 앉으세요",
        "값이 많이 올랐습니다",
        "사과를 먹고 학교에 갑니다",
        "한국어 발음은 어렵습니까",
        "버스가 3시 30분에 도착합니다",
    ]
    original = [g2p(text) for text in examples]
    g2p.table = optimized
    assert [g2p(text) for text in examples] == original
