# ADAPTED from https://github.com/Greatdane/Convert-Numbers-to-Japanese/blob/master/Convert-Numbers-to-Japanese.py
# Original License: MIT

_DIGIT_NAMES = (
    "ゼロ",
    "いち",
    "に",
    "さん",
    "よん",
    "ご",
    "ろく",
    "なな",
    "はち",
    "きゅう",
)


def _spell_under_10000(number: int, standalone_thousands: bool) -> str:
    parts = []

    thousands, number = divmod(number, 1000)
    if thousands:
        if thousands == 1:
            parts.append("せん" if standalone_thousands else "いっせん")
        elif thousands == 3:
            parts.append("さんぜん")
        elif thousands == 8:
            parts.append("はっせん")
        else:
            parts.append(_DIGIT_NAMES[thousands] + "せん")

    hundreds, number = divmod(number, 100)
    if hundreds:
        if hundreds == 1:
            parts.append("ひゃく")
        elif hundreds == 3:
            parts.append("さんびゃく")
        elif hundreds == 6:
            parts.append("ろっぴゃく")
        elif hundreds == 8:
            parts.append("はっぴゃく")
        else:
            parts.append(_DIGIT_NAMES[hundreds] + "ひゃく")

    tens, ones = divmod(number, 10)
    if tens:
        if tens == 1:
            parts.append("じゅう")
        else:
            parts.append(_DIGIT_NAMES[tens] + "じゅう")
    if ones:
        parts.append(_DIGIT_NAMES[ones])

    return "".join(parts)


def number_to_hiragana(digits: str) -> str:
    digits = digits.lstrip("0") or "0"
    if len(digits) > 9:
        return "".join(_DIGIT_NAMES[int(digit)] for digit in digits)
    if digits == "0":
        return _DIGIT_NAMES[0]

    number = int(digits)
    parts = []

    oku, number = divmod(number, 100_000_000)
    if oku:
        parts.append(_spell_under_10000(oku, standalone_thousands=False))
        parts.append("おく")

    man, number = divmod(number, 10_000)
    if man:
        parts.append(_spell_under_10000(man, standalone_thousands=False))
        parts.append("まん")

    if number:
        parts.append(
            _spell_under_10000(
                number,
                standalone_thousands=len(digits) == 4,
            )
        )

    return "".join(parts)
