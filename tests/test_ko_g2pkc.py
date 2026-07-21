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
