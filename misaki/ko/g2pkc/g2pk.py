# -*- coding: utf-8 -*-
"""
https://github.com/kyubyong/g2pK
"""

import os
import re

from jamo import h2j

from .numerals import convert_num
from .regular import link1, link2, link4
from .special import (balb, consonant_ui, jamo, josa_ui, jyeo, modifying_rieul,
                      palatalize, rieulbieub, rieulgiyeok, verb_nieun,
                      vowel_ui, ye)
from .utils import annotate, compose, get_rule_id2text, group, parse_table


class G2p(object):
    def __init__(self):
        self.mecab = self.get_mecab()
        self.table = parse_table()

        self.rule2text = get_rule_id2text()  # for comments of main rules
        self.idioms_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "idioms.txt"
        )

    def get_mecab(self):
        if os.name == "nt":
            import MeCab

            return MeCab.Tagger()
        elif os.name == "posix":
            import mecab

            return mecab.MeCab()

    def idioms(self, string, descriptive=False, verbose=False):
        """Process each line in `idioms.txt`
        Each line is delimited by "===",
        and the left string is replaced by the right one.
        inp: input string.
        descriptive: not used.
        verbose: boolean.
        """
        out = string

        for line in open(self.idioms_path, "r", encoding="utf8"):
            line = line.split("#")[0].rstrip("\n")
            if "===" in line:
                str1, str2 = line.split("===")
                out = re.sub(str1, str2, out)
        # gloss(verbose, out, string, rule)

        return out

    def __call__(
        self,
        string,
        descriptive=False,
        verbose=False,
        group_vowels=False,
        to_syl=False,
        use_dict=True,
    ):
        """Main function
        string: Korean input string
        descriptive: boolean.
        verbose: boolean
        group_vowels: boolean. If True, the vowels of the identical sound are normalized.
        to_syl: boolean. If True, hangul letters or jamo are assembled to form syllables.

        For example, given an input string "나의 친구가 3개를 받고 있다",
        STEP 1. idioms
        -> 나의 친구가 3개를 받고 있다

        STEP 2. annotate
        -> 나의/J 친구가 3개/B를 받고 있다

        STEP 3. Spell out arabic numbers
        -> 나의/J 친구가 세개/B를 받고 있다

        STEP 4. decompose
        -> 나의/J 친구가 세개/B를 받고 있다

        STEP 5-8. Apply Korean pronunciation rules, linking, and composition
        -> 나의 친구가 세개를 받꼬 읻따
        """
        # 1. idioms
        string = self.idioms(string, descriptive, verbose)

        # 2. annotate
        if use_dict:
            string = annotate(string, self.mecab)

        # 3. Spell out arabic numbers
        string = convert_num(string)

        # 4. decompose
        inp = h2j(string)

        # 5. special
        for func in (
            jyeo,
            ye,
            consonant_ui,
            josa_ui,
            vowel_ui,
            jamo,
            rieulgiyeok,
            rieulbieub,
            verb_nieun,
            balb,
            palatalize,
            modifying_rieul,
        ):
            inp = func(inp, descriptive, verbose)
        inp = re.sub("/[PJEB]", "", inp)

        # 6. regular table: batchim + onset
        for str1, str2, rule_ids in self.table:
            _inp = inp
            inp = re.sub(str1, str2, inp)

            # if len(rule_ids)>0:
            #     rule = "\n".join(self.rule2text.get(rule_id, "") for rule_id in rule_ids)
            # else:
            #     rule = ""
            # gloss(verbose, inp, _inp, rule)

        # 7. link
        for func in (link1, link2, link4):  # remove link3
            inp = func(inp, descriptive, verbose)

        # 8. postprocessing
        if group_vowels:
            inp = group(inp)

        if to_syl:
            inp = compose(inp)
        # 국어법칙 적용하고 싶지 않을 때 문자들 사이에 ^ 사용.
        inp = inp.replace("^", "")
        return inp


if __name__ == "__main__":
    g2p = G2p()
    g2p("나의 친구가 세 개를 받고 있다")
