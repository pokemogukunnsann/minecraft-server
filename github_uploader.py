import os
import requests
import json
import base64

# --- 環境変数からGitHub認証情報を取得 ---
# NOTE: 実際の運用では、環境変数やシークレットストアに保存します
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "YOUR_SECRET_TOKEN") 
REPO_OWNER = "kakaomames"
REPO_NAME = "minecraft-data"
GITHUB_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents"
print(f"REPO_NAME:{REPO_NAME}")

# --- 他のモジュールからのインポート (整形ロジックを呼び出す場合) ---
from mobs import validate_and_format_mob_data
from item import validate_and_format_item_data
from lang import validate_and_format_lang_data
from block import validate_and_format_block_data
from ai import format_ai_behaviors # mobs.pyにマージされることを想定
from textures import format_rp_entity_texture, format_rp_block_texture
from geometry import format_rp_custom_geometry
from environment import format_world_render_settings, format_world_generation_parameters

print("All_Data_Formatters_Imported")

# --- 共通のヘッダー関数（変更なし） ---
def get_headers():
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    return headers

# --- 修正・追加関数：単一ファイルコミット（再利用のため残す） ---
# ... (get_sha_of_file関数、upload_file_to_github関数は残す) ...

# --- 新規統合関数：全てのデータを処理し、コミットリストを作成する ---

def prepare_files_for_commit(client_input: dict):
    """
    クライアントからの全データを受け取り、GitHubコミット用のファイルリストを生成する。
    
    Args:
        client_input (dict): クライアントから送信された全てのカスタムデータ
        
    Returns:
        list: コミットするファイルのリスト [{'path': '...', 'content': '...', 'encoding': 'base64', 'sha': '...'}, ...]
    """
    commit_files = []
    
    # ----------------------------------------------------
    # 1. モブデータ (BP & RP) の処理
    # ----------------------------------------------------
    if 'mobs' in client_input:
        for mob_name, mob_data in client_input['mobs'].items():
            
            # BP: モブの振る舞い (entity/mob_name.json)
            # AIデータをmobs.pyに統合してBP JSONを生成
            bp_content = validate_and_format_mob_data(mob_name, mob_data)
            
            # RP: モブの見た目 (models/entity/geometry.mob_name.json と client_entity/mob_name.json)
            if 'texture_info' in mob_data:
                # RP Entity JSON
                rp_content = format_rp_entity_texture(mob_name, **mob_data['texture_info']['rp_entity'])
                
                # Geometry JSON
                geometry_content = format_rp_custom_geometry(mob_name, **mob_data['texture_info']['geometry'])

                # ファイルリストに追加
                # RP Entity JSON
                commit_files.append({
                    "path": f"RP/entity/{mob_name}.json",
                    "content": json.dumps(rp_content, indent=2, ensure_ascii=False)
                })
                # Geometry JSON
                commit_files.append({
                    "path": f"RP/models/entity/geometry.{mob_name}.json",
                    "content": json.dumps(geometry_content, indent=2, ensure_ascii=False)
                })

            # BP Entity JSON (最後にエンコードして追加)
            commit_files.append({
                "path": f"BP/entity/{mob_name}.json",
                "content": json.dumps(bp_content, indent=2, ensure_ascii=False)
            })
            print(f"Processed_Mob:{mob_name}")

    # ----------------------------------------------------
    # 2. 言語データ (RP) の処理
    # ----------------------------------------------------
    if 'lang' in client_input:
        lang_data, error = validate_and_format_lang_data(client_input['lang'])
        if lang_data:
            commit_files.append({
                "path": f"RP/texts/ja_JP.lang", # ja_JPファイルに固定して追加
                "content": lang_data
            })
            print("Processed_Lang_File")

    # ----------------------------------------------------
    # 3. マニフェストファイルの処理
    # ----------------------------------------------------
    # マニフェストはRPとBPの両方に必要
    if 'manifest' in client_input:
        # BP Manifest
        bp_manifest = client_input['manifest'].get('BP')
        if bp_manifest:
            # manifest.pyの関数で最終整形することを想定
            bp_manifest_content = json.dumps(bp_manifest, indent=2, ensure_ascii=False)
            commit_files.append({"path": "BP/manifest.json", "content": bp_manifest_content})
            print("Processed_BP_Manifest")
            
        # RP Manifest
        rp_manifest = client_input['manifest'].get('RP')
        if rp_manifest:
            rp_manifest_content = json.dumps(rp_manifest, indent=2, ensure_ascii=False)
            commit_files.append({"path": "RP/manifest.json", "content": rp_manifest_content})
            print("Processed_RP_Manifest")

    # (アイテム、ブロック、環境データなども同様に処理を続ける)
    
    return commit_files


# --- GitHub APIへのコミット実行関数（新規/要修正） ---

def unified_commit_to_github(commit_files: list, commit_message: str, branch: str = "main"):
    """
    複数のファイルを一つのコミットとしてGitHubにプッシュする。
    
    NOTE: GitHubのContents APIは1ファイルずつしか処理できないため、
          ここではGit Data API (Tree, Commit) を使用する、より高度な方法が必要です。
          しかし、シンプルな実装として、ここではContents APIのputリクエストをファイル数分繰り返します。
    """
    
    success_count = 0
    
    for file_data in commit_files:
        path = file_data['path']
        content = file_data['content']
        
        # Base64エンコード
        content_bytes = content.encode('utf-8')
        content_encoded = base64.b64encode(content_bytes).decode('utf-8')
        
        # 既存ファイルのSHAを取得
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
            print(f"File_Commit_Error:{path}_{response.status_code}_{response.text[:100]}...")
            
    return success_count == len(commit_files) # 全てのファイルが成功したかどうか

# --- 実行例 (仮のデータを使用) ---
# NOTE: 実際に実行するには有効な GITHUB_TOKEN が必要です。
"""
# サーバーAPIに送られてきたデータ全体を想定
full_client_data = {
    "manifest": {
        "BP": {"format_version": 2, "header": {"name": "BP", ...}, "modules": [...]},
        "RP": {"format_version": 2, "header": {"name": "RP", ...}, "modules": [...]},
    },
    "mobs": {
        "super_sheep": {
            "hp": 12, "speed": 0.4, "families": ["sheep", "animal"],
            "texture_info": {
                "rp_entity": {"texture_path": "...", "model_id": "geometry.super_sheep"},
                "geometry": {"texture_width": 64, "texture_height": 64, "bone_data": []}
            }
        }
    },
    "lang": {
        "item.custom:super_sword": "超絶すごい剣！"
    }
}

files_to_commit = prepare_files_for_commit(full_client_data)
print(f"Total_Files_Prepared:{len(files_to_commit)}")

# コミット実行（コメントアウト）
# unified_commit_to_github(files_to_commit, "feat: Initial custom pack upload")
"""
