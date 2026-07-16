# 🏗️ AI-OPTIMIZED ULTRA COMPACT CODEBASE MAP (INTELLIGENT SCAN)

> **[AI 프로토콜 매뉴얼]** 이 문서는 다른 AI 비서들의 경로 오해를 차단하기 위해 파일마다 **실제 하드디스크 상대 경로 `[📂 실제경로]`**를 강제 명시해 둔 특수 지도입니다.
> AI 비서는 절대 눈치로 경로를 추측하지 말고, 파일명 뒤에 박혀있는 `[📂 실제경로]` 규격을 그대로 복사하여 agent_navigator를 호출하십시오.

```markdown
project_root/
├── assets/
│   ├── data/
│   │   ├── dialogues.json [📂 assets/data/dialogues.json] -> [💡 📦 json_keys: 2개 포착 | 🔑 "stage1_start_chat" [list] | 🔑 "stage1_clear_chat" [list]]
│   ├── images/
│   │   ├── enemy/
│   │   │   ├── dummy/
│   │   │   │   ├── dummy_dead.png [📂 assets/images/enemy/dummy/dummy_dead.png]
│   │   │   │   ├── dummy_hit.png [📂 assets/images/enemy/dummy/dummy_hit.png]
│   │   │   │   ├── dummy_idle.png [📂 assets/images/enemy/dummy/dummy_idle.png]
│   │   ├── map/
│   │   │   ├── background/
│   │   │   │   ├── bg_sky.png [📂 assets/images/map/background/bg_sky.png]
│   │   │   │   ├── test_map/
│   │   │   │   │   ├── backdrop.jpg [📂 assets/images/map/background/test_map/backdrop.jpg]
│   │   │   │   │   ├── background.jpg [📂 assets/images/map/background/test_map/background.jpg]
│   │   │   ├── ground/
│   │   │   │   ├── ground_dirt.png [📂 assets/images/map/ground/ground_dirt.png]
│   │   ├── platform/
│   │   │   ├── platform_brick.png [📂 assets/images/platform/platform_brick.png]
│   │   ├── player/
│   │   │   ├── attack_effect/
│   │   │   │   ├── effect_hit1.png [📂 assets/images/player/attack_effect/effect_hit1.png]
│   │   │   │   ├── effect_hit2.png [📂 assets/images/player/attack_effect/effect_hit2.png]
│   │   │   │   ├── effect_hit3.png [📂 assets/images/player/attack_effect/effect_hit3.png]
│   │   │   ├── player_move/
│   │   │   │   ├── player_attack1.png [📂 assets/images/player/player_move/player_attack1.png]
│   │   │   │   ├── player_attack2.png [📂 assets/images/player/player_move/player_attack2.png]
│   │   │   │   ├── player_attack3.png [📂 assets/images/player/player_move/player_attack3.png]
│   │   │   │   ├── player_fall.png [📂 assets/images/player/player_move/player_fall.png]
│   │   │   │   ├── player_idle.png [📂 assets/images/player/player_move/player_idle.png]
│   │   │   │   ├── player_jump1.png [📂 assets/images/player/player_move/player_jump1.png]
│   │   │   │   ├── player_jump2.png [📂 assets/images/player/player_move/player_jump2.png]
│   │   │   │   ├── player_jump3.png [📂 assets/images/player/player_move/player_jump3.png]
│   │   │   │   ├── player_jump_up.png [📂 assets/images/player/player_move/player_jump_up.png]
│   │   │   │   ├── player_readyjump.png [📂 assets/images/player/player_move/player_readyjump.png]
│   │   │   │   ├── player_run.png [📂 assets/images/player/player_move/player_run.png]
│   │   │   │   ├── player_run1.png [📂 assets/images/player/player_move/player_run1.png]
│   │   │   │   ├── player_run2.png [📂 assets/images/player/player_move/player_run2.png]
│   │   │   │   ├── player_run3.png [📂 assets/images/player/player_move/player_run3.png]
│   │   │   │   ├── player_stand1.png [📂 assets/images/player/player_move/player_stand1.png]
│   │   │   │   ├── player_stand2.png [📂 assets/images/player/player_move/player_stand2.png]
│   │   │   │   ├── player_stand3.png [📂 assets/images/player/player_move/player_stand3.png]
│   │   │   │   ├── player_walk.png [📂 assets/images/player/player_move/player_walk.png]
├── camera.py [📂 camera.py] -> [💡 📦 imp: math | 🧬 class ElasticCamera [L4-118] |     └─ def __init__() [L12-34] |     └─ def set_center() [L36-38] |     └─ def _frame_lerp() [L41-45] |     └─ def update() [L47-115] |     └─ def get_offset() [L117-118]]
│     ├── 🔑 [REGISTRY]: "ElasticCamera"
├── dialogue_system/
│   ├── dialogue_manager.py [📂 dialogue_system/dialogue_manager.py] -> [💡 📦 imp: json, map_system.map_engine, os, pygame | 🧬 class DialogueManager [L7-156] |     └─ def __init__() [L12-39] |     └─ def load_dialogues() [L41-52] |     └─ def start_dialogue() [L54-67] |     └─ def next_line() [L69-78] |     └─ def end_dialogue() [L80-85] |     └─ def _trigger_current_action() [L87-95] |     └─ def draw() [L97-140] |     └─ def _wrap_text() [L142-156]]
├── enemy/
│   ├── enemys/
│   │   ├── dummy/
│   │   │   ├── __init__.py [📂 enemy/enemys/dummy/__init__.py]
│   │   │   ├── dummy_main.py [📂 enemy/enemys/dummy/dummy_main.py] -> [💡 📦 imp: enemy.enemys.dummy.variables, map_system.map_engine, os, pygame, settings, sys | 🧬 class DummyEnemy [L7-163] |     └─ def __init__() [L8-22] |     └─ def load_images() [L24-57] |     └─ def check_player_attack() [L59-74] |     └─ def update() [L76-91] |     └─ def apply_gravity_and_physics() [L93-149] |     └─ def draw() [L151-163] | 🎯 def auto_register_entity() [L169-179]]
│   │   │   ├── variables.py [📂 enemy/enemys/dummy/variables.py] -> [🧬 class DummyVariables [L1-26] |     └─ def __init__() [L2-26]]
│   │   ├── test_enemy1/
│   │   │   ├── __init__.py [📂 enemy/enemys/test_enemy1/__init__.py]
│   │   │   ├── test_enemy1_main.py [📂 enemy/enemys/test_enemy1/test_enemy1_main.py] -> [💡 📦 imp: math, pygame, variables | 🧬 class TestEnemy1 [L5-64] |     └─ def __init__() [L6-7] |     └─ def update() [L9-42] |     └─ def perform_attack() [L44-49] |     └─ def draw() [L51-64]]
│   │   │   ├── variables.py [📂 enemy/enemys/test_enemy1/variables.py] -> [💡 📦 imp: pygame | 🧬 class TestEnemy1Variables [L3-21] |     └─ def __init__() [L4-21]]
├── event_system/
│   ├── actions/
│   │   ├── move_map.py [📂 event_system/actions/move_map.py]
│   │   ├── play_dialogue.py [📂 event_system/actions/play_dialogue.py]
│   │   ├── spawn_ambush.py [📂 event_system/actions/spawn_ambush.py]
│   ├── triggers/
│   │   ├── enemy_clear.py [📂 event_system/triggers/enemy_clear.py]
│   │   ├── npc_interact.py [📂 event_system/triggers/npc_interact.py]
│   │   ├── zone_enter.py [📂 event_system/triggers/zone_enter.py]
├── fabric_system/
│   ├── editor_objects.json [📂 fabric_system/editor_objects.json] -> [💡 📦 json_keys: 1개 포착 | 🔑 "objects" [list]]
├── main.py [📂 main.py] -> [💡 📦 imp: camera, dialogue_system.dialogue_manager, map_editor_tool.map_editor, map_system.map_main, math, player.player_main, pygame, settings, sys | 🧬 class AppState [L16-19] | 🎯 def draw_player_hp_hud() [L21-74] | 🎯 def run_game() [L76-150] | 🎯 def run_main_menu() [L152-236] | 🎯 def main() [L238-262]]
├── map_editor_tool/
│   ├── __init__.py [📂 map_editor_tool/__init__.py] -> [💡 📦 imp: map_editor_tool.editor_main, map_editor_tool.object_registry]
│   ├── editor_main.py [📂 map_editor_tool/editor_main.py] -> [💡 📦 imp: map_editor_tool, map_editor_tool.object_registry, map_system.map_main, os, pygame, settings | 🧬 class MapEditor [L10-210] |     └─ def __init__() [L16-40] |     └─ def _ensure_maps_dir() [L42-45] |     └─ def _build_map_selection_buttons() [L47-48] |     └─ def get_object_visibility() [L50-51] |     └─ def calculate_placement_pos() [L53-54] |     └─ def load_map() [L56-72] |     └─ def _file_to_map_name() [L74-75] |     └─ def _map_name_to_file() [L77-78] |     └─ def _next_new_map_file() [L80-81] |     └─ def run() [L83-104] |     └─ def _handle_event() [L106-107] |     └─ def _handle_select_event() [L109-110] |     └─ def _handle_keydown() [L112-113] |     └─ def _handle_selected_shortcuts() [L115-116] |     └─ def _handle_mouse_down() [L118-119] |     └─ def _handle_sidebar_click() [L121-122] |     └─ def _update_camera() [L124-125] |     └─ def place_selected() [L127-128] |     └─ def find_platform_at() [L130-131] |     └─ def delete_selected() [L133-134] |     └─ def save_map() [L136-137] |     └─ def load_saved_or_source() [L139-140] |     └─ def serialize_map() [L142-143] |     └─ def _serialize_platform() [L145-146] |     └─ def _serialize_structure() [L148-149] |     └─ def _serialize_entity() [L151-152] |     └─ def _serialize_trigger() [L154-155] |     └─ def _infer_entity_type() [L157-158] |     └─ def _draw() [L160-161] |     └─ def _draw_map_select() [L163-164] |     └─ def _draw_button() [L166-167] |     └─ def _draw_grid() [L169-170] |     └─ def _draw_selection() [L172-173] |     └─ def _draw_sidebar() [L175-176] |     └─ def _draw_tool_button() [L178-179] |     └─ def _draw_inspector() [L181-182] |     └─ def _draw_help() [L184-185] |     └─ def _draw_status() [L187-188] |     └─ def _text() [L190-191] |     └─ def _window_to_virtual() [L193-194] |     └─ def _screen_to_world() [L196-197] |     └─ def _snap() [L199-200] |     └─ def _app_state() [L202-207] |     └─ def scan_map_files() [L209-210]]
│   ├── event_discover.py [📂 map_editor_tool/event_discover.py]
│   ├── input_handler.py [📂 map_editor_tool/input_handler.py] -> [💡 📦 imp: map_editor_tool, pygame, settings | 🎯 def calculate_placement_pos() [L8-16] | 🎯 def handle_event() [L19-46] | 🎯 def handle_keydown() [L48-68] | 🎯 def handle_sidebar_click() [L73-143] | 🎯 def handle_mouse_down() [L146-186] | 🎯 def handle_sidebar_click() [L189-262] | 🎯 def update_camera() [L265-280] | 🎯 def window_to_virtual() [L283-285] | 🎯 def screen_to_world() [L288-290] | 🎯 def snap() [L293-294]]
│   ├── map_editor.py [📂 map_editor_tool/map_editor.py] -> [💡 📦 imp: map_editor_tool.editor_main, map_editor_tool.object_registry]
│   ├── map_selector.py [📂 map_editor_tool/map_selector.py] -> [💡 📦 imp: os, pygame, settings | 🎯 def scan_map_files() [L8-13] | 🎯 def build_map_selection_buttons() [L16-33] | 🎯 def handle_select_event() [L36-54] | 🎯 def file_to_map_name() [L57-63] | 🎯 def map_name_to_file() [L66-74] | 🎯 def next_new_map_file() [L77-86]]
│   ├── object_registry.py [📂 map_editor_tool/object_registry.py] -> [💡 📦 imp: dataclasses, json, os, typing | 🧬 class EditorObjectDefinition [L8-14] | 🧬 class EditorObjectRegistry [L17-116] |     └─ def register() [L21-22] |     └─ def definitions() [L25-26] |     └─ def get() [L29-30] |     └─ def ensure_defaults() [L33-65] |     └─ def discover_fabric_definitions() [L67-90] |     └─ def discover_fabric_definitions() [L93-116]]
│   ├── renderer.py [📂 map_editor_tool/renderer.py] -> [💡 📦 imp: map_editor_tool, pygame, settings | 🎯 def draw() [L6-12] | 🎯 def draw_map_select() [L15-35] | 🎯 def draw_button() [L38-44] | 🎯 def draw_grid() [L47-61] | 🎯 def draw_selection() [L64-74] | 🎯 def draw_sidebar() [L77-104] | 🎯 def draw_tool_button() [L107-112] | 🎯 def draw_inspector() [L118-177] | 🎯 def draw_help() [L180-190] | 🎯 def draw_status() [L193-195] | 🎯 def text() [L198-199]]
│   ├── selection.py [📂 map_editor_tool/selection.py] -> [💡 📦 imp: enemy.enemys.dummy.dummy_main, map_system.map_engine, platform_system.platform_main, pygame | 🎯 def get_object_visibility() [L6-10] | 🎯 def find_platform_at() [L13-33] | 🎯 def delete_selected() [L36-52] | 🎯 def place_selected() [L55-121]]
│   ├── serializer.py [📂 map_editor_tool/serializer.py] -> [💡 📦 imp: json, map_system.map_main, os, pygame | 🎯 def save_map() [L7-27] | 🎯 def load_saved_or_source() [L30-37] | 🎯 def serialize_map() [L40-75] | 🎯 def _serialize_platform() [L81-98] | 🎯 def _serialize_structure() [L100-121] | 🎯 def _serialize_entity() [L124-137] | 🎯 def _serialize_trigger() [L140-152] | 🎯 def _infer_entity_type() [L155-160]]
├── map_system/
│   ├── __init__.py [📂 map_system/__init__.py]
│   ├── map_engine.py [📂 map_system/map_engine.py] -> [💡 📦 imp: importlib, json, math, os, pygame, settings, sys, traceback | 🧬 class AssetManager [L9-32] |     └─ def get_image() [L17-32] | 🧬 class EntityRegistry [L35-56] |     └─ def register() [L43-45] |     └─ def create() [L48-56] | 🧬 class TriggerBoxInstance [L58-73] |     └─ def __init__() [L59-63] |     └─ def to_dict() [L65-73] | 🧬 class MapManager [L75-511] |     └─ def __init__() [L81-106] |     └─ def add_trigger_box() [L109-115] |     └─ def remove_at_position() [L118-121] |     └─ def load_map_data() [L123-266] |     └─ def _create_entity_from_data() [L268-299] |     └─ def fallback_default_map() [L301-311] |     └─ def load_assets() [L313-334] |     └─ def register_action_handler() [L336-338] |     └─ def execute_trigger_action() [L340-358] |     └─ def update() [L360-412] |     └─ def update_trigger_system() [L414-441] |     └─ def draw() [L443-486] |     └─ def _draw_x_tiled() [L488-496] |     └─ def _draw_2d_tiled() [L498-511]]
│   │     ├── 🔑 [REGISTRY]: "EntityRegistry"
│   ├── map_main.py [📂 map_system/map_main.py] -> [💡 📦 imp: dialogue_system.dialogue_manager, enemy.enemys.dummy.dummy_main, importlib, json, map_system.map_engine, map_system.variables, math, os, platform_system.platform_main, pygame, settings, sys, traceback | 🧬 class GameMap [L21-705] |     └─ def __init__() [L22-45] |     └─ def load_map_from_json() [L47-121] |     └─ def register_action_handler() [L123-125] |     └─ def load_map_assets() [L127-167] |     └─ def build_map() [L169-251] |     └─ def register_action_handler() [L253-254] |     └─ def execute_trigger_action() [L256-268] |     └─ def update() [L270-336] |     └─ def draw() [L338-482] |     └─ def update_trigger_system() [L484-502] |     └─ def fallback_default_map() [L504-526] |     └─ def add_platform() [L528-571] |     └─ def add_trigger_box() [L573-583] |     └─ def remove_at_position() [L585-591] |     └─ def _infer_entity_type() [L593-596] |     └─ def save_map() [L598-699] |     └─ def load_map() [L701-705]]
│   ├── map_settings.py [📂 map_system/map_settings.py]
│   ├── maps/
│   │   ├── map_1.json [📂 map_system/maps/map_1.json] -> [💡 📦 json_keys: 12개 포착 | 🔑 "schema_version" [int] | 🔑 "map_id" [str] | 🔑 "map_width" [int] | 🔑 "map_height" [int] | 🔑 "background_type" [str] | ...외 7개]
│   │   ├── map_editor_draft.json [📂 map_system/maps/map_editor_draft.json] -> [💡 📦 json_keys: 12개 포착 | 🔑 "schema_version" [int] | 🔑 "map_id" [str] | 🔑 "map_width" [int] | 🔑 "map_height" [int] | 🔑 "background_type" [str] | ...외 7개]
│   │   ├── map_stage1.json [📂 map_system/maps/map_stage1.json] -> [💡 📦 json_keys: 12개 포착 | 🔑 "schema_version" [int] | 🔑 "map_id" [str] | 🔑 "map_width" [int] | 🔑 "map_height" [int] | 🔑 "background_type" [str] | ...외 7개]
│   ├── variables.py [📂 map_system/variables.py] -> [💡 📦 imp: map_system.map_settings, math, settings | 🧬 class MapVariables [L6-49] |     └─ def __init__() [L7-49]]
├── platform_system/
│   ├── __init__.py [📂 platform_system/__init__.py]
│   ├── platform_main.py [📂 platform_system/platform_main.py] -> [💡 📦 imp: os, platform_system.variables, pygame, sys | 🧬 class Platform [L7-33] |     └─ def __init__() [L8-10] |     └─ def load_image() [L12-24] |     └─ def update() [L26-27] |     └─ def draw() [L29-33]]
│   │     ├── 🔑 [REGISTRY]: "Platform"
│   ├── platform_settings.py [📂 platform_system/platform_settings.py]
│   ├── variables.py [📂 platform_system/variables.py] -> [💡 📦 imp: platform_system.platform_settings | 🧬 class PlatformVariables [L4-40] |     └─ def __init__() [L5-40]]
│   │     ├── 🔑 [REGISTRY]: "PlatformVariables"
├── player/
│   ├── __init__.py [📂 player/__init__.py]
│   ├── asset_loader.py [📂 player/asset_loader.py] -> [💡 📦 imp: os, pygame, sys | 🧬 class PlayerAssetLoader [L6-70] |     └─ def __init__() [L7-10] |     └─ def load_all_assets() [L12-60] |     └─ def _load_series() [L62-70]]
│   ├── combat_processor.py [📂 player/combat_processor.py] -> [💡 📦 imp: pygame | 🧬 class PlayerCombatProcessor [L4-31] |     └─ def process() [L5-31]]
│   ├── input_handler.py [📂 player/input_handler.py] -> [💡 📦 imp: pygame | 🧬 class PlayerInputHandler [L4-66] |     └─ def __init__() [L5-6] |     └─ def update() [L8-48] |     └─ def trigger_attack() [L50-66]]
│   │     ├── 🔑 [REGISTRY]: "PlayerInputHandler"
│   ├── motions/
│   │   ├── __init__.py [📂 player/motions/__init__.py]
│   │   ├── air_motions.py [📂 player/motions/air_motions.py] -> [💡 📦 imp: player.motions.motion_base | 🧬 class AirMotions [L4-12] |     └─ def handle_state() [L5-12]]
│   │   ├── attack_motions.py [📂 player/motions/attack_motions.py] -> [💡 📦 imp: player.motions.motion_base | 🧬 class AttackMotions [L4-14] |     └─ def handle_state() [L5-14]]
│   │   ├── ground_motions.py [📂 player/motions/ground_motions.py] -> [💡 📦 imp: player.motions.motion_base | 🧬 class GroundMotions [L4-13] |     └─ def handle_state() [L5-13]]
│   │   ├── motion_base.py [📂 player/motions/motion_base.py] -> [🧬 class MotionBase [L2-8] |     └─ def __init__() [L3-4] |     └─ def handle_state() [L6-8]]
│   ├── physics_processor.py [📂 player/physics_processor.py] -> [💡 📦 imp: pygame, settings | 🧬 class PlayerPhysicsProcessor [L5-61] |     └─ def process() [L6-61]]
│   ├── player_main.py [📂 player/player_main.py] -> [💡 📦 imp: player.asset_loader, player.combat_processor, player.input_handler, player.motions.air_motions, player.motions.attack_motions, player.motions.ground_motions, player.physics_processor, player.variables, pygame | 🧬 class Player [L12-117] |     └─ def __init__() [L13-27] |     └─ def update_animation_state() [L29-40] |     └─ def update() [L42-88] |     └─ def draw() [L90-117]]
│   ├── variables.py [📂 player/variables.py] -> [💡 📦 imp: settings | 🧬 class PlayerVariables [L4-70] |     └─ def __init__() [L5-56] |     └─ def take_damage() [L58-64] |     └─ def heal() [L66-70]]
├── settings.py [📂 settings.py]
