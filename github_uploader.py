import os
import requests
import json
import base64

# --- 環境変数からGitHub認証情報を取得 ---
# NOTE: 実際の運用では、環境変数やシークレットストアに保存します
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "YOUR_SECRET_TOKEN") # 実際には環境変数を設定する
REPO_OWNER = "kakaomames"
REPO_NAME = "minecraft-data"
GITHUB_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents"
print(f"REPO_NAME:{REPO_NAME}")
print(f"GITHUB_API_URL:{GITHUB_API_URL}")

def get_headers():
    """GitHub APIリクエストに使用する認証ヘッダーを生成する"""
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    return headers
print("GitHub_Headers_Setup")

def get_sha_of_file(file_path: str):
    """既存ファイルのSHAを取得する (更新時に必要)"""
    url = f"{GITHUB_API_URL}/{file_path}"
    headers = get_headers()
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        file_info = response.json()
        print(f"Existing_File_SHA_Found:{file_info.get('sha')}")
        return file_info.get("sha")
    elif response.status_code == 404:
        print(f"File_Not_Found:{file_path}_New_File")
        return None
    else:
        print(f"Error_Getting_SHA:{response.status_code}_{response.text}")
        return None

def upload_file_to_github(file_path: str, content: dict, commit_message: str, branch: str = "main"):
    """
    指定されたJSONデータをGitHubリポジトリにコミット/アップロードする。
    
    Args:
        file_path (str): リポジトリ内のファイルのパス (例: 'BP/entity/super_sheep.json')
        content (dict): アップロードするJSONデータ (mobs.py, item.pyなどの結果)
        commit_message (str): コミットメッセージ
        branch (str): 対象ブランチ
        
    Returns:
        bool: 成功したかどうか
    """
    url = f"{GITHUB_API_URL}/{file_path}"
    headers = get_headers()
    
    # 1. JSONデータを文字列に変換 (カカオマメさんの設定を遵守)
    json_content_string = json.dumps(content, indent=2, ensure_ascii=False)
    
    # 2. Base64エンコード
    content_bytes = json_content_string.encode('utf-8')
    content_encoded = base64.b64encode(content_bytes).decode('utf-8')
    
    # 3. 既存ファイルのSHAを取得 (ファイルの更新か新規作成かを区別するため)
    sha = get_sha_of_file(file_path)

    # 4. アップロードペイロードの構築
    payload = {
        "message": commit_message,
        "content": content_encoded,
        "branch": branch,
    }
    if sha:
        payload["sha"] = sha # 既存ファイルを更新する場合に必要
        
    # 5. APIリクエストの実行
    response = requests.put(url, headers=headers, data=json.dumps(payload, ensure_ascii=False))

    if response.status_code in [200, 201]:
        # 200: 更新, 201: 新規作成
        print(f"File_Successfully_Uploaded/Updated:{file_path}")
        return True
    else:
        print(f"Error_Uploading_File:{response.status_code}_{response.text}")
        return False

# --- 実行例 (仮のデータを使用) ---
# NOTE: 実際に実行するには有効な GITHUB_TOKEN が必要です。

# 1. mobs.pyで整形されたデータ (例)
from mobs import validate_and_format_mob_data # mobs.pyからインポートを想定

client_input_data = {
    "hp": 12,
    "speed": 0.4,
    "families": ["sheep", "animal", "friendly_mob"]
}
MOB_NAME = "super_sheep"
MOB_PATH = f"BP/entity/{MOB_NAME}.json"
COMMIT_MSG = f"feat: Add custom entity {MOB_NAME} via server API"

formatted_data = validate_and_format_mob_data(MOB_NAME, client_input_data)
print(f"Formatted_Data_Ready_for_Upload:{isinstance(formatted_data, dict)}")


# 2. アップローダー関数の呼び出し (コメントアウト: 実際にトークンがないと失敗するため)
"""
if isinstance(formatted_data, dict) and 'error' not in formatted_data:
    upload_success = upload_file_to_github(
        file_path=MOB_PATH, 
        content=formatted_data, 
        commit_message=COMMIT_MSG
    )
    print(f"Upload_Result:{upload_success}")
"""
