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

    # [📂 map_editor_tool/object_registry.py] 수정안

    @classmethod
    def ensure_defaults(cls):
        # 1. 지형 플랫폼 등 기본 오브젝트는 먼저 등록해둡니다.
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

        # 2. 🪐 [폴더 동적 스캔 프로토콜] enemy/enemys 폴더 내부를 실시간 탐색합니다.
        # 프로젝트 루트 기준으로 경로를 유연하게 탐색하기 위한 베이스 설정
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # 실제 적 폴더들이 위치한 물리 경로 계산
        enemys_dir = os.path.join(current_dir, "enemy", "enemys")

        if os.path.exists(enemys_dir):
            try:
                # 폴더 내부를 뒤져서 하위 폴더(디렉토리) 목록만 추출합니다.
                for folder_name in os.listdir(enemys_dir):
                    sub_path = os.path.join(enemys_dir, folder_name)
                    if os.path.isdir(sub_path) and not folder_name.startswith("__"):
                        
                        # 예: folder_name이 "test_enemy1" 이라면
                        type_id = f"enemy.{folder_name}"      # "enemy.test_enemy1"
                        # 에디터 UI에 보여줄 레이블 이름 자동 변환 ("test_enemy1" -> "Test Enemy1")
                        label = folder_name.replace("_", " ").title() 
                        
                        if type_id not in cls._definitions:
                            cls.register(
                                EditorObjectDefinition(
                                    type_id=type_id,
                                    label=label,
                                    category="enemy",
                                    factory_type=folder_name, # "test_enemy1" (serializer 및 factory 연동 이름)
                                    defaults={"z_index": 3}
                                )
                            )
                            print(f"🤖 [EditorRegistry] 동적 적 버튼 등록 성공: {label} ({type_id})")
            except Exception as e:
                print(f"⚠️ [EditorRegistry] 적 폴더 스캔 중 오류 발생: {e}")
        else:
            # 폴더를 찾을 수 없는 경우를 대비한 비상 안전 폴백 (더미 기본 등록)
            if "enemy.dummy" not in cls._definitions:
                cls.register(
                    EditorObjectDefinition(
                        type_id="enemy.dummy",
                        label="Dummy Enemy (Fallback)",
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
