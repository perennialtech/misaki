# ADAPTED from https://github.com/polm/cutlet/blob/main/cutlet/cutlet.py
# Original License: MIT
import importlib.resources
import re
import unicodedata
from dataclasses import dataclass
from typing import Tuple

import jaconv
import mojimoji
from fugashi import Tagger

from . import data
from .num2kana import number_to_hiragana

HEPBURN = {
    # Monographs
    "ぁ": "a",
    "あ": "a",
    "ぃ": "i",
    "い": "i",
    "ぅ": "ɯ",
    "う": "ɯ",
    "ぇ": "e",
    "え": "e",
    "ぉ": "o",
    "お": "o",
    "か": "ka",
    "が": "ɡa",
    "き": "kʲi",
    "ぎ": "ɡʲi",
    "く": "kɯ",
    "ぐ": "ɡɯ",
    "け": "ke",
    "げ": "ɡe",
    "こ": "ko",
    "ご": "ɡo",
    "さ": "sa",
    "ざ": "ʣa",
    "し": "ɕi",
    "じ": "ʥi",
    "す": "sɨ",
    "ず": "zɨ",
    "せ": "se",
    "ぜ": "ʣe",
    "そ": "so",
    "ぞ": "ʣo",
    "た": "ta",
    "だ": "da",
    "ち": "ʨi",
    "ぢ": "ʥi",
    "つ": "ʦɨ",
    "づ": "zɨ",
    "て": "te",
    "で": "de",
    "と": "to",
    "ど": "do",
    "な": "na",
    "に": "ɲi",
    "ぬ": "nɯ",
    "ね": "ne",
    "の": "no",
    "は": "ha",
    "ば": "ba",
    "ぱ": "pa",
    "ひ": "çi",
    "び": "bʲi",
    "ぴ": "pʲi",
    "ふ": "ɸɯ",
    "ぶ": "bɯ",
    "ぷ": "pɯ",
    "へ": "he",
    "べ": "be",
    "ぺ": "pe",
    "ほ": "ho",
    "ぼ": "bo",
    "ぽ": "po",
    "ま": "ma",
    "み": "mʲi",
    "む": "mɯ",
    "め": "me",
    "も": "mo",
    "ゃ": "ja",
    "や": "ja",
    "ゅ": "jɯ",
    "ゆ": "jɯ",
    "ょ": "jo",
    "よ": "jo",
    "ら": "ɾa",
    "り": "ɾʲi",
    "る": "ɾɯ",
    "れ": "ɾe",
    "ろ": "ɾo",
    "ゎ": "βa",
    "わ": "βa",
    "ゐ": "i",
    "ゑ": "e",
    "を": "o",
    "ゔ": "vɯ",
    "ゕ": "ka",
    "ゖ": "ke",
    "ヷ": "va",
    "ヸ": "vʲi",
    "ヹ": "ve",
    "ヺ": "vo",
    # Digraphs
    "いぇ": "je",
    "うぃ": "βi",
    "うぇ": "βe",
    "うぉ": "βo",
    "きぇ": "kʲe",
    "きゃ": "kʲa",
    "きゅ": "kʲɨ",
    "きょ": "kʲo",
    "ぎゃ": "ɡʲa",
    "ぎゅ": "ɡʲɨ",
    "ぎょ": "ɡʲo",
    "くぁ": "kᵝa",
    "くぃ": "kᵝi",
    "くぇ": "kᵝe",
    "くぉ": "kᵝo",
    "ぐぁ": "ɡᵝa",
    "ぐぃ": "ɡᵝi",
    "ぐぇ": "ɡᵝe",
    "ぐぉ": "ɡᵝo",
    "しぇ": "ɕe",
    "しゃ": "ɕa",
    "しゅ": "ɕɨ",
    "しょ": "ɕo",
    "じぇ": "ʥe",
    "じゃ": "ʥa",
    "じゅ": "ʥɨ",
    "じょ": "ʥo",
    "ちぇ": "ʨe",
    "ちゃ": "ʨa",
    "ちゅ": "ʨɨ",
    "ちょ": "ʨo",
    "ぢゃ": "ʥa",
    "ぢゅ": "ʥɨ",
    "ぢょ": "ʥo",
    "つぁ": "ʦa",
    "つぃ": "ʦʲi",
    "つぇ": "ʦe",
    "つぉ": "ʦo",
    "てぃ": "tʲi",
    "てゅ": "tʲɨ",
    "でぃ": "dʲi",
    "でゅ": "dʲɨ",
    "とぅ": "tɯ",
    "どぅ": "dɯ",
    "にぇ": "ɲe",
    "にゃ": "ɲa",
    "にゅ": "ɲɨ",
    "にょ": "ɲo",
    "ひぇ": "çe",
    "ひゃ": "ça",
    "ひゅ": "çɨ",
    "ひょ": "ço",
    "びゃ": "bʲa",
    "びゅ": "bʲɨ",
    "びょ": "bʲo",
    "ぴゃ": "pʲa",
    "ぴゅ": "pʲɨ",
    "ぴょ": "pʲo",
    "ふぁ": "ɸa",
    "ふぃ": "ɸʲi",
    "ふぇ": "ɸe",
    "ふぉ": "ɸo",
    "ふゅ": "ɸʲɨ",
    "ふょ": "ɸʲo",
    "みゃ": "mʲa",
    "みゅ": "mʲɨ",
    "みょ": "mʲo",
    "りゃ": "ɾʲa",
    "りゅ": "ɾʲɨ",
    "りょ": "ɾʲo",
    "ゔぁ": "va",
    "ゔぃ": "vʲi",
    "ゔぇ": "ve",
    "ゔぉ": "vo",
    "ゔゅ": "bʲɨ",
    "ゔょ": "bʲo",
    # Symbols
    "。": ".",
    "、": ",",
    "？": "?",
    "！": "!",
    "「": "“",
    "」": "”",
    "『": "“",
    "』": "”",
    "：": ":",
    "；": ";",
    "（": "(",
    "）": ")",
    "《": "(",
    "》": ")",
    "【": "[",
    "】": "]",
    "・": " ",
    "，": ",",
    "～": "—",
    "〜": "—",
    "—": "—",
    "«": "“",
    "»": "”",
    "゚": "",
    "゙": "",
}

KATAKANA_PHONETIC_EXTENSIONS = {
    "ㇰ": "ク",
    "ㇱ": "シ",
    "ㇲ": "ス",
    "ㇳ": "ト",
    "ㇴ": "ヌ",
    "ㇵ": "ハ",
    "ㇶ": "ヒ",
    "ㇷ": "フ",
    "ㇸ": "ヘ",
    "ㇹ": "ホ",
    "ㇺ": "ム",
    "ㇻ": "ラ",
    "ㇼ": "リ",
    "ㇽ": "ル",
    "ㇾ": "レ",
    "ㇿ": "ロ",
}

with (importlib.resources.files(data) / "ja_words.txt").open(
    "r", encoding="utf-8"
) as resource:
    JA_WORDS = frozenset(line.strip() for line in resource)


def add_dakuten(kk):
    """Given a kana (single-character string), add a dakuten."""
    try:
        ii = "かきくけこさしすせそたちつてとはひふへほ".index(kk)
        return "がぎぐげござじずぜぞだぢづでどばびぶべぼ"[ii]
    except ValueError:
        # this is normal if the input is nonsense
        return None


SUTEGANA = frozenset("ゃゅょぁぃぅぇぉ")
ODORI = frozenset("〃々ゝゞヽ")


@dataclass
class Word:
    surface: str
    hira: str
    char_type: int


@dataclass
class Token:
    surface: str
    space: bool  # if a space should follow

    def __str__(self):
        sp = " " if self.space else ""
        return f"{self.surface}{sp}"


class Cutlet:
    def __init__(self):
        self.tagger = Tagger()

    def __call__(self, text) -> Tuple[str, None]:
        """Build a complete string from input text."""
        # TODO: Return List[MToken] instead of None
        if not text:
            return "", None
        text = self._normalize_text(text)
        words = [
            Word(
                w.surface,
                jaconv.kata2hira(w.feature.pron or w.feature.kana or w.surface),
                6 if w.char_type == 7 or not w.is_unk else w.char_type,
            )
            for w in self.tagger(text)
        ]
        tokens = self._romaji_tokens(words)
        out = "".join([str(tok) for tok in tokens])
        ps = re.sub(r"\s+", " ", out.strip()).replace("(", "«").replace(")", "»")
        ps = re.sub(r'(?<![!",.:;?»—…”]) (?=ʔ)|(?<=ʔ) (?!["«“])', "", ps)
        return ps, None

    def _normalize_text(self, text):
        """Given text, normalize variations in Japanese.

        This specifically removes variations that are meaningless for romaji
        conversion using the following steps:

        - Unicode NFKC normalization
        - Full-width Latin to half-width
        - Half-width katakana to full-width
        """
        # perform unicode normalization
        text = re.sub(r"[〜～](?=\d)", "から", text)  # wave dash range
        for k, v in KATAKANA_PHONETIC_EXTENSIONS.items():
            text = text.replace(k, v)
        text = unicodedata.normalize("NFKC", text)
        # convert all full-width alphanum to half-width, since it can go out as-is
        text = mojimoji.zen_to_han(text, kana=False)
        # replace half-width katakana with full-width
        text = mojimoji.han_to_zen(text, digit=False, ascii=False)
        return "".join(
            [
                (" " + number_to_hiragana(t)) if t.isdigit() else t
                for t in re.findall(r"\d+|\D+", text)
            ]
        )

    def _romaji_tokens(self, words):
        """Build a list of tokens from input nodes."""
        groups = []
        i = 0
        while i < len(words):
            z = next(
                (
                    z
                    for z in range(i + 1, len(words))
                    if words[z].char_type != words[i].char_type
                ),
                len(words),
            )
            j = next(
                (
                    j
                    for j in range(z, i, -1)
                    if "".join(w.surface for w in words[i:j]) in JA_WORDS
                ),
                None,
            )
            if j is None:
                groups.append([words[i]])
                i += 1
            else:
                groups.append(words[i:j])
                i = j
        words = [
            Word(
                "".join(w.surface for w in g),
                "".join(w.hira for w in g),
                g[0].char_type,
            )
            for g in groups
        ]
        out = []
        for word in words:
            po = out[-1] if out else None
            roma = self._romaji_word(word)
            tok = Token(roma, False)
            # handle punctuation with atypical spacing
            surface = word.surface
            if surface in "「『«" or roma in "([":
                if po:
                    po.space = True
            elif surface in "」』»" or roma in "]).,?!:":
                if po:
                    po.space = False
                tok.space = True
            elif roma == " ":
                tok.space = False
            else:
                tok.space = True
            out.append(tok)
        # remove any leftover sokuon
        for tok in out:
            tok.surface = tok.surface.replace("っ", "")
        return out

    def _romaji_word(self, word):
        """Return the romaji for a single word (node)."""
        surface = word.surface
        assert not surface.isdigit(), surface
        if surface.isascii():
            return surface
        if word.char_type == 3:  # symbol
            return "".join(HEPBURN.get(c, c) for c in surface)
        elif word.char_type != 6:
            return ""  # TODO: silently fail
        out = ""
        hira = word.hira
        for ki, char in enumerate(hira):
            nk = hira[ki + 1] if ki < len(hira) - 1 else None
            pk = hira[ki - 1] if ki > 0 else None
            out += self._get_single_mapping(pk, char, nk)
        return out

    def _get_single_mapping(self, pk, kk, nk):
        """Given a single kana and its neighbors, return the mapped romaji."""
        # handle odoriji
        # NOTE: This is very rarely useful at present because odoriji are not
        # left in readings for dictionary words, and we can't follow kana
        # across word boundaries.
        if kk in ODORI:
            if kk in "ゝヽ":
                if pk:
                    return pk
                else:
                    return ""  # invalid but be nice
            if kk in "ゞヾ":  # repeat with voicing
                if not pk:
                    return ""
                vv = add_dakuten(pk)
                if vv:
                    return HEPBURN[vv]
                else:
                    return ""
            # remaining are 々 for kanji and 〃 for symbols, but we can't
            # infer their span reliably (or handle rendaku)
            return ""
        # handle digraphs
        if pk and (pk + kk) in HEPBURN:
            return HEPBURN[pk + kk]
        if nk and (kk + nk) in HEPBURN:
            return ""
        if nk and nk in SUTEGANA:
            if kk == "っ":
                return ""  # never valid, just ignore
            return HEPBURN[kk][:-1] + HEPBURN[nk]
        if kk in SUTEGANA:
            return ""
        if kk == "ー":  # 長音符
            return "ː"
        if kk == "っ":
            return "ʔ"
        if kk == "ん":
            # https://en.wikipedia.org/wiki/N_(kana)
            # m before m,p,b
            # ŋ before k,g
            # ɲ before ɲ,ʨ,ʥ
            # n before n,t,d,r,z
            # ɴ otherwise
            tnk = HEPBURN.get(nk)
            if tnk:
                if tnk[0] in "mpb":
                    return "m"
                elif tnk[0] in "kɡ":
                    return "ŋ"
                elif any(tnk.startswith(p) for p in ("ɲ", "ʨ", "ʥ")):
                    return "ɲ"
                elif tnk[0] in "ntdɾz":
                    return "n"
            return "ɴ"
        return HEPBURN.get(kk, "")
