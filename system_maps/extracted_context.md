# ==========================================================================
# 🎯 AI GLOBAL GUIDELINES: 코드 무결성 및 디버깅 중심 가이드
# [SCAN_MODE] EXTRACTION_TARGET_PROJECT
# ==========================================================================
# 📄 [요청 1] TARGET: extraction_target_project/map_system/map_main.py (270-336라인)
# ----------------------------------------------------------
```python
    def update(self, dt, player_obj):
        """main.py의 호출 규격(dt, player_obj)에 맞춘 맵 전체 요소 실시간 업데이트 프로토콜"""
        for entity in self.entities:
            # 1. 엔티티가 dt 기반 업데이트(update_with_dt)를 지원하는지 먼저 확인
            if hasattr(entity, "update_with_dt"):
                try:
                    # 맵 정보(self)와 dt를 같이 전달
                    entity.update_with_dt(player_obj, self.platforms, self, dt)
                except Exception as e:
                    print(f"⚠️ [GameMap] 엔티티 dt 업데이트 중 오류 발생: {e}")
            
            # 2. 지원하지 않고 일반 update만 있다면 기존 규칙대로 self(지형 정보)를 포함하여 호출
            elif hasattr(entity, "update"):
                try:
                    entity.update(player_obj, self.platforms, self)
                except Exception as e:
                    print(f"⚠️ [GameMap] 엔티티 일반 업데이트 중 오류 발생: {e}")
            
            # 2. 전용 메서드가 없고 일반 update만 있다면 이전 규칙대로 self(지형 정보)를 포함하여 호출
            elif hasattr(entity, "update"):
                try:
                    entity.update(player_obj, self.platforms, self)
                except Exception as e:
                    print(f"⚠️ [GameMap] 엔티티 일반 업데이트 중 오류 발생: {e}")
            
            # 2. 전용 메서드가 없고 일반 update만 있다면 이전 규칙대로 self(지형 정보)를 포함하여 호출
            elif hasattr(entity, "update"):
                try:
                    entity.update(player_obj, self.platforms, self)
                except Exception as e:
                    print(f"⚠️ [GameMap] 엔티티 일반 업데이트 중 오류 발생: {e}")
        # 트리거 박스 인스턴스 실시간 업데이트 보장 
        for box in self.trigger_boxes:
            if hasattr(box, "update"):
                try:
                    box.update(dt)
                except Exception as e:
                    print(f"⚠️ [GameMap] 트리거 박스 업데이트 실패: {e}")

        # 실시간 영역 진입형 트리거(Triggers) 검사 로직 무결성 전개
        if hasattr(player_obj, 'vars') and hasattr(player_obj.vars, 'x'):
            p_rect = pygame.Rect(player_obj.vars.x, player_obj.vars.y, 
                                 getattr(player_obj.vars, 'width', 40), 
                                 getattr(player_obj.vars, 'height', 60))
            
            for trigger in self.triggers:
                if not trigger.get("triggered", False):
                    bounds = trigger.get("bounds")
                    if bounds and p_rect.colliderect(bounds):
                        trigger["triggered"] = True
                        action = trigger.get("action", {})
                        a_type = action.get("type")
                        
                        print(f"🎬 [GameMap] 트리거 발동 -> 타입: '{a_type}'")
                        
                        # 대사 트리거 연동 프로토콜
                        if a_type == "start_dialogue":
                            d_id = action.get("dialogue_id")
                            from dialogue_system.dialogue_manager import DialogueManager
                            DialogueManager.get_instance().start_dialogue(d_id)
                        
                        # 핸들러 확장성 대응
                        if a_type in self.action_handlers:
                            try:
                                self.action_handlers[a_type](action)
                            except Exception as e:
                                print(f"⚠️ [GameMap] 액션 핸들러 실행 실패: {e}")
```

# 📄 [요청 2] TARGET: extraction_target_project/enemy/enemys/dummy/dummy_main.py (76-91라인)
# ----------------------------------------------------------
```python
    def update(self, player_obj, platforms, game_map=None):
        """인게임 실시간 피격 판정과 함께, 플레이어와 동일한 규칙의 물리 업데이트 처리"""
        if self.vars.hp <= 0:
            return
        
        # 1. 플레이어 피격 체크
        self.check_player_attack(player_obj)

        # 2. 플레이어의 PhysicsProcessor와 완벽히 동일한 메커니즘으로 중력 및 지형 착지 연동
        self.apply_gravity_and_physics(platforms, game_map)

        # 3. 피격 경직 타이머
        if self.vars.is_hit:
            self.vars.hit_timer -= 1
            if self.vars.hit_timer <= 0:
                self.vars.is_hit = False
```
