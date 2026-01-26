"""
Prompt Templates for Gemini API
プロンプトテンプレートの管理ファイル
"""

# システムプロンプト: 案内ロボットとしての基本的な振る舞いを定義
STATION_GUIDE_SYSTEM_PROMPT = """You are a helpful station guide robot.
Use the following context information (shops, facilities) to answer the user's question if relevant.
If the context doesn't have the answer, answer naturally as a helpful assistant.

IMPORTANT: Your responses will be read aloud by a robot and displayed on screen.
- Do NOT use markdown formatting (no asterisks, hashes, backticks, etc.)
- Use plain text only
- Keep responses concise and natural for speech
- Respond in Japanese"""


def build_chat_prompt(message: str, context: str = "") -> str:
    """
    チャット用のプロンプトを構築する
    
    Args:
        message: ユーザーからのメッセージ
        context: 店舗・施設などのコンテキスト情報
    
    Returns:
        構築されたプロンプト文字列
    """
    return f"""{STATION_GUIDE_SYSTEM_PROMPT}

Context Information:
{context}

User Question: {message}
"""


# 将来的に追加するプロンプトの例
# GREETING_PROMPT = "..."
# FAREWELL_PROMPT = "..."
