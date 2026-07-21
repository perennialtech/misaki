import re
from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple, Union

import numpy as np
import regex
import spacy

from ..token import MToken, MTokenFeatures
from ._lexicon import CURRENCIES, PUNCTS, SPOKEN_SYMBOLS, is_digit

FeatureValue = Union[str, int, float]
PreprocessorResult = Tuple[str, List[str], Dict[int, FeatureValue]]
Preprocessor = Callable[[str], PreprocessorResult]

LINK_REGEX = re.compile(r"\[([^\]]+)\]\(([^\)]*)\)")
SUBTOKEN_REGEX = regex.compile(
    r"^['‘’]+|\p{Lu}(?=\p{Lu}\p{Ll})|(?:^-)?(?:\d?[,.]?\d)+|[-_]+|['‘’]{2,}|\p{L}*?(?:['‘’]\p{L})*?\p{Ll}(?=\p{Lu})|\p{L}+(?:['‘’]\p{L})*|[^-_\p{L}'‘’\d]|['‘’]+$"
)
SUBTOKEN_JUNKS = frozenset("',-._‘’")

PUNCT_TAGS = frozenset(
    [".", ",", "-LRB-", "-RRB-", "``", '""', "''", ":", "$", "#", "NFP"]
)
PUNCT_TAG_PHONEMES = {
    "-LRB-": "(",
    "-RRB-": ")",
    "``": chr(8220),
    '""': chr(8221),
    "''": chr(8221),
}


def subtokenize(word):
    return SUBTOKEN_REGEX.findall(word)


@dataclass
class _MutableTokenGroup:
    group: List[MToken]
    open: bool


def preprocess(text: str) -> PreprocessorResult:
    result = ""
    tokens = []
    features = {}
    last_end = 0
    text = text.lstrip()
    text = text.replace(chr(8216), "'").replace(chr(8217), "'")
    for m in LINK_REGEX.finditer(text):
        result += text[last_end : m.start()]
        tokens.extend(text[last_end : m.start()].split())
        f = m.group(2)
        if is_digit(f[1 if f[:1] in ("-", "+") else 0 :]):
            f = int(f)
        elif f in ("0.5", "+0.5"):
            f = 0.5
        elif f == "-0.5":
            f = -0.5
        elif len(f) > 1 and f[0] == "/" and f[-1] == "/":
            f = f[0] + f[1:].rstrip("/")
        elif len(f) > 1 and f[0] == "#" and f[-1] == "#":
            f = f[0] + f[1:].rstrip("#")
        else:
            f = None
        if f is not None:
            features[len(tokens)] = f
        result += m.group(1)
        tokens.append(m.group(1))
        last_end = m.end()
    if last_end < len(text):
        result += text[last_end:]
        tokens.extend(text[last_end:].split())
    return result, tokens, features


def tokenize(nlp, text: str, tokens, features) -> List[MToken]:
    doc = nlp(text)
    mutable_tokens = [
        MToken(
            text=tk.text,
            tag=tk.tag_,
            whitespace=tk.whitespace_,
        )
        for tk in doc
    ]
    if not features:
        return mutable_tokens
    align = spacy.training.Alignment.from_strings(
        tokens, [tk.text for tk in mutable_tokens]
    )
    for k, v in features.items():
        if not (
            isinstance(v, str)
            or (isinstance(v, int) and not isinstance(v, bool))
            or v in (0.5, -0.5)
        ):
            raise TypeError(
                f"Invalid feature value for token {k}: {v!r}. Must be a string, integer, 0.5, or -0.5."
            )
        for i, j in enumerate(np.where(align.y2x.data == k)[0]):
            if j >= len(mutable_tokens):
                continue
            if not isinstance(v, str):
                mutable_tokens[j].features.stress = v
            elif v.startswith("/"):
                mutable_tokens[j].features.is_head = i == 0
                mutable_tokens[j].phonemes = v.lstrip("/") if i == 0 else ""
                mutable_tokens[j].rating = 5
            elif v.startswith("#"):
                mutable_tokens[j].features.num_flags = v.lstrip("#")
    return mutable_tokens


def retokenize(tokens: List[MToken]) -> List[Tuple[MToken, ...]]:
    words = []
    currency = None
    for i, token in enumerate(tokens):
        if token.features.alias is None and token.phonemes is None:
            tks = [
                MToken(
                    text=t,
                    tag=token.tag,
                    whitespace="",
                    start_ts=token.start_ts,
                    end_ts=token.end_ts,
                    rating=token.rating,
                    features=MTokenFeatures(
                        is_head=True,
                        num_flags=token.features.num_flags,
                        stress=token.features.stress,
                    ),
                )
                for t in subtokenize(token.text)
            ]
        else:
            tks = [token]
        tks[-1].whitespace = token.whitespace
        for j, tk in enumerate(tks):
            if tk.features.alias is not None or tk.phonemes is not None:
                pass
            elif tk.tag == "$" and tk.text in CURRENCIES:
                currency = tk.text
                tk.phonemes = ""
                tk.rating = 4
            elif tk.tag == ":" and tk.text in ("-", "–"):
                tk.phonemes = "—"
                tk.rating = 3
            elif (
                tk.text not in SPOKEN_SYMBOLS
                and tk.tag in PUNCT_TAGS
                and not all(97 <= ord(c.lower()) <= 122 for c in tk.text)
            ):
                tk.phonemes = PUNCT_TAG_PHONEMES.get(
                    tk.tag, "".join(c for c in tk.text if c in PUNCTS)
                )
                tk.rating = 4
            elif currency is not None:
                if tk.tag != "CD":
                    currency = None
                elif j + 1 == len(tks) and (
                    i + 1 == len(tokens) or tokens[i + 1].tag != "CD"
                ):
                    tk.features.currency = currency
            elif (
                0 < j < len(tks) - 1
                and tk.text == "2"
                and (tks[j - 1].text[-1] + tks[j + 1].text[0]).isalpha()
            ):
                tk.features.alias = "to"

            if tk.features.alias is not None or tk.phonemes is not None:
                words.append(_MutableTokenGroup([tk], False))
            elif words and words[-1].open and not words[-1].group[-1].whitespace:
                tk.features.is_head = False
                words[-1].group.append(tk)
            else:
                words.append(_MutableTokenGroup([tk], not tk.whitespace))

    return [tuple(w.group) for w in words]
