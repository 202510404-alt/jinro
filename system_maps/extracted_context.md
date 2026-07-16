# ==========================================================================
# 🎯 AI GLOBAL GUIDELINES: 코드 무결성 및 디버깅 중심 가이드
# [SCAN_MODE] EXTRACTION_TARGET_PROJECT
# ==========================================================================
# 📄 [요청 1] TARGET: extraction_target_project/map_editor_tool/serializer.py (100-127라인)
# ----------------------------------------------------------
```python
def _serialize_structure(editor, struct):
    vars_obj = struct.vars
    return {
        "type": getattr(struct, "type", "platform"),
        "x": int(vars_obj.x),
        "y": int(vars_obj.y),
        "width": int(vars_obj.width),
        "height": int(vars_obj.height),
        "is_visible": bool(vars_obj.is_visible),
        "can_pass_through": bool(getattr(vars_obj, "passable_from_bottom", False) or getattr(vars_obj, "can_pass_through", False)),
        "z_index": int(getattr(struct, "z_index", 2)),
    }


def _serialize_entity(editor, entity):
    vars_obj = getattr(entity, "vars", None)

    # 타입 추론의 무결성을 확보하기 위한 폴백 처리
    entity_type = _infer_entity_type(editor, entity)
    if not entity_type and entity.__class__.__name__ == "DummyEnemy":
        entity_type = "dummy_enemy"

    return {
        "type": entity_type,
        "x": int(getattr(vars_obj, "x", 0)),
        "y": int(getattr(vars_obj, "y", 0)),
        "z_index": int(getattr(entity, "z_index", 3)),
    }
```
