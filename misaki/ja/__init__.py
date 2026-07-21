from typing import Tuple


class JAG2P:
    def __init__(self):
        from .cutlet import Cutlet

        self.cutlet = Cutlet()

    def __call__(self, text) -> Tuple[str, None]:
        return self.cutlet(text)
