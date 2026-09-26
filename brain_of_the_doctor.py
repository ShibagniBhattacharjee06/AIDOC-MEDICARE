from dotenv import load_dotenv
load_dotenv()

# Step 1: Setup GROQ API key
import os
import base64
import mimetypes
from groq import Groq

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Candidate multimodal/vision models on Groq in priority order
CANDIDATE_VISION_MODELS = [
    "qwen/qwen3.8-27b",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "qwen/qwen3-vl-32b-instruct",
    "llama-3.2-11b-vision-preview",
    "llama-3.2-90b-vision-preview",
    "llava-v1.5-7b-4096-preview"
]

# Robust text models for medical reasoning
TEXT_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "llama3-70b-8192",
    "llama3-8b-8192",
    "mixtral-8x7b-32768"
]


def encode_image(image_path):
    if not image_path or not os.path.exists(image_path):
        return None
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except Exception:
        return None


def get_active_models(client):
    """Dynamically fetch list of available models from Groq account."""
    try:
        model_list = client.models.list()
        return [m.id for m in model_list.data]
    except Exception:
        return []


def analyze_image_with_query(query, model=None, encoded_image=None, groq_api_key=None, image_path=None):
    api_key = groq_api_key or os.environ.get("GROQ_API_KEY")
    if not api_key:
        return "Error: GROQ_API_KEY is not configured. Please set your GROQ_API_KEY in the environment or .env file."

    client = Groq(api_key=api_key)
    active_models = get_active_models(client)

    if encoded_image is None and image_path:
        encoded_image = encode_image(image_path)

    # 1. Attempt Multimodal Analysis if Image is present
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

        # Prioritize active vision models discovered from Groq API
        models_to_try = []
        if model and (not active_models or model in active_models):
            models_to_try.append(model)

        for candidate in CANDIDATE_VISION_MODELS:
            if candidate not in models_to_try and (not active_models or candidate in active_models):
                models_to_try.append(candidate)

        # Also add any other active model that has vision/vl/scout in its name
        if active_models:
            for m in active_models:
                if any(kw in m.lower() for kw in ["vision", "vl", "scout", "qwen3.8", "llava"]) and m not in models_to_try:
                    models_to_try.append(m)

        for m in models_to_try:
            try:
                chat_completion = client.chat.completions.create(
                    messages=messages,
                    model=m
                )
                if chat_completion.choices and chat_completion.choices[0].message.content:
                    return chat_completion.choices[0].message.content
            except Exception:
                continue

    # 2. Text-Based Medical Reasoning (Primary or Fallback)
    text_prompt = query
    if encoded_image:
        text_prompt = f"{query}\n\n[Note: The patient also uploaded a medical image of the affected area. Provide preliminary clinical advice, remedies, and suggest consulting a physician.]"

    messages = [
        {
            "role": "user",
            "content": text_prompt
        }
    ]

    text_candidates = []
    if active_models:
        for t in TEXT_MODELS:
            if t in active_models:
                text_candidates.append(t)
        for m in active_models:
            if m not in text_candidates and not any(kw in m.lower() for kw in ["guard", "whisper"]):
                text_candidates.append(m)
    else:
        text_candidates = TEXT_MODELS

    last_error = None
    for m in text_candidates:
        try:
            chat_completion = client.chat.completions.create(
                messages=messages,
                model=m
            )
            if chat_completion.choices and chat_completion.choices[0].message.content:
                return chat_completion.choices[0].message.content
        except Exception as e:
            last_error = e
            continue

    return f"Error analyzing symptoms: {last_error}"

