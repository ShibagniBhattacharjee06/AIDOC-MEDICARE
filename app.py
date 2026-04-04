# if you dont use pipenv uncomment the following:
from dotenv import load_dotenv
load_dotenv()

# VoiceBot UI with Gradio
import os
import gradio as gr

from brain_of_the_doctor import encode_image, analyze_image_with_query
from voice_of_the_patient import record_audio, transcribe_with_groq
from voice_of_the_doctor import text_to_speech


system_prompt = """
You have to act as a professional doctor for learning purposes.
Respond in the SAME language that the patient speaks.
If the patient speaks Hindi, answer in Hindi.
If the patient speaks English, answer in English.

Look at the image and the patient question. If you find something medically wrong,
suggest possible remedies. Do not add numbers or special characters.
Answer like a real doctor speaking to a patient. Keep the response concise
(max two sentences).
"""


# -------- LANGUAGE DETECTION FUNCTION --------
def detect_language(text):
    for char in text:
        if '\u0900' <= char <= '\u097F':   # Hindi unicode range
            return "hi"
    return "en"


# -------- MAIN PROCESS FUNCTION --------
def process_inputs(audio_filepath, image_filepath):

    speech_to_text_output = transcribe_with_groq(
        GROQ_API_KEY=os.environ.get("GROQ_API_KEY"),
        audio_filepath=audio_filepath,
        stt_model="whisper-large-v3"
    )

    # Handle image input
    if image_filepath:
        doctor_response = analyze_image_with_query(
            query=system_prompt + speech_to_text_output,
            encoded_image=encode_image(image_filepath),
            model="meta-llama/llama-4-scout-17b-16e-instruct"
        )
    else:
        doctor_response = "No image provided for me to analyze"

    # -------- Detect language for voice --------
    lang = detect_language(doctor_response)

    # -------- Generate Doctor Voice --------
    voice_of_doctor = text_to_speech(doctor_response, "final.mp3", lang)

    return speech_to_text_output, doctor_response, voice_of_doctor


# -------- MOBILE RESPONSIVE UI USING BLOCKS --------
with gr.Blocks() as demo:

    gr.Markdown("# AI Doctor with Vision and Voice")

    with gr.Column():

        audio_input = gr.Audio(
            sources=["microphone"],
            type="filepath",
            label="Speak Your Symptoms"
        )

        image_input = gr.Image(
            type="filepath",
            label="Upload Medical Image (Optional)"
        )

        submit_btn = gr.Button("Analyze")

        speech_output = gr.Textbox(
            label="Speech to Text"
        )

        doctor_text = gr.Textbox(
            label="Doctor's Response"
        )

        doctor_voice = gr.Audio(
            label="Doctor Voice",
            autoplay=True
        )

    submit_btn.click(
        fn=process_inputs,
        inputs=[audio_input, image_input],
        outputs=[speech_output, doctor_text, doctor_voice]
    )


demo.launch(debug=True)