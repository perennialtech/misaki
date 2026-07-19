# Misaki English phoneme symbols

Misaki emits a compact, model-oriented phoneme alphabet for English. Many symbols are IPA, while several are merged phones or Misaki-specific aliases.

This document describes the standard inventory produced by Misaki's English lexicon and pronunciation rules. Output-format versions refer to phoneme formats, not Misaki package versions.

## Inventory

| Output mode                                 | Count | Mode-specific symbols |
| ------------------------------------------- | ----: | --------------------- |
| Shared English inventory                    |    42 | None                  |
| American, default or legacy, `version=None` |    46 | `æ O ᵻ T`             |
| American, v2, `version="2.0"`               |    47 | `æ O ᵻ ɾ ʔ`           |
| British                                     |    46 | `a Q ɒ ː`             |
| Union across English dialects and versions  |    52 | `æ O ᵻ T ɾ ʔ a Q ɒ ː` |

These counts exclude:

- Punctuation and whitespace
- Empty pronunciations
- The configured unknown marker
- Explicit pronunciation overrides
- Symbols returned by caller-provided custom fallbacks

Custom fallbacks and explicit overrides are not restricted to this inventory.

## Reading Misaki phonemes

Phonemes within a word are written without separators. Stress marks appear before the stressed vowel, as in `jˈɛs`.

Some symbols require special attention:

- `A I O Q W Y` are vowel aliases, not ordinary Latin letters.
- `ʤ` and `ʧ` are single merged symbols representing `dʒ` and `tʃ`.
- `ɡ` is IPA `U+0261`, not ASCII `g`.
- `T` is Misaki's legacy American flap symbol.
- `ᵊ` is a small schwa used for a muted or syllabic reduction.

## Shared English symbols

The following 42 symbols are shared by American and British output.

### Stress marks

| Symbol | Meaning          |
| ------ | ---------------- |
| `ˈ`    | Primary stress   |
| `ˌ`    | Secondary stress |

### Consonants

| Symbols                       | Meaning or example                          |
| ----------------------------- | ------------------------------------------- |
| `b d f h k l m n p s t v w z` | Common consonants, used largely as expected |
| `j`                           | "y" in `yes`, `jˈɛs`                        |
| `ɡ`                           | Hard "g" in `get`, `ɡɛt`                    |
| `ŋ`                           | "ng" in `sung`, `sˈʌŋ`                      |
| `ɹ`                           | English "r" in `red`, `ɹˈɛd`                |
| `ʃ`                           | "sh" in `shin`, `ʃˈɪn`                      |
| `ʒ`                           | "zh" in `Asia`, `ˈAʒə`                      |
| `ð`                           | Voiced "th" in `than`, `ðən`                |
| `θ`                           | Voiceless "th" in `thin`, `θˈɪn`            |

### Merged consonants

| Symbol | Approximate IPA | Example          |
| ------ | --------------- | ---------------- |
| `ʤ`    | `dʒ`            | `jump`, `ʤˈʌmp`  |
| `ʧ`    | `tʃ`            | `lunch`, `lˈʌnʧ` |

### Vowels

| Symbol | Example                          |
| ------ | -------------------------------- |
| `ə`    | Schwa, a common unstressed vowel |
| `i`    | `easy`, `ˈizi`                   |
| `u`    | `flu`, `flˈu`                    |
| `ɑ`    | `spa`, `spˈɑ`                    |
| `ɔ`    | `all`, `ˈɔl`                     |
| `ɛ`    | `bed`, `bˈɛd`                    |
| `ɜ`    | American `her`, `hɜɹ`            |
| `ɪ`    | `brick`, `bɹˈɪk`                 |
| `ʊ`    | `wood`, `wˈʊd`                   |
| `ʌ`    | `sun`, `sˈʌn`                    |

### Diphthong aliases

| Symbol | Approximate IPA | Example       |
| ------ | --------------- | ------------- |
| `A`    | `eɪ`            | `hey`, `hˈA`  |
| `I`    | `aɪ`            | `high`, `hˈI` |
| `W`    | `aʊ`            | `how`, `hˌW`  |
| `Y`    | `ɔɪ`            | `soy`, `sˈY`  |

### Reduced vowels

| Symbol | Meaning or example                                           |
| ------ | ------------------------------------------------------------ |
| `ᵊ`    | Small schwa, as in `pixel`, `pˈɪksᵊl`                        |
| `ɐ`    | Weak reduced vowel, as in determiner `a`, `ɐ`, or `an`, `ɐn` |

## American symbols

American output adds the following symbols to the shared inventory.

### Symbols used in all American formats

| Symbol | Meaning or example                                          |
| ------ | ----------------------------------------------------------- |
| `æ`    | TRAP vowel, as in `ash`, `ˈæʃ`                              |
| `O`    | GOAT vowel, approximately `oʊ`, as in `go`, `ɡˈO`           |
| `ᵻ`    | Reduced vowel between `ə` and `ɪ`, as in `boxes`, `bˈɑksᵻz` |

### Default or legacy format

With `version=None`, American flaps use:

| Symbol | Meaning                                                           |
| ------ | ----------------------------------------------------------------- |
| `T`    | Legacy Misaki flap symbol, corresponding approximately to IPA `ɾ` |

Glottal stops are represented as `t` in this format.

### Version 2.0 format

With `version="2.0"`, American output can additionally contain:

| Symbol | Meaning                                 |
| ------ | --------------------------------------- |
| `ɾ`    | Alveolar flap, as in `butter`, `bˈʌɾəɹ` |
| `ʔ`    | Glottal stop                            |

## British symbols

British output adds the following symbols to the shared inventory.

| Symbol | Meaning or example                                        |
| ------ | --------------------------------------------------------- |
| `a`    | British TRAP vowel, as in `ash`, `ˈaʃ`                    |
| `Q`    | British GOAT vowel, approximately `əʊ`, as in `go`, `ɡˈQ` |
| `ɒ`    | British LOT vowel, as in `on`, `ˌɒn`                      |
| `ː`    | Vowel length mark, as in `or`, `ɔː`                       |

## Punctuation and other output

English G2P output can contain punctuation alongside phonemes:
