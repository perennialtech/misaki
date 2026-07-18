from dataclasses import dataclass, field
from typing import Optional


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
    """None means unresolved, "" means intentionally silent or absorbed, and a nonempty string means resolved."""

    start_ts: Optional[float] = None
    end_ts: Optional[float] = None

    rating: Optional[int] = None
    """Ordered pronunciation provenance/confidence, with the current conventional levels 1 through 5. Merged ratings use the weakest available rating."""

    features: MTokenFeatures = field(default_factory=MTokenFeatures)
