import json
import uuid

# ブロック定義JSONのバージョン
FORMAT_VERSION = "1.10.0" 
print(f"BLOCK_FORMAT_VERSION:{FORMAT_VERSION}")

# ブロックデータ生成時の必須コンポーネントテンプレート
BLOCK_TEMPLATE = {
    "format_version": FORMAT_VERSION,
    "minecraft:block": {
        "description": {
            # identifierは外部から注入
            "is_experimental": False,
        },
        "components": {
            # 必須コンポーネントとデフォルト値
            "minecraft:destroy_time": 1.0, # 破壊にかかる時間 (デフォルト: 1.0秒)
            "minecraft:explosion_resistance": 1.0, # 爆破耐性 (デフォルト: 1.0)
            "minecraft:map_color": "#ffffff", # 地図上での色 (デフォルト: 白)
            "minecraft:friction": 0.6, # 摩擦力
            "minecraft:loot": "loot_tables/blocks/default.json" # ドロップアイテム
        }
    }
}
print("BLOCK_TEMPLATE_LOADED")

def validate_and_format_block_data(block_name: str, client_data: dict):
    """
    クライアントデータを検証し、Minecraft BPのblocks/*.json形式に整形する。
    
    Args:
        block_name (str): ブロックの内部識別子 (例: 'custom_ore')
        client_data (dict): クライアントから送信されたデータ (例: {'hardness': 5.0, 'resistance': 20.0, 'collidable': True, 'map_color': '#a0a0a0'})
        
    Returns:
        dict: 整形されたBP JSONデータ、または検証エラー
    """
    
    # 1. データの検証 (必須項目のチェック - 特に必須は設けないが、数値型をチェック)
    if 'hardness' not in client_data or 'resistance' not in client_data:
        # 最低限の物理特性が不足している場合はエラー
        return {"error": "Missing required block properties: hardness or resistance."}
    
    # 2. テンプレートのコピーとidentifierの設定
    final_json = BLOCK_TEMPLATE.copy()
    
    # 内部識別子 (例: custom:custom_ore) を設定
    identifier = f"custom:{block_name}"
    final_json["minecraft:block"]["description"]["identifier"] = identifier
    print(f"Identifier_Set:{identifier}")
    
    # 3. クライアントデータでテンプレートを更新
    components = final_json["minecraft:block"]["components"]

    # --- 硬さ (破壊時間) の設定 ---
    hardness = float(client_data['hardness'])
    components["minecraft:destroy_time"] = hardness
    print(f"Hardness_Set:{hardness}")

    # --- 爆破耐性の設定 ---
    resistance = float(client_data['resistance'])
    components["minecraft:explosion_resistance"] = resistance
    print(f"Resistance_Set:{resistance}")
    
    # --- 地図上の色の設定 ---
    if 'map_color' in client_data:
        map_color = client_data['map_color']
        # シンプルな検証 (例: #RRGGBB形式)
        if map_color.startswith('#') and len(map_color) == 7:
            components["minecraft:map_color"] = map_color
            print(f"Map_Color_Set:{map_color}")

    # --- 当たり判定の設定 ---
    collidable = client_data.get('collidable', True) # デフォルトはTrue
    if collidable is False:
        # 当たり判定を無くす（空気ブロックの振る舞いに近づく）
        # この場合、minecraft:selection_box と minecraft:collision_box を上書きするか削除する
        components["minecraft:collision_box"] = {"enabled": False}
        print("Collision_Disabled")
    
    return final_json

# --- 実行例 ---

# クライアントからカスタム鉱石の設定が送られてきたと仮定
client_input_ore = {
    "hardness": 8.0,        # 黒曜石に近い硬さ
    "resistance": 1000.0,   # 高い爆破耐性
    "collidable": True,     # 通常の当たり判定あり
    "map_color": "#1c1c1c", # 濃い灰色
}
print(f"client_input_ore:{client_input_ore}")

# 整形関数の呼び出し
formatted_ore_bp = validate_and_format_block_data("super_ore", client_input_ore)
print(f"formatted_ore_bp_identifier:{formatted_ore_bp['minecraft:block']['description']['identifier'] if isinstance(formatted_ore_bp, dict) and 'error' not in formatted_ore_bp else 'Error'}")
# 出力例: formatted_ore_bp_identifier:custom:super_ore

# 整形後のJSON全体を出力
formatted_output = json.dumps(formatted_ore_bp, indent=2, ensure_ascii=False)
print(f"Formatted_JSON:\n{formatted_output}")
