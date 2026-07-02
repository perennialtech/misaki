# Misaki English phonemes

This document describes the English phoneme symbols emitted by Misaki 0.9.4.

Misaki's English inventory is version-dependent. Counts below exclude punctuation, whitespace, empty phoneme strings, the default unknown marker `❓`, and explicit user overrides such as `[word](/customphones/)`.

The practical English output inventory is:

| Mode                                            | Count | Dialect-specific symbols |
| ----------------------------------------------- | ----: | ------------------------ |
| Shared English output                           |    42 | None                     |
| American, default or legacy, `version != "2.0"` |    46 | `æ O ᵻ T`                |
| American, v2, `version == "2.0"`                |    47 | `æ O ᵻ ɾ ʔ`              |
| British                                         |    46 | `a Q ɒ ː`                |
| Union across English dialects and versions      |    52 | `æ O ᵻ T ɾ ʔ a Q ɒ ː`    |

Important implementation note: `ɐ` is not currently included in the `US_VOCAB` or `GB_VOCAB` constants, but English special cases do emit it for weak function words such as `a`, `an`, and weak `am`. This document counts `ɐ` as a shared practical output symbol.

The symbols are intended as input tokens for neural networks. Some are IPA symbols, some are merged clusters, and some are Misaki-specific aliases.

### Shared English output symbols (42)

#### Stress marks (2)

- `ˈ`: Primary stress.
- `ˌ`: Secondary stress.

#### IPA-style consonants (22)

- `b d f h k l m n p s t v w z`: Common consonants, mostly used as expected.
- `j`: The "y" sound, as in `yes => jˈɛs`.
- `ɡ`: Hard "g" sound, as in `get => ɡɛt`. This is `U+0261`, not the ASCII letter `g`.
- `ŋ`: The "ng" sound, as in `sung => sˈʌŋ`.
- `ɹ`: English "r" sound, as in `red => ɹˈɛd`.
- `ʃ`: The "sh" sound, as in `shin => ʃˈɪn`.
- `ʒ`: The "zh" sound, as in `Asia => ˈAʒə`.
- `ð`: Voiced "th" sound, as in `than => ðən`.
- `θ`: Voiceless "th" sound, as in `thin => θˈɪn`.

#### Merged consonant clusters (2)

- `ʤ`: The "j" or "dg" sound, merged from `dʒ`, as in `jump => ʤˈʌmp` or `lunge => lˈʌnʤ`.
- `ʧ`: The "ch" sound, merged from `tʃ`, as in `chump => ʧˈʌmp` or `lunch => lˈʌnʧ`.

#### IPA-style vowels (10)

- `ə`: Schwa, a common reduced vowel.
- `i`: As in `easy => ˈizi`.
- `u`: As in `flu => flˈu`.
- `ɑ`: As in `spa => spˈɑ`.
- `ɔ`: As in `all => ˈɔl`.
- `ɛ`: As in `bed => bˈɛd`.
- `ɜ`: As in American `her => hɜɹ`.
- `ɪ`: As in `brick => bɹˈɪk`.
- `ʊ`: As in `wood => wˈʊd`.
- `ʌ`: As in `sun => sˈʌn`.

#### Diphthong vowels shared by both dialects (4)

- `A`: The "ay" vowel, expands roughly to IPA `eɪ`, as in `hey => hˈA`.
- `I`: The "eye" vowel, expands roughly to IPA `aɪ`, as in `high => hˈI`.
- `W`: The "ow" vowel, expands roughly to IPA `aʊ`, as in `how => hˌW`.
- `Y`: The "oy" vowel, expands roughly to IPA `ɔɪ`, as in `soy => sˈY`.

#### Reduced or custom vowels (2)

- `ᵊ`: Small schwa, a muted version of `ə`, as in `pixel => pˈɪksᵊl`.
- `ɐ`: Weak reduced vowel emitted by English special cases, as in determiner `a => ɐ`, `an => ɐn`, and weak `am => ɐm`.

### American-only symbols

American output differs depending on `version`.

#### American symbols in all English versions (3)

- `æ`: TRAP vowel, as in `ash => ˈæʃ`.
- `O`: American GOAT vowel, expands roughly to IPA `oʊ`, as in `go => ɡˈO`.
- `ᵻ`: Reduced vowel between `ə` and `ɪ`, often used in some suffixes, as in `boxes => bˈɑksᵻz`.

#### American default or legacy symbol, `version != "2.0"` (1)

- `T`: Legacy Misaki flap token. In default mode, final English output maps `ɾ` to `T`, so American `butter`-like flaps are represented with `T`.

#### American v2 symbols, `version == "2.0"` (2)

- `ɾ`: Alveolar flap, as in American `butter => bˈʌɾəɹ`.
- `ʔ`: Glottal stop. This is preserved in v2 output and folded to `t` in default or legacy output.

### British-only symbols (4)

- `a`: British TRAP vowel, as in `ash => ˈaʃ`.
- `Q`: British GOAT vowel, expands roughly to IPA `əʊ`, as in `go => ɡˈQ`.
- `ɒ`: British LOT vowel, as in `on => ˌɒn`.
- `ː`: Vowel length mark, as in British `or => ɔː`.

### Punctuation and non-phone output

The English G2P result can include punctuation symbols. These are not phonemes and are not counted in the phoneme inventory.

Punctuation that can be emitted includes:

```txt
; : , . ! ? — … " “ ” ( )
```

Other non-phone output behavior:

- Whitespace is preserved from the token stream.
- Some tokens can produce an empty phoneme string, for example currency signs before numbers.
- Unknown tokens use `❓` by default, controlled by `unk`.
- Explicit user overrides such as `[word](/phonemes/)` can inject arbitrary strings, so strict inventory guarantees only apply when such overrides are excluded.

### Inventory validation sets

These sets describe practical English output, not only the `US_VOCAB` and `GB_VOCAB` constants.

```py
SHARED_ENGLISH_OUTPUT = frozenset(
    "AIWY"
    "bdfhijklmnpstuvwz"
    "ðŋɑɔəɛɜɡɪɹʃʊʌʒʤʧˈˌθᵊɐ"
)

US_DEFAULT_OR_LEGACY_ONLY = frozenset("æOᵻT")
US_V2_ONLY = frozenset("æOᵻɾʔ")
GB_ONLY = frozenset("aQɒː")

US_DEFAULT_OR_LEGACY = SHARED_ENGLISH_OUTPUT | US_DEFAULT_OR_LEGACY_ONLY
US_V2 = SHARED_ENGLISH_OUTPUT | US_V2_ONLY
GB = SHARED_ENGLISH_OUTPUT | GB_ONLY
ENGLISH_UNION = (
    SHARED_ENGLISH_OUTPUT
    | US_DEFAULT_OR_LEGACY_ONLY
    | US_V2_ONLY
    | GB_ONLY
)

assert len(SHARED_ENGLISH_OUTPUT) == 42
assert len(US_DEFAULT_OR_LEGACY) == 46
assert len(US_V2) == 47
assert len(GB) == 46
assert len(ENGLISH_UNION) == 52
```

### From eSpeak to Misaki for English fallback

`EspeakFallback` uses this English-specific conversion. The replacement order matters, longest eSpeak strings are replaced first.

```py
import re

E2M_ENGLISH = sorted(
    {
        "ʔˌn\u0329": "ʔn",
        "ʔn\u0329": "ʔn",
        "a^ɪ": "I",
        "a^ʊ": "W",
        "d^ʒ": "ʤ",
        "e^ɪ": "A",
        "e": "A",
        "t^ʃ": "ʧ",
        "ɔ^ɪ": "Y",
        "ə^l": "ᵊl",
        "ʲo": "jo",
        "ʲə": "jə",
        "ʲ": "",
        "ɚ": "əɹ",
        "r": "ɹ",
        "x": "k",
        "ç": "k",
        "ɐ": "ə",
        "ɬ": "l",
        "\u0303": "",
    }.items(),
    key=lambda kv: -len(kv[0]),
)


def english_from_espeak(ps, british, version=None):
    for old, new in E2M_ENGLISH:
        ps = ps.replace(old, new)

    ps = re.sub(r"(\S)\u0329", r"ᵊ\1", ps).replace(chr(809), "")

    if british:
        ps = ps.replace("e^ə", "ɛː")
        ps = ps.replace("iə", "ɪə")
        ps = ps.replace("ə^ʊ", "Q")
    else:
        ps = ps.replace("o^ʊ", "O")
        ps = ps.replace("ɜːɹ", "ɜɹ")
        ps = ps.replace("ɜː", "ɜɹ")
        ps = ps.replace("ɪə", "iə")
        ps = ps.replace("ː", "")

    # For eSpeak versions before 1.52.
    ps = ps.replace("o", "ɔ")

    if version != "2.0":
        ps = ps.replace("ɾ", "T").replace("ʔ", "t")

    return ps.replace("^", "")


espeak_ps = "mˈɜːt^ʃəntʃˌɪp"

assert english_from_espeak(espeak_ps, british=False) == "mˈɜɹʧəntʃˌɪp"
assert english_from_espeak(espeak_ps, british=True) == "mˈɜːʧəntʃˌɪp"
```

Note that English `EspeakFallback` maps eSpeak `ɐ` to Misaki `ə`, while the English lexicon's own special cases can emit Misaki `ɐ`.

### Generic eSpeak G2P note

`EspeakG2P` is used for most non-English and non-CJK languages. It has a separate mapping and, in `version == "2.0"`, can introduce non-English nasal-vowel placeholder symbols such as `B C D E V U X Z`. Those are not part of the English inventory documented here.

### From Misaki to eSpeak-like IPA

This helper reverses the main English aliases approximately.

```py
def to_espeak(ps):
    # Optionally, insert tie characters between the two replacement characters.
    ps = ps.replace("ʤ", "dʒ").replace("ʧ", "tʃ")

    ps = ps.replace("A", "eɪ")
    ps = ps.replace("I", "aɪ")
    ps = ps.replace("Y", "ɔɪ")
    ps = ps.replace("O", "oʊ")
    ps = ps.replace("Q", "əʊ")
    ps = ps.replace("W", "aʊ")

    ps = ps.replace("T", "ɾ")
    ps = ps.replace("ᵊ", "ə")
    ps = ps.replace("ɐ", "ə")

    return ps
```
