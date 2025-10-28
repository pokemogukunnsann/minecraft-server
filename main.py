from flask import Flask, request, render_template_string, jsonify
import zipfile
import io
import os
import json

# --- 外部モジュールのインポート ---
from pack_parser import parse_pack_file_to_client_data # 新しい解析モジュール
from github_uploader import prepare_files_for_commit, unified_commit_to_github 

app = Flask(__name__)
print(f"Flask_App_Initialized: {app.name}")

# --- HTMLフォームの定義 (変更なし) ---
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
        print("Received_GET_Request")
        return render_template_string(PACK_UPLOAD_HTML)

    elif request.method == 'POST':
        print("Received_POST_Request")
        
        # 1. ファイルとコミットメッセージの取得 (エラーチェックは省略)
        uploaded_file = request.files['pack_file']
        commit_message = request.form.get('commit_message', 'feat: Uploaded new pack via web server')
        
        if uploaded_file.filename == '':
            return jsonify({"error": "ファイルが選択されていません。"}), 400
            
        # 2. ファイルの解凍と解析
        try:
            # ファイルをメモリ上で操作するためのバイトストリームに変換
            file_stream = io.BytesIO(uploaded_file.read())
            
            # ZIPファイルとして開く
            with zipfile.ZipFile(file_stream, 'r') as zf:
                
                # --- [統合ポイント 1] pack_parser を呼び出し、シンプルなデータ構造にマッピング ---
                # この結果が、以前作成した整形モジュール群が期待する形式です。
                client_input_data = parse_pack_file_to_client_data(zf)
                print(f"Pack_Parsed_Successfully._Keys:{list(client_input_data.keys())}")
                
                if not client_input_data:
                     return jsonify({"status": "warning", "message": "パックを解析しましたが、コミット対象となるデータ（モブやアイテムなど）は見つかりませんでした。"}), 200

                # 3. 整形・コミットリストを作成
                # --- [統合ポイント 2] github_uploader の prepare 関数に解析結果を渡す ---
                files_to_commit = prepare_files_for_commit(client_input_data)
                print(f"Total_Files_Prepared_for_Commit:{len(files_to_commit)}")

                if not files_to_commit:
                    return jsonify({"status": "warning", "message": "解析されたデータから、コミット可能なファイルは生成されませんでした。"}), 200

                # 4. GitHubへのコミットを実行
                # NOTE: 実際に実行するには有効なGITHUB_TOKENが必要です
                commit_success = unified_commit_to_github(files_to_commit, commit_message)

                if commit_success:
                    return jsonify({
                        "status": "success", 
                        "message": f"アドオンパックが解析され、{len(files_to_commit)} 個のファイルがGitHubにコミットされました。🎉", 
                        "commit_msg": commit_message
                    }), 200
                else:
                    return jsonify({"status": "error", "message": "GitHubへのコミット中にエラーが発生しました。トークンまたはAPIを確認してください。"}), 500

        except zipfile.BadZipFile:
            return jsonify({"error": "無効なZIPまたはMCPACKファイル形式です。"}), 400
        except Exception as e:
            # エラーをログに出力し、ユーザーに通知
            import traceback
            traceback.print_exc()
            return jsonify({"error": f"予期せぬサーバーエラーが発生しました: {str(e)}"}), 500

# サーバー起動コマンド (開発用)
 if __name__ == '__main__'
  app.run(debug=True, host='0.0.0.0', port=5000)
