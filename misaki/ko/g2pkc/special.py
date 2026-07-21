# -*- coding: utf-8 -*-
"""
Special rule for processing Hangul
https://github.com/kyubyong/g2pK
"""

import re


def jyeo(inp):
    return re.sub("([ᄌᄍᄎ])ᅧ", r"\1ᅥ", inp)


def consonant_ui(inp):
    return re.sub("([ᄀᄁᄂᄃᄄᄅᄆᄇᄈᄉᄊᄌᄍᄎᄏᄐᄑᄒ])ᅴ", r"\1ᅵ", inp)


def josa_ui(inp):
    return inp.replace("/J", "")


def jamo(inp):
    out = re.sub("(디그)ᆮᄋ", r"\1ᄉ", inp)
    out = re.sub("([ᄌᄎᄐᄒ]ᅵ으)[ᆽᆾᇀᇂ]ᄋ", r"\1ᄉ", out)
    out = re.sub("(키으)ᆿᄋ", r"\1ᄀ", out)
    return re.sub("(피으)ᇁᄋ", r"\1ᄇ", out)


def rieulgiyeok(inp):
    return re.sub("ᆰ/P([ᄀᄁ])", r"ᆯᄁ", inp)


def rieulbieub(inp):
    out = re.sub("([ᆲᆴ])/Pᄀ", r"\1ᄁ", inp)
    out = re.sub("([ᆲᆴ])/Pᄃ", r"\1ᄄ", out)
    out = re.sub("([ᆲᆴ])/Pᄉ", r"\1ᄊ", out)
    return re.sub("([ᆲᆴ])/Pᄌ", r"\1ᄍ", out)


def verb_nieun(inp):
    out = inp
    pairs = [
        ("([ᆫᆷ])/Pᄀ", r"\1ᄁ"),
        ("([ᆫᆷ])/Pᄃ", r"\1ᄄ"),
        ("([ᆫᆷ])/Pᄉ", r"\1ᄊ"),
        ("([ᆫᆷ])/Pᄌ", r"\1ᄍ"),
        ("ᆬ/Pᄀ", "ᆫᄁ"),
        ("ᆬ/Pᄃ", "ᆫᄄ"),
        ("ᆬ/Pᄉ", "ᆫᄊ"),
        ("ᆬ/Pᄌ", "ᆫᄍ"),
        ("ᆱ/Pᄀ", "ᆷᄁ"),
        ("ᆱ/Pᄃ", "ᆷᄄ"),
        ("ᆱ/Pᄉ", "ᆷᄊ"),
        ("ᆱ/Pᄌ", "ᆷᄍ"),
    ]
    for str1, str2 in pairs:
        out = re.sub(str1, str2, out)
    return out


def balb(inp):
    syllable_final_or_consonants = "($|[^ᄋᄒ])"
    out = re.sub(f"(바)ᆲ({syllable_final_or_consonants})", r"\1ᆸ\2", inp)
    return re.sub("(너)ᆲ([ᄌᄍ]ᅮ|[ᄃᄄ]ᅮ)", r"\1ᆸ\2", out)


def palatalize(inp):
    out = re.sub("ᆮᄋ([ᅵᅧ])", r"ᄌ\1", inp)
    out = re.sub("ᇀᄋ([ᅵᅧ])", r"ᄎ\1", out)
    out = re.sub("ᆴᄋ([ᅵᅧ])", r"ᆯᄎ\1", out)
    return re.sub("ᆮᄒ([ᅵ])", r"ᄎ\1", out)


def modifying_rieul(inp):
    out = inp
    pairs = [
        ("ᆯ걸", "ᆯ껄"),
        ("ᆯ밖에", "ᆯ빠께"),
        ("ᆯ세라", "ᆯ쎄라"),
        ("ᆯ수록", "ᆯ쑤록"),
        ("ᆯ지라도", "ᆯ찌라도"),
        ("ᆯ지언정", "ᆯ찌언정"),
        ("ᆯ진대", "ᆯ찐대"),
    ]
    for str1, str2 in pairs:
        out = re.sub(str1, str2, out)
    return out
