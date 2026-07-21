# -*- coding: utf-8 -*-
"""
https://github.com/kyubyong/g2pK
"""

import importlib.resources
import re

import mecab
from jamo import h2j

from .numerals import convert_num
from .regular import link1, link2, link4
from .special import (balb, consonant_ui, jamo, josa_ui, jyeo, modifying_rieul,
                      palatalize, rieulbieub, rieulgiyeok, verb_nieun)
from .utils import annotate, parse_table


class G2p:
    def __init__(self):
        self.mecab = mecab.MeCab()
        self.table = parse_table()
        self.idiom_rules: list[tuple[re.Pattern, str]] = []
        with (importlib.resources.files(__package__) / "idioms.txt").open(
            "r", encoding="utf-8"
        ) as resource:
            for line in resource:
                line = line.split("#", 1)[0].strip()
                if "===" in line:
                    pattern, replacement = line.split("===", 1)
                    self.idiom_rules.append((re.compile(pattern), replacement))

    def idioms(self, string):
        """Apply the bundled idiom substitutions in file order."""
        out = string
        for pattern, replacement in self.idiom_rules:
            out = pattern.sub(replacement, out)
        return out

    def __call__(self, string):
        """Convert Korean text to decomposed, pronunciation-adjusted jamo.

        The fixed pipeline applies idioms, morphological annotation, numeral
        spelling, decomposition, special pronunciation rules, the regular
        coda/onset table, linking rules, and final marker removal.
        """
        string = self.idioms(string)
        string = annotate(string, self.mecab)
        string = convert_num(string)
        inp = h2j(string)

        for func in (
            jyeo,
            consonant_ui,
            josa_ui,
            jamo,
            rieulgiyeok,
            rieulbieub,
            verb_nieun,
            balb,
            palatalize,
            modifying_rieul,
        ):
            inp = func(inp)
        inp = re.sub("/[PJEB]", "", inp)

        for str1, str2 in self.table:
            inp = re.sub(str1, str2, inp)

        for func in (link1, link2, link4):
            inp = func(inp)

        return inp.replace("^", "")
