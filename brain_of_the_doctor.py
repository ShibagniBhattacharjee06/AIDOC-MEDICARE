from dotenv import load_dotenv
load_dotenv()

# Step 1: Setup GROQ API key
import os
import base64
import mimetypes
from groq import Groq

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Primary and fallback models
VISION_MODELS = [
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "llama-3.2-11b-vision-preview",
    "llama-3.2-90b-vision-preview",
]

TEXT_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
]


def encode_image(image_path):
    if not image_path or not os.path.exists(image_path):
        return None
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def analyze_image_with_query(query, model="meta-llama/llama-4-scout-17b-16e-instruct", encoded_image=None, groq_api_key=None, image_path=None):
    api_key = groq_api_key or os.environ.get("GROQ_API_KEY")
    if not api_key:
        return "Error: GROQ_API_KEY is not configured. Please set your GROQ_API_KEY in the environment or .env file."

    client = Groq(api_key=api_key)

    if encoded_image is None and image_path:
        encoded_image = encode_image(image_path)

    # Multimodal analysis if image is present
    if encoded_image:
        mime_type = "image/jpeg"
        if image_path:
            guessed_type, _ = mimetypes.guess_type(image_path)
            if guessed_type:
                mime_type = guessed_type

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": query
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{encoded_image}",
                        },
                    },
                ],
            }
        ]

        models_to_try = [model] if model else []
        for m in VISION_MODELS:
            if m not in models_to_try:
                models_to_try.append(m)

        last_error = None
        for m in models_to_try:
            try:
                chat_completion = client.chat.completions.create(
                    messages=messages,
                    model=m
                )
                return chat_completion.choices[0].message.content
            except Exception as e:
                last_error = e
                continue

        return f"Error analyzing image: {last_error}"

    # Text-only consultation if no image is present
    else:
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]
        models_to_try = [model] if (model and model in TEXT_MODELS) else TEXT_MODELS
        last_error = None
        for m in models_to_try:
            try:
                chat_completion = client.chat.completions.create(
                    messages=messages,
                    model=m
                )
                return chat_completion.choices[0].message.content
            except Exception as e:
                last_error = e
                continue

        return f"Error analyzing symptoms: {last_error}"
