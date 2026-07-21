import importlib.resources
import os
import re

from jamo import h2j


def parse_table():
    """Parse the main rule table."""
    with (importlib.resources.files(__package__) / "table.csv").open(
        "r", encoding="utf-8"
    ) as resource:
        lines = resource.read().splitlines()

    onsets = lines[0].split(",")
    table = []
    for line in lines[1:]:
        cols = line.split(",")
        coda = cols[0]
        for i, onset in enumerate(onsets):
            cell = cols[i]
            if not cell or i == 0:
                continue
            str1 = f"{coda}{onset}"
            if "(" in cell:
                str2 = cell.split("(")[0]
                rule_ids = cell.split("(")[1][:-1].split("/")
            else:
                str2 = cell
                rule_ids = []
            table.append((str1, str2, rule_ids))
    return table


def annotate(string, mecab):
    """Attach POS tags to the given string using Mecab."""
    if os.name == "nt":
        parse = mecab.parse(string).split("\n")
        tokens = []
        for p in parse[:-2]:
            p1, p2 = p.split("\t")
            p2 = p2.split(",")[0]
            tokens.append((p1, p2))
    elif os.name == "posix":
        tokens = mecab.pos(string)

    if re.sub(r"[ \n]", "", string) != "".join(token for token, _ in tokens):
        return string
    blanks = [(i, char) for i, char in enumerate(string) if char in (" ", "\n")]

    tag_seq = []
    for token, tag in tokens:
        tag = tag.split("+")[-1]
        if tag == "NNBC" or token == "곳":
            tag = "B"
        else:
            tag = tag[0]
        tag_seq.append("_" * (len(token) - 1) + tag)
    tag_seq = "".join(tag_seq)

    for i, char in blanks:
        tag_seq = tag_seq[:i] + char + tag_seq[i:]

    annotated = ""
    for char, tag in zip(string, tag_seq):
        annotated += char
        if char == "의" and tag == "J":
            annotated += "/J"
        elif tag == "E":
            if h2j(char)[-1] in "ᆯ":
                annotated += "/E"
        elif tag == "V":
            if h2j(char)[-1] in "ᆫᆬᆷᆱᆰᆲᆴ":
                annotated += "/P"
        elif tag == "B":
            annotated += "/B"

    return annotated
