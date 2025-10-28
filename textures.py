import json

# リソースパック側のエンティティ定義JSONのバージョン
FORMAT_VERSION_RP = "1.10.0" 
print(f"RP_FORMAT_VERSION:{FORMAT_VERSION_RP}")

# --- 1. エンティティ (モブ) のテクスチャ定義JSONを整形する関数 ---

def format_rp_entity_texture(entity_name: str, texture_path: str, model_id: str = "geometry.default"):
    """
    エンティティのリソースパック (RP) 定義ファイル (entity/mob_name.json) を整形する。
    
    Args:
        entity_name (str): モブの内部識別子 (例: 'super_sheep')
        texture_path (str): テクスチャファイルへのパス (例: 'textures/entity/super_sheep')
        model_id (str): 使用するモデルの識別子 (例: 'geometry.super_sheep')
        
    Returns:
        dict: 整形されたRP JSONデータ
    """
    
    # リソースパック側のエンティティ定義テンプレート
    rp_entity_template = {
        "format_version": FORMAT_VERSION_RP,
        "minecraft:client_entity": {
            "description": {
                # 識別子はBPとRPで一致させる必要がある
                "identifier": f"custom:{entity_name}", 
                "materials": { "default": "entity_alphatest" },
                # RP側の最も重要な項目
                "textures": {
                    "default": texture_path # クライアントがロードするテクスチャパス
                },
                "geometry": {
                    "default": model_id # クライアントがロードするモデルID
                },
                # その他の設定 (レンダーコントローラー、アニメーションなど) はここでは省略
            }
        }
    }
    
    # 実行例の確認用
    print(f"RP_Entity_Texture_Path:{rp_entity_template['minecraft:client_entity']['description']['textures']['default']}")
    
    return rp_entity_template

# --- 2. ブロックのテクスチャ定義JSONを整形する関数 ---

def format_rp_block_texture(block_name: str, texture_name: str, sound_type: str = "stone"):
    """
    ブロックのリソースパック (RP) 定義ファイル (textures/terrain_texture.json) に使用される情報を整形する。
    
    NOTE: ブロックのRP定義は blocks.json または terrain_texture.json に集約されるため、
          ここではその一部として使用する定義を返す。
    
    Args:
        block_name (str): ブロックの内部識別子 (例: 'custom_ore')
        texture_name (str): テクスチャファイルの物理名 (例: 'super_ore_texture')
        sound_type (str): ブロックを踏んだ時の音 (例: 'stone', 'grass')
        
    Returns:
        dict: terrain_texture.json の 'texture_data' にマージされる形式のデータ
    """
    
    rp_block_entry = {
        "textures": f"textures/blocks/{texture_name}", # 実際のテクスチャファイルへのパス
        "sound": sound_type
    }
    
    # 実行例の確認用
    print(f"RP_Block_Texture_Name:{texture_name}_Sound:{sound_type}")
    
    return rp_block_entry

# --- 実行例 ---

# 1. カスタムモブのRP定義を整形
custom_mob_rp_data = format_rp_entity_texture(
    entity_name="super_sheep",
    texture_path="textures/entity/super_sheep/white_wool",
    model_id="geometry.super_sheep"
)
# print(f"Custom_Mob_RP_JSON:\n{json.dumps(custom_mob_rp_data, indent=2, ensure_ascii=False)}")

# 2. カスタムブロックのRPエントリを整形 (これは後に terrain_texture.json にマージされる)
custom_block_rp_data = format_rp_block_texture(
    block_name="super_ore",
    texture_name="super_ore_tex",
    sound_type="metal"
)
# print(f"Custom_Block_RP_Entry:\n{json.dumps(custom_block_rp_data, indent=2, ensure_ascii=False)}")
