import re
from typing import Tuple

from .g2pkc import G2p


class KOG2P:
    def __init__(self):
        self.g2pk = G2p()

    def __call__(self, text) -> Tuple[str, None]:
        if re.search(r"[A-Za-z]", text):
            raise ValueError(
                "KOG2P accepts Korean text only; use MultilingualG2P for mixed "
                "English/Korean text."
            )
        # TODO: Return List[MToken] instead of None
        ps = self.g2pk(text)
        return ps, None
