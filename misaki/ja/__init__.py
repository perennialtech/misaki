from ..token import G2PResult


class JAG2P:
    def __init__(self):
        from .cutlet import Cutlet

        self.cutlet = Cutlet()

    def __call__(self, text) -> G2PResult:
        return self.cutlet(text)
