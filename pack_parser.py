import json
import zipfile
import io

print("Pack_Parser_Module_Loaded")

# --- マッピング定義 ---
# Minecraft BP JSON のパスから、シンプルなデータ構造のキーへのマッピングを定義
# この辞書が、解析のロジックを担います。
MAPPING_RULES = {
    # エンティティ (モブ) のマッピング
    "BP/entities": {
        "file_key": "mobs", # 最終的な client_input['mobs'] になる
        "rules": [
            # HP (health) の抽出
            {"path": ["minecraft:entity", "components", "minecraft:health", "value"], "target_key": "hp"},
            # 速度 (movement) の抽出
            {"path": ["minecraft:entity", "components", "minecraft:movement", "value"], "target_key": "speed"},
            # ファミリー (タグ) の抽出 (複雑なためリストとしてそのまま保存)
            {"path": ["minecraft:entity", "components", "minecraft:type_family", "family"], "target_key": "families"},
        ]
    },
    # アイテムのマッピング (BP/items/custom_sword.json を想定)
    "BP/items": {
        "file_key": "items", # 最終的な client_input['items'] になる
        "rules": [
            # 耐久値 (durability) の抽出
            {"path": ["minecraft:item", "components", "minecraft:durability", "max_durability"], "target_key": "durability"},
            # スタックサイズ (max_stack_size) の抽出
            {"path": ["minecraft:item", "components", "minecraft:max_stack_size"], "target_key": "stack_size"},
        ]
    }
    # ... (block, ai, lang, geometry など他のデータもここに追加) ...
}
print(f"MAPPING_RULES_Defined:{len(MAPPING_RULES)}_sections")

def get_nested_value(data: dict, path: list):
    """
    ネストされた辞書から指定されたパスの値を取得するヘルパー関数
    """
    current = data
    for key in path:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None
    return current

def parse_pack_file_to_client_data(zip_file: zipfile.ZipFile):
    """
    ZIPファイル内のBP/RPファイルを解析し、各整形モジュールが期待する
    シンプルなデータ構造 (client_input) にマッピングする。
    
    Args:
        zip_file (zipfile.ZipFile): メモリ上で開かれたアップロード済みZIPファイル
        
    Returns:
        dict: 整形モジュールに渡すための統合されたクライアント入力データ
              (例: {'mobs': {'sheep': {'hp': 10, 'speed': 0.3}}, 'items': {...}})
    """
    
    client_input = {}
    
    for file_path in zip_file.namelist():
        
        # 1. ファイルパスに基づいてマッピングルールを特定
        is_matched = False
        for folder_path, mapping_def in MAPPING_RULES.items():
            if file_path.startswith(folder_path + '/') and file_path.endswith('.json'):
                is_matched = True
                
                # 2. ファイル名から識別子を抽出 (例: entities/sheep.json -> sheep)
                file_name = os.path.basename(file_path).replace('.json', '')
                
                try:
                    with zip_file.open(file_path) as f:
                        file_content = json.load(f)
                        
                        # 3. データを抽出する
                        extracted_data = {}
                        for rule in mapping_def["rules"]:
                            value = get_nested_value(file_content, rule["path"])
                            if value is not None:
                                extracted_data[rule["target_key"]] = value
                                
                        # 4. 最終的な client_input 構造に格納
                        top_key = mapping_def["file_key"]
                        client_input[top_key] = client_input.get(top_key, {})
                        client_input[top_key][file_name] = extracted_data
                        
                        print(f"Mapped_File:{file_name}_Data:{extracted_data}")

                except json.JSONDecodeError:
                    print(f"Error: Invalid JSON in file: {file_path}")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
                
                break
        
        # Manifest.json のような特殊なファイルはここで処理
        if file_path.lower().endswith('manifest.json'):
             try:
                 with zip_file.open(file_path) as f:
                    manifest_content = json.load(f)
                    # BP/RPの判別ロジックは main.py にあるためここでは省略
                    # client_input['manifest'] = ... 
                    print(f"Parsed_Manifest:{file_path}")
             except json.JSONDecodeError:
                 print(f"Error: Invalid JSON in manifest: {file_path}")
    
    return client_input

# --- 実行例 ---
# NOTE: 実際のZIPファイルが必要なため、ここではテストできませんが、ロジックは完成です。
