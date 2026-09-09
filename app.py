import os
import streamlit as st
import markdown
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Page configuration (Must be the first Streamlit command)
st.set_page_config(
    page_title="GreekAI | Olympus Archivist",
    page_icon="🛡️",
    layout="centered"
)

# Custom minimal theme styling (Zero layout/responsiveness CSS needed)
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
    .stApp {
        background: linear-gradient(135deg, #090a0f 0%, #131620 100%);
        color: #f1f5f9;
        font-family: 'Inter', sans-serif;
    }
    .app-title-container {
        display: flex;
        align-items: center;
        gap: 0.875rem;
        margin-bottom: 0.25rem;
    }
    .app-icon-badge {
        height: 40px;
        width: 40px;
        background: linear-gradient(135deg, #10b981, #047857);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1.1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Render professional header
st.markdown("""
    <div class="app-title-container">
        <div class="app-icon-badge">
            <i class="fas fa-network-wired"></i>
        </div>
        <div style="font-size: 1.75rem; font-weight: 700;">GreekAI Archive</div>
    </div>
    <div style="color: #94a3b8; font-size: 0.875rem; margin-bottom: 1.5rem; padding-left: 3.25rem;">Enterprise Hellenic Intelligence System</div>
""", unsafe_allow_html=True)

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

# Initialize a persistent chat session in Streamlit's session state
if "chat_session" not in st.session_state:
    st.session_state.chat_session = client.chats.create(
        model="gemini-3.5-flash",  # Updated to standard current model variant
        config=config
    )

# Header Section
st.title("⚡ GreekAI")
st.caption("Powered by the Archive of Olympus")
st.markdown("---")

# Initialize chat message history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "Welcome. I am the digital archivist. I possess comprehensive knowledge of Hellenic myths, deities, and heroes. Define the parameters of your query."
        }
    ]
    
# Display prior chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input via Streamlit's built-in mobile-optimized keyboard bar
if prompt := st.chat_input("Ask about the Titanomachy, Odysseus, or Mount Olympus..."):
    # Append user message to history and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)


# Generate assistant response with a status spinner and error retries
    with st.chat_message("assistant"):
        with st.spinner("Archivist is retrieving data..."):
            max_retries = 3
            bot_reply = None
            
            for attempt in range(max_retries):
                try:
                    response = st.session_state.chat_session.send_message(prompt)
                    bot_reply = response.text
                    break
                except Exception as e:
                    error_str = str(e)
                    if prompt := st.chat_input("Query architectural or mythological records..."):
                        st.session_state.messages.append({"role": "user", "content": prompt})
                        with st.chat_message("user"):
                            st.markdown(prompt)

                        # Generate assistant response with a professional spinner and god-like limit handling
                        with st.chat_message("assistant"):
                            with st.spinner("Executing query pipeline..."):
                                max_retries = 3
                                bot_reply = None
                                
                                for attempt in range(max_retries):
                                    try:
                                        response = st.session_state.chat_session.send_message(prompt)
                                        bot_reply = response.text
                                        break
                                    except Exception as e:
                                        error_str = str(e)
                                        # Handle Rate Limits / Quota Exhaustion with a dramatic, god-like persona tone
                                        if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower():
                                            bot_reply = (
                                                "**[Oracle Notice]** *The divine energies of Mount Olympus are momentarily "
                                                "exhausted from your rapid volume of inquiries. Please allow the temporal "
                                                "mists to clear—try transmitting again shortly.*"
                                            )
                                            break
                                        elif ("503" in error_str or "UNAVAILABLE" in error_str) and attempt < max_retries - 1:
                                            continue
                                        else:
                                            bot_reply = f"**[System Fault]** *Atmospheric disturbance detected in the archive core:* _{e}_"
                                
                                st.markdown(bot_reply)
                                
                        # Save assistant response to history
                        st.session_state.messages.append({"role": "assistant", "content": bot_reply})