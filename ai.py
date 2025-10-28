import json
import uuid

# AIコンポーネントはモブ定義の components 内にリストとして追加される
print("AI_MODULE_START")

def format_ai_behaviors(client_behaviors: list):
    """
    クライアントが指定したAIのリストを、BPのJSON形式（priority付き）に整形する。
    
    Args:
        client_behaviors (list): 優先度、タイプ、設定を含む辞書のリスト
                                (例: [{'type': 'follow_owner', 'priority': 1, 'speed': 1.0, 'stop_distance': 4.0}, ...] )
                          
    Returns:
        dict: 整形された components 辞書の一部（mobs.pyにマージされる）
    """
    
    formatted_components = {}
    
    # AIの優先度（priority）は数値が小さいほど優先される
    
    for behavior in client_behaviors:
        behavior_type = behavior.get('type')
        priority = behavior.get('priority')
        
        if priority is None or not isinstance(priority, int):
            # 優先度はAIの基本なので必須
            return {"error": f"AI behavior '{behavior_type}' missing required priority."}

        # --- 共通設定 ---
        base_component = {"priority": priority}

        # --- 行動タイプによるマッピング ---
        component_key = None
        
        if behavior_type == 'follow_owner':
            component_key = "minecraft:behavior.follow_owner"
            base_component["speed_multiplier"] = behavior.get('speed', 1.0)
            base_component["stop_distance"] = behavior.get('stop_distance', 2.0)
            
        elif behavior_type == 'stroll':
            component_key = "minecraft:behavior.random_stroll"
            base_component["speed_multiplier"] = behavior.get('speed', 0.8)

        elif behavior_type == 'look_at_player':
            component_key = "minecraft:behavior.look_at_player"
            base_component["look_distance"] = behavior.get('distance', 6.0)
            
        elif behavior_type == 'melee_attack':
            component_key = "minecraft:behavior.melee_attack"
            base_component["speed_multiplier"] = behavior.get('speed', 1.0)

        # ... (他のAI行動の追加)

        if component_key:
            formatted_components[component_key] = base_component
            print(f"AI_Component_Added:{component_key}_Priority:{priority}")
        else:
            return {"error": f"Unknown AI behavior type: {behavior_type}"}
    
    return formatted_components

# --- 実行例 ---

# クライアントからカスタムペットのAIリストが送られてきたと仮定
client_ai_input = [
    {"type": "follow_owner", "priority": 1, "speed": 1.1, "stop_distance": 3.0}, # 最優先
    {"type": "look_at_player", "priority": 2, "distance": 8.0},
    {"type": "stroll", "priority": 10, "speed": 0.6} # 最低優先度
]
print(f"client_ai_input:{client_ai_input}")

# 整形関数の呼び出し
formatted_ai_components = format_ai_behaviors(client_ai_input)

if "error" in formatted_ai_components:
    print(f"Error_Found:{formatted_ai_components['error']}")
else:
    # この結果は、mobs.pyで生成されたJSONの "components" 辞書にマージされます。
    formatted_output = json.dumps(formatted_ai_components, indent=2, ensure_ascii=False)
    print(f"Formatted_AI_Components:\n{formatted_output}")
