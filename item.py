import json
import uuid

# アイテム定義JSONのバージョン
FORMAT_VERSION = "1.10.0"
print(f"ITEM_FORMAT_VERSION:{FORMAT_VERSION}")

# アイテムデータ生成時の必須コンポーネントテンプレート
ITEM_TEMPLATE = {
    "format_version": FORMAT_VERSION,
    "minecraft:item": {
        "description": {
            # identifierは外部から注入
        },
        "components": {
            # 全てのアイテムに共通で必要な基本コンポーネントを定義
            "minecraft:max_stack_size": 64, 
            "minecraft:icon": {},
            "minecraft:hand_equipped": False,
            "minecraft:foil": False,
        }
    }
}
print("ITEM_TEMPLATE_LOADED")

def validate_and_format_item_data(item_name: str, client_data: dict):
    """
    クライアントデータを検証し、Minecraft BPのitems/*.json形式に整形する。
    
    Args:
        item_name (str): アイテムの内部識別子 (例: 'custom_sword')
        client_data (dict): クライアントから送信されたデータ (例: {'attack': 7, 'durability': 100, 'stack_size': 1})
        
    Returns:
        dict: 整形されたBP JSONデータ、または検証エラー
    """
    
    # 1. データの検証 (必須項目のチェック)
    required_keys = ['stack_size']
    for key in required_keys:
        if key not in client_data:
            return {"error": f"Missing required key: {key}"}
    
    # 2. テンプレートのコピーとidentifierの設定
    final_json = ITEM_TEMPLATE.copy()
    
    # 内部識別子 (例: custom:custom_sword) を設定
    identifier = f"custom:{item_name}"
    final_json["minecraft:item"]["description"]["identifier"] = identifier
    print(f"Identifier_Set:{identifier}")
    
    # 3. クライアントデータでテンプレートを更新
    components = final_json["minecraft:item"]["components"]

    # --- スタックサイズの設定 ---
    components["minecraft:max_stack_size"] = int(client_data['stack_size'])
    print(f"Stack_Size_Set:{components['minecraft:max_stack_size']}")
    
    # --- 耐久値の設定 (オプション) ---
    if 'durability' in client_data and client_data['durability'] > 0:
        durability_value = int(client_data['durability'])
        components["minecraft:durability"] = {
            "max_durability": durability_value
        }
        print(f"Durability_Set:{durability_value}")

    # --- 攻撃力の設定 (オプション) ---
    if 'attack' in client_data and client_data['attack'] > 0:
        attack_damage = float(client_data['attack'])
        # ツールや武器のコンポーネントを設定
        components["minecraft:damage"] = attack_damage
        components["minecraft:hand_equipped"] = True
        components["minecraft:enchantable"] = {
            "slot": "sword", # 例として剣のエンチャントスロットを指定
            "value": 10
        }
        print(f"Attack_Damage_Set:{attack_damage}")

    return final_json

# --- 実行例 ---

# クライアントからカスタムソードの設定が送られてきたと仮定
client_input_sword = {
    "stack_size": 1,
    "durability": 250,
    "attack": 6.5,
}
print(f"client_input_sword:{client_input_sword}")

# 整形関数の呼び出し
formatted_sword_bp = validate_and_format_item_data("super_sword", client_input_sword)
print(f"formatted_sword_bp_identifier:{formatted_sword_bp['minecraft:item']['description']['identifier'] if isinstance(formatted_sword_bp, dict) and 'error' not in formatted_sword_bp else 'Error'}")
# 出力例: formatted_sword_bp_identifier:custom:super_sword

# 整形後のJSON全体を出力
formatted_output = json.dumps(formatted_sword_bp, indent=2, ensure_ascii=False)
print(f"Formatted_JSON:\n{formatted_output}")
