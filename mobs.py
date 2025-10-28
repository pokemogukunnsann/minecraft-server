import json
import uuid
import re

# モブ定義JSONのバージョン
FORMAT_VERSION = "1.10.0" 
print(f"FORMAT_VERSION:{FORMAT_VERSION}")

# モブデータ生成時の必須コンポーネントテンプレート
MOB_TEMPLATE = {
    "format_version": FORMAT_VERSION,
    "minecraft:entity": {
        "description": {
            # identifierは外部から注入
            "is_spawnable": True,
            "is_summonable": True,
            "is_experimental": False
        },
        "components": {
            # 必須コンポーネントはここで定義し、値を外部から注入
            "minecraft:type_family": {}, 
            "minecraft:health": {},
            "minecraft:movement": {},
            "minecraft:collision_box": {
                "width": 0.9, # 衝突判定ボックスは共通値を使用
                "height": 1.3
            },
            "minecraft:physics": {},
            "minecraft:nameable": {},
            
            # 基本的なAI (AIの優先度は固定値とする)
            "minecraft:behavior.float": {"priority": 0},
            "minecraft:behavior.random_stroll": {"priority": 7, "speed_multiplier": 0.8},
        }
        # component_groups や events はここでは省略
    }
}
print("MOB_TEMPLATE_LOADED")

def validate_and_format_mob_data(mob_name: str, client_data: dict):
    """
    クライアントデータを検証し、Minecraft BPのentities/*.json形式に整形する。
    
    Args:
        mob_name (str): モブの内部識別子 (例: 'sheep')
        client_data (dict): クライアントから送信されたデータ (例: {'hp': 10, 'speed': 0.3, 'families': ['animal']})
        
    Returns:
        dict: 整形されたBP JSONデータ、または検証エラー
    """
    
    # 1. データの検証 (必須項目のチェック)
    required_keys = ['hp', 'speed', 'families']
    for key in required_keys:
        if key not in client_data:
            return {"error": f"Missing required key: {key}"}
    
    if not isinstance(client_data['families'], list) or not client_data['families']:
        return {"error": "Families must be a non-empty list."}
    
    # 2. テンプレートのコピーとidentifierの設定
    final_json = MOB_TEMPLATE.copy()
    
    # 内部識別子 (例: minecraft:sheep) を設定
    identifier = f"minecraft:{mob_name}"
    final_json["minecraft:entity"]["description"]["identifier"] = identifier
    print(f"Identifier_Set:{identifier}")
    
    # 3. クライアントデータでテンプレートを更新
    components = final_json["minecraft:entity"]["components"]

    # --- HPの設定 ---
    hp_value = int(client_data['hp'])
    components["minecraft:health"] = {
        "value": hp_value,
        "max": hp_value
    }
    print(f"Health_Set:{hp_value}")
    
    # --- 速度の設定 ---
    speed_value = float(client_data['speed'])
    # random_strollの速度も更新
    components["minecraft:movement"]["value"] = speed_value
    components["minecraft:behavior.random_stroll"]["speed_multiplier"] = speed_value
    print(f"Speed_Set:{speed_value}")

    # --- Familyの設定 ---
    family_list = client_data['families']
    components["minecraft:type_family"]["family"] = family_list
    print(f"Families_Set:{family_list}")
    
    return final_json

# --- 実行例 ---

# クライアントから新しい羊の設定が送られてきたと仮定
client_input_data = {
    "hp": 12,                # デフォルトの8から12に増加
    "speed": 0.4,            # デフォルトの0.2から0.4に増加
    "families": ["sheep", "animal", "friendly_mob"] # カスタムファミリーの追加
}
print(f"client_input_data:{client_input_data}")

# 整形関数の呼び出し
formatted_sheep_bp = validate_and_format_mob_data("super_sheep", client_input_data)
print(f"formatted_sheep_bp_identifier:{formatted_sheep_bp['minecraft:entity']['description']['identifier'] if isinstance(formatted_sheep_bp, dict) and 'error' not in formatted_sheep_bp else 'Error'}")
# 出力例: formatted_sheep_bp_identifier:minecraft:super_sheep

# 整形後のJSON全体を出力 (バックスラッシュの扱いに注意しながら整形)
formatted_output = json.dumps(formatted_sheep_bp, indent=2, ensure_ascii=False)
print(f"Formatted_JSON:\n{formatted_output}")
