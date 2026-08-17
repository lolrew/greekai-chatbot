import os
import time
import markdown
from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Initialize the Gemini client using environment variable
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set")

client = genai.Client(api_key=API_KEY)

# Set up the system instruction persona for the chatbot
system_instruction = (
    "You are Mount Olympus's ultimate archivist—an expert on "
    "Greek Mythology. When users ask simple questions, keep your answers short, direct, "
    "and concise (1-3 sentences maximum). Only provide detailed, storytelling-oriented narratives "
    "if the user explicitly asks for a story, a deep dive, or background history.\n\n"
    "IMPORTANT FORMATTING RULES:\n"
    "1. Use Markdown for all responses\n"
    "2. Use ### for section headers when needed\n"
    "3. Use **bold** for emphasis on key names and terms\n"
    "4. Keep formatting clean and minimal for short answers"
)
config = types.GenerateContentConfig(
    system_instruction=system_instruction,
    temperature=0.7,
)

# Maintain a persistent chat session
# Try these model names in order:
# 1. "gemini-1.5-flash" (Recommended - fastest)
# 2. "gemini-1.5-pro" (More powerful)
# 3. "gemini-1.0-pro" (Older but stable)

chat_session = client.chats.create(
    model="gemini-3.5-flash",  # Changed from "gemini-pro"
    config=config
)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "").strip()
    if not user_message:
        return jsonify({"response": "Speak, mortal, for your mind was blank."})
    
    # Retry configuration for high-demand 503 errors
    max_retries = 3
    delay = 2  # seconds

    for attempt in range(max_retries):
        try:
            response = chat_session.send_message(user_message)
            
            # Convert Markdown to HTML
            html_response = markdown.markdown(
                response.text,
                extensions=['extra', 'codehilite', 'toc']
            )
            
            return jsonify({"response": html_response})
        except Exception as e:
            error_str = str(e)
            # Check if it's a temporary 503 or overloaded error and we have retries left
            if ("503" in error_str or "UNAVAILABLE" in error_str) and attempt < max_retries - 1:
                time.sleep(delay)
                delay *= 2  # Exponential backoff
                continue
            else:
                return jsonify({"response": f"[The mists of Olympus obscure your query: {e}]"})

# For local development
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)