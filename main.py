from flask import Flask, request, render_template_string, jsonify
import zipfile
import io
import os
import json

# --- 外部モジュールのインポート (今回は構造物のNBTは除外して、JSON/LANGのみを扱う) ---
# NOTE: 実際の処理では、全ての整形モジュール (mobs.py, item.py, lang.py, ...) をインポートします
from github_uploader import prepare_files_for_commit, unified_commit_to_github # GitHub連携モジュール

app = Flask(__name__)
print(f"Flask_App_Initialized: {app.name}")

# --- HTMLフォームの定義 ---
# GETリクエスト時に返す、パックアップロード用のシンプルなHTML
PACK_UPLOAD_HTML = """
<!doctype html>
<title>Minecraft Pack Uploader</title>
<h1>マイクラ アドオンパック アップロード</h1>
<form method="POST" enctype="multipart/form-data">
    <input type="file" name="pack_file">
    <input type="text" name="commit_message" placeholder="コミットメッセージを入力">
    <input type="submit" value="アップロードしてGitHubにコミット">
</form>
"""
print("PACK_UPLOAD_HTML_Defined")

# --- メインルーティング ---

@app.route('/', methods=['GET', 'POST'])
def handle_pack():
    if request.method == 'GET':
        # type=GET の時: pack.html (Python内の文字列) を返す
        print("Received_GET_Request")
        return render_template_string(PACK_UPLOAD_HTML)

    elif request.method == 'POST':
        # type=POST の時: ファイルを受け取り、処理する
        print("Received_POST_Request")
        
        # 1. ファイルとコミットメッセージの取得
        if 'pack_file' not in request.files:
            return jsonify({"error": "No pack_file part in the request"}), 400
        
        uploaded_file = request.files['pack_file']
        commit_message = request.form.get('commit_message', 'feat: Uploaded new pack via web server')
        
        if uploaded_file.filename == '':
            return jsonify({"error": "No selected file"}), 400
            
        if not uploaded_file.filename.endswith(('.zip', '.mcpack')):
            return jsonify({"error": "Invalid file type. Only .zip or .mcpack allowed."}), 400
        
        # 2. ファイルの解凍と解析
        try:
            # ファイルをメモリ上で操作するためのバイトストリームに変換
            file_stream = io.BytesIO(uploaded_file.read())
            
            # ZIPファイルとして開く
            with zipfile.ZipFile(file_stream, 'r') as zf:
                
                # --- ここが最も重要なステップ：解凍したファイルを各 *.py に渡す ---
                
                # 解凍したデータ構造を保持する辞書
                pack_data = {} 
                
                # ZIP内のファイルリストを読み込む
                for name in zf.namelist():
                    # manifest.json のような重要なファイルを読み込む
                    if name.lower().endswith('manifest.json'):
                        with zf.open(name) as f:
                            # manifest.py の整形関数を呼び出す代わりに、ここではデータをそのまま解析すると仮定
                            manifest_content = json.load(f)
                            pack_type = "BP" if "data" in manifest_content.get("modules", [{}])[0].get("type", "").lower() else "RP"
                            # pack_data の構造を定義
                            pack_data['manifest'] = pack_data.get('manifest', {})
                            pack_data['manifest'][pack_type] = manifest_content
                            print(f"Parsed_Manifest_Type:{pack_type}")
                            
                    # 例: langファイルの内容を抽出
                    elif name.lower().endswith('.lang'):
                        with zf.open(name) as f:
                            # lang.py の整形関数が後に使用できる形式に変換
                            # NOTE: .langをDictに変換する処理は複雑なので、ここでは単純にコンテンツとして保存
                            lang_content = f.read().decode('utf-8')
                            # pack_data['lang'] = lang_content # 適切なデータ構造に保存
                            print(f"Found_Lang_File:{name}")

                    # ... (他の BP/RP ファイルの解析ロジックが続く) ...
                    
                # 3. 各pyにデータを渡して整形・コミットリストを作成
                # NOTE: ここでは、解凍したデータからクライアントデータ (full_client_data) を生成する複雑なロジックが必要
                
                # 仮のデータ構造を作成し、GitHubアップローダーに渡す
                # 実際には、pack_dataから整形モジュールを呼び出す
                dummy_client_data = {
                    "manifest": pack_data.get('manifest', {}),
                    # ... (他の整形済みデータ) ...
                }
                
                files_to_commit = prepare_files_for_commit(dummy_client_data)
                print(f"Files_Prepared_for_Commit:{len(files_to_commit)}")

                # 4. GitHubへのコミットを実行
                # commit_success = unified_commit_to_github(files_to_commit, commit_message)
                # NOTE: 実行には有効なGITHUB_TOKENが必要です
                commit_success = True # 仮に成功とする

                if commit_success:
                    return jsonify({"status": "success", "message": f"Pack uploaded and {len(files_to_commit)} files committed to GitHub.", "commit_msg": commit_message}), 200
                else:
                    return jsonify({"status": "error", "message": "Files prepared but GitHub commit failed."}), 500

        except zipfile.BadZipFile:
            return jsonify({"error": "Invalid ZIP or MCPACK file format."}), 400
        except Exception as e:
            # デバッグ用にエラーを出力
            print(f"An_Unexpected_Error_Occurred:{e}")
            return jsonify({"error": f"Internal server error during processing: {str(e)}"}), 500


# サーバー起動コマンド (開発用)
 if __name__ == '__main__':
     app.run(debug=True)
