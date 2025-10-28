import json

# JSONファイルのバージョンは、対象となるRP/BPファイルに合わせる
FORMAT_VERSION_ENV = "1.13.0" 
print(f"ENV_FORMAT_VERSION:{FORMAT_VERSION_ENV}")

# --- 1. ワールド環境の描画設定 (biomes_client.json に影響) ---

def format_world_render_settings(client_settings: dict):
    """
    クライアントから受け取った環境設定を、RP描画設定JSONの一部として整形する。
    
    Args:
        client_settings (dict): クライアントから送信されたデータ
                                (例: {'cloud_type': 'thick', 'sky_color': [0.5, 0.7, 1.0], 'fog_density': 0.05})
                          
    Returns:
        dict: biomes_client.json などにマージされる描画コンポーネント
    """
    
    formatted_render_settings = {}
    
    # --- 雲 (Clouds) の設定 ---
    # MinecraftのRPでは、通常は render_controllers.json や material に影響しますが、
    # ここではカスタムバイオーム定義に含める情報を整形します。
    
    cloud_type = client_settings.get('cloud_type', 'default')
    
    # 実際にはRP側で複雑な定義が必要だが、ここでは識別子と基本的な設定を返す
    if cloud_type == 'none':
        formatted_render_settings['has_clouds'] = False
    else:
        # 雲の色、テクスチャ、高さなどを指定するカスタム設定
        formatted_render_settings['clouds'] = {
            "type": cloud_type, # 例: 'default', 'thick'
            "height": client_settings.get('cloud_height', 192.0)
        }
    print(f"Clouds_Setting_Type:{cloud_type}")
    
    # --- 空と霧 (Sky & Fog) の設定 ---
    
    # 霧の色と範囲
    fog_settings = {
        "fog_color": client_settings.get('fog_color', [0.8, 0.8, 0.8]),
        "fog_start": client_settings.get('fog_start', 0.05),
        "fog_end": client_settings.get('fog_end', 1.0) # 距離は0.0～1.0で正規化
    }
    formatted_render_settings['fog'] = fog_settings
    print(f"Fog_Color_Set:{fog_settings['fog_color']}")
    
    # 空の色
    formatted_render_settings['sky_color'] = client_settings.get('sky_color', [0.7, 0.8, 1.0])
    
    return formatted_render_settings

# --- 2. ワールド生成パラメータ (BP側の設定ファイル) ---

def format_world_generation_parameters(client_generation_data: dict):
    """
    ワールド生成に関するパラメータをBP側のJSON形式に整形する。
    
    Args:
        client_generation_data (dict): クライアントから送信された生成データ
                                      (例: {'sea_level': 63, 'ore_frequency': {'diamond': 0.001}})
                          
    Returns:
        dict: BP側のワールド設定JSONの一部
    """
    
    formatted_generation_settings = {}
    
    # 海面の高さ
    sea_level = client_generation_data.get('sea_level', 63)
    formatted_generation_settings['sea_level'] = sea_level
    print(f"Sea_Level_Set:{sea_level}")
    
    # 鉱石の生成頻度 (BPのloot_tables/ または feature の設定に影響)
    ore_freq = client_generation_data.get('ore_frequency', {})
    
    if ore_freq:
        # このデータを feature/*.json にマージするためのシンプルなリストを返す
        formatted_generation_settings['custom_ores'] = [
            {"type": ore, "frequency": freq} for ore, freq in ore_freq.items()
        ]
        print(f"Custom_Ore_Types_Found:{len(ore_freq)}")
        
    return formatted_generation_settings


# --- 実行例 ---

# 1. クライアントからカスタムバイオームの描画設定が送られてきたと仮定
client_render_input = {
    "cloud_type": "thick",
    "cloud_height": 256.0,
    "sky_color": [0.3, 0.4, 0.5], # 少し暗い空
    "fog_color": [0.2, 0.2, 0.2], # 濃い霧
    "fog_start": 0.01,
    "fog_end": 0.5 
}
print(f"\nclient_render_input_ready")

formatted_render_data = format_world_render_settings(client_render_input)
# print(f"Formatted_Render_JSON:\n{json.dumps(formatted_render_data, indent=2, ensure_ascii=False)}")


# 2. クライアントからワールド生成パラメータが送られてきたと仮定
client_gen_input = {
    "sea_level": 50,
    "ore_frequency": {
        "ruby_ore": 0.005,
        "sapphire_ore": 0.003
    }
}
print(f"\nclient_gen_input_ready")

formatted_gen_data = format_world_generation_parameters(client_gen_input)
# print(f"Formatted_Gen_JSON:\n{json.dumps(formatted_gen_data, indent=2, ensure_ascii=False)}")
