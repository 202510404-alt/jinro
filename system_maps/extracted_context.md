# ==========================================================================
# 🎯 AI GLOBAL GUIDELINES: 코드 무결성 및 디버깅 중심 가이드
# [SCAN_MODE] EXTRACTION_TARGET_PROJECT
# ==========================================================================
# 📄 [요청 1] TARGET: extraction_target_project/player/motions/attack_motions.py (1-14라인)
# ----------------------------------------------------------
```python
# player/motions/attack_motions.py
from player.motions.motion_base import MotionBase

class AttackMotions(MotionBase):
    def handle_state(self, vars_obj):
        # 플레이어가 공격 중일 때만 작동
        if vars_obj.is_attacking:
            if vars_obj.combo_step == 1:
                return "ATTACK_1"
            elif vars_obj.combo_step == 2:
                return "ATTACK_2"
            elif vars_obj.combo_step == 3:
                return "ATTACK_3"
        return None
```

# 📄 [요청 2] TARGET: extraction_target_project/player/player_main.py (120-155라인)
# ----------------------------------------------------------
```python
            if self.vars.anim_timer >= delay:
                self.vars.anim_timer = 0
                self.vars.current_frame_idx = (self.vars.current_frame_idx + 1) % len(anim_list)

    def update_with_dt(self, platforms, game_map, dt, entities=None):
        """main.py의 호출 인터페이스를 지원하기 위한 update 래퍼 메서드"""
        self.update(platforms, entities=entities, game_map=game_map, dt=dt)

    def draw(self, screen, camera_offset=(0, 0)):
        """플레이어 본체 이미지와 공격 시 콤보 이펙트를 화면에 렌더링합니다."""
        ox, oy = camera_offset
        # 🎬 1. 캐릭터 본체 스프라이트 시퀀스 추출 및 출력
        anim_list = self.assets.images.get(self.vars.current_state, [])
        if not anim_list:
            return
            
        # 혹시 모를 인덱스 바운드 에러를 막기 위한 최종 안전 필터링
        idx = min(self.vars.current_frame_idx, len(anim_list) - 1)
        player_image = anim_list[idx]
        
        # 왼쪽을 바라보고 있다면 이미지 좌우 반전
        if not self.vars.facing_right:
            player_image = pygame.transform.flip(player_image, True, False)
            
        screen.blit(player_image, (self.vars.x - ox, self.vars.y - oy))
        
        # 2. ⚔️ 공격 애니메이션 중일 때 콤보 검기 이펙트 출력 (원본 로직 완벽 보존)
        if self.vars.is_attacking and self.vars.combo_step in self.assets.effect_images:
            effect_img = self.assets.effect_images[self.vars.combo_step]
            
            # 플레이어가 바라보는 방향에 맞춰 이펙트도 반전 및 위치 정렬
            if not self.vars.facing_right:
                effect_img = pygame.transform.flip(effect_img, True, False)
                screen.blit(effect_img, (self.vars.x - ox - 60, self.vars.y - oy))
            else:
                screen.blit(effect_img, (self.vars.x - ox + 30, self.vars.y - oy))
```
