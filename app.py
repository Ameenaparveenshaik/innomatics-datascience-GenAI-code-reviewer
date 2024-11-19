import google.generativeai as genai
import streamlit as st
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from .env file
api_key = os.getenv("API_KEY")
if not api_key:
    st.error("API key not found. Please set your API key in a .env file.")
    st.stop()

# Load system prompt
try:
    with open("system_prompt.txt", "r") as file:
        sys_prompt = file.read()
except FileNotFoundError:
    st.error("System prompt file (system_prompt.txt) not found.")
    st.stop()

# Configure Generative AI
genai.configure(api_key=api_key)

# Initialize the Generative AI model
try:
    model = genai.GenerativeModel(model_name="gemini-1.5-pro", system_instruction=sys_prompt)
except Exception as e:
    st.error(f"Error initializing Generative AI model: {e}")
    st.stop()

# Streamlit app UI customization
st.set_page_config(page_title="PyGenAI Code Reviewer", page_icon="🤖", layout="wide")

# Sidebar: App Description
with st.sidebar:
    st.title("About PyGenAI")
    st.markdown(
        """
        **PyGenAI** is an AI-powered Python code reviewer that:
        - Highlights bugs, errors, and areas for improvement.
        - Supports file uploads for `.py` scripts or manual code input.
        - Streams feedback in real-time for a conversational experience.
        
        ### **How to Use**:
        1. Upload a Python script using the file uploader, or paste code directly in the input box.
        2. Click **Analyze** to get AI-powered feedback.
        3. Review feedback in the chat interface.
        
        ---
        Made by **Ameena** 🚀
        """
    )

# Main app UI
st.title(":red[Ameena's PyGenAI Code Reviewer] :robot_face:")
st.write("Your Personal Python Code Reviewer :mechanical_arm:")

# Chat history
if "history" not in st.session_state:
    st.session_state.history = []

# Format chat history for AI
def format_history(history):
    return [{"role": entry["role"], "parts": [{"text": entry["content"]}]} for entry in history]

# Function to get AI's response for code review
def get_response(message):
    formatted_history = format_history(st.session_state.history)
    chatbot = model.start_chat(history=formatted_history)
    response = chatbot.send_message(message)

    st.session_state.history.append({"role": "user", "content": message})
    st.session_state.history.append({"role": "model", "content": response.text})

    return response.text

# Function to get bug report and suggestions
def get_bug_report_and_suggestions(code):
    bug_report_prompt = f"Analyze the following Python code and generate a bug report along with suggestions for improvement:\n\n{code}"
    return get_response(bug_report_prompt)

# File upload widget (for Python script)
uploaded_file = st.file_uploader("Upload your Python script", type=["py"])

# Check if a file is uploaded
if uploaded_file is not None:
    file_content = uploaded_file.read().decode("utf-8")
    st.text_area("Your Python Script", file_content, height=200)

    # Handle user input from uploaded file
    if file_content:
        st.chat_message("human").write(file_content)  # Display the user's input
        with st.spinner("Analyzing your code..."):
            try:
                # Review the code
                ai_message = st.chat_message("ai")  # Create a single message box for code review
                response_text = get_response(file_content)
                ai_message.write(response_text)     # Display the complete response

                # Generate bug report and suggestions
                st.write("### Bug Report and Suggestions:")
                bug_report = get_bug_report_and_suggestions(file_content)
                st.write(bug_report)  # Display the bug report and suggestions

            except Exception as e:
                st.error(f"Error processing your request: {e}")

# User input for Python code (if no file uploaded)
user_prompt = st.chat_input("Enter your Python script here...")

# Handle user input if not using file upload
if user_prompt:
    st.chat_message("human").write(user_prompt)
    with st.spinner("Analyzing your code..."):
        try:
            ai_message = st.chat_message("ai")  # Create a single message box for code review
            response_text = get_response(user_prompt)
            ai_message.write(response_text)     # Display the complete response

            # Generate bug report and suggestions
            st.write("### Bug Report and Suggestions:")
            bug_report = get_bug_report_and_suggestions(user_prompt)
            st.write(bug_report)  # Display the bug report and suggestions

        except Exception as e:
            st.error(f"Error processing your request: {e}")
