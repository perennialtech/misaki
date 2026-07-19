import traceback

import gradio as gr

from misaki import MultilingualG2P, espeak

# Dictionary to store loaded models or initialization errors.
models = {}


def load_models():
    """Load the unified English/Mandarin/Japanese/Korean G2P pipeline."""
    print("Loading multilingual model... This may take a moment.")

    try:
        # Bare Han text such as "世界" is interpreted as Mandarin Chinese.
        # Kana identifies Japanese automatically, and Hangul identifies Korean.
        models["Multilingual"] = MultilingualG2P(
            default_han_language="zh",
            trf=False,
            fallback=espeak.EspeakFallback(british=False),
        )
    except Exception as e:
        models["Multilingual"] = e

    print("Model loading complete.")


load_models()


def format_tokens(tokens):
    """Format emitted tokens when the selected G2P implementation provides them."""
    if tokens is None:
        return (
            "MultilingualG2P intentionally returns no aligned token list because "
            "its English, Mandarin, Japanese, and Korean frontends do not share "
            "one token model."
        )

    if not tokens:
        return "No tokens returned."

    result = []
    for i, tk in enumerate(tokens):
        if isinstance(tk, list) and len(tk) == 1:
            tk = tk[0]

        if hasattr(tk, "text") and hasattr(tk, "tag"):
            phonemes = getattr(tk, "phonemes", "None")
            result.append(
                f"[{i}] Text: {tk.text!r} | Tag: {tk.tag} | Phonemes: {phonemes}"
            )
        else:
            result.append(f"[{i}] {tk}")

    return "\n".join(result)


def process_text(text):
    """Run unified multilingual G2P inference."""
    if not text.strip():
        return "Please enter some text.", ""

    model = models.get("Multilingual")

    if isinstance(model, Exception):
        return (
            f"Error loading multilingual model: {model}",
            "Please ensure the multilingual dependencies and the selected English "
            "spaCy model are installed.\n\n"
            + "".join(
                traceback.format_exception(
                    type(model),
                    model,
                    model.__traceback__,
                )
            ),
        )

    try:
        phonemes, tokens = model(text)
        return phonemes, format_tokens(tokens)
    except Exception as e:
        return (
            f"Error during inference: {e}",
            traceback.format_exc(),
        )


with gr.Blocks(title="Misaki Multilingual G2P engine") as app:
    gr.Markdown("""
        # 🌸 Misaki Multilingual G2P engine

        This demo uses `MultilingualG2P`, which automatically routes mixed English,
        Mandarin Chinese, Japanese, and Korean text to the appropriate frontend.

        Bare Han text such as `世界` is interpreted as Mandarin Chinese in this demo.
        Japanese kana identifies Japanese automatically, while Hangul identifies Korean.
        """)

    with gr.Row():
        with gr.Column(scale=1):
            text_input = gr.Textbox(
                lines=5,
                label="Input text",
                placeholder="Enter mixed English, Chinese, Japanese, or Korean text...",
            )
            submit_btn = gr.Button("Phonemize", variant="primary")

            gr.Markdown("### Examples")
            gr.Examples(
                examples=[
                    ["English, 中文, 日本語, 한국어."],
                    ["你好，世界！This is a mixed English sentence."],
                    ["こんにちは、世界。Hello, world!"],
                    ["안녕하세요, 세계입니다. Nice to meet you!"],
                    ["Misaki supports English, 日本語, 한국어, and 中文."],
                ],
                inputs=text_input,
                cache_examples=False,
            )

        with gr.Column(scale=1):
            phoneme_output = gr.Textbox(
                label="Generated phonemes",
                interactive=False,
                lines=3,
            )
            token_output = gr.TextArea(
                label="Token breakdown",
                interactive=False,
                lines=15,
            )

    submit_btn.click(
        fn=process_text,
        inputs=text_input,
        outputs=[phoneme_output, token_output],
    )


if __name__ == "__main__":
    app.launch(share=False)
