from ..token import PronunciationResult


class FallbackNetwork:
    def __init__(self, british):
        import torch
        from transformers import BartForConditionalGeneration

        self.torch = torch
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = BartForConditionalGeneration.from_pretrained(
            "PeterReid/graphemes_to_phonemes_en_" + ("gb" if british else "us")
        )
        self.model.to(self.device)
        self.model.eval()
        self.grapheme_to_token = {
            g: i for i, g in enumerate(self.model.config.grapheme_chars)
        }
        self.token_to_phoneme = {
            i: p for i, p in enumerate(self.model.config.phoneme_chars)
        }

    def graphemes_to_tokens(self, graphemes):
        return [1] + [self.grapheme_to_token.get(g, 3) for g in graphemes] + [2]

    def tokens_to_phonemes(self, tokens):
        return "".join([self.token_to_phoneme.get(t, "") for t in tokens if t > 3])

    def __call__(self, input_token) -> PronunciationResult:
        input_ids = self.torch.tensor(
            [self.graphemes_to_tokens(input_token.text)], device=self.device
        )

        with self.torch.no_grad():
            generated_ids = self.model.generate(input_ids=input_ids)
        output_text = self.tokens_to_phonemes(generated_ids[0].tolist())
        return (output_text, 1)
