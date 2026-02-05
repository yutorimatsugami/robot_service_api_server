import warnings
# Suppress Google Generative AI deprecation warning
warnings.filterwarnings("ignore", message=".*All support for the `google.generativeai` package has ended.*")

import google.generativeai as genai
import os
from dotenv import load_dotenv
from prompt import build_chat_prompt
from sqlalchemy.orm import Session
import crud
import json
import re

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)

# Tool Definitions
def get_timetable_info(station_name: str):
    """
    Get train timetable information for a specific destination station from Osaka Station.
    JR大阪駅から指定された行き先駅への時刻表情報を取得します。
    
    Args:
        station_name: The name of the destination station (e.g., "京都", "三ノ宮", "神戸"). 行き先の駅名。
    """
    pass

# generate_chat_responseの中で tools=[get_timetable_info] として使用する
# timetable_tool 辞書変数は不要になったため削除

def clean_text_for_speech(text: str) -> str:
    """音声読み上げ用にテキストをクリーニングする（Markdown記号の削除）"""
    if not text:
        return ""
    
    # Remove markdown bold/italic (** or *)
    text = re.sub(r'\*\*|__', '', text)
    # Remove list bullets (* or - at start of line)
    text = re.sub(r'(?m)^[\s]*[\*\-]\s+', '', text)
    # Remove markdown headers (#)
    text = re.sub(r'(?m)^#+\s*', '', text)
    
    return text.strip()



def generate_chat_response(message: str, db: Session = None, context: str = "", lang: str = "ja"):
    """チャット応答を生成する (Function Calling対応 - generate_content版)"""
    if not API_KEY:
        return "Gemini API Key is missing. Please check .env file."
    
    try:
        # ツール定義を含めてモデルを初期化
        # tool_configでFunction Callingの挙動を制御
        tool_config = {'function_calling_config': {'mode': 'AUTO'}}
        model = genai.GenerativeModel('gemini-2.5-flash', tools=[get_timetable_info], tool_config=tool_config)
        
        # プロンプト構築
        # prompt.pyのbuild_chat_promptはContext重視の指示が含まれるため、
        # Function Calling用に独自に構築する。
        
        system_instructions = f"""You are a helpful station guide robot.
Your primary task is to provide train timetable information using the 'get_timetable_info' tool.
If the user asks about train schedules, departure times, destinations, or platform numbers, YOU MUST USE THE TOOL.
Do not answer train-related questions from your internal knowledge or context below.

Data Usage Rules:
- Tool usage is PRIORITY #1 for train inquiries.
- "Context Information" below is PRIORITY #2 (only for shop/facility info, NOT for trains).

Response Rules:
- When providing train info from the tool, ALWAYS include:
  1. Departure Time
  2. Platform Number (乗り場)
  3. Destination
- Keep responses concise and natural for speech.
- Do not use markdown formatting like asterisks (**) or bullet points. Use simple sentences.
- Respond in { "Japanese" if lang == "ja" else "English" }.
"""
        
        full_prompt = f"""{system_instructions}

Context Information (Use only for shops/facilities):
{context}

User Question: {message}
"""

        
        print(f"DEBUG: Prompt: {full_prompt[:100]}...")

        # 1. 最初のリクエスト (ツール使用の判断)
        response = model.generate_content(full_prompt)
        
        # Function Callが返ってきたか確認
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.function_call:
                    fc = part.function_call
                    print(f"DEBUG: Function Call detected: {fc.name}({fc.args})")
                    
                    if fc.name == 'get_timetable_info':
                        station_name = fc.args['station_name']
                        
                        # DB検索実行
                        result_text = "Database connection error."
                        if db:
                            from datetime import datetime
                            now_str = datetime.now().strftime("%H:%M")
                            print(f"DEBUG: Querying DB for {station_name} at {now_str}")
                            timetables = crud.get_timetable(db, station_name=station_name, time=now_str, limit=5)
                            
                            if timetables:
                                result_text = f"Timetable for {station_name} (from Osaka, Current Time: {now_str}):\n"
                                for t in timetables:
                                    result_text += f"- {t.osaka_departure_time} Dep, Platform {t.osaka_platform}, {t.train_type}, Dest: {t.destination}\n"
                            else:
                                result_text = f"No trains found for {station_name} after {now_str}."
                        
                        print(f"DEBUG: Tool Result: {result_text}")

                        # 2. ツール実行結果を含めて再度リクエスト (Function Response)
                        # generate_contentでは履歴を維持しないので、過去のやり取りとツール結果をまとめて送る必要がある
                        # ここでは簡易的に、ツール結果をコンテキストとして追加して再度プロンプトを送る
                        
                        function_context = f"""
                        \n--- TOOL EXECUTION RESULT ---
                        Tool 'get_timetable_info' was called with station_name='{station_name}'.
                        Result:
                        {result_text}
                        -----------------------------
                        Use this result to answer the user's question.
                        """
                        
                        # ツール結果を含んだ新しいプロンプトで再生成
                        final_prompt = full_prompt + function_context
                        final_response = model.generate_content(final_prompt)
                        return clean_text_for_speech(final_response.text)

        # Function Callがなければそのまま返す
        # Function Callがなければそのまま返す
        return clean_text_for_speech(response.text)

    except Exception as e:
        error_msg = str(e)
        print(f"ERROR: {error_msg}")
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
