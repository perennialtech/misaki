import unicodedata
from typing import Literal, Optional

import regex

from .en_phonemes import ENGLISH_OUTPUT_PUNCTUATION, US_DEFAULT_OR_LEGACY
from .token import G2PResult, TokenFallback

_PUNCTUATION_TRANSLATION = str.maketrans(
    {
        "、": ",",
        "，": ",",
        "。": ".",
        "．": ".",
        "！": "!",
        "？": "?",
        "：": ":",
        "；": ";",
        "«": "“",
        "《": "“",
        "「": "“",
        "『": "“",
        "【": "“",
        "»": "”",
        "》": "”",
        "」": "”",
        "』": "”",
        "】": "”",
        "（": "(",
        "）": ")",
        "～": "—",
        "〜": "—",
        "–": "—",
    }
)

_JAPANESE_MARKS = frozenset("々〆ヶー・ヽヾゝゞ")
_JAPANESE_CANDIDATE = regex.compile(
    r"(?:\p{Script=Han}|\p{Script=Hiragana}|\p{Script=Katakana}|\p{Nd}|"
    r"[々〆ヶー・ヽヾゝゞ])+"
)
_JAPANESE_EVIDENCE = regex.compile(
    r"\p{Script=Hiragana}|\p{Script=Katakana}|[々〆ヶー・ヽヾゝゞ]"
)
_KOREAN_CANDIDATE = regex.compile(r"(?:\p{Script=Hangul}|\p{Nd})+")
_KOREAN_EVIDENCE = regex.compile(r"\p{Script=Hangul}")
_HAN_CANDIDATE = regex.compile(r"(?:\p{Script=Han}|\p{Nd})+")
_HAN_EVIDENCE = regex.compile(r"\p{Script=Han}")

_TARGET_VOWELS = frozenset("AIOWYæOᵻɑɔəɛɜɪʊʌᵊɐiu")
_TARGET_CONSONANTS = US_DEFAULT_OR_LEGACY - _TARGET_VOWELS - frozenset("ˈˌ")

_JAPANESE_VOWELS = {
    "a": "ɑ",
    "ɑ": "ɑ",
    "e": "ɛ",
    "ɛ": "ɛ",
    "i": "i",
    "o": "O",
    "O": "O",
    "u": "u",
    "ɯ": "u",
    "ɨ": "u",
}
_JAPANESE_CONSONANTS = {
    **{c: c for c in "bdfhjklmnpstvwz"},
    "g": "ɡ",
    "ɡ": "ɡ",
    "ŋ": "ŋ",
    "ɴ": "n",
    "ɲ": "nj",
    "ɾ": "T",
    "β": "w",
    "ç": "h",
    "ɸ": "f",
    "ɕ": "ʃ",
    "ʒ": "ʒ",
    "ʣ": "dz",
    "ʥ": "ʤ",
    "ʦ": "ts",
    "ʨ": "ʧ",
}
_JAPANESE_PUNCTUATION = {"«": "“", "»": "”", "[": "(", "]": ")"}

_KOREAN_LEADS = {
    "ᄀ": "ɡ",
    "ᄁ": "kk",
    "ᄂ": "n",
    "ᄃ": "d",
    "ᄄ": "tt",
    "ᄅ": "ɹ",
    "ᄆ": "m",
    "ᄇ": "b",
    "ᄈ": "pp",
    "ᄉ": "s",
    "ᄊ": "ss",
    "ᄋ": "",
    "ᄌ": "ʤ",
    "ᄍ": "ʤʤ",
    "ᄎ": "ʧh",
    "ᄏ": "kh",
    "ᄐ": "th",
    "ᄑ": "ph",
    "ᄒ": "h",
}
_KOREAN_FRONT_MEDIALS = frozenset("ᅵᅣᅤᅧᅨᅭᅲᅱ")
_KOREAN_MEDIALS = {
    "ᅡ": "ɑ",
    "ᅢ": "ɛ",
    "ᅣ": "jɑ",
    "ᅤ": "jɛ",
    "ᅥ": "ʌ",
    "ᅦ": "ɛ",
    "ᅧ": "jʌ",
    "ᅨ": "jɛ",
    "ᅩ": "O",
    "ᅪ": "wɑ",
    "ᅫ": "wɛ",
    "ᅬ": "wɛ",
    "ᅭ": "jO",
    "ᅮ": "u",
    "ᅯ": "wʌ",
    "ᅰ": "wɛ",
    "ᅱ": "wi",
    "ᅲ": "ju",
    "ᅳ": "ʊ",
    "ᅴ": "ʊi",
    "ᅵ": "i",
}
_KOREAN_FINALS = {
    "ᆨ": "k",
    "ᆩ": "k",
    "ᆪ": "k",
    "ᆫ": "n",
    "ᆬ": "n",
    "ᆭ": "n",
    "ᆮ": "t",
    "ᆯ": "l",
    "ᆰ": "k",
    "ᆱ": "m",
    "ᆲ": "l",
    "ᆳ": "l",
    "ᆴ": "l",
    "ᆵ": "p",
    "ᆶ": "l",
    "ᆷ": "m",
    "ᆸ": "p",
    "ᆹ": "p",
    "ᆺ": "t",
    "ᆻ": "t",
    "ᆼ": "ŋ",
    "ᆽ": "t",
    "ᆾ": "t",
    "ᆿ": "k",
    "ᇀ": "t",
    "ᇁ": "p",
    "ᇂ": "t",
}

_MANDARIN_INITIALS = {
    "ㄅ": "b",
    "ㄆ": "p",
    "ㄇ": "m",
    "ㄈ": "f",
    "ㄉ": "d",
    "ㄊ": "t",
    "ㄋ": "n",
    "ㄌ": "l",
    "ㄍ": "ɡ",
    "ㄎ": "k",
    "ㄏ": "h",
    "ㄐ": "ʤ",
    "ㄑ": "ʧ",
    "ㄒ": "ʃ",
    "ㄓ": "ʤ",
    "ㄔ": "ʧ",
    "ㄕ": "ʃ",
    "ㄖ": "ɹ",
    "ㄗ": "dz",
    "ㄘ": "ts",
    "ㄙ": "s",
}
_MANDARIN_FINALS = {
    "ㄚ": "ɑ",
    "ㄛ": "O",
    "ㄜ": "ʌ",
    "ㄝ": "ɛ",
    "ㄞ": "I",
    "ㄟ": "A",
    "ㄠ": "W",
    "ㄡ": "O",
    "ㄢ": "ɑn",
    "ㄣ": "ən",
    "ㄤ": "ɑŋ",
    "ㄥ": "əŋ",
    "ㄦ": "ɜɹ",
    "ㄧ": "i",
    "ㄨ": "u",
    "ㄭ": "ᵊ",
    "十": "ɜɹ",
}
_MANDARIN_ROUNDED_FINALS = {
    "ㄩ": ("u", "ju"),
    "月": ("wɛ", "jwɛ"),
    "元": ("wɛn", "jwɛn"),
    "云": ("un", "jun"),
}
_MANDARIN_COMPOUND_FINALS = {
    "压": "jɑ",
    "言": "jɛn",
    "阳": "jɑŋ",
    "要": "jW",
    "阴": "in",
    "应": "iŋ",
    "用": "jʊŋ",
    "又": "jO",
    "中": "ʊŋ",
    "穵": "wɑ",
    "外": "wI",
    "万": "wɑn",
    "王": "wɑŋ",
    "为": "wA",
    "文": "wən",
    "瓮": "wəŋ",
    "我": "wO",
}


def normalize_multilingual_punctuation(text: str) -> str:
    return text.translate(_PUNCTUATION_TRANSLATION)


def _append_unknown_or_source(
    source: str,
    index: int,
    unk: str,
    output: list[str],
) -> Optional[int]:
    if source.startswith(unk, index):
        output.append(unk)
        return index + len(unk)
    return None


def project_japanese(source: str, unk: str = "❓") -> str:
    output = []
    index = 0
    pending_gemination = False
    last_vowel = None

    def append_phones(phones: str) -> None:
        nonlocal pending_gemination, last_vowel
        if pending_gemination and phones and phones[0] in _TARGET_CONSONANTS:
            output.append(phones[0])
            pending_gemination = False
        output.append(phones)
        for phone in phones:
            if phone in _TARGET_VOWELS:
                last_vowel = phone

    def flush_gemination() -> None:
        nonlocal pending_gemination
        if pending_gemination:
            output.append("t")
            pending_gemination = False

    while index < len(source):
        unknown_end = _append_unknown_or_source(source, index, unk, output)
        if unknown_end is not None:
            flush_gemination()
            last_vowel = None
            index = unknown_end
            continue

        if source.startswith("ʲi", index):
            append_phones("i")
            index += 2
            continue
        if source.startswith("ɲi", index):
            append_phones("ni")
            index += 2
            continue

        symbol = source[index]
        if symbol.isspace():
            flush_gemination()
            output.append(symbol)
            last_vowel = None
        elif symbol in ENGLISH_OUTPUT_PUNCTUATION:
            flush_gemination()
            output.append(symbol)
            last_vowel = None
        elif symbol in _JAPANESE_PUNCTUATION:
            flush_gemination()
            output.append(_JAPANESE_PUNCTUATION[symbol])
            last_vowel = None
        elif symbol == "ʔ":
            if pending_gemination:
                output.append("t")
            pending_gemination = True
        elif symbol == "ː":
            if last_vowel is None:
                output.append(unk)
            else:
                output.append(last_vowel)
        elif symbol == "ʲ":
            append_phones("j")
        elif symbol == "ᵝ":
            append_phones("w")
        elif symbol in _JAPANESE_VOWELS:
            append_phones(_JAPANESE_VOWELS[symbol])
        elif symbol in _JAPANESE_CONSONANTS:
            append_phones(_JAPANESE_CONSONANTS[symbol])
        else:
            output.append(unk)
            last_vowel = None
        index += 1

    flush_gemination()
    return "".join(output)


def project_korean(source: str, unk: str = "❓") -> str:
    source = unk.join(
        unicodedata.normalize("NFD", segment) for segment in source.split(unk)
    )
    output = []
    index = 0

    while index < len(source):
        unknown_end = _append_unknown_or_source(source, index, unk, output)
        if unknown_end is not None:
            index = unknown_end
            continue

        symbol = source[index]
        if symbol.isspace() or symbol in ENGLISH_OUTPUT_PUNCTUATION:
            output.append(symbol)
        elif symbol in ("ᄉ", "ᄊ"):
            front = (
                index + 1 < len(source) and source[index + 1] in _KOREAN_FRONT_MEDIALS
            )
            if front:
                output.append("ʃ" if symbol == "ᄉ" else "ʃʃ")
            else:
                output.append(_KOREAN_LEADS[symbol])
        elif symbol in _KOREAN_LEADS:
            output.append(_KOREAN_LEADS[symbol])
        elif symbol in _KOREAN_MEDIALS:
            output.append(_KOREAN_MEDIALS[symbol])
        elif symbol in _KOREAN_FINALS:
            output.append(_KOREAN_FINALS[symbol])
        else:
            output.append(unk)
        index += 1

    return "".join(output)


def project_mandarin(source: str, unk: str = "❓") -> str:
    output = []
    index = 0
    current_initial = None

    while index < len(source):
        unknown_end = _append_unknown_or_source(source, index, unk, output)
        if unknown_end is not None:
            current_initial = None
            index = unknown_end
            continue

        symbol = source[index]
        if symbol in _MANDARIN_INITIALS:
            current_initial = symbol
            output.append(_MANDARIN_INITIALS[symbol])
        elif symbol in _MANDARIN_FINALS:
            output.append(_MANDARIN_FINALS[symbol])
        elif symbol in _MANDARIN_ROUNDED_FINALS:
            after_jqx = current_initial in {"ㄐ", "ㄑ", "ㄒ"}
            output.append(_MANDARIN_ROUNDED_FINALS[symbol][0 if after_jqx else 1])
        elif symbol in _MANDARIN_COMPOUND_FINALS:
            output.append(_MANDARIN_COMPOUND_FINALS[symbol])
        elif symbol == "R":
            output.append("ɹ")
        elif symbol == "/":
            output.append(" ")
            current_initial = None
        elif symbol in "012345":
            current_initial = None
        elif symbol.isspace() or symbol in ENGLISH_OUTPUT_PUNCTUATION:
            output.append(symbol)
            current_initial = None
        else:
            output.append(unk)
        index += 1

    return "".join(output)


def validate_multilingual_output(output: str, unk: str = "❓") -> None:
    index = 0
    while index < len(output):
        if output.startswith(unk, index):
            index += len(unk)
            continue
        symbol = output[index]
        if (
            symbol in US_DEFAULT_OR_LEGACY
            or symbol in ENGLISH_OUTPUT_PUNCTUATION
            or symbol.isspace()
        ):
            index += 1
            continue
        raise ValueError(f"Invalid multilingual output symbol {symbol!r}")


class MultilingualG2P:
    def __init__(
        self,
        default_han_language: Literal["zh", "ja"],
        trf: bool = False,
        fallback: Optional[TokenFallback] = None,
        unk: str = "❓",
    ):
        if default_han_language not in ("zh", "ja"):
            raise ValueError(
                "default_han_language must be exactly 'zh' or 'ja', "
                f"not {default_han_language!r}"
            )
        if not isinstance(unk, str) or not unk:
            raise ValueError("unk must be a nonempty string")

        from cn2an import transform

        from . import en
        from .ja.cutlet import Cutlet
        from .ko import KOG2P
        from .zh.frontend import ZHFrontend

        self.default_han_language = default_han_language
        self.unk = unk
        self.en = en.G2P(
            version=None,
            trf=trf,
            british=False,
            fallback=fallback,
            unk=unk,
        )
        self.ja = Cutlet()
        self.ko = KOG2P()
        self.zh = ZHFrontend(unk=unk)
        self._an2cn = transform

    @staticmethod
    def _candidate_at(text: str, position: int):
        candidates = []

        match = _JAPANESE_CANDIDATE.match(text, position)
        if match and _JAPANESE_EVIDENCE.search(match.group()):
            candidates.append((match.end(), 0, "ja"))

        match = _KOREAN_CANDIDATE.match(text, position)
        if match and _KOREAN_EVIDENCE.search(match.group()):
            candidates.append((match.end(), 1, "ko"))

        match = _HAN_CANDIDATE.match(text, position)
        if match and _HAN_EVIDENCE.search(match.group()):
            candidates.append((match.end(), 2, "han"))

        if not candidates:
            return None
        return max(
            candidates, key=lambda candidate: (candidate[0] - position, -candidate[1])
        )

    def _route_spans(self, text: str):
        text = normalize_multilingual_punctuation(text)
        spans = []
        english_start = 0
        position = 0

        while position < len(text):
            candidate = self._candidate_at(text, position)
            if candidate is None:
                position += 1
                continue

            end, _, language = candidate
            if english_start < position:
                spans.append(("en", text[english_start:position]))
            if language == "han":
                language = self.default_han_language
            spans.append((language, text[position:end]))
            position = end
            english_start = end

        if english_start < len(text):
            spans.append(("en", text[english_start:]))
        return spans

    def _english(self, text: str) -> str:
        start = len(text) - len(text.lstrip())
        end = len(text.rstrip())
        if start >= end:
            return text
        phonemes, _ = self.en(text[start:end])
        return text[:start] + phonemes + text[end:]

    def __call__(self, text: str) -> G2PResult:
        if not text:
            return "", None

        output = []
        for language, span in self._route_spans(text):
            if language == "en":
                output.append(self._english(span))
            elif language == "ja":
                phonemes, _ = self.ja(span)
                output.append(project_japanese(phonemes, self.unk))
            elif language == "ko":
                phonemes, _ = self.ko(span)
                output.append(project_korean(phonemes, self.unk))
            else:
                phonemes, _ = self.zh(self._an2cn(span, "an2cn"))
                output.append(project_mandarin(phonemes, self.unk))

        result = "".join(output)
        validate_multilingual_output(result, self.unk)
        return result, None
