"""
Prompt Templates for Gemini API
プロンプトテンプレートの管理ファイル
"""


def get_system_prompt(lang: str = "ja") -> str:
    """
    言語に応じたシステムプロンプトを返す
    
    Args:
        lang: 言語コード ("ja" or "en")
    
    Returns:
        システムプロンプト文字列
    """
    lang_instruction = "Respond in Japanese" if lang == "ja" else "Respond in English"
    
    return f"""You are a helpful station guide robot.
Use the following context information (shops, facilities) to answer the user's question if relevant.
If the context doesn't have the answer, answer naturally as a helpful assistant.

IMPORTANT: Your responses will be read aloud by a robot and displayed on screen.
- Do NOT use markdown formatting (no asterisks, hashes, backticks, etc.)
- Use plain text only
- Keep responses concise and natural for speech
- {lang_instruction}"""


def build_chat_prompt(message: str, context: str = "", lang: str = "ja") -> str:
    """
    チャット用のプロンプトを構築する
    
    Args:
        message: ユーザーからのメッセージ
        context: 店舗・施設などのコンテキスト情報
        lang: 言語コード ("ja" or "en")
    
    Returns:
        構築されたプロンプト文字列
    """
    return f"""{get_system_prompt(lang)}

Context Information:
{context}

User Question: {message}
"""
