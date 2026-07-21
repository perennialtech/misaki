# -*- coding: utf-8 -*-
"""
https://github.com/kyubyong/g2pK
"""


def link1(inp):
    out = inp
    pairs = [
        ("ᆨᄋ", "ᄀ"),
        ("ᆩᄋ", "ᄁ"),
        ("ᆫᄋ", "ᄂ"),
        ("ᆮᄋ", "ᄃ"),
        ("ᆯᄋ", "ᄅ"),
        ("ᆷᄋ", "ᄆ"),
        ("ᆸᄋ", "ᄇ"),
        ("ᆺᄋ", "ᄉ"),
        ("ᆻᄋ", "ᄊ"),
        ("ᆽᄋ", "ᄌ"),
        ("ᆾᄋ", "ᄎ"),
        ("ᆿᄋ", "ᄏ"),
        ("ᇀᄋ", "ᄐ"),
        ("ᇁᄋ", "ᄑ"),
    ]
    for str1, str2 in pairs:
        out = out.replace(str1, str2)
    return out


def link2(inp):
    out = inp
    pairs = [
        ("ᆪᄋ", "ᆨᄊ"),
        ("ᆬᄋ", "ᆫᄌ"),
        ("ᆰᄋ", "ᆯᄀ"),
        ("ᆱᄋ", "ᆯᄆ"),
        ("ᆲᄋ", "ᆯᄇ"),
        ("ᆳᄋ", "ᆯᄊ"),
        ("ᆴᄋ", "ᆯᄐ"),
        ("ᆵᄋ", "ᆯᄑ"),
        ("ᆹᄋ", "ᆸᄊ"),
    ]
    for str1, str2 in pairs:
        out = out.replace(str1, str2)
    return out


def link4(inp):
    out = inp
    pairs = [("ᇂᄋ", "ᄋ"), ("ᆭᄋ", "ᄂ"), ("ᆶᄋ", "ᄅ")]
    for str1, str2 in pairs:
        out = out.replace(str1, str2)
    return out
