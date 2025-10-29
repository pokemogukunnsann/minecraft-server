import requests
import base64
import json
import os
# --- 修正点: 必要な整形モジュールを全てインポート ---
# NOTE: 実際にはこれらのファイルに適切な整形関数が定義されている必要があります。
# 今回は関数が存在すると仮定します。
from mobs import format_mob_data_for_bp 
from items import format_item_data_for_bp
from blocks import format_block_data_for_bp
from structure import process_structure_data 
from lang import format_lang_data_for_rp

# --- 定数設定 ---
GITHUB_OWNER = os.environ.get("GITHUB_OWNER", "kakaomame") 
GITHUB_REPO = os.environ.get("GITHUB_REPO", "minecraft-data")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    print("WARNING: GITHUB_TOKEN environment variable is not set. Commit functionality will fail.")
else:
    print("GITHUB_TOKEN_Found")

GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents"
print(f"GITHUB_API_URL:{GITHUB_API_URL}")


def get_headers():
    """GitHub APIリクエストに必要なヘッダーを生成する。"""
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    return headers


def get_sha_of_file(path: str):
    """GitHub上の既存ファイルのSHA (バージョン識別子) を取得する。"""
    url = f"{GITHUB_API_URL}/{path}"
    response = requests.get(url, headers=get_headers())
    
    if response.status_code == 200:
        sha = response.json().get("sha")
        print(f"SHA_Found_for:{path}_SHA:{sha}")
        return sha
    else:
        if response.status_code != 404:
            print(f"Error_Fetching_SHA_for:{path}_Status:{response.status_code}")
        return None


def prepare_files_for_commit(client_input: dict) -> list:
    """
    クライアントからの整形済みデータを受け取り、GitHub APIにコミットするための
    ファイルリスト（パスとコンテンツ）を生成する。
    """
    
    commit_files = [] 
    
    # JSON化処理の共通関数 (バックスラッシュを維持するカスタム処理はjson.dumpsのensure_ascii=Falseで対応)
    def add_json_file(top_key, sub_folder, format_func):
        if top_key in client_input:
            for name, data in client_input[top_key].items():
                # データを整形関数に渡して最終的なJSONデータを得る
                final_json_data = format_func(name, data) 
                
                path = f"BP/{sub_folder}/{name}.json" 
                
                # NOTE: ユーザー設定により、バックスラッシュはそのまま維持（ensure_ascii=False）
                commit_files.append({
                    "path": path,
                    "content": json.dumps(final_json_data, indent=4, ensure_ascii=False),
                    "is_binary": False
                })
                print(f"Prepared_JSON_File:{path}")
    
    
    # 1. マニフェストファイルの処理 (特殊ケース)
    if 'manifest' in client_input:
        for pack_type, content in client_input['manifest'].items():
            path = f"{pack_type}/manifest.json" 
            commit_files.append({
                "path": path,
                "content": json.dumps(content, indent=4, ensure_ascii=False),
                "is_binary": False
            })
            print(f"Prepared_Manifest:{path}")

    # 2. .langファイルの処理 (特殊ケース - JSONではない)
    if 'lang' in client_input:
        for lang_code, data in client_input['lang'].items():
            # lang.pyの整形関数を呼び出し、テキストコンテンツを得る
            final_lang_content = format_lang_data_for_rp(lang_code, data)
            
            path = f"RP/texts/{lang_code}.lang" 
            commit_files.append({
                "path": path,
                "content": final_lang_content, # .langファイルはJSONではない
                "is_binary": False
            })
            print(f"Prepared_Lang:{path}")
            
    # 3. モブデータの処理
    add_json_file('mobs', 'entities', format_mob_data_for_bp)
            
    # 4. アイテムデータの処理
    add_json_file('items', 'items', format_item_data_for_bp)
    
    # 5. ブロックデータの処理
    add_json_file('blocks', 'blocks', format_block_data_for_bp)

    # ----------------------------------------------------
    # 6. 構造物データ (BP) の処理 (NBTバイナリ)
    # ----------------------------------------------------
    if 'structures' in client_input:
        for struct_name, struct_data in client_input['structures'].items():
            # structure.py を呼び出し、NBTバイナリ（Base64エンコード済み）を取得
            nbt_for_upload, error = process_structure_data(struct_name, struct_data, action='to_nbt')
            
            if nbt_for_upload and 'content_base64' in nbt_for_upload:
                # NBTバイナリはすでにBase64エンコード済み
                commit_files.append({
                    "path": nbt_for_upload["path"],
                    "content": nbt_for_upload["content_base64"], 
                    "is_binary": True 
                })
                print(f"Prepared_Structure:{struct_name}_As_Binary")
            elif error:
                print(f"Structure_Conversion_Error_for:{struct_name}_{error}")
            
    return commit_files


def unified_commit_to_github(commit_files: list, commit_message: str, branch: str = "main"):
    """
    複数のファイルを一つのコミットとしてGitHubにプッシュする。（バイナリ対応）
    """
    
    # ... (GitHubコミットロジックは変更なし。以前のコードと同一です。) ...
    if not GITHUB_TOKEN:
        print("Commit_Failed: GITHUB_TOKEN is missing.")
        return False
        
    success_count = 0
    
    for file_data in commit_files:
        path = file_data['path']
        content = file_data['content']
        is_binary = file_data.get('is_binary', False) 
        
        if is_binary:
            content_encoded = content
            print(f"Content_Type:Binary_{path}")
        else:
            content_bytes = content.encode('utf-8')
            content_encoded = base64.b64encode(content_bytes).decode('utf-8')
            print(f"Content_Type:Text/JSON_{path}")

        sha = get_sha_of_file(path)
        
        payload = {
            "message": commit_message,
            "content": content_encoded,
            "branch": branch,
        }
        if sha:
            payload["sha"] = sha 
            
        url = f"{GITHUB_API_URL}/{path}"
        response = requests.put(url, headers=get_headers(), data=json.dumps(payload, ensure_ascii=False))

        if response.status_code in [200, 201]:
            print(f"File_Commit_Success:{path}")
            success_count += 1
        else:
            print(f"File_Commit_Error:{path}_Status:{response.status_code}_Response:{response.text[:100]}...")
            
    return success_count == len(commit_files)

# --- 実行例 (コメントアウト) ---
# if __name__ == '__main__':
#     # 実際には main.py から渡される
#     test_client_data = {
#         # ... テストデータ ...
#     }
    
#     # files = prepare_files_for_commit(test_client_data)
#     # unified_commit_to_github(files, "Test Commit from Python Server")
