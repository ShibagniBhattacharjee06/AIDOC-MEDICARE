from gtts import gTTS
import time

def text_to_speech(text, filename, lang="en"):
    try:
        print("Generating voice...")

        filename = f"doctor_voice_{int(time.time())}.mp3"

        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(filename)

        print("Audio saved as:", filename)

        return filename

    except Exception as e:
        print("Error:", e)
        return None

if __name__ == "__main__":
    text = "Hi this is AI with Hassan, autoplay testing!"
    output_file = "doctor_voice.mp3"

    text_to_speech(text, output_file)