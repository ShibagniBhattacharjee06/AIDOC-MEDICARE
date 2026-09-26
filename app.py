# if you dont use pipenv uncomment the following:
from dotenv import load_dotenv
load_dotenv()

# VoiceBot UI with Gradio
import os
import gradio as gr

from brain_of_the_doctor import encode_image, analyze_image_with_query
from voice_of_the_patient import transcribe_with_groq
from voice_of_the_doctor import text_to_speech


system_prompt = """
You are a knowledgeable and empathetic AI Doctor Assistant designed for educational consultation and initial symptom analysis.
Respond in the EXACT SAME language that the patient speaks or asks in.
- If the patient speaks Hindi, answer in Hindi (Devanagari script).
- If the patient speaks English, answer in English.

Carefully examine the medical image (if provided) and the patient's symptoms/concerns.
If you detect any potential medical issue, clearly explain what it might be and suggest safe preliminary remedies.
Always remind the patient to consult a qualified healthcare professional or dermatologist for confirmation.
Do not output raw special characters or markdown stars/asterisks that disrupt text-to-speech.
Answer concisely in 2 to 3 doctor-like sentences.
"""


# -------- LANGUAGE DETECTION FUNCTION --------
def detect_language(text):
    if not text or not isinstance(text, str):
        return "en"
    for char in text:
        if '\u0900' <= char <= '\u097F':   # Devanagari / Hindi unicode block
            return "hi"
    return "en"


# -------- MAIN PROCESS FUNCTION --------
def process_inputs(audio_filepath, image_filepath):
    groq_api_key = os.environ.get("GROQ_API_KEY")

    if not groq_api_key:
        error_msg = "Error: GROQ_API_KEY is not set. Please add GROQ_API_KEY to your .env file or environment."
        return (
            "No audio processed.",
            error_msg,
            None
        )

    # Validate that at least one input is provided
    if not audio_filepath and not image_filepath:
        return (
            "No voice input recorded.",
            "Please speak your symptoms using the microphone or upload an image to analyze.",
            None
        )

    speech_to_text_output = ""

    # Step 1: Transcribe audio if provided
    if audio_filepath:
        try:
            speech_to_text_output = transcribe_with_groq(
                stt_model="whisper-large-v3",
                audio_filepath=audio_filepath,
                GROQ_API_KEY=groq_api_key
            )
            if not speech_to_text_output:
                speech_to_text_output = "[Voice recorded, but no clear speech was detected]"
        except Exception as e:
            speech_to_text_output = f"Transcription error: {str(e)}"
    else:
        speech_to_text_output = "No audio recording provided (Image-only analysis)."

    # Step 2: Build Doctor Query Prompt
    has_valid_speech = (
        speech_to_text_output
        and not speech_to_text_output.startswith("Transcription error:")
        and not speech_to_text_output.startswith("No audio recording provided")
        and not speech_to_text_output.startswith("[Voice recorded")
    )

    if has_valid_speech:
        patient_query = f"{system_prompt}\n\nPatient voice description: {speech_to_text_output}"
    else:
        patient_query = f"{system_prompt}\n\nPlease inspect the uploaded medical image and describe possible conditions, remedies, and next steps."

    # Step 3: Multimodal or text reasoning with Groq
    try:
        doctor_response = analyze_image_with_query(
            query=patient_query,
            encoded_image=encode_image(image_filepath) if image_filepath else None,
            image_path=image_filepath,
            groq_api_key=groq_api_key,
            model="meta-llama/llama-4-scout-17b-16e-instruct"
        )
    except Exception as e:
        doctor_response = f"Error during medical analysis: {str(e)}"

    # Step 4: Detect language for voice output
    lang = detect_language(doctor_response)

    # Step 5: Convert Doctor Response to Speech
    voice_of_doctor = None
    if doctor_response and not doctor_response.startswith("Error:"):
        voice_of_doctor = text_to_speech(doctor_response, filename="doctor_voice.mp3", lang=lang)

    return speech_to_text_output, doctor_response, voice_of_doctor


# -------- GRADIO USER INTERFACE --------
theme = gr.themes.Soft(
    primary_hue="teal",
    secondary_hue="blue",
    neutral_hue="slate",
)

with gr.Blocks(theme=theme, title="AI Doctor Assistant - Medicare") as demo:
    gr.Markdown(
        """
        # 🩺 AI Doctor Assistant with Vision & Voice
        ### Multimodal AI Consultation • Voice & Image Analysis • Bilingual (English / Hindi)
        """
    )

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 📥 Patient Inputs")
            audio_input = gr.Audio(
                sources=["microphone"],
                type="filepath",
                label="🎤 Speak Your Symptoms"
            )
            image_input = gr.Image(
                type="filepath",
                label="🖼️ Upload Medical Image (Skin condition, scan, etc.)"
            )
            with gr.Row():
                submit_btn = gr.Button("🔬 Analyze Symptoms & Image", variant="primary")
                clear_btn = gr.Button("🗑️ Clear Inputs")

        with gr.Column(scale=1):
            gr.Markdown("### 🩺 Doctor Assessment & Voice Output")
            speech_output = gr.Textbox(
                label="📝 Transcribed Patient Symptoms (Whisper)",
                interactive=False,
                lines=2
            )
            doctor_text = gr.Textbox(
                label="👨‍⚕️ Doctor's Diagnosis & Guidance",
                interactive=False,
                lines=4
            )
            doctor_voice = gr.Audio(
                label="🔊 Doctor's Spoken Advice",
                autoplay=True,
                type="filepath"
            )

    def clear_all():
        return None, None, "", "", None

    clear_btn.click(
        fn=clear_all,
        inputs=[],
        outputs=[audio_input, image_input, speech_output, doctor_text, doctor_voice],
        show_api=False
    )

    submit_btn.click(
        fn=process_inputs,
        inputs=[audio_input, image_input],
        outputs=[speech_output, doctor_text, doctor_voice],
        show_api=False
    )


if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_api=False
    )