import importlib.resources
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
            pattern = f"{coda}{onset}"
            replacement = cell.split("(", 1)[0]
            table.append((pattern, replacement))
    return table


def annotate(string, mecab):
    """Attach POS tags to the given string using Mecab."""
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
