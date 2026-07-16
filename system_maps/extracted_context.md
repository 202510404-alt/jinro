# ==========================================================================
# 🎯 AI GLOBAL GUIDELINES: 코드 무결성 및 디버깅 중심 가이드
# [SCAN_MODE] EXTRACTION_TARGET_PROJECT
# ==========================================================================
# 📄 [요청 1] TARGET: extraction_target_project/map_editor_tool/selection.py (45-85라인)
# ----------------------------------------------------------
```python
        editor.selected_platform = None
        editor.status_message = "Deleted selected platform"

    # 2. 엔티티 컨테이너에서 제거 시도
    elif hasattr(editor.map_manager, "entities") and editor.selected_platform in editor.map_manager.entities:
        editor.map_manager.entities.remove(editor.selected_platform)
        editor.selected_platform = None
        editor.status_message = "Deleted selected entity unit"


def place_selected(editor, world):
    if not editor.palette:
        return
    definition = editor.palette[editor.palette_index]
    data = dict(definition.defaults)

    # 🧱 [분기 1] 순정 지형 플랫폼 생성 로직 (인자 규격 유지)
    if definition.category == "platform":
        data.setdefault("width", 240)
        data.setdefault("height", 40)
        platform = EntityRegistry.create(
            definition.factory_type,
            x=editor._snap(world.x),
            y=editor._snap(world.y),
            width=data["width"],
            height=data["height"],
            is_visible=data.get("is_visible", True),
            can_pass_through=data.get("can_pass_through", False),
        )
        if not platform and definition.factory_type == "platform":
            from platform_system.platform_main import Platform
            platform = Platform(
                x=editor._snap(world.x),
                y=editor._snap(world.y),
                width=data["width"],
                height=data["height"],
                is_visible=data.get("is_visible", True),
                can_pass_through=data.get("can_pass_through", False),
            )
        if platform:
            platform.type = definition.factory_type
```
