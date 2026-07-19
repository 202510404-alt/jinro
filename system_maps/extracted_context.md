# ==========================================================================
# 🎯 AI GLOBAL GUIDELINES: 코드 무결성 및 디버깅 중심 가이드
# [SCAN_MODE] EXTRACTION_TARGET_PROJECT
# ==========================================================================
# 📄 [요청 1] TARGET: extraction_target_project/player/asset_loader.py (12-60라인)
# ----------------------------------------------------------
```python
    def load_all_assets(self, vars_obj):
        # 🌟 현재 파일(src/player/asset_loader.py) 위치 기준 상위의 src/ 폴더 절대 경로 추출
        src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 정확히 src/assets/images/player 경로 조립
        base_dir = os.path.join(src_dir, "assets", "images", "player")
        move_dir = os.path.join(base_dir, "player_move")
        effect_dir = os.path.join(base_dir, "attack_effect")
        
        try:
            # 🎬 1. 캐릭터 모션 이미지 로드 (여러 장의 프레임을 리스트로 바인딩)
            self.images = {
                # 대기: 1 -> 2 -> 3
                "IDLE": self._load_series(move_dir, ["player_stand1.png", "player_stand2.png", "player_stand3.png"], vars_obj.width, vars_obj.height),
                
                # 이동/달리기: 1 -> 2 -> 3 (동일한 3장 애니메이션 시퀀스 공유)
                "WALK": self._load_series(move_dir, ["player_run1.png", "player_run2.png", "player_run3.png"], vars_obj.width, vars_obj.height),
                "RUN": self._load_series(move_dir, ["player_run1.png", "player_run2.png", "player_run3.png"], vars_obj.width, vars_obj.height),
                
                # 점프 시작 찰나 (W 누른 순간)
                "READY_JUMP": self._load_series(move_dir, ["player_readyjump.png"], vars_obj.width, vars_obj.height),
                
                # 공중 체공 전체 (상승/하강 전체 루프): 1 -> 2 -> 3
                "JUMP_UP": self._load_series(move_dir, ["player_jump1.png", "player_jump2.png", "player_jump3.png"], vars_obj.width, vars_obj.height),
                "FALL": self._load_series(move_dir, ["player_jump1.png", "player_jump2.png", "player_jump3.png"], vars_obj.width, vars_obj.height),
                
                # ⚔️ 기존 공격 모션 (애니메이션 연동 전까지 첫 번째 프레임으로 안전 유지)
                "ATTACK_1": self._load_series(move_dir, ["player_stand1.png"], vars_obj.width, vars_obj.height),
                "ATTACK_2": self._load_series(move_dir, ["player_stand1.png"], vars_obj.width, vars_obj.height),
                "ATTACK_3": self._load_series(move_dir, ["player_stand1.png"], vars_obj.width, vars_obj.height)
            }

            # 🧱 2. 공격 콤보 이펙트 이미지 로드
            self.effect_images = {
                1: pygame.image.load(os.path.join(effect_dir, "effect_hit1.png")).convert_alpha(),
                2: pygame.image.load(os.path.join(effect_dir, "effect_hit2.png")).convert_alpha(),
                3: pygame.image.load(os.path.join(effect_dir, "effect_hit3.png")).convert_alpha()
            }
            # 원본과 완벽히 동일하게 이펙트 규격 자동화 (플레이어 너비의 2배 스케일링)
            for step in self.effect_images:
                self.effect_images[step] = pygame.transform.scale(
                    self.effect_images[step], (vars_obj.width * 2, vars_obj.height)
                )

        except pygame.error as e:
            print(f"\n❌ 에러: 플레이어 또는 이펙트 에셋 로드 실패! ({e})")
            print(f"참조 실패한 디렉터리: {base_dir}")
            pygame.quit()
            sys.exit()
```
