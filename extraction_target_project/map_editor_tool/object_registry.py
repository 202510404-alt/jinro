import json
import os
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class EditorObjectDefinition:
    type_id: str
    label: str
    category: str
    factory_type: str
    defaults: dict = field(default_factory=dict)
    serializer: Callable | None = None


class EditorObjectRegistry:
    _definitions: dict[str, EditorObjectDefinition] = {}

    @classmethod
    def register(cls, definition: EditorObjectDefinition):
        cls._definitions[definition.type_id] = definition

    @classmethod
    def definitions(cls):
        return list(cls._definitions.values())

    @classmethod
    def get(cls, type_id):
        return cls._definitions.get(type_id)

    @classmethod
    def ensure_defaults(cls):
         if "platform.basic" not in cls._definitions:
             cls.register(
                 EditorObjectDefinition(
                     type_id="platform.basic",
                     label="Platform",
                     category="platform",
                     factory_type="platform",
                     defaults={"width": 240, "height": 40, "z_index": 2}
                 )
             )
         # 🎯 더미 엔티티 생성 실패 방지를 위한 기본 명세 강제 등록 보장
         if "enemy.dummy" not in cls._definitions:
             cls.register(
                 EditorObjectDefinition(
                     type_id="enemy.dummy",
                     label="Dummy Enemy",
                     category="enemy",
                     factory_type="dummy",
                     defaults={"z_index": 3}
                 )
             )
         # 🎯 더미 엔티티 생성 실패 방지를 위한 기본 명세 강제 등록 보장
         if "enemy.dummy" not in cls._definitions:
             cls.register(
                 EditorObjectDefinition(
                     type_id="enemy.dummy",
                     label="Dummy Enemy",
                     category="enemy",
                     factory_type="dummy",
                     defaults={"z_index": 3}
                 )
             )
    
    def discover_fabric_definitions(cls):
        src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        candidates = [
            os.path.join(src_dir, "fabric_system", "editor_objects.json"),
            os.path.join(src_dir, "fabric", "editor_objects.json"),
        ]
        for path in candidates:
            if not os.path.exists(path):
                continue
            try:
                with open(path, "r", encoding="utf-8") as f:
                    payload = json.load(f)
                for item in payload.get("objects", []):
                    cls.register(
                        EditorObjectDefinition(
                            type_id=item["type_id"],
                            label=item.get("label", item["type_id"]),
                            category=item.get("category", "fabric"),
                            factory_type=item.get("factory_type", item["type_id"]),
                            defaults=item.get("defaults", {}),
                        )
                    )
            except (KeyError, TypeError, json.JSONDecodeError) as exc:
                print(f"[MapEditor] fabric palette load skipped: {path} ({exc})")

    @classmethod
    def discover_fabric_definitions(cls):
        src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        candidates = [
            os.path.join(src_dir, "fabric_system", "editor_objects.json"),
            os.path.join(src_dir, "fabric", "editor_objects.json"),
        ]
        for path in candidates:
            if not os.path.exists(path):
                continue
            try:
                with open(path, "r", encoding="utf-8") as f:
                    payload = json.load(f)
                for item in payload.get("objects", []):
                    cls.register(
                        EditorObjectDefinition(
                            type_id=item["type_id"],
                            label=item.get("label", item["type_id"]),
                            category=item.get("category", "fabric"),
                            factory_type=item.get("factory_type", item["type_id"]),
                            defaults=item.get("defaults", {}),
                        )
                    )
            except (KeyError, TypeError, json.JSONDecodeError) as exc:
                print(f"[MapEditor] fabric palette load skipped: {path} ({exc})")
