import json
import re

# 言語データの検証 (必須ではないが、キー形式のチェックを行う)
LANG_KEY_PATTERN = re.compile(r"^[a-z0-9_.:]+$")
print(f"LANG_KEY_PATTERN_COMPILED:{LANG_KEY_PATTERN.pattern}")

def validate_and_format_lang_data(client_data: dict):
    """
    クライアントデータを検証し、Minecraftの.langファイル形式の文字列に整形する。
    
    Args:
        client_data (dict): クライアントから送信された言語キーと値のペア
                          (例: {'item.custom:super_sword': 'Super Sword'})
        
    Returns:
        tuple: (整形された.lang文字列, 検証エラー)
    """
    
    formatted_lines = []
    
    for key, value in client_data.items():
        # 1. キー形式の検証 (基本的な英数字と記号のチェック)
        if not LANG_KEY_PATTERN.match(key):
            return (None, {"error": f"Invalid language key format: {key}"})
        
        # 2. 値の処理 (改行やエスケープ処理は一旦無視し、基本のテキストとして扱う)
        #    ただし、値に等号記号 (=) が含まれているとファイルが破損するため、その確認は必要
        if "=" in str(value):
            # 通常、値に等号は含めないが、含める場合はエスケープが必要になるためエラーとする
            return (None, {"error": f"Value contains prohibited '=' character: {value}"})

        # 3. .lang 形式 (key=value) に整形
        #    日本語などの多バイト文字も扱えるようにする
        line = f"{key}={value}"
        formatted_lines.append(line)
    
    # 全ての行を改行で結合し、.lang ファイルのコンテンツとして返す
    lang_content = "\n".join(formatted_lines)
    print("Language_Content_Formatted")
    
    return (lang_content, None)

# --- 実行例 ---

# クライアントからカスタム要素の多言語データが送られてきたと仮定
client_lang_data = {
    "item.custom:super_sword": "超絶すごい剣！🗡️",
    "entity.minecraft:super_sheep.name": "スーパーひつじ",
    "tile.custom:cool_block.name": "クールなブロック"
}
print(f"client_lang_data:{client_lang_data}")

# 整形関数の呼び出し
lang_content, error = validate_and_format_lang_data(client_lang_data)

if error:
    print(f"Error_Found:{error}")
else:
    print(f"Lang_Content_Ready_for_Upload:\n{lang_content}")
# 出力例: Lang_Content_Ready_for_Upload:
# item.custom:super_sword=超絶すごい剣！🗡️
# entity.minecraft:super_sheep.name=スーパーひつじ
# tile.custom:cool_block.name=クールなブロック
