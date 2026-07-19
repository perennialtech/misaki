from dataclasses import dataclass, field
from typing import Optional, Protocol, Tuple

PronunciationResult = Tuple[Optional[str], Optional[int]]


class TokenFallback(Protocol):
    def __call__(self, token: "MToken") -> PronunciationResult: ...


@dataclass
class MTokenFeatures:
    is_head: bool = True
    alias: Optional[str] = None
    stress: Optional[float] = None
    currency: Optional[str] = None
    num_flags: str = ""
    prespace: bool = False


@dataclass
class MToken:
    text: str
    tag: str
    whitespace: str

    phonemes: Optional[str] = None
    """
    None means unresolved, "" means intentionally silent or absorbed, and a nonempty string means resolved.
    Final unresolved tokens become the configured unk marker.
    """

    start_ts: Optional[float] = None
    end_ts: Optional[float] = None

    rating: Optional[int] = None
    """
    Ordered pronunciation provenance/confidence, with conventional levels:
    - 5 (explicit user override)
    - 4 (high-confidence lexical or rule-derived)
    - 3 (lower-confidence dictionary or structural)
    - 2 (bundled eSpeak fallback)
    - 1 (bundled neural fallback)
    - None (unrated or a merged result containing an unrated component)

    Merged ratings use the minimum rating only when every contributing component has a rating.
    Custom fallbacks may return their own integer rating and arbitrary phoneme strings.
    """

    features: MTokenFeatures = field(default_factory=MTokenFeatures)
