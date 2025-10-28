import json
import uuid

# モデル定義JSONのバージョン (BedrockのジオメトリJSONのバージョン)
FORMAT_VERSION_MODEL = "1.12.0" 
print(f"MODEL_FORMAT_VERSION:{FORMAT_VERSION_MODEL}")

# --- カスタムモデル (ジオメトリ) 定義JSONを整形する関数 ---

def format_rp_custom_geometry(model_name: str, texture_width: int, texture_height: int, bone_data: list):
    """
    エンティティのカスタムジオメトリファイル (models/entity/geometry.*.json) を整形する。
    
    Args:
        model_name (str): モデルの識別名 (例: 'super_sheep')
        texture_width (int): 使用するテクスチャの幅 (例: 64)
        texture_height (int): 使用するテクスチャの高さ (例: 64)
        bone_data (list): クライアントから送られたボーン（立方体）定義のリスト。
                          (例: [{'name': 'body', 'origin': [0, 12, -2], 'size': [8, 12, 4], 'uv': [0, 0], 'parent': 'root'}, ...] )
                          
    Returns:
        dict: 整形されたRPジオメトリJSONデータ
    """
    
    # ジオメトリのトップレベル構造
    geometry_json = {
        "format_version": FORMAT_VERSION_MODEL,
        f"minecraft:geometry": [
            {
                # geometry.super_sheep のように identifier を設定
                "description": {
                    "identifier": f"geometry.{model_name}", 
                    "texture_width": texture_width,
                    "texture_height": texture_height,
                    "visible_bounds_width": 2,
                    "visible_bounds_height": 2,
                    "visible_bounds_offset": [0, 1.5, 0]
                },
                "bones": [] # クライアントからのボーンデータがここに入る
            }
        ]
    }
    print(f"Geometry_Identifier_Set:geometry.{model_name}")

    # 必須ボーン構造の検証と追加
    formatted_bones = []
    
    for bone in bone_data:
        # クライアントからのデータをそのまま、または必要に応じて検証・変換して追加
        # ここでは簡略化のため、必須キーの有無のみをチェック
        if all(k in bone for k in ['name', 'origin', 'size', 'uv']):
            
            # ボーンの最小単位である 'cubes' リストを作成
            cubes = [{
                "origin": bone['origin'],
                "size": bone['size'],
                "uv": bone['uv']
            }]
            
            # ボーンオブジェクトの作成
            formatted_bone = {
                "name": bone['name'],
                "parent": bone.get('parent', 'root'), # 親ボーンが指定されていない場合は 'root'
                "pivot": [o + s/2 for o, s in zip(bone['origin'], bone['size'])] if 'pivot' not in bone else bone['pivot'], # ピボットを設定
                "cubes": cubes
            }
            
            formatted_bones.append(formatted_bone)
        else:
            return {"error": "Missing required bone properties (name, origin, size, or uv)."}
            
    geometry_json[f"minecraft:geometry"][0]["bones"] = formatted_bones
    
    print(f"Total_Bones_Formatted:{len(formatted_bones)}")
    return geometry_json

# --- 実行例 ---

# クライアントからカスタム羊のボーン構造が送られてきたと仮定
client_bone_input = [
    {
        "name": "body",
        "origin": [-4, 12, -2],
        "size": [8, 8, 4],
        "uv": [28, 0],
        "parent": "root"
    },
    {
        "name": "head",
        "origin": [-4, 20, -6],
        "size": [6, 6, 8],
        "uv": [0, 0],
        "parent": "body"
    }
]
print(f"client_bone_input_ready:{len(client_bone_input)}_bones")

# 整形関数の呼び出し
formatted_geometry_rp = format_rp_custom_geometry(
    model_name="super_sheep",
    texture_width=64,
    texture_height=64,
    bone_data=client_bone_input
)
print(f"formatted_geometry_rp_id:{formatted_geometry_rp['minecraft:geometry'][0]['description']['identifier'] if isinstance(formatted_geometry_rp, dict) and 'error' not in formatted_geometry_rp else 'Error'}")

# 整形後のJSON全体を出力 (確認のため一部のみ)
# formatted_output = json.dumps(formatted_geometry_rp, indent=2, ensure_ascii=False)
# print(f"Formatted_JSON_Snippet:\n{formatted_output[:500]}...")
