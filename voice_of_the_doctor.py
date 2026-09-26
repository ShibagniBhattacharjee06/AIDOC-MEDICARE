import os
import time
import re
from gtts import gTTS


def clean_text_for_speech(text):
    """Remove markdown syntax, asterisks, headers, and format text for natural speech."""
    if not text or not isinstance(text, str):
        return ""
    # Remove markdown headers (#)
    text = re.sub(r'#+\s*', '', text)
    # Remove bold, italics, strikethrough, backticks
    text = re.sub(r'[*_~`]', '', text)
    # Convert markdown links [text](url) to text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Normalize spaces and newlines
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def text_to_speech(text, filename="doctor_voice.mp3", lang="en"):
    try:
        cleaned_text = clean_text_for_speech(text)
        if not cleaned_text:
            print("No valid text provided for speech generation.")
            return None

        # If the text is an error message, don't necessarily generate speech unless desired
        if cleaned_text.startswith("Error:"):
            print("Skipping speech generation for error message.")
            return None

        print(f"Generating voice output (language: {lang})...")
        output_filename = f"doctor_voice_{int(time.time())}.mp3"

        # Supported language codes for gTTS
        supported_langs = ["en", "hi", "es", "fr", "de", "ar", "bn", "ta", "te", "mr", "gu", "ur"]
        target_lang = lang if lang in supported_langs else "en"

        try:
            tts = gTTS(text=cleaned_text, lang=target_lang, slow=False)
            tts.save(output_filename)
        except Exception as tts_err:
            print(f"Language {target_lang} failed with {tts_err}, falling back to English...")
            tts = gTTS(text=cleaned_text, lang="en", slow=False)
            tts.save(output_filename)

        print("Audio saved as:", output_filename)
        return output_filename

    except Exception as e:
        print("Error in text_to_speech:", e)
        return None


if __name__ == "__main__":
    test_text = "Hi, this is your AI doctor. Autoplay testing is active!"
    text_to_speech(test_text, "doctor_voice.mp3", lang="en")