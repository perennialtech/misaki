import re
import warnings

import cn2an

from ..token import G2PResult

_PUNCTUATION_TABLE = str.maketrans(
    {
        "、": ", ",
        "，": ", ",
        ",": ", ",
        "。": ". ",
        "．": ". ",
        ".": ". ",
        "！": "! ",
        "!": "! ",
        "：": ": ",
        ":": ": ",
        "；": "; ",
        ";": "; ",
        "？": "? ",
        "?": "? ",
        "«": " “",
        "»": "” ",
        "《": " “",
        "》": "” ",
        "「": " “",
        "」": "” ",
        "【": " “",
        "】": "” ",
        "（": " (",
        "）": ") ",
        "(": " (",
        ")": ") ",
    }
)


class ZHG2P:
    def __init__(self, unk="❓", en_callable=None):
        from .frontend import ZHFrontend

        self.frontend = ZHFrontend(unk=unk)
        self.en_callable = en_callable
        self.unk = unk
        if en_callable is None:
            warnings.warn("en_callable is None, so English may be removed")

    @staticmethod
    def map_punctuation(text):
        return text.translate(_PUNCTUATION_TABLE).strip()

    def __call__(self, text, en_callable=None) -> G2PResult:
        if not text.strip():
            return "", None
        text = cn2an.transform(text, "an2cn")
        text = ZHG2P.map_punctuation(text)
        # TODO: Interleaved English is brittle, needs improvement.
        en_callable = self.en_callable if en_callable is None else en_callable
        segments = []
        for en, zh in re.findall(
            r"([A-Za-z \'-]*[A-Za-z][A-Za-z \'-]*)|([^A-Za-z]+)", text
        ):
            en, zh = en.strip(), zh.strip()
            if zh:
                segments.append(self.frontend(zh)[0])
            elif en_callable is None:
                segments.append(self.unk)
            else:
                segments.append(en_callable(en))
        # TODO: Return List[MToken] instead of None
        return " ".join(segments), None
