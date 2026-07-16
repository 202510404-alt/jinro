# 🏗️ 짭커서 프로젝트 CODEBASE MAP

현재 인덱싱된 총 파일 수: **43개**

## 🗂️ [Module Index]
- `src/camera.py`
- `src/dialogue_system/dialogue_manager.py`
- `src/enemy/enemys/dummy/__init__.py`
- `src/enemy/enemys/dummy/dummy_main.py`
- `src/enemy/enemys/dummy/variables.py`
- `src/enemy/enemys/test_enemy1/__init__.py`
- `src/enemy/enemys/test_enemy1/test_enemy1_main.py`
- `src/enemy/enemys/test_enemy1/variables.py`
- `src/event_system/actions/move_map.py`
- `src/event_system/actions/play_dialogue.py`
- `src/event_system/actions/spawn_ambush.py`
- `src/event_system/triggers/enemy_clear.py`
- `src/event_system/triggers/npc_interact.py`
- `src/event_system/triggers/zone_enter.py`
- `src/main.py`
- `src/map_editor_tool/__init__.py`
- `src/map_editor_tool/editor_main.py`
- `src/map_editor_tool/event_discover.py`
- `src/map_editor_tool/input_handler.py`
- `src/map_editor_tool/map_editor.py`
- `src/map_editor_tool/renderer.py`
- `src/map_system/__init__.py`
- `src/map_system/map_engine.py`
- `src/map_system/map_main.py`
- `src/map_system/map_settings.py`
- `src/map_system/variables.py`
- `src/platform_system/__init__.py`
- `src/platform_system/platform_main.py`
- `src/platform_system/platform_settings.py`
- `src/platform_system/variables.py`
- `src/player/__init__.py`
- `src/player/asset_loader.py`
- `src/player/combat_processor.py`
- `src/player/input_handler.py`
- `src/player/motions/__init__.py`
- `src/player/motions/air_motions.py`
- `src/player/motions/attack_motions.py`
- `src/player/motions/ground_motions.py`
- `src/player/motions/motion_base.py`
- `src/player/physics_processor.py`
- `src/player/player_main.py`
- `src/player/variables.py`
- `src/settings.py`

## 💀 [Skeleton & Dependency 명세서]
### 📄 src/camera.py
#### 🔍 내부 심볼 및 의존성 관계:
- **[CLASS]** `ElasticCamera` (Line: 4~118)
- **[METHOD]** `ElasticCamera.__init__` (Line: 12~34)
  - 🔗 *Calls (호출하는 것)*: `float, int`
- **[METHOD]** `ElasticCamera.set_center` (Line: 36~38)
  - 🔗 *Calls (호출하는 것)*: `float`
- **[METHOD]** `ElasticCamera._frame_lerp` (Line: 41~45)
  - 🔗 *Calls (호출하는 것)*: `float, min, pow, max`
  - 🎯 *Used By (나를 부르는 곳)*: `src/camera.py::ElasticCamera.update`
- **[METHOD]** `ElasticCamera.update` (Line: 47~115)
  - 🔗 *Calls (호출하는 것)*: `float, min, _frame_lerp, hypot`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_system/map_engine.py::MapManager.update, src/map_system/map_main.py::GameMap.update, src/player/player_main.py::Player.update`
- **[METHOD]** `ElasticCamera.get_offset` (Line: 117~118)

#### 🧱 Code Skeleton:
```python
class ElasticCamera:
    def __init__(...):
        ...
    def set_center(...):
        ...
    def _frame_lerp(...):
        ...
    def update(...):
        ...
    def get_offset(...):
        ...
```

--------------------------------------------------

### 📄 src/dialogue_system/dialogue_manager.py
#### 🔍 내부 심볼 및 의존성 관계:
- **[CLASS]** `DialogueManager` (Line: 7~156)
- **[METHOD]** `DialogueManager.__init__` (Line: 12~39)
  - 🔗 *Calls (호출하는 것)*: `SysFont, abspath, dirname, init, Font`
- **[METHOD]** `DialogueManager.load_dialogues` (Line: 41~52)
  - 🔗 *Calls (호출하는 것)*: `join, open, print, len, load`
- **[METHOD]** `DialogueManager.start_dialogue` (Line: 54~67)
  - 🔗 *Calls (호출하는 것)*: `_trigger_current_action, print, len`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_system/map_main.py::GameMap.update`
- **[METHOD]** `DialogueManager.next_line` (Line: 69~78)
  - 🔗 *Calls (호출하는 것)*: `_trigger_current_action, end_dialogue, len`
- **[METHOD]** `DialogueManager.end_dialogue` (Line: 80~85)
  - 🔗 *Calls (호출하는 것)*: `print`
  - 🎯 *Used By (나를 부르는 곳)*: `src/dialogue_system/dialogue_manager.py::DialogueManager.next_line`
- **[METHOD]** `DialogueManager._trigger_current_action` (Line: 87~95)
  - 🔗 *Calls (호출하는 것)*: `print, len, get`
  - 🎯 *Used By (나를 부르는 곳)*: `src/dialogue_system/dialogue_manager.py::DialogueManager.next_line, src/dialogue_system/dialogue_manager.py::DialogueManager.start_dialogue`
- **[METHOD]** `DialogueManager.draw` (Line: 97~140)
  - 🔗 *Calls (호출하는 것)*: `fill, rect, render, Surface, get, join, get_image, Rect, blit, scale, _wrap_text`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/editor_main.py::MapEditor.draw, src/map_editor_tool/map_editor.py::MapEditor._draw, src/map_system/map_engine.py::MapManager.draw, src/map_system/map_main.py::GameMap.draw`
- **[METHOD]** `DialogueManager._wrap_text` (Line: 142~156)
  - 🔗 *Calls (호출하는 것)*: `append, size`
  - 🎯 *Used By (나를 부르는 곳)*: `src/dialogue_system/dialogue_manager.py::DialogueManager.draw`

#### 🧱 Code Skeleton:
```python
class DialogueManager:
    def __init__(...):
        ...
    def load_dialogues(...):
        ...
    def start_dialogue(...):
        ...
    def next_line(...):
        ...
    def end_dialogue(...):
        ...
    def _trigger_current_action(...):
        ...
    def draw(...):
        ...
    def _wrap_text(...):
        ...
```

--------------------------------------------------

### 📄 src/enemy/enemys/dummy/__init__.py
*선언된 클래스나 함수가 없는 파일이거나 모듈입니다.*

--------------------------------------------------

### 📄 src/enemy/enemys/dummy/dummy_main.py
#### 🔍 내부 심볼 및 의존성 관계:
- **[CLASS]** `DummyEnemy` (Line: 7~163)
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor.place_selected`
- **[METHOD]** `DummyEnemy.__init__` (Line: 8~22)
  - 🔗 *Calls (호출하는 것)*: `load_images, isinstance, get, Rect, DummyVariables`
- **[METHOD]** `DummyEnemy.load_images` (Line: 24~57)
  - 🔗 *Calls (호출하는 것)*: `convert_alpha, fill, abspath, load, join, Surface, print, scale`
  - 🎯 *Used By (나를 부르는 곳)*: `src/enemy/enemys/dummy/dummy_main.py::DummyEnemy.__init__`
- **[METHOD]** `DummyEnemy.check_player_attack` (Line: 59~74)
  - 🔗 *Calls (호출하는 것)*: `hasattr, colliderect, print, Rect`
  - 🎯 *Used By (나를 부르는 곳)*: `src/enemy/enemys/dummy/dummy_main.py::DummyEnemy.update`
- **[METHOD]** `DummyEnemy.update` (Line: 76~91)
  - 🔗 *Calls (호출하는 것)*: `apply_gravity_and_physics, check_player_attack`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_system/map_engine.py::MapManager.update, src/map_system/map_main.py::GameMap.update, src/player/player_main.py::Player.update`
- **[METHOD]** `DummyEnemy.apply_gravity_and_physics` (Line: 93~149)
  - 🔗 *Calls (호출하는 것)*: `hasattr, colliderect, getattr, Rect`
  - 🎯 *Used By (나를 부르는 곳)*: `src/enemy/enemys/dummy/dummy_main.py::DummyEnemy.update`
- **[METHOD]** `DummyEnemy.draw` (Line: 151~163)
  - 🔗 *Calls (호출하는 것)*: `blit, get`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/editor_main.py::MapEditor.draw, src/map_editor_tool/map_editor.py::MapEditor._draw, src/map_system/map_engine.py::MapManager.draw, src/map_system/map_main.py::GameMap.draw`
- **[FUNCTION]** `auto_register_entity` (Line: 169~179)

#### 🧱 Code Skeleton:
```python
class DummyEnemy:
    def __init__(...):
        ...
    def load_images(...):
        ...
    def check_player_attack(...):
        ...
    def update(...):
        ...
    def apply_gravity_and_physics(...):
        ...
    def draw(...):
        ...
def auto_register_entity(...):
    ...
```

--------------------------------------------------

### 📄 src/enemy/enemys/dummy/variables.py
#### 🔍 내부 심볼 및 의존성 관계:
- **[CLASS]** `DummyVariables` (Line: 1~26)
  - 🎯 *Used By (나를 부르는 곳)*: `src/enemy/enemys/dummy/dummy_main.py::DummyEnemy.__init__`
- **[METHOD]** `DummyVariables.__init__` (Line: 2~26)

#### 🧱 Code Skeleton:
```python
class DummyVariables:
    def __init__(...):
        ...
```

--------------------------------------------------

### 📄 src/enemy/enemys/test_enemy1/__init__.py
*선언된 클래스나 함수가 없는 파일이거나 모듈입니다.*

--------------------------------------------------

### 📄 src/enemy/enemys/test_enemy1/test_enemy1_main.py
#### 🔍 내부 심볼 및 의존성 관계:
- **[CLASS]** `TestEnemy1` (Line: 5~64)
- **[METHOD]** `TestEnemy1.__init__` (Line: 6~7)
  - 🔗 *Calls (호출하는 것)*: `TestEnemy1Variables`
- **[METHOD]** `TestEnemy1.update` (Line: 9~42)
  - 🔗 *Calls (호출하는 것)*: `perform_attack, sqrt`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_system/map_engine.py::MapManager.update, src/map_system/map_main.py::GameMap.update, src/player/player_main.py::Player.update`
- **[METHOD]** `TestEnemy1.perform_attack` (Line: 44~49)
  - 🔗 *Calls (호출하는 것)*: `hasattr, take_damage`
  - 🎯 *Used By (나를 부르는 곳)*: `src/enemy/enemys/test_enemy1/test_enemy1_main.py::TestEnemy1.update`
- **[METHOD]** `TestEnemy1.draw` (Line: 51~64)
  - 🔗 *Calls (호출하는 것)*: `rect, move`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/editor_main.py::MapEditor.draw, src/map_editor_tool/map_editor.py::MapEditor._draw, src/map_system/map_engine.py::MapManager.draw, src/map_system/map_main.py::GameMap.draw`

#### 🧱 Code Skeleton:
```python
class TestEnemy1:
    def __init__(...):
        ...
    def update(...):
        ...
    def perform_attack(...):
        ...
    def draw(...):
        ...
```

--------------------------------------------------

### 📄 src/enemy/enemys/test_enemy1/variables.py
#### 🔍 내부 심볼 및 의존성 관계:
- **[CLASS]** `TestEnemy1Variables` (Line: 3~21)
  - 🎯 *Used By (나를 부르는 곳)*: `src/enemy/enemys/test_enemy1/test_enemy1_main.py::TestEnemy1.__init__`
- **[METHOD]** `TestEnemy1Variables.__init__` (Line: 4~21)
  - 🔗 *Calls (호출하는 것)*: `Rect`

#### 🧱 Code Skeleton:
```python
class TestEnemy1Variables:
    def __init__(...):
        ...
```

--------------------------------------------------

### 📄 src/event_system/actions/move_map.py
*선언된 클래스나 함수가 없는 파일이거나 모듈입니다.*

--------------------------------------------------

### 📄 src/event_system/actions/play_dialogue.py
*선언된 클래스나 함수가 없는 파일이거나 모듈입니다.*

--------------------------------------------------

### 📄 src/event_system/actions/spawn_ambush.py
*선언된 클래스나 함수가 없는 파일이거나 모듈입니다.*

--------------------------------------------------

### 📄 src/event_system/triggers/enemy_clear.py
*선언된 클래스나 함수가 없는 파일이거나 모듈입니다.*

--------------------------------------------------

### 📄 src/event_system/triggers/npc_interact.py
*선언된 클래스나 함수가 없는 파일이거나 모듈입니다.*

--------------------------------------------------

### 📄 src/event_system/triggers/zone_enter.py
*선언된 클래스나 함수가 없는 파일이거나 모듈입니다.*

--------------------------------------------------

### 📄 src/main.py
#### 🔍 내부 심볼 및 의존성 관계:
- **[CLASS]** `AppState` (Line: 16~19)
- **[FUNCTION]** `draw_player_hp_hud` (Line: 21~27)
- **[FUNCTION]** `run_game` (Line: 29~103)
- **[FUNCTION]** `run_main_menu` (Line: 105~189)
- **[FUNCTION]** `main` (Line: 191~215)

#### 🧱 Code Skeleton:
```python
class AppState:
def draw_player_hp_hud(...):
    ...
def run_game(...):
    ...
def run_main_menu(...):
    ...
def main(...):
    ...
```

--------------------------------------------------

### 📄 src/map_editor_tool/__init__.py
*선언된 클래스나 함수가 없는 파일이거나 모듈입니다.*

--------------------------------------------------

### 📄 src/map_editor_tool/editor_main.py
#### 🔍 내부 심볼 및 의존성 관계:
- **[CLASS]** `MapEditor` (Line: 11~154)
- **[METHOD]** `MapEditor.__init__` (Line: 16~42)
  - 🔗 *Calls (호출하는 것)*: `EditorEventDiscoverer, EditorRenderer, EditorInputHandler, GameMap`
- **[METHOD]** `MapEditor.handle_events` (Line: 44~122)
  - 🔗 *Calls (호출하는 것)*: `shift_action, shift_trigger, add_trigger_box, add_platform, get_pressed, get_snapped_world_mouse, get, remove_at_position, get_current_pair, handle_brush_resize, save_map, get_pos, load_map`
- **[METHOD]** `MapEditor.update` (Line: 124~128)
  - 🔗 *Calls (호출하는 것)*: `handle_continuous_camera_pan`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_system/map_engine.py::MapManager.update, src/map_system/map_main.py::GameMap.update, src/player/player_main.py::Player.update`
- **[METHOD]** `MapEditor.draw` (Line: 130~154)
  - 🔗 *Calls (호출하는 것)*: `draw_sidebar_panel, draw_gizmo_preview, get_snapped_world_mouse, draw_status_bar, draw, get_current_pair, get_pos`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor._draw, src/map_system/map_engine.py::MapManager.draw, src/map_system/map_main.py::GameMap.draw`

#### 🧱 Code Skeleton:
```python
class MapEditor:
    def __init__(...):
        ...
    def handle_events(...):
        ...
    def update(...):
        ...
    def draw(...):
        ...
```

--------------------------------------------------

### 📄 src/map_editor_tool/event_discover.py
#### 🔍 내부 심볼 및 의존성 관계:
- **[CLASS]** `EditorEventDiscoverer` (Line: 4~61)
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/editor_main.py::MapEditor.__init__`
- **[METHOD]** `EditorEventDiscoverer.__init__` (Line: 9~14)
  - 🔗 *Calls (호출하는 것)*: `discover_modules`
- **[METHOD]** `EditorEventDiscoverer.discover_modules` (Line: 16~40)
  - 🔗 *Calls (호출하는 것)*: `endswith, listdir, join, replace, exists`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/event_discover.py::EditorEventDiscoverer.__init__`
- **[METHOD]** `EditorEventDiscoverer.get_current_pair` (Line: 42~47)
  - 🔗 *Calls (호출하는 것)*: `len`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/editor_main.py::MapEditor.draw, src/map_editor_tool/editor_main.py::MapEditor.handle_events`
- **[METHOD]** `EditorEventDiscoverer.shift_trigger` (Line: 49~54)
  - 🔗 *Calls (호출하는 것)*: `len`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/editor_main.py::MapEditor.handle_events`
- **[METHOD]** `EditorEventDiscoverer.shift_action` (Line: 56~61)
  - 🔗 *Calls (호출하는 것)*: `len`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/editor_main.py::MapEditor.handle_events`

#### 🧱 Code Skeleton:
```python
class EditorEventDiscoverer:
    def __init__(...):
        ...
    def discover_modules(...):
        ...
    def get_current_pair(...):
        ...
    def shift_trigger(...):
        ...
    def shift_action(...):
        ...
```

--------------------------------------------------

### 📄 src/map_editor_tool/input_handler.py
#### 🔍 내부 심볼 및 의존성 관계:
- **[CLASS]** `EditorInputHandler` (Line: 5~87)
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/editor_main.py::MapEditor.__init__`
- **[METHOD]** `EditorInputHandler.__init__` (Line: 10~11)
- **[METHOD]** `EditorInputHandler.get_snapped_world_mouse` (Line: 13~43)
  - 🔗 *Calls (호출하는 것)*: `Info, int`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/editor_main.py::MapEditor.draw, src/map_editor_tool/editor_main.py::MapEditor.handle_events`
- **[METHOD]** `EditorInputHandler.handle_continuous_camera_pan` (Line: 45~67)
  - 🔗 *Calls (호출하는 것)*: `get_pressed, int`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/editor_main.py::MapEditor.update`
- **[METHOD]** `EditorInputHandler.handle_brush_resize` (Line: 69~87)
  - 🔗 *Calls (호출하는 것)*: `min, max`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/editor_main.py::MapEditor.handle_events`

#### 🧱 Code Skeleton:
```python
class EditorInputHandler:
    def __init__(...):
        ...
    def get_snapped_world_mouse(...):
        ...
    def handle_continuous_camera_pan(...):
        ...
    def handle_brush_resize(...):
        ...
```

--------------------------------------------------

### 📄 src/map_editor_tool/map_editor.py
#### 🔍 내부 심볼 및 의존성 관계:
- **[CLASS]** `EditorObjectDefinition` (Line: 14~20)
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::EditorObjectRegistry.discover_fabric_definitions, src/map_editor_tool/map_editor.py::EditorObjectRegistry.ensure_defaults`
- **[CLASS]** `EditorObjectRegistry` (Line: 23~122)
- **[METHOD]** `EditorObjectRegistry.register` (Line: 27~28)
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::EditorObjectRegistry.discover_fabric_definitions, src/map_editor_tool/map_editor.py::EditorObjectRegistry.ensure_defaults`
- **[METHOD]** `EditorObjectRegistry.definitions` (Line: 31~32)
  - 🔗 *Calls (호출하는 것)*: `values, list`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor.__init__`
- **[METHOD]** `EditorObjectRegistry.get` (Line: 35~36)
  - 🔗 *Calls (호출하는 것)*: `get`
  - 🎯 *Used By (나를 부르는 곳)*: `src/dialogue_system/dialogue_manager.py::DialogueManager._trigger_current_action, src/dialogue_system/dialogue_manager.py::DialogueManager.draw, src/enemy/enemys/dummy/dummy_main.py::DummyEnemy.__init__, src/enemy/enemys/dummy/dummy_main.py::DummyEnemy.draw, src/map_editor_tool/editor_main.py::MapEditor.handle_events, src/map_editor_tool/map_editor.py::EditorObjectRegistry.discover_fabric_definitions, src/map_editor_tool/map_editor.py::MapEditor._serialize_trigger, src/map_editor_tool/map_editor.py::MapEditor.place_selected, src/map_editor_tool/map_editor.py::MapEditor.run, src/map_system/map_engine.py::MapManager._create_entity_from_data, src/map_system/map_engine.py::MapManager.execute_trigger_action, src/map_system/map_engine.py::MapManager.load_map_data, src/map_system/map_main.py::GameMap.build_map, src/map_system/map_main.py::GameMap.execute_trigger_action, src/map_system/map_main.py::GameMap.load_map_from_json, src/map_system/map_main.py::GameMap.save_map, src/map_system/map_main.py::GameMap.update, src/map_system/variables.py::MapVariables.__init__, src/player/player_main.py::Player.draw, src/player/player_main.py::Player.update`
- **[METHOD]** `EditorObjectRegistry.ensure_defaults` (Line: 39~71)
  - 🔗 *Calls (호출하는 것)*: `EditorObjectDefinition, register`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor.__init__`
- **[METHOD]** `EditorObjectRegistry.discover_fabric_definitions` (Line: 73~96)
  - 🔗 *Calls (호출하는 것)*: `abspath, dirname, register, get, join, open, EditorObjectDefinition, print, load, exists`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor.__init__`
- **[METHOD]** `EditorObjectRegistry.discover_fabric_definitions` (Line: 99~122)
  - 🔗 *Calls (호출하는 것)*: `abspath, dirname, register, get, join, open, EditorObjectDefinition, print, load, exists`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor.__init__`
- **[CLASS]** `MapEditor` (Line: 123~824)
- **[METHOD]** `MapEditor.__init__` (Line: 129~153)
  - 🔗 *Calls (호출하는 것)*: `_map_name_to_file, discover_fabric_definitions, ensure_defaults, scan_map_files, SysFont, Vector2, _ensure_maps_dir, definitions, load_map, _build_map_selection_buttons`
- **[METHOD]** `MapEditor._ensure_maps_dir` (Line: 155~158)
  - 🔗 *Calls (호출하는 것)*: `abspath, dirname, makedirs, join`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor.__init__`
- **[METHOD]** `MapEditor.scan_map_files` (Line: 160~165)
  - 🔗 *Calls (호출하는 것)*: `endswith, listdir, join, sorted, isfile, lower`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor.__init__`
- **[METHOD]** `MapEditor._build_map_selection_buttons` (Line: 167~184)
  - 🔗 *Calls (호출하는 것)*: `append, len, Rect, enumerate, max`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor.__init__`
- **[METHOD]** `MapEditor.get_object_visibility` (Line: 187~191)
  - 🔗 *Calls (호출하는 것)*: `hasattr, getattr`
- **[METHOD]** `MapEditor.calculate_placement_pos` (Line: 193~201)
- **[METHOD]** `MapEditor._handle_select_event` (Line: 203~221)
  - 🔗 *Calls (호출하는 것)*: `_file_to_map_name, collidepoint, _app_state, load_map, _next_new_map_file`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor._handle_event`
- **[METHOD]** `MapEditor.load_map` (Line: 223~239)
  - 🔗 *Calls (호출하는 것)*: `_map_name_to_file, GameMap, hasattr`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/editor_main.py::MapEditor.handle_events, src/map_editor_tool/map_editor.py::MapEditor.__init__, src/map_editor_tool/map_editor.py::MapEditor._handle_select_event`
- **[METHOD]** `MapEditor._file_to_map_name` (Line: 241~247)
  - 🔗 *Calls (호출하는 것)*: `startswith, splitext, isdigit`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor._handle_select_event`
- **[METHOD]** `MapEditor._map_name_to_file` (Line: 249~257)
  - 🔗 *Calls (호출하는 것)*: `isdigit, endswith, str, startswith`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor.__init__, src/map_editor_tool/map_editor.py::MapEditor.load_map, src/map_editor_tool/map_editor.py::MapEditor.save_map`
- **[METHOD]** `MapEditor._next_new_map_file` (Line: 259~268)
  - 🔗 *Calls (호출하는 것)*: `join, exists`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor._handle_select_event`
- **[METHOD]** `MapEditor.run` (Line: 270~291)
  - 🔗 *Calls (호출하는 것)*: `get_pos, smoothscale, _update_camera, flip, _draw, get, _draw_map_select, tick, _handle_event, _window_to_virtual, blit, set_caption`
- **[METHOD]** `MapEditor._handle_event` (Line: 293~309)
  - 🔗 *Calls (호출하는 것)*: `_handle_select_event, _snap, _screen_to_world, _handle_keydown, _app_state, _handle_mouse_down`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor.run`
- **[METHOD]** `MapEditor._handle_keydown` (Line: 311~331)
  - 🔗 *Calls (호출하는 것)*: `load_saved_or_source, _handle_selected_shortcuts, len, save_map, delete_selected, _app_state`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor._handle_event`
- **[METHOD]** `MapEditor._handle_selected_shortcuts` (Line: 333~350)
  - 🔗 *Calls (호출하는 것)*: `getattr, load_image, max`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor._handle_keydown`
- **[METHOD]** `MapEditor._handle_mouse_down` (Line: 352~388)
  - 🔗 *Calls (호출하는 것)*: `_handle_sidebar_click, remove, hasattr, Vector2, find_platform_at, _screen_to_world, place_selected, max`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor._handle_event`
- **[METHOD]** `MapEditor._handle_sidebar_click` (Line: 390~415)
  - 🔗 *Calls (호출하는 것)*: `collidepoint, save_map, Rect, _app_state, enumerate`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor._handle_mouse_down`
- **[METHOD]** `MapEditor._update_camera` (Line: 417~432)
  - 🔗 *Calls (호출하는 것)*: `get_pressed, min, max`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor.run`
- **[METHOD]** `MapEditor.place_selected` (Line: 434~500)
  - 🔗 *Calls (호출하는 것)*: `append, dict, _snap, hasattr, Platform, setdefault, get, DummyEnemy, create`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor._handle_mouse_down`
- **[METHOD]** `MapEditor.find_platform_at` (Line: 502~522)
  - 🔗 *Calls (호출하는 것)*: `hasattr, getattr, reversed, collidepoint, Rect`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor._handle_mouse_down`
- **[METHOD]** `MapEditor.delete_selected` (Line: 524~540)
  - 🔗 *Calls (호출하는 것)*: `hasattr, remove`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor._handle_keydown`
- **[METHOD]** `MapEditor.save_map` (Line: 542~562)
  - 🔗 *Calls (호출하는 것)*: `_map_name_to_file, remove, write, dump, join, open, makedirs, serialize_map, replace, exists`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/editor_main.py::MapEditor.handle_events, src/map_editor_tool/map_editor.py::MapEditor._handle_keydown, src/map_editor_tool/map_editor.py::MapEditor._handle_sidebar_click`
- **[METHOD]** `MapEditor.load_saved_or_source` (Line: 564~571)
  - 🔗 *Calls (호출하는 것)*: `hasattr, GameMap`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor._handle_keydown`
- **[METHOD]** `MapEditor.serialize_map` (Line: 573~608)
  - 🔗 *Calls (호출하는 것)*: `hasattr, _serialize_platform, getattr, _serialize_structure, _serialize_entity, _serialize_trigger`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor.save_map`
- **[METHOD]** `MapEditor._serialize_platform` (Line: 610~621)
  - 🔗 *Calls (호출하는 것)*: `getattr, bool, int`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor.serialize_map`
- **[METHOD]** `MapEditor._serialize_structure` (Line: 623~634)
  - 🔗 *Calls (호출하는 것)*: `getattr, bool, int`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor.serialize_map`
- **[METHOD]** `MapEditor._serialize_entity` (Line: 636~649)
  - 🔗 *Calls (호출하는 것)*: `getattr, int, _infer_entity_type`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor.serialize_map`
- **[METHOD]** `MapEditor._serialize_trigger` (Line: 651~663)
  - 🔗 *Calls (호출하는 것)*: `Rect, get, bool`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor.serialize_map`
- **[METHOD]** `MapEditor._infer_entity_type` (Line: 665~670)
  - 🔗 *Calls (호출하는 것)*: `lower, getattr`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor._serialize_entity, src/map_system/map_main.py::GameMap.save_map`
- **[METHOD]** `MapEditor._draw` (Line: 672~678)
  - 🔗 *Calls (호출하는 것)*: `fill, _draw_sidebar, _draw_status, draw, _draw_grid, _draw_selection`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor.run`
- **[METHOD]** `MapEditor._draw_map_select` (Line: 680~700)
  - 🔗 *Calls (호출하는 것)*: `fill, _draw_button, get_rect, render, collidepoint, len, blit`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor.run`
- **[METHOD]** `MapEditor._draw_button` (Line: 702~708)
  - 🔗 *Calls (호출하는 것)*: `rect, blit, render, get_rect`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor._draw_map_select, src/map_editor_tool/map_editor.py::MapEditor._draw_sidebar`
- **[METHOD]** `MapEditor._draw_grid` (Line: 710~724)
  - 🔗 *Calls (호출하는 것)*: `Surface, line, int, blit, range`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor._draw`
- **[METHOD]** `MapEditor._draw_selection` (Line: 726~736)
  - 🔗 *Calls (호출하는 것)*: `rect, Rect`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor._draw`
- **[METHOD]** `MapEditor._draw_sidebar` (Line: 738~764)
  - 🔗 *Calls (호출하는 것)*: `rect, _draw_button, _text, line, collidepoint, _window_to_virtual, _draw_inspector, _draw_help, Rect, get_pos, enumerate, _draw_tool_button`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor._draw`
- **[METHOD]** `MapEditor._draw_tool_button` (Line: 766~771)
  - 🔗 *Calls (호출하는 것)*: `rect, Rect, _text`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor._draw_sidebar`
- **[METHOD]** `MapEditor._draw_inspector` (Line: 773~787)
  - 🔗 *Calls (호출하는 것)*: `int, getattr, enumerate, _text`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor._draw_sidebar`
- **[METHOD]** `MapEditor._draw_help` (Line: 789~799)
  - 🔗 *Calls (호출하는 것)*: `enumerate, _text`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor._draw_sidebar`
- **[METHOD]** `MapEditor._draw_status` (Line: 801~803)
  - 🔗 *Calls (호출하는 것)*: `rect, _text`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor._draw`
- **[METHOD]** `MapEditor._text` (Line: 805~806)
  - 🔗 *Calls (호출하는 것)*: `blit, str, render`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor._draw_help, src/map_editor_tool/map_editor.py::MapEditor._draw_inspector, src/map_editor_tool/map_editor.py::MapEditor._draw_sidebar, src/map_editor_tool/map_editor.py::MapEditor._draw_status, src/map_editor_tool/map_editor.py::MapEditor._draw_tool_button`
- **[METHOD]** `MapEditor._window_to_virtual` (Line: 808~810)
  - 🔗 *Calls (호출하는 것)*: `int`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor._draw_sidebar, src/map_editor_tool/map_editor.py::MapEditor.run`
- **[METHOD]** `MapEditor._screen_to_world` (Line: 812~814)
  - 🔗 *Calls (호출하는 것)*: `Vector2`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor._handle_event, src/map_editor_tool/map_editor.py::MapEditor._handle_mouse_down`
- **[METHOD]** `MapEditor._snap` (Line: 816~817)
  - 🔗 *Calls (호출하는 것)*: `float, round, int`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor._handle_event, src/map_editor_tool/map_editor.py::MapEditor.place_selected`
- **[METHOD]** `MapEditor._app_state` (Line: 819~824)
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor._handle_event, src/map_editor_tool/map_editor.py::MapEditor._handle_keydown, src/map_editor_tool/map_editor.py::MapEditor._handle_select_event, src/map_editor_tool/map_editor.py::MapEditor._handle_sidebar_click`

#### 🧱 Code Skeleton:
```python
class EditorObjectDefinition:
class EditorObjectRegistry:
    def register(...):
        ...
    def definitions(...):
        ...
    def get(...):
        ...
    def ensure_defaults(...):
        ...
    def discover_fabric_definitions(...):
        ...
    def discover_fabric_definitions(...):
        ...
class MapEditor:
    def __init__(...):
        ...
    def _ensure_maps_dir(...):
        ...
    def scan_map_files(...):
        ...
    def _build_map_selection_buttons(...):
        ...
    def get_object_visibility(...):
        ...
    def calculate_placement_pos(...):
        ...
    def _handle_select_event(...):
        ...
    def load_map(...):
        ...
    def _file_to_map_name(...):
        ...
    def _map_name_to_file(...):
        ...
    def _next_new_map_file(...):
        ...
    def run(...):
        ...
    def _handle_event(...):
        ...
    def _handle_keydown(...):
        ...
    def _handle_selected_shortcuts(...):
        ...
    def _handle_mouse_down(...):
        ...
    def _handle_sidebar_click(...):
        ...
    def _update_camera(...):
        ...
    def place_selected(...):
        ...
    def find_platform_at(...):
        ...
    def delete_selected(...):
        ...
    def save_map(...):
        ...
    def load_saved_or_source(...):
        ...
    def serialize_map(...):
        ...
    def _serialize_platform(...):
        ...
    def _serialize_structure(...):
        ...
    def _serialize_entity(...):
        ...
    def _serialize_trigger(...):
        ...
    def _infer_entity_type(...):
        ...
    def _draw(...):
        ...
    def _draw_map_select(...):
        ...
    def _draw_button(...):
        ...
    def _draw_grid(...):
        ...
    def _draw_selection(...):
        ...
    def _draw_sidebar(...):
        ...
    def _draw_tool_button(...):
        ...
    def _draw_inspector(...):
        ...
    def _draw_help(...):
        ...
    def _draw_status(...):
        ...
    def _text(...):
        ...
    def _window_to_virtual(...):
        ...
    def _screen_to_world(...):
        ...
    def _snap(...):
        ...
    def _app_state(...):
        ...
```

--------------------------------------------------

### 📄 src/map_editor_tool/renderer.py
#### 🔍 내부 심볼 및 의존성 관계:
- **[CLASS]** `EditorRenderer` (Line: 5~108)
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/editor_main.py::MapEditor.__init__`
- **[METHOD]** `EditorRenderer.__init__` (Line: 10~16)
  - 🔗 *Calls (호출하는 것)*: `init, SysFont`
- **[METHOD]** `EditorRenderer.draw_text` (Line: 18~21)
  - 🔗 *Calls (호출하는 것)*: `blit, str, render`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/renderer.py::EditorRenderer.draw_sidebar_panel, src/map_editor_tool/renderer.py::EditorRenderer.draw_status_bar`
- **[METHOD]** `EditorRenderer.draw_gizmo_preview` (Line: 23~48)
  - 🔗 *Calls (호출하는 것)*: `blit, rect, Surface`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/editor_main.py::MapEditor.draw`
- **[METHOD]** `EditorRenderer.draw_sidebar_panel` (Line: 50~94)
  - 🔗 *Calls (호출하는 것)*: `rect, upper, line, draw_text, enumerate`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/editor_main.py::MapEditor.draw`
- **[METHOD]** `EditorRenderer.draw_status_bar` (Line: 96~108)
  - 🔗 *Calls (호출하는 것)*: `draw_text, rect`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/editor_main.py::MapEditor.draw`

#### 🧱 Code Skeleton:
```python
class EditorRenderer:
    def __init__(...):
        ...
    def draw_text(...):
        ...
    def draw_gizmo_preview(...):
        ...
    def draw_sidebar_panel(...):
        ...
    def draw_status_bar(...):
        ...
```

--------------------------------------------------

### 📄 src/map_system/__init__.py
*선언된 클래스나 함수가 없는 파일이거나 모듈입니다.*

--------------------------------------------------

### 📄 src/map_system/map_engine.py
#### 🔍 내부 심볼 및 의존성 관계:
- **[CLASS]** `AssetManager` (Line: 9~32)
- **[METHOD]** `AssetManager.get_image` (Line: 17~32)
  - 🔗 *Calls (호출하는 것)*: `convert_alpha, fill, abspath, load, Surface, print, convert`
  - 🎯 *Used By (나를 부르는 곳)*: `src/dialogue_system/dialogue_manager.py::DialogueManager.draw, src/map_system/map_engine.py::MapManager.load_assets`
- **[CLASS]** `EntityRegistry` (Line: 35~56)
- **[METHOD]** `EntityRegistry.register` (Line: 43~45)
  - 🔗 *Calls (호출하는 것)*: `print`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::EditorObjectRegistry.discover_fabric_definitions, src/map_editor_tool/map_editor.py::EditorObjectRegistry.ensure_defaults`
- **[METHOD]** `EntityRegistry.create` (Line: 48~56)
  - 🔗 *Calls (호출하는 것)*: `print`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor.place_selected, src/map_system/map_engine.py::MapManager._create_entity_from_data, src/map_system/map_engine.py::MapManager.execute_trigger_action, src/map_system/map_engine.py::MapManager.load_map_data, src/map_system/map_main.py::GameMap.add_platform, src/map_system/map_main.py::GameMap.execute_trigger_action, src/map_system/map_main.py::GameMap.load_map_from_json`
- **[CLASS]** `TriggerBoxInstance` (Line: 58~73)
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_system/map_engine.py::MapManager.add_trigger_box, src/map_system/map_engine.py::MapManager.load_map_data, src/map_system/map_main.py::GameMap.add_trigger_box, src/map_system/map_main.py::GameMap.load_map_from_json`
- **[METHOD]** `TriggerBoxInstance.__init__` (Line: 59~63)
  - 🔗 *Calls (호출하는 것)*: `Rect`
- **[METHOD]** `TriggerBoxInstance.to_dict` (Line: 65~73)
- **[CLASS]** `MapManager` (Line: 75~511)
- **[METHOD]** `MapManager.__init__` (Line: 81~106)
  - 🔗 *Calls (호출하는 것)*: `load_assets, load_map_data`
- **[METHOD]** `MapManager.add_trigger_box` (Line: 109~115)
  - 🔗 *Calls (호출하는 것)*: `append, TriggerBoxInstance`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/editor_main.py::MapEditor.handle_events`
- **[METHOD]** `MapManager.remove_at_position` (Line: 118~121)
  - 🔗 *Calls (호출하는 것)*: `hasattr, collidepoint`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/editor_main.py::MapEditor.handle_events`
- **[METHOD]** `MapManager.load_map_data` (Line: 123~266)
  - 🔗 *Calls (호출하는 것)*: `isinstance, str, dirname, fallback_default_map, exists, _create_entity_from_data, int, isdigit, float, append, abspath, get, TriggerBoxInstance, print_exc, Rect, join, open, print, create, extend, load`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_system/map_engine.py::MapManager.__init__`
- **[METHOD]** `MapManager._create_entity_from_data` (Line: 268~299)
  - 🔗 *Calls (호출하는 것)*: `append, hasattr, getattr, get, create`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_system/map_engine.py::MapManager.load_map_data`
- **[METHOD]** `MapManager.fallback_default_map` (Line: 301~311)
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_system/map_engine.py::MapManager.load_map_data, src/map_system/map_main.py::GameMap.load_map_from_json`
- **[METHOD]** `MapManager.load_assets` (Line: 313~334)
  - 🔗 *Calls (호출하는 것)*: `get_width, abspath, dirname, get_height, join, get_image, int, scale`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_system/map_engine.py::MapManager.__init__`
- **[METHOD]** `MapManager.register_action_handler` (Line: 336~338)
- **[METHOD]** `MapManager.execute_trigger_action` (Line: 340~358)
  - 🔗 *Calls (호출하는 것)*: `print, append, get, create`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_system/map_engine.py::MapManager.update`
- **[METHOD]** `MapManager.update` (Line: 360~412)
  - 🔗 *Calls (호출하는 것)*: `append, destroy, colliderect, hasattr, getattr, execute_trigger_action, print, Rect, update_trigger_system, on_remove, update`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_system/map_main.py::GameMap.update, src/player/player_main.py::Player.update`
- **[METHOD]** `MapManager.update_trigger_system` (Line: 414~441)
  - 🔗 *Calls (호출하는 것)*: `hasattr, getattr, execute, print, condition_check, import_module`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_system/map_engine.py::MapManager.update`
- **[METHOD]** `MapManager.draw` (Line: 443~486)
  - 🔗 *Calls (호출하는 것)*: `float, append, _draw_x_tiled, get_width, sort, hasattr, get_height, _draw_2d_tiled, getattr, int, draw, ceil, floor, blit, range`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/editor_main.py::MapEditor.draw, src/map_editor_tool/map_editor.py::MapEditor._draw, src/map_system/map_main.py::GameMap.draw`
- **[METHOD]** `MapManager._draw_x_tiled` (Line: 488~496)
  - 🔗 *Calls (호출하는 것)*: `blit, range, ceil, get_width`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_system/map_engine.py::MapManager.draw, src/map_system/map_main.py::GameMap.draw`
- **[METHOD]** `MapManager._draw_2d_tiled` (Line: 498~511)
  - 🔗 *Calls (호출하는 것)*: `float, get_width, get_height, ceil, blit, range`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_system/map_engine.py::MapManager.draw, src/map_system/map_main.py::GameMap.draw`

#### 🧱 Code Skeleton:
```python
class AssetManager:
    def get_image(...):
        ...
class EntityRegistry:
    def register(...):
        ...
    def create(...):
        ...
class TriggerBoxInstance:
    def __init__(...):
        ...
    def to_dict(...):
        ...
class MapManager:
    def __init__(...):
        ...
    def add_trigger_box(...):
        ...
    def remove_at_position(...):
        ...
    def load_map_data(...):
        ...
    def _create_entity_from_data(...):
        ...
    def fallback_default_map(...):
        ...
    def load_assets(...):
        ...
    def register_action_handler(...):
        ...
    def execute_trigger_action(...):
        ...
    def update(...):
        ...
    def update_trigger_system(...):
        ...
    def draw(...):
        ...
    def _draw_x_tiled(...):
        ...
    def _draw_2d_tiled(...):
        ...
```

--------------------------------------------------

### 📄 src/map_system/map_main.py
#### 🔍 내부 심볼 및 의존성 관계:
- **[CLASS]** `GameMap` (Line: 21~683)
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/editor_main.py::MapEditor.__init__, src/map_editor_tool/map_editor.py::MapEditor.load_map, src/map_editor_tool/map_editor.py::MapEditor.load_saved_or_source`
- **[METHOD]** `GameMap.__init__` (Line: 22~45)
  - 🔗 *Calls (호출하는 것)*: `load_map_assets, build_map, load_map_from_json`
- **[METHOD]** `GameMap.load_map_from_json` (Line: 47~121)
  - 🔗 *Calls (호출하는 것)*: `isinstance, str, dirname, startswith, exit, fallback_default_map, isdigit, float, append, abspath, get, TriggerBoxInstance, normpath, print_exc, MapVariables, join, open, print, create, load`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_system/map_main.py::GameMap.__init__, src/map_system/map_main.py::GameMap.load_map`
- **[METHOD]** `GameMap.register_action_handler` (Line: 123~125)
- **[METHOD]** `GameMap.load_map_assets` (Line: 127~167)
  - 🔗 *Calls (호출하는 것)*: `convert_alpha, float, fill, get_width, convert, dirname, abspath, get_height, load, join, int, Surface, print, scale`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_system/map_main.py::GameMap.__init__`
- **[METHOD]** `GameMap.build_map` (Line: 169~242)
  - 🔗 *Calls (호출하는 것)*: `float, isinstance, append, str, get_width, hasattr, get_height, Platform, get, int, print, extend, ceil, bool, Rect, range`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_system/map_main.py::GameMap.__init__, src/map_system/map_main.py::GameMap.load_map`
- **[METHOD]** `GameMap.register_action_handler` (Line: 244~245)
- **[METHOD]** `GameMap.execute_trigger_action` (Line: 247~259)
  - 🔗 *Calls (호출하는 것)*: `append, get, create`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_system/map_engine.py::MapManager.update`
- **[METHOD]** `GameMap.update` (Line: 261~327)
  - 🔗 *Calls (호출하는 것)*: `start_dialogue, colliderect, hasattr, getattr, get, update_with_dt, print, Rect, get_instance, update`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_system/map_engine.py::MapManager.update, src/player/player_main.py::Player.update`
- **[METHOD]** `GameMap.draw` (Line: 329~473)
  - 🔗 *Calls (호출하는 것)*: `float, append, _draw_x_tiled, get_width, sort, hasattr, get_height, _draw_2d_tiled, getattr, int, draw, ceil, floor, blit, range`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/editor_main.py::MapEditor.draw, src/map_editor_tool/map_editor.py::MapEditor._draw, src/map_system/map_engine.py::MapManager.draw`
- **[METHOD]** `GameMap.update_trigger_system` (Line: 475~493)
  - 🔗 *Calls (호출하는 것)*: `hasattr, getattr, execute, print, condition_check, import_module`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_system/map_engine.py::MapManager.update`
- **[METHOD]** `GameMap.fallback_default_map` (Line: 495~517)
  - 🔗 *Calls (호출하는 것)*: `MapVariables`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_system/map_engine.py::MapManager.load_map_data, src/map_system/map_main.py::GameMap.load_map_from_json`
- **[METHOD]** `GameMap.add_platform` (Line: 519~549)
  - 🔗 *Calls (호출하는 것)*: `hasattr, Platform, append, create`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/editor_main.py::MapEditor.handle_events`
- **[METHOD]** `GameMap.add_trigger_box` (Line: 551~561)
  - 🔗 *Calls (호출하는 것)*: `hasattr, append, TriggerBoxInstance`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/editor_main.py::MapEditor.handle_events`
- **[METHOD]** `GameMap.remove_at_position` (Line: 563~569)
  - 🔗 *Calls (호출하는 것)*: `hasattr, collidepoint`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/editor_main.py::MapEditor.handle_events`
- **[METHOD]** `GameMap._infer_entity_type` (Line: 571~574)
  - 🔗 *Calls (호출하는 것)*: `lower`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor._serialize_entity, src/map_system/map_main.py::GameMap.save_map`
- **[METHOD]** `GameMap.save_map` (Line: 576~677)
  - 🔗 *Calls (호출하는 것)*: `isinstance, str, dirname, startswith, dump, bool, replace, exists, int, isdigit, abspath, hasattr, getattr, get, makedirs, remove, write, join, _infer_entity_type, open`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/editor_main.py::MapEditor.handle_events, src/map_editor_tool/map_editor.py::MapEditor._handle_keydown, src/map_editor_tool/map_editor.py::MapEditor._handle_sidebar_click`
- **[METHOD]** `GameMap.load_map` (Line: 679~683)
  - 🔗 *Calls (호출하는 것)*: `build_map, load_map_from_json`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/editor_main.py::MapEditor.handle_events, src/map_editor_tool/map_editor.py::MapEditor.__init__, src/map_editor_tool/map_editor.py::MapEditor._handle_select_event`

#### 🧱 Code Skeleton:
```python
class GameMap:
    def __init__(...):
        ...
    def load_map_from_json(...):
        ...
    def register_action_handler(...):
        ...
    def load_map_assets(...):
        ...
    def build_map(...):
        ...
    def register_action_handler(...):
        ...
    def execute_trigger_action(...):
        ...
    def update(...):
        ...
    def draw(...):
        ...
    def update_trigger_system(...):
        ...
    def fallback_default_map(...):
        ...
    def add_platform(...):
        ...
    def add_trigger_box(...):
        ...
    def remove_at_position(...):
        ...
    def _infer_entity_type(...):
        ...
    def save_map(...):
        ...
    def load_map(...):
        ...
```

--------------------------------------------------

### 📄 src/map_system/map_settings.py
*선언된 클래스나 함수가 없는 파일이거나 모듈입니다.*

--------------------------------------------------

### 📄 src/map_system/variables.py
#### 🔍 내부 심볼 및 의존성 관계:
- **[CLASS]** `MapVariables` (Line: 6~49)
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_system/map_main.py::GameMap.fallback_default_map, src/map_system/map_main.py::GameMap.load_map_from_json`
- **[METHOD]** `MapVariables.__init__` (Line: 7~49)
  - 🔗 *Calls (호출하는 것)*: `float, isinstance, getattr, get, ceil`

#### 🧱 Code Skeleton:
```python
class MapVariables:
    def __init__(...):
        ...
```

--------------------------------------------------

### 📄 src/platform_system/__init__.py
*선언된 클래스나 함수가 없는 파일이거나 모듈입니다.*

--------------------------------------------------

### 📄 src/platform_system/platform_main.py
#### 🔍 내부 심볼 및 의존성 관계:
- **[CLASS]** `Platform` (Line: 7~33)
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor.place_selected, src/map_system/map_main.py::GameMap.add_platform, src/map_system/map_main.py::GameMap.build_map`
- **[METHOD]** `Platform.__init__` (Line: 8~10)
  - 🔗 *Calls (호출하는 것)*: `PlatformVariables, load_image`
- **[METHOD]** `Platform.load_image` (Line: 12~24)
  - 🔗 *Calls (호출하는 것)*: `convert_alpha, abspath, dirname, load, join, print, exit, scale, quit`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/map_editor.py::MapEditor._handle_selected_shortcuts, src/platform_system/platform_main.py::Platform.__init__`
- **[METHOD]** `Platform.update` (Line: 26~27)
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_system/map_engine.py::MapManager.update, src/map_system/map_main.py::GameMap.update, src/player/player_main.py::Player.update`
- **[METHOD]** `Platform.draw` (Line: 29~33)
  - 🔗 *Calls (호출하는 것)*: `blit`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/editor_main.py::MapEditor.draw, src/map_editor_tool/map_editor.py::MapEditor._draw, src/map_system/map_engine.py::MapManager.draw, src/map_system/map_main.py::GameMap.draw`

#### 🧱 Code Skeleton:
```python
class Platform:
    def __init__(...):
        ...
    def load_image(...):
        ...
    def update(...):
        ...
    def draw(...):
        ...
```

--------------------------------------------------

### 📄 src/platform_system/platform_settings.py
*선언된 클래스나 함수가 없는 파일이거나 모듈입니다.*

--------------------------------------------------

### 📄 src/platform_system/variables.py
#### 🔍 내부 심볼 및 의존성 관계:
- **[CLASS]** `PlatformVariables` (Line: 4~33)
  - 🎯 *Used By (나를 부르는 곳)*: `src/platform_system/platform_main.py::Platform.__init__`
- **[METHOD]** `PlatformVariables.__init__` (Line: 5~33)

#### 🧱 Code Skeleton:
```python
class PlatformVariables:
    def __init__(...):
        ...
```

--------------------------------------------------

### 📄 src/player/__init__.py
*선언된 클래스나 함수가 없는 파일이거나 모듈입니다.*

--------------------------------------------------

### 📄 src/player/asset_loader.py
#### 🔍 내부 심볼 및 의존성 관계:
- **[CLASS]** `PlayerAssetLoader` (Line: 6~70)
  - 🎯 *Used By (나를 부르는 곳)*: `src/player/player_main.py::Player.__init__`
- **[METHOD]** `PlayerAssetLoader.__init__` (Line: 7~10)
  - 🔗 *Calls (호출하는 것)*: `load_all_assets`
- **[METHOD]** `PlayerAssetLoader.load_all_assets` (Line: 12~60)
  - 🔗 *Calls (호출하는 것)*: `convert_alpha, abspath, dirname, load, join, _load_series, print, exit, scale, quit`
  - 🎯 *Used By (나를 부르는 곳)*: `src/player/asset_loader.py::PlayerAssetLoader.__init__`
- **[METHOD]** `PlayerAssetLoader._load_series` (Line: 62~70)
  - 🔗 *Calls (호출하는 것)*: `convert_alpha, scale, append, join, load`
  - 🎯 *Used By (나를 부르는 곳)*: `src/player/asset_loader.py::PlayerAssetLoader.load_all_assets`

#### 🧱 Code Skeleton:
```python
class PlayerAssetLoader:
    def __init__(...):
        ...
    def load_all_assets(...):
        ...
    def _load_series(...):
        ...
```

--------------------------------------------------

### 📄 src/player/combat_processor.py
#### 🔍 내부 심볼 및 의존성 관계:
- **[CLASS]** `PlayerCombatProcessor` (Line: 4~31)
  - 🎯 *Used By (나를 부르는 곳)*: `src/player/player_main.py::Player.__init__`
- **[METHOD]** `PlayerCombatProcessor.process` (Line: 5~31)
  - 🔗 *Calls (호출하는 것)*: `Rect`
  - 🎯 *Used By (나를 부르는 곳)*: `src/player/player_main.py::Player.update`

#### 🧱 Code Skeleton:
```python
class PlayerCombatProcessor:
    def process(...):
        ...
```

--------------------------------------------------

### 📄 src/player/input_handler.py
#### 🔍 내부 심볼 및 의존성 관계:
- **[CLASS]** `PlayerInputHandler` (Line: 4~66)
  - 🎯 *Used By (나를 부르는 곳)*: `src/player/player_main.py::Player.__init__`
- **[METHOD]** `PlayerInputHandler.__init__` (Line: 5~6)
- **[METHOD]** `PlayerInputHandler.update` (Line: 8~48)
  - 🔗 *Calls (호출하는 것)*: `get_pressed, trigger_attack`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_system/map_engine.py::MapManager.update, src/map_system/map_main.py::GameMap.update, src/player/player_main.py::Player.update`
- **[METHOD]** `PlayerInputHandler.trigger_attack` (Line: 50~66)
  - 🎯 *Used By (나를 부르는 곳)*: `src/player/input_handler.py::PlayerInputHandler.update`

#### 🧱 Code Skeleton:
```python
class PlayerInputHandler:
    def __init__(...):
        ...
    def update(...):
        ...
    def trigger_attack(...):
        ...
```

--------------------------------------------------

### 📄 src/player/motions/__init__.py
*선언된 클래스나 함수가 없는 파일이거나 모듈입니다.*

--------------------------------------------------

### 📄 src/player/motions/air_motions.py
#### 🔍 내부 심볼 및 의존성 관계:
- **[CLASS]** `AirMotions` (Line: 4~12)
  - 🎯 *Used By (나를 부르는 곳)*: `src/player/player_main.py::Player.__init__`
- **[METHOD]** `AirMotions.handle_state` (Line: 5~12)
  - 🎯 *Used By (나를 부르는 곳)*: `src/player/player_main.py::Player.update_animation_state`

#### 🧱 Code Skeleton:
```python
class AirMotions:
    def handle_state(...):
        ...
```

--------------------------------------------------

### 📄 src/player/motions/attack_motions.py
#### 🔍 내부 심볼 및 의존성 관계:
- **[CLASS]** `AttackMotions` (Line: 4~14)
  - 🎯 *Used By (나를 부르는 곳)*: `src/player/player_main.py::Player.__init__`
- **[METHOD]** `AttackMotions.handle_state` (Line: 5~14)
  - 🎯 *Used By (나를 부르는 곳)*: `src/player/player_main.py::Player.update_animation_state`

#### 🧱 Code Skeleton:
```python
class AttackMotions:
    def handle_state(...):
        ...
```

--------------------------------------------------

### 📄 src/player/motions/ground_motions.py
#### 🔍 내부 심볼 및 의존성 관계:
- **[CLASS]** `GroundMotions` (Line: 4~13)
  - 🎯 *Used By (나를 부르는 곳)*: `src/player/player_main.py::Player.__init__`
- **[METHOD]** `GroundMotions.handle_state` (Line: 5~13)
  - 🎯 *Used By (나를 부르는 곳)*: `src/player/player_main.py::Player.update_animation_state`

#### 🧱 Code Skeleton:
```python
class GroundMotions:
    def handle_state(...):
        ...
```

--------------------------------------------------

### 📄 src/player/motions/motion_base.py
#### 🔍 내부 심볼 및 의존성 관계:
- **[CLASS]** `MotionBase` (Line: 2~8)
- **[METHOD]** `MotionBase.__init__` (Line: 3~4)
- **[METHOD]** `MotionBase.handle_state` (Line: 6~8)
  - 🎯 *Used By (나를 부르는 곳)*: `src/player/player_main.py::Player.update_animation_state`

#### 🧱 Code Skeleton:
```python
class MotionBase:
    def __init__(...):
        ...
    def handle_state(...):
        ...
```

--------------------------------------------------

### 📄 src/player/physics_processor.py
#### 🔍 내부 심볼 및 의존성 관계:
- **[CLASS]** `PlayerPhysicsProcessor` (Line: 5~43)
  - 🎯 *Used By (나를 부르는 곳)*: `src/player/player_main.py::Player.__init__`
- **[METHOD]** `PlayerPhysicsProcessor.process` (Line: 6~43)
  - 🔗 *Calls (호출하는 것)*: `hasattr, colliderect, Rect`
  - 🎯 *Used By (나를 부르는 곳)*: `src/player/player_main.py::Player.update`

#### 🧱 Code Skeleton:
```python
class PlayerPhysicsProcessor:
    def process(...):
        ...
```

--------------------------------------------------

### 📄 src/player/player_main.py
#### 🔍 내부 심볼 및 의존성 관계:
- **[CLASS]** `Player` (Line: 12~117)
- **[METHOD]** `Player.__init__` (Line: 13~27)
  - 🔗 *Calls (호출하는 것)*: `PlayerAssetLoader, PlayerCombatProcessor, PlayerVariables, PlayerInputHandler, PlayerPhysicsProcessor, AirMotions, GroundMotions, AttackMotions`
- **[METHOD]** `Player.update_animation_state` (Line: 29~40)
  - 🔗 *Calls (호출하는 것)*: `handle_state`
  - 🎯 *Used By (나를 부르는 곳)*: `src/player/player_main.py::Player.update`
- **[METHOD]** `Player.update` (Line: 42~88)
  - 🔗 *Calls (호출하는 것)*: `update_animation_state, get_pressed, getattr, get, update, len, process`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_system/map_engine.py::MapManager.update, src/map_system/map_main.py::GameMap.update`
- **[METHOD]** `Player.draw` (Line: 90~117)
  - 🔗 *Calls (호출하는 것)*: `flip, get, len, blit, min`
  - 🎯 *Used By (나를 부르는 곳)*: `src/map_editor_tool/editor_main.py::MapEditor.draw, src/map_editor_tool/map_editor.py::MapEditor._draw, src/map_system/map_engine.py::MapManager.draw, src/map_system/map_main.py::GameMap.draw`

#### 🧱 Code Skeleton:
```python
class Player:
    def __init__(...):
        ...
    def update_animation_state(...):
        ...
    def update(...):
        ...
    def draw(...):
        ...
```

--------------------------------------------------

### 📄 src/player/variables.py
#### 🔍 내부 심볼 및 의존성 관계:
- **[CLASS]** `PlayerVariables` (Line: 4~70)
  - 🎯 *Used By (나를 부르는 곳)*: `src/player/player_main.py::Player.__init__`
- **[METHOD]** `PlayerVariables.__init__` (Line: 5~56)
- **[METHOD]** `PlayerVariables.take_damage` (Line: 58~64)
  - 🔗 *Calls (호출하는 것)*: `max`
  - 🎯 *Used By (나를 부르는 곳)*: `src/enemy/enemys/test_enemy1/test_enemy1_main.py::TestEnemy1.perform_attack`
- **[METHOD]** `PlayerVariables.heal` (Line: 66~70)
  - 🔗 *Calls (호출하는 것)*: `min`

#### 🧱 Code Skeleton:
```python
class PlayerVariables:
    def __init__(...):
        ...
    def take_damage(...):
        ...
    def heal(...):
        ...
```

--------------------------------------------------

### 📄 src/settings.py
*선언된 클래스나 함수가 없는 파일이거나 모듈입니다.*

--------------------------------------------------

