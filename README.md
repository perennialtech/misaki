# misaki

Misaki is a G2P engine designed for [Kokoro](https://github.com/hexgrad/kokoro) models.

Hosted demo: <https://hf.co/spaces/hexgrad/Misaki-G2P>

### English usage

Misaki checks for the selected model but does not download it at runtime.

- `G2P(trf=False)` requires the `en-sm` extra.
- `G2P(trf=True)` requires the `en-trf` extra.

From a source checkout, synchronize the small English pipeline:

```bash
uv sync --no-dev --extra en,en-sm
```

For the transformer pipeline instead:

```bash
uv sync --no-dev --extra en,en-trf
```

Create an `example.py` file:

```py
from misaki import en

g2p = en.G2P(trf=False, british=False, fallback=None)

text = '[Misaki](/misˈɑki/) is a G2P engine designed for [Kokoro](/kˈOkəɹO/) models.'

phonemes, tokens = g2p(text)

print(phonemes)  # misˈɑki ɪz ɐ ʤˈitəpˈi ˈɛnʤən dəzˈInd fɔɹ kˈOkəɹO mˈɑdᵊlz.
```

Run it inside the synchronized project environment:

```bash
uv run --no-sync python example.py
```

To explicitly use the neural network fallback, synchronize its optional dependencies together with the small English pipeline:

```bash
uv sync --no-dev --extra en,en-fallback,en-sm
```

Then configure the fallback:

```py
from misaki import en

fallback = en.FallbackNetwork(british=False)
g2p = en.G2P(trf=False, british=False, fallback=fallback)
```

### Custom fallback

You can provide a custom fallback for unresolved words. A fallback is called with an `MToken` and must return a `Tuple[Optional[str], Optional[int]]` containing the phonemes, or `None` if unresolved, and an integer rating. For unresolved compounds, the fallback receives one synthetic `MToken` representing the entire group.

```py
from misaki import en
from misaki.token import MToken


class MyFallback:
    def __call__(self, token: MToken):
        if token.text == "unresolved-compound":
            return "kəmˈpWnd", 5
        return None, None  # Leaves the token unresolved, emitting the unk marker.


g2p = en.G2P(fallback=MyFallback())
```

Any returned phonemes pass through final version conversion, such as swapping `ɾ` and `T`, but custom fallbacks may return arbitrary symbols outside the regular English inventory if desired.

### Multilingual English-phone approximations

The multilingual pipeline combines the English, Mandarin Chinese, Japanese, and Korean frontends while projecting every pronunciation into the American `version=None` [EN_PHONES](EN_PHONES.md) inventory. Install its direct dependencies together with the small English spaCy model:

```bash
uv sync --no-dev --extra multilingual,en-sm
```

Use `--extra en-trf` instead of `--extra en-sm` and pass `trf=True` for the transformer English pipeline. The bundled neural English fallback additionally requires `--extra en-fallback`. The eSpeak fallback requires `--extra espeak`.

```py
from misaki import MultilingualG2P

g2p = MultilingualG2P(default_han_language="zh")
phonemes, tokens = g2p("English, 中文, 日本語, 한국어.")
print(phonemes)
assert tokens is None
```

`default_han_language` is required and accepts only `"zh"` or `"ja"`. Bare Han follows that configured language because strings such as `世界` do not identify whether a Mandarin or Japanese reading is intended. Kana and Japanese-specific marks identify their contiguous Han/Kana/digit span as Japanese. Hangul identifies Korean, but adjacent Han is routed separately rather than treated as Korean Hanja. Here, Chinese support specifically means Mandarin Chinese rather than arbitrary Chinese varieties.

The output is always American `version=None` English phones. CJK pronunciation is an English-model-compatible approximation, not native pronunciation: Mandarin tone and Japanese pitch accent are omitted, Japanese timing is approximated, and native Korean aspiration, tenseness, vowel contrasts, coarticulation, and prosody are reduced. `tokens` is intentionally `None` because the language frontends do not share an aligned token model.

Mixed English/Korean text must use `MultilingualG2P`; `KOG2P` accepts Korean text only.

To use eSpeak as the fallback, synchronize its optional dependencies together with the small English pipeline:

```bash
uv sync --no-dev --extra en,espeak,en-sm
```

Then configure the fallback:

```py
from misaki import en, espeak

fallback = espeak.EspeakFallback(british=False)  # en-us

# We construct G2P with version="2.0" because the output example contains v2 ɾ.
g2p = en.G2P(version="2.0", trf=False, british=False, fallback=fallback)

text = "Now outofdictionary words are handled by espeak."

phonemes, tokens = g2p(text)

print(phonemes)  # nˈW Wɾɑfdˈɪkʃənˌɛɹi wˈɜɹdz ɑɹ hˈændəld bI ˈispik.
```

### English

- https://github.com/explosion/spaCy
- https://github.com/savoirfairelinux/num2words
- https://github.com/hexgrad/misaki/blob/main/EN_PHONES.md

### Japanese

The Japanese tokenizer uses cutlet, fugashi, MeCab, and unidic-lite. Jaconv and mojimoji normalize kana and character-width variants. Deep gratitude to [@Respaired](https://github.com/Respaired) for helping me learn the ropes of Japanese tokenization before any Kokoro model had started training.

- https://github.com/polm/cutlet
- https://github.com/polm/fugashi
- https://github.com/ikegami-yukino/jaconv
- https://github.com/studio-ousia/mojimoji

### Korean

The Korean tokenizer is copied from 5Hyeons's g2pkc fork of Kyubyong's widely used g2pK library. Deep gratitude to [@5Hyeons](https://github.com/5Hyeons) for kindly helping with Korean and extending the original code by [@Kyubyong](https://github.com/Kyubyong).

- https://github.com/5Hyeons/StyleTTS2/tree/vocos/g2pK/g2pkc
- https://github.com/Kyubyong/g2pK

### Chinese

The second gen Chinese tokenizer adapts better logic from paddlespeech's frontend. Jieba now cuts and tags, and pinyin-to-ipa is no longer used.

- https://github.com/PaddlePaddle/PaddleSpeech/tree/develop/paddlespeech/t2s/frontend

The first gen Chinese tokenizer uses jieba to cut, pypinyin, and pinyin-to-ipa.

- https://github.com/fxsjy/jieba
- https://github.com/mozillazg/python-pinyin
- https://github.com/stefantaubert/pinyin-to-ipa

### TODO

- [ ] Data: Compress [data](https://github.com/hexgrad/misaki/tree/main/misaki/data) (no need for indented json) and eliminate redundancy between gold and silver dictionaries.
- [ ] Fallbacks: Train seq2seq fallback models on dictionaries using [this notebook](https://github.com/Kyubyong/nlp_made_easy/blob/master/PyTorch%20seq2seq%20template%20based%20on%20the%20g2p%20task.ipynb).
- [ ] Homographs: Escalate hard words like `axes bass bow lead tear wind` using BERT contextual word embeddings (CWEs) and logistic regression (LR) models (`nn.Linear` followed by sigmoid) as described in [this paper](https://assets.amazon.science/c3/db/23ca18d7450d8dbb5b80a11fcdd3/homograph-disambiguation-with-contextual-word-embeddings-for-tts-systems.pdf). Assuming `trf=True`, BERT CWEs can be accessed via `doc._.trf_data`, see [en.py#L479](https://github.com/hexgrad/misaki/blob/main/misaki/en.py#L479). Per-word LR models can be trained on [WikipediaHomographData](https://github.com/google-research-datasets/WikipediaHomographData), [llama-hd-dataset](https://github.com/facebookresearch/llama-hd-dataset), and LLM-generated data.
- [x] More languages: Add `ko.py`, `ja.py`, `zh.py`.
- [x] Per-language optional dependencies

### Acknowledgements

- 🛠️ Misaki builds on top of many excellent G2P projects linked above.
- 🌐 Thank you to all native speakers who advised and contributed G2P in many languages.
- 👾 Kokoro Discord server: https://discord.gg/QuGxSWBfQy
- 🌸 Misaki is a Japanese name and a [character in the Terminator franchise](https://terminator.fandom.com/wiki/Misaki) along with [Kokoro](https://github.com/hexgrad/kokoro?tab=readme-ov-file#acknowledgements).

<img src="https://static.wikia.nocookie.net/terminator/images/2/2e/Character_Misaki.png/revision/latest?cb=20240914020038" width="400" alt="misaki" />
