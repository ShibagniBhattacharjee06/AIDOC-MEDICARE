# 🩺 AI Doctor with Vision and Voice

Welcome to the **AI Doctor** project! This is an interactive, Gradio-based web application that acts as a virtual medical assistant. It allows users to speak their symptoms, upload medical or infected area images for analysis, and receive a voice-based diagnosis and remedy suggestions.

---

## ✨ Features
- **🎤 Voice Input (Speech-to-Text):** Speak your symptoms directly into your microphone. The app uses [Groq's Whisper-large-v3](https://groq.com/) to quickly and accurately transcribe your speech.
- **🖼️ Vision Analysis:** Upload medical images (like an X-ray or a picture of a skin condition). The app uses **Meta Llama 4 Scout (17B)** via Groq to analyze the image along with your spoken symptoms.
- **🗣️ Voice Output (Text-to-Speech):** The AI responds just like a real doctor! It uses `gTTS` (Google Text-to-Speech) to generate human-like audio of its diagnosis.
- **🌍 Auto-Language Detection:** The system automatically detects if the AI's response is in English or Hindi and generates the appropriate voice response!
- **📱 Mobile Responsive UI:** Built with Gradio Blocks to ensure the interface looks great on both desktop and mobile devices.

---

## 🛠️ Technology Stack
- **Frontend:** [Gradio](https://gradio.app/) for the web UI.
- **AI/LLM Provider:** [Groq API](https://groq.com/) (Lightning-fast inference).
- **Speech-to-Text:** Whisper-large-v3 (via Groq).
- **Vision Model:** `meta-llama/llama-4-scout-17b-16e-instruct` (via Groq).
- **Text-to-Speech:** `gTTS` (Google Text-to-Speech).
- **Audio Processing:** `pydub`, `ffmpeg`.

---

## 🚀 How to Run Locally

### 1. Prerequisites
Ensure you have Python installed. You will also need **FFmpeg** installed on your system for `pydub` and audio recording to work correctly.

### 2. Clone the Repository
```bash
git clone <your-repo-link>
cd <your-repo-directory>
```

### 3. Install Dependencies
You can install the required packages using the `requirements.txt` file:
```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables
The application requires a Groq API key to function. 
1. Create a `.env` file in the root directory.
2. Add your Groq API key to it:
```env
GROQ_API_KEY=your_api_key_here
```

### 5. Run the Application
Start the Gradio app by running:
```bash
python app.py
```
A local URL (usually `http://127.0.0.1:7860`) will be generated. Open this URL in your web browser to start using your AI Doctor!

---

## 📁 Project Structure

- **`app.py`**: The main entry point. Sets up the Gradio UI and wires all the components together.
- **`brain_of_the_doctor.py`**: Handles image encoding and communicates with Groq's Vision LLM.
- **`voice_of_the_patient.py`**: Captures voice input from the user and transcribes it using Whisper.
- **`voice_of_the_doctor.py`**: Converts the AI's text response back into spoken audio using gTTS.
- **`.env`**: Stores secret API keys (ignored by Git).
- **`requirements.txt` / `Pipfile`**: Lists all the necessary dependencies.

---

## 📝 Usage Note
*This application is designed for **learning purposes only**. The AI responses should not replace professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider for any medical condition.*

---
Made with ❤️ using Python, Gradio, and Groq.
