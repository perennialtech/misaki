from typing import List, Optional, Tuple

import spacy

from ..en_phonemes import finalize_english_phonemes
from ..token import MToken, MTokenFeatures, TokenFallback
from ._lexicon import (CONSONANTS, NON_QUOTE_PUNCTS, PRIMARY_STRESS, VOWELS,
                       Lexicon, TokenContext, apply_stress, stress_weight)
from ._tokenization import (SUBTOKEN_JUNKS, Preprocessor, TokenGroup,
                            preprocess, retokenize, tokenize)


def _merge_metadata(tokens: List[MToken]):
    stress = {tk.features.stress for tk in tokens if tk.features.stress is not None}
    currency = {
        tk.features.currency for tk in tokens if tk.features.currency is not None
    }
    ratings = {tk.rating for tk in tokens}
    merged_rating = None if None in ratings else min(ratings)

    text = (
        "".join(tk.text + tk.whitespace for tk in tokens[:-1]) + tokens[-1].text
    ).strip()
    tag = max(
        tokens, key=lambda tk: sum(1 if c == c.lower() else 2 for c in tk.text)
    ).tag

    features = MTokenFeatures(
        is_head=tokens[0].features.is_head,
        alias=None,
        stress=list(stress)[0] if len(stress) == 1 else None,
        currency=max(currency) if currency else None,
        num_flags="".join(
            sorted({c for tk in tokens for c in (tk.features.num_flags or "")})
        ),
        prespace=tokens[0].features.prespace,
    )
    return (
        text,
        tag,
        tokens[-1].whitespace,
        tokens[0].start_ts,
        tokens[-1].end_ts,
        merged_rating,
        features,
    )


def make_lookup_token(tokens: List[MToken]) -> MToken:
    text, tag, whitespace, start_ts, end_ts, merged_rating, features = _merge_metadata(
        tokens
    )
    return MToken(
        text=text,
        tag=tag,
        whitespace=whitespace,
        phonemes=None,
        start_ts=start_ts,
        end_ts=end_ts,
        rating=merged_rating,
        features=features,
    )


def collapse_tokens(tokens: List[MToken], unk: str) -> MToken:
    text, tag, whitespace, start_ts, end_ts, merged_rating, features = _merge_metadata(
        tokens
    )
    phonemes = ""
    for tk in tokens:
        if (
            tk.features.prespace
            and phonemes
            and not phonemes[-1].isspace()
            and tk.phonemes
        ):
            phonemes += " "
        phonemes += unk if tk.phonemes is None else tk.phonemes
    return MToken(
        text=text,
        tag=tag,
        whitespace=whitespace,
        phonemes=phonemes,
        start_ts=start_ts,
        end_ts=end_ts,
        rating=merged_rating,
        features=features,
    )


def resolve_tokens(tokens: List[MToken]):
    text = "".join(tk.text + tk.whitespace for tk in tokens[:-1]) + tokens[-1].text
    prespace = (
        " " in text
        or "/" in text
        or len(
            {
                0 if c.isalpha() else (1 if c.isdigit() else 2)
                for c in text
                if c not in SUBTOKEN_JUNKS
            }
        )
        > 1
    )
    for i, tk in enumerate(tokens):
        if tk.phonemes is None:
            if i == len(tokens) - 1 and tk.text in NON_QUOTE_PUNCTS:
                tk.phonemes = tk.text
                tk.rating = 3
            elif all(c in SUBTOKEN_JUNKS for c in tk.text):
                tk.phonemes = ""
                tk.rating = 3
        elif i > 0:
            tk.features.prespace = prespace
    if prespace:
        return
    indices = [
        (PRIMARY_STRESS in tk.phonemes, stress_weight(tk.phonemes), i)
        for i, tk in enumerate(tokens)
        if tk.phonemes
    ]
    if len(indices) == 2 and len(tokens[indices[0][2]].text) == 1:
        i = indices[1][2]
        tokens[i].phonemes = apply_stress(tokens[i].phonemes, -0.5)
        return
    elif len(indices) < 2 or sum(b for b, _, _ in indices) <= (len(indices) + 1) // 2:
        return
    indices = sorted(indices)[: len(indices) // 2]
    for _, _, i in indices:
        tokens[i].phonemes = apply_stress(tokens[i].phonemes, -0.5)


def get_token_context(
    ctx: TokenContext, ps: Optional[str], token: MToken
) -> TokenContext:
    vowel = ctx.future_vowel
    vowel = (
        next(
            (
                None if c in NON_QUOTE_PUNCTS else (c in VOWELS)
                for c in ps
                if any(c in s for s in (VOWELS, CONSONANTS, NON_QUOTE_PUNCTS))
            ),
            vowel,
        )
        if ps
        else vowel
    )
    future_to = token.text in ("to", "To") or (
        token.text == "TO" and token.tag in ("TO", "IN")
    )
    return TokenContext(future_vowel=vowel, future_to=future_to)


class G2P:
    """English grapheme-to-phoneme converter.

    The converter uses either spaCy's small English pipeline or transformer
    pipeline for tokenization and part-of-speech tagging. The selected spaCy
    model must already be installed; this class does not download models at
    runtime.

    Args:
        version: Optional G2P version setting.
        trf: Selects the spaCy pipeline. When False, uses
            ``en_core_web_sm``. When True, uses ``en_core_web_trf``.
        british: Whether to use the British English lexicon.
        fallback: Fallback used for unresolved tokens. When None, fallback is
            disabled and unresolved tokens use the ``unk`` marker.
        unk: Marker emitted for unresolved tokens when no fallback is
            available.

    Raises:
        RuntimeError: If the selected spaCy model is not installed.
        ValueError: If an unsupported version is requested.
    """

    def __init__(
        self,
        version=None,
        trf=False,
        british=False,
        fallback: Optional[TokenFallback] = None,
        unk="❓",
    ):
        if version not in (None, "2.0"):
            raise ValueError(
                f"Unsupported output version {version!r}. Must be None or '2.0'."
            )
        self.version = version
        self.british = british

        name = f"en_core_web_{'trf' if trf else 'sm'}"
        if not spacy.util.is_package(name):
            raise RuntimeError(
                f"Selected spaCy model {name!r} must be installed before "
                "constructing G2P. Please install it first."
            )

        components = ["transformer" if trf else "tok2vec", "tagger"]
        self.nlp = spacy.load(name, enable=components)
        self.lexicon = Lexicon(british)
        self.fallback = fallback
        self.unk = unk

    def fold_left(self, tokens: List[MToken]) -> List[MToken]:
        result = []
        for tk in tokens:
            tk = (
                collapse_tokens([result.pop(), tk], unk=self.unk)
                if result and not tk.features.is_head
                else tk
            )
            result.append(tk)
        return result

    def _resolve_group(
        self,
        group: TokenGroup,
        ctx: TokenContext,
    ) -> Tuple[MToken, TokenContext]:
        """
        Resolves a single TokenGroup right-to-left.
        - Lexical lookup greedily resolves the longest available right-bounded span.
        - If an unresolved component requires fallback, fallback applies to the entire group.
        - Successful fallback pronunciation determines context for the group to its left.
        """
        w = list(group.tokens)
        if len(w) == 1:
            tk = w[0]
            if tk.phonemes is None:
                tk.phonemes, tk.rating = self.lexicon(tk, ctx)
            if tk.phonemes is None and self.fallback is not None:
                tk.phonemes, tk.rating = self.fallback(tk)
            ctx = get_token_context(ctx, tk.phonemes, tk)
            return tk, ctx

        left, right = 0, len(w)
        should_fallback = False
        while left < right:
            if any(
                tk.features.alias is not None or tk.phonemes is not None
                for tk in w[left:right]
            ):
                tk = None
            else:
                tk = make_lookup_token(w[left:right])
            ps, rating = (None, None) if tk is None else self.lexicon(tk, ctx)
            if ps is not None:
                w[left].phonemes = ps
                w[left].rating = rating
                for x in w[left + 1 : right]:
                    x.phonemes = ""
                    x.rating = rating
                ctx = get_token_context(ctx, ps, tk)
                right = left
                left = 0
            elif left + 1 < right:
                left += 1
            else:
                right -= 1
                tk = w[right]
                if tk.phonemes is None:
                    if all(c in SUBTOKEN_JUNKS for c in tk.text):
                        tk.phonemes = ""
                        tk.rating = 3
                    elif self.fallback is not None:
                        should_fallback = True
                        break
                left = 0

        if should_fallback:
            tk = make_lookup_token(w)
            w[0].phonemes, w[0].rating = self.fallback(tk)
            for j in range(1, len(w)):
                w[j].phonemes = ""
                w[j].rating = w[0].rating
            ctx = get_token_context(ctx, w[0].phonemes, tk)
        else:
            resolve_tokens(w)

        return collapse_tokens(w, unk=self.unk), ctx

    def __call__(
        self, text: str, preprocess_fn: Optional[Preprocessor] = preprocess
    ) -> Tuple[str, List[MToken]]:
        text, tokens, features = (
            preprocess_fn(text) if preprocess_fn is not None else (text, [], {})
        )
        tokens = tokenize(self.nlp, text, tokens, features)
        tokens = self.fold_left(tokens)
        token_groups = retokenize(tokens)
        ctx = TokenContext()

        final_tokens = []
        for group in reversed(token_groups):
            tk, ctx = self._resolve_group(group, ctx)
            final_tokens.append(tk)

        final_tokens.reverse()

        for tk in final_tokens:
            if tk.phonemes is not None:
                tk.phonemes = finalize_english_phonemes(tk.phonemes, self.version)
            else:
                tk.phonemes = self.unk

        result = "".join(
            (tk.phonemes if tk.phonemes is not None else "") + tk.whitespace
            for tk in final_tokens
        )
        return result, final_tokens
