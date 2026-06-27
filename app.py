import traceback

import gradio as gr

# Dictionary to store our loaded models
models = {}


def load_models():
    """
    Safely load models for each language to ensure the app still runs
    even if the user is missing a specific optional dependency (e.g., cutlet, cn2an).
    """
    print("Loading models... This may take a moment.")

    # 1. Load English (US and UK)
    try:
        from misaki.en import G2P as ENG2P
        from misaki.espeak import EspeakFallback

        # Use EspeakFallback to resolve Out-Of-Vocabulary (OOM) words natively
        fallback_us = EspeakFallback(british=False)
        fallback_gb = EspeakFallback(british=True)

        models["English (US)"] = ENG2P(trf=False, british=False, fallback=fallback_us)
        models["English (UK)"] = ENG2P(trf=False, british=True, fallback=fallback_gb)
    except Exception as e:
        models["English (US)"] = e
        models["English (UK)"] = e

    # 2. Load Japanese
    try:
        from misaki.ja import JAG2P

        # Try the 2nd Gen pyopenjtalk tokenizer first, fallback to cutlet if missing
        try:
            models["Japanese"] = JAG2P(version="pyopenjtalk")
        except:
            models["Japanese"] = JAG2P(version="cutlet")
    except Exception as e:
        models["Japanese"] = e

    # 3. Load Korean
    try:
        from misaki.ko import KOG2P

        models["Korean"] = KOG2P()
    except Exception as e:
        models["Korean"] = e

    # 4. Load Chinese
    try:
        from misaki.zh import ZHG2P

        models["Chinese"] = ZHG2P(version="1.1")
    except Exception as e:
        models["Chinese"] = e

    print("Model loading complete.")


# Initialize the models
load_models()


def format_tokens(tokens):
    """Utility format the emitted MTokens for the UI."""
    if not tokens:
        return "No tokens returned (or tokenization details not supported for this language version)."

    res = []
    for i, tk in enumerate(tokens):
        # Flatten singleton lists (sometimes returned by fold_left algorithms)
        if isinstance(tk, list) and len(tk) == 1:
            tk = tk[0]

        if hasattr(tk, "text") and hasattr(tk, "tag"):
            phonemes = getattr(tk, "phonemes", "None")
            res.append(
                f"[{i}] Text: {tk.text!r} | Tag: {tk.tag} | Phonemes: {phonemes}"
            )
        else:
            res.append(f"[{i}] {str(tk)}")

    return "\n".join(res)


def process_text(text, language):
    """Main inference function for Gradio."""
    if not text.strip():
        return "Please enter some text.", ""

    model = models.get(language, None)

    # Catch initialization errors
    if isinstance(model, Exception):
        err_out = f"Error loading model for {language}: {str(model)}"
        token_out = (
            "Please ensure all pip dependencies for this language are installed.\n\n"
            + traceback.format_exc()
        )
        return err_out, token_out

    try:
        # Inference step
        if language == "Chinese":
            # For Chinese, we can provide an English callable to elegantly handle mixed Text!
            en_model = models.get("English (US)")
            if not isinstance(en_model, Exception):
                phonemes, tokens = model(text, en_callable=lambda x: en_model(x)[0])
            else:
                phonemes, tokens = model(text)
        else:
            phonemes, tokens = model(text)

        # Structure output
        return phonemes, format_tokens(tokens)

    except Exception as e:
        return f"Error during inference: {str(e)}", traceback.format_exc()


# Gradio UI layout
with gr.Blocks(title="Misaki G2P engine") as app:
    gr.Markdown("""
        # 🌸 Misaki G2P engine
        Misaki is a G2P engine designed for [Kokoro](https://github.com/hexgrad/kokoro) models.
        Select your language and see the generated phonemes and token breakdowns below.
        """)

    with gr.Row():
        with gr.Column(scale=1):
            text_input = gr.Textbox(
                lines=5,
                label="Input text",
                placeholder="Enter text to phonemize here...",
            )
            lang_drop = gr.Dropdown(
                choices=[
                    "English (US)",
                    "English (UK)",
                    "Japanese",
                    "Korean",
                    "Chinese",
                ],
                value="English (US)",
                label="Language",
            )
            submit_btn = gr.Button("Phonemize", variant="primary")

            gr.Markdown("### Examples")
            gr.Examples(
                examples=[
                    [
                        "[Misaki](/misˈɑki/) is a G2P engine designed for [Kokoro](/kˈOkəɹO/) models.",
                        "English (US)",
                    ],
                    [
                        "merchantship. Now out-of-dictionary words are handled by espeak.",
                        "English (UK)",
                    ],
                    ["こんにちは、世界。", "Japanese"],
                    ["안녕하세요, 세계입니다.", "Korean"],
                    ["你好，世界！This is a mixed English sentence.", "Chinese"],
                ],
                inputs=[text_input, lang_drop],
                cache_examples=False,
            )

        with gr.Column(scale=1):
            phoneme_output = gr.Textbox(
                label="Generated phonemes",
                interactive=False,
                lines=2,
            )
            token_output = gr.TextArea(
                label="Token breakdown", interactive=False, lines=15
            )

    submit_btn.click(
        fn=process_text,
        inputs=[text_input, lang_drop],
        outputs=[phoneme_output, token_output],
    )

if __name__ == "__main__":
    app.launch(share=False)
