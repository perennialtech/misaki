# Misaki English phonemes

This document describes the English phoneme symbols emitted by the current Misaki English output implementation.

## Architecture and Pipeline

The English implementation operates as a staged pipeline:

1. **Preprocessing:** An optional callable parses explicit pronunciation overrides and feature flags. The built-in preprocessor extracts `[text](/phonemes/)` annotations and applies `#...#` number flags.
2. **Tokenization:** Text is tokenized and tagged using spaCy (`en_core_web_sm` or `en_core_web_trf`).
3. **MToken Conversion:** spaCy tokens are converted into Misaki's `MToken` representation.
4. **Grouping:** Tokens are split into pronunciation-oriented subtokens (separating punctuation, camel case, etc.) and grouped into `TokenGroup`s.
5. **Right-to-Left Resolution:** Groups are processed right-to-left. This allows lexical weak forms (e.g. `to`, `the`) to depend on whether the following pronunciation begins with a vowel (`TokenContext.future_vowel`). It also gives the preceding token information about following functional structure (`TokenContext.future_to`).
6. **Lexical Lookup:** Within a group, spans eagerly resolve right-to-left using English rules and dictionaries.
7. **Fallback:** If an unresolved component requires fallback in a multi-token group, fallback is applied once to the complete, uncollapsed group text.
8. **Collapse:** Each `TokenGroup` is collapsed into exactly one final output `MToken`.
9. **Finalization:** The `MToken`'s internal English phonemes pass through `finalize_english_phonemes` for output-version conversion.
10. **Concatenation:** Final phonemes and preserved whitespace are concatenated into the output string.

### MToken and Group Invariants

The `MToken.phonemes` property indicates resolution state:
- `None`: Resolution has not succeeded (leaves token unresolved). Unresolved tokens later become the configured `unk` marker.
- `""`: The token was intentionally made silent or absorbed.
- Nonempty string: The token has a resolved pronunciation.

Every `TokenGroup` is guaranteed to produce exactly one output `MToken`. If fallback is applied to a multi-token group, the complete group is combined into one synthetic token before calling the fallback. This prevents producing disconnected fragments for compound words.

### Phoneme Ratings

Output origins receive a confidence `rating`. When multiple tokens are collapsed, the resulting group token keeps the minimum rating of its components (unrated if any component is unrated). Custom fallbacks may return arbitrary integer ratings.

Conventional bundled levels:
- `5`: Explicit user pronunciation overrides.
- `4`: High-confidence lexical or rule-derived output (gold dictionary, special cases).
- `3`: Lower-confidence dictionary or structural output (silver dictionary, plain letter spelling).
- `2`: Bundled `EspeakFallback` output.
- `1`: Bundled fallback network output.
- `None`: Unrated output.

Misaki's English inventory is version-dependent. The `version` values discussed in this document refer to phoneme output-format versions, not to Misaki package versions. Counts below apply to the inventory produced by Misaki's English lexicon, transformations, and bundled English adapters. They explicitly exclude:

- Punctuation and whitespace
- Empty phoneme strings and the configured unknown marker
- Explicit user phoneme overrides
- Arbitrary output returned by caller-provided custom fallbacks

The practical English output inventory is:

| Mode                                           | Count | Dialect-specific symbols |
| ---------------------------------------------- | ----: | ------------------------ |
| Shared English output                          |    42 | None                     |
| American, default or legacy, `version is None` |    46 | `æ O ᵻ T`                |
| American, v2, `version == "2.0"`               |    47 | `æ O ᵻ ɾ ʔ`              |
| British                                        |    46 | `a Q ɒ ː`                |
| Union across English dialects and versions     |    52 | `æ O ᵻ T ɾ ʔ a Q ɒ ː`    |

Internal validation inventories include `ɐ`. Bundled eSpeak conversion maps eSpeak `ɐ` to Misaki `ə`, while English lexical special cases emit Misaki `ɐ`. This document counts `ɐ` as a shared practical output symbol.

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

American output differs depending on `version`. Expected version configuration is exactly `None` and `"2.0"`.

#### American symbols in all English versions (3)

- `æ`: TRAP vowel, as in `ash => ˈæʃ`.
- `O`: American GOAT vowel, expands roughly to IPA `oʊ`, as in `go => ɡˈO`.
- `ᵻ`: Reduced vowel between `ə` and `ɪ`, often used in some suffixes, as in `boxes => bˈɑksᵻz`.

#### American default or legacy symbol, `version is None` (1)

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

These sets describe practical English output.

```py
from misaki.en_phonemes import (
    ENGLISH_UNION,
    GB,
    SHARED_ENGLISH_OUTPUT,
    US_DEFAULT_OR_LEGACY,
    US_V2,
)

assert len(SHARED_ENGLISH_OUTPUT) == 42
assert len(US_DEFAULT_OR_LEGACY) == 46
assert len(US_V2) == 47
assert len(GB) == 46
assert len(ENGLISH_UNION) == 52
```

### From eSpeak to Misaki for English fallback

`EspeakFallback` uses an English-specific conversion loop provided by `english_from_espeak`. The replacement order matters, longest eSpeak strings are replaced first.

```py
from misaki.en_phonemes import english_from_espeak, finalize_english_phonemes

espeak_ps = "mˈɜːt^ʃəntʃˌɪp"
assert english_from_espeak(espeak_ps, british=False) == "mˈɜɹʧəntʃˌɪp"
assert english_from_espeak(espeak_ps, british=True) == "mˈɜːʧəntʃˌɪp"
assert finalize_english_phonemes("mˈɜɹʧəntʃˌɪp", version="2.0") == "mˈɜɹʧəntʃˌɪp"
assert finalize_english_phonemes("ɾʔ", version=None) == "Tt"
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
