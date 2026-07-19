# src/enemy/enemys/dummy/dummy_main.py
import pygame
import os
import sys
from enemy.enemys.dummy.variables import DummyVariables

DEBUG = True

class DummyEnemy:
    def __init__(self, x=0, y=0, *args, **kwargs):
        # 🎯 [기능 보존 + 호환성 확장] 어떤 데이터 규격(값, dict 등)으로 들어와도 안전하게 x, y 좌표 바인딩
        actual_x = x if x != 0 else kwargs.get("x", 0)
        actual_y = y if y != 0 else kwargs.get("y", 0)
        
        # 맵 시스템 구조에서 혹시나 데이터가 dict 통째로 들어올 경우를 대비한 2중 방어선
        if isinstance(actual_x, dict):
            actual_y = actual_x.get("y", 0)
            actual_x = actual_x.get("x", 0)

        self.vars = DummyVariables(actual_x, actual_y)
        self.load_images()
        
        # 🎯 에디터 기즈모 및 선택 영역에서 충돌 크기(50, 80)를 안전하게 측정할 수 있도록 순정 pygame.Rect 바인딩 보장
        self.rect = pygame.Rect(actual_x, actual_y, 50, 80)

    def load_images(self):
        """🌟 파일 위치와 상관없이, 실행 기준점에서 assets 폴더를 안정적으로 탐색합니다."""
        base_dir = os.path.abspath(".")
        dummy_dir = os.path.join(base_dir, "assets", "images", "enemy", "dummy")
        
        # FileNotFoundError뿐만 아니라 Pygame 자체 로드 에러(convert_alpha 등)까지 한 번에 방어하도록 호환성 개선
        try:
            self.images = {
                "IDLE": pygame.image.load(os.path.join(dummy_dir, "dummy_idle.png")).convert_alpha(),
                "HIT": pygame.image.load(os.path.join(dummy_dir, "dummy_hit.png")).convert_alpha(),
                "DEAD": pygame.image.load(os.path.join(dummy_dir, "dummy_dead.png")).convert_alpha()
            }
            for state in self.images:
                self.images[state] = pygame.transform.scale(self.images[state], (50, 80))
                
        except (FileNotFoundError, pygame.error):
            print("⚠️ 애니메이션 파일이 없거나 경로가 달라 기본 dummy.png 단일 이미지 탐색을 시도합니다.")
            try:
                single_img = pygame.image.load(os.path.join(dummy_dir, "dummy.png")).convert_alpha()
                self.images = {
                    "IDLE": pygame.transform.scale(single_img, (50, 80)),
                    "HIT": pygame.transform.scale(single_img, (50, 80)),
                    "DEAD": pygame.transform.scale(single_img, (50, 80))
                }
            except (FileNotFoundError, pygame.error):
                print("⚠️ 기본 dummy.png 마저 없어 단색 Surface 대체 비상 패치를 적용합니다.")
                # 비디오 디스플레이가 초기화되지 않은 특수 환경(에디터 백그라운드) 크래시 방지
                try:
                    surf = pygame.Surface((50, 80), pygame.SRCALPHA)
                    surf.fill((255, 100, 100))
                    self.images = {"IDLE": surf, "HIT": surf, "DEAD": surf}
                except pygame.error:
                    # Pygame 자체가 미준비 상태인 경우 프로그램이 튕기지 않게 None 처리 후 렌더러에서 우회
                    self.images = {"IDLE": None, "HIT": None, "DEAD": None}

    def check_player_attack(self, player_obj):
        """플레이어의 실시간 공격 히트박스 충돌 감지"""
        # 🎯 [구조 보환] 플레이어가 없거나(에디터 모드), 플레이어가 공격 상태가 아니면 안전하게 패스
        if not player_obj or not hasattr(player_obj, 'vars') or not player_obj.vars.is_attacking or not player_obj.vars.attack_rect:
            return

        dummy_rect = pygame.Rect(self.vars.x, self.vars.y, self.vars.width, self.vars.height)

        if dummy_rect.colliderect(player_obj.vars.attack_rect):
            if not self.vars.is_hit:
                self.vars.is_hit = True
                self.vars.hit_timer = self.vars.hit_duration
                self.vars.hp -= 10
                
                player_obj.vars.has_hit_enemy = True
                print(f"💥 더미 피격 성공! 남은 HP: {self.vars.hp}/100")

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

    def apply_gravity_and_physics(self, platforms, game_map=None):
        """PlayerPhysicsProcessor의 로직을 그대로 이식한 더미 전용 물리 엔진"""
        from settings import GROUND_Y  # 안전망용 기본 바닥 상숫값
        
        # 1. 중력 적용 및 이동 (플레이어 변수명 구조에 맞춰 vy 사용)
        # 플레이어 시펙: vars_obj.vertical_velocity += vars_obj.gravity
        self.vars.vy += 0.8  # 중력가속도 상수값 직접 부여 (필요시 self.vars.gravity 등으로 대체 가능)
        self.vars.y += self.vars.vy

        dummy_rect = pygame.Rect(self.vars.x, self.vars.y, self.vars.width, self.vars.height)
        on_sub_platform = False

        # 2. 플랫폼(발판) 충돌 검사 (플레이어의 platform.vars 구조 완전 매칭)
        if platforms:
            for platform in platforms:
                # 플랫폼의 solid 여부 체크 (플레이어 코드 준수)
                if hasattr(platform, 'vars') and not getattr(platform.vars, 'is_solid', True):
                    continue
                
                # platform.vars.x, y, width, height 추출
                if hasattr(platform, 'vars'):
                    p_x = platform.vars.x
                    p_y = platform.vars.y
                    p_w = platform.vars.width
                    p_h = platform.vars.height
                else:
                    # 혹시나 예외 케이스용 방어선
                    p_x = getattr(platform, 'x', 0)
                    p_y = getattr(platform, 'y', 0)
                    p_w = getattr(platform, 'width', 0)
                    p_h = getattr(platform, 'height', 0)

                plat_rect = pygame.Rect(p_x, p_y, p_w, p_h)
                
                if dummy_rect.colliderect(plat_rect):
                    # 위에서 아래로 떨어지는 중일 때만 착지
                    if self.vars.vy > 0:
                        if (self.vars.y + self.vars.height - self.vars.vy) <= p_y + 10:
                            self.vars.y = p_y - self.vars.height
                            self.vars.vy = 0
                            self.vars.is_grounded = True
                            on_sub_platform = True
                            break

        # 3. 메인 바닥(ground_y) 착지 검사 (플레이어 코드 핵심 이식)
        if not on_sub_platform:
            g_y = game_map.ground_y if (game_map and hasattr(game_map, 'ground_y')) else GROUND_Y
            if self.vars.y + self.vars.height >= g_y:
                self.vars.y = g_y - self.vars.height
                self.vars.vy = 0
                self.vars.is_grounded = True
            else:
                self.vars.is_grounded = False

        # 4. 최종 Rect 동기화
        self.rect.x = self.vars.x
        self.rect.y = self.vars.y

    def draw(self, screen, camera_offset=(0, 0)):
        ox, oy = camera_offset
        if self.vars.hp <= 0 or not screen:
            return 
        
        state = "IDLE"
        if self.vars.is_hit:
            state = "HIT"
            
        current_img = self.images.get(state, self.images.get("IDLE"))
        # 🎯 이미지가 성공적으로 로드된 경우에만 출력하여 크래시 완전 차단
        if current_img:
            screen.blit(current_img, (self.vars.x - ox, self.vars.y - oy))
    
    def draw_debug_overlay(self, screen, camera_offset=(0, 0)):
        """더미 엔티티의 피격 판정(AABB) 상자 및 체력 상태 메타데이터를 화면에 투영합니다."""
        if not DEBUG or self.vars.hp <= 0 or not screen:
            return

        ox, oy = camera_offset
        d_width = getattr(self.vars, 'width', 0)
        d_height = getattr(self.vars, 'height', 0)

        # 1. 🔴 DummyEnemy 피격 판정 상자(AABB) 실선 렌더링
        if d_width > 0 and d_height > 0:
            aabb_rect = pygame.Rect(self.vars.x - ox, self.vars.y - oy, d_width, d_height)
            pygame.draw.rect(screen, (255, 0, 0), aabb_rect, 2)

        # 2. 📊 실시간 체력 및 히트 상태 메타데이터 투영 (Lazy Evaluation 적용)
        try:
            font = pygame.font.SysFont("Consolas", 12)
        except:
            font = pygame.font.Font(None, 12)

        debug_texts = [
            f"HP: {self.vars.hp}/{getattr(self.vars, 'max_hp', '??')}",
            f"HIT: {self.vars.is_hit}",
            f"GND: {self.vars.is_grounded}"
        ]

        for i, text in enumerate(debug_texts):
            text_surf = font.render(text, True, (255, 0, 0))
            screen.blit(text_surf, (self.vars.x - ox, self.vars.y - oy - 15 - (i * 13)))

        # 규격화된 출력 로그 생성
        print(f"[dummy_main.py] draw_debug_overlay() -> Rendered Dummy AABB: HP={self.vars.hp}, HIT={self.vars.is_hit}")


# ==============================================================================
# 🎯 [결정적 해결] 순환 참조(Circular Import) 방지형 런타임 자동 등록 함수
# ==============================================================================
def auto_register_entity():
    """ 전역 공간이 아닌 함수 내부에서 임포트하여 상호 임포트 락(Lock)을 완전히 우회합니다. """
    try:
        from map_system.map_engine import EntityRegistry
        EntityRegistry.register("DummyEnemy", DummyEnemy)
        EntityRegistry.register("dummy_enemy", DummyEnemy)
        EntityRegistry.register("dummy", DummyEnemy)
    except (ImportError, AttributeError):
        # 메인 프로세스 초기화 순서에 의해 아직 모듈이 로드되지 않았다면 예외를 패스하여
        # 이후 맵 매니저 작동 시 정상 참조되도록 우회 유도
        pass

auto_register_entity()