import warnings
# Suppress Google Generative AI deprecation warning
warnings.filterwarnings("ignore", message=".*All support for the `google.generativeai` package has ended.*")

import google.generativeai as genai
import os
from dotenv import load_dotenv
from prompt import build_chat_prompt

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)

def generate_chat_response(message: str, context: str = "", lang: str = "ja"):
    """チャット応答を生成する"""
    if not API_KEY:
        return "Gemini API Key is missing. Please check .env file."
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = build_chat_prompt(message, context, lang)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "Quota exceeded" in error_msg:
            if lang == "ja":
                return "Error: アクセス集中によりAIが応答できません。しばらく時間をおいてお試しください。"
            else:
                return "Error: The AI is currently overloaded. Please try again later."
        if lang == "ja":
            return f"Error: AIシステムエラーが発生しました。({error_msg})"
        else:
            return f"Error: AI system error occurred. ({error_msg})"


def voice_to_text(audio_path: str, lang: str = "ja") -> str:
    """音声ファイルをテキストに変換する"""
    if not API_KEY:
        return "Gemini API Key is missing. Please check .env file."
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # 音声ファイルをアップロード
        audio_file = genai.upload_file(audio_path)
        
        # 言語に応じた文字起こしプロンプト
        if lang == "ja":
            prompt = "この音声を日本語で文字起こししてください。発話内容のみを出力してください。"
        else:
            prompt = "Transcribe this audio in English. Output only the spoken content."
        
        response = model.generate_content([audio_file, prompt])
        
        # アップロードしたファイルを削除
        genai.delete_file(audio_file.name)
        
        return response.text.strip()
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "Quota exceeded" in error_msg:
            if lang == "ja":
                return "Error: アクセス集中により音声認識ができませんでした。しばらく時間をおいてお試しください。"
            else:
                return "Error: Voice recognition failed due to overload. Please try again later."
        if lang == "ja":
            return f"Error: 音声認識システムエラーが発生しました。({error_msg})"
        else:
            return f"Error: Voice recognition system error occurred. ({error_msg})"
