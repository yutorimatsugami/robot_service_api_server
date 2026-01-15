import warnings
# Suppress Google Generative AI deprecation warning
warnings.filterwarnings("ignore", message=".*All support for the `google.generativeai` package has ended.*")

import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)

def generate_chat_response(message: str, context: str = ""):
    if not API_KEY:
        return "Gemini API Key is missing. Please check .env file."
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
You are a helpful station guide robot.
Use the following context information (shops, facilities) to answer the user's question if relevant.
If the context doesn't have the answer, answer naturally as a helpful assistant.

Context Information:
{context}

User Question: {message}
"""
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error communicating with Gemini: {str(e)}"
